from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from io import BytesIO
from PIL import Image
import threading
import google.generativeai as genai
import logging
from conexion import obtener_historial
from conexion import guardar_diagnostico



# ==========================
# Config FastAPI y CORS
# ==========================
app = FastAPI(title="IA First Aid API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Rutas y proyecto
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from model import ModelManager, clases  # traigo el modelo y las clases

# ==========================
# Config Gemini API
# ==========================
GEMINI_API_KEY = "AIzaSyBcy89im5JOLDfQKLaEN9G2eTUBhl1YNzo"
genai.configure(api_key=GEMINI_API_KEY)

def recomendacion_gemini(clase_detectada: str) -> str:
    """Pido al AI que me diga qué hacer según la lesión"""
    prompt = f"""
    Actúa como un experto asistente de primeros auxilios. 
    La lesión ha sido clasificada como: **{clase_detectada}**.

    Genera una respuesta profesional, clara y concisa sobre primeros auxilios.
    Incluye:
    1. Breve descripción de la lesión.
    2. Tres pasos cruciales de acción inmediata.
    3. Una advertencia clara (qué NO hacer).
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"Error al generar la recomendación: {e}"


# ==========================
# Inicialización del modelo
# ==========================
modelo_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras")
modelo_manager = ModelManager(modelo_path)
modelo_lock = threading.Lock()  # bloqueo para evitar que varios entrenen a la vez

# ==========================
# Procesamiento de imagen
# ==========================
def procesar_imagen_memoria(contents: bytes):
    """Convierto la imagen a array listo para el modelo"""
    try:
        with Image.open(BytesIO(contents)) as img:
            img = img.convert("RGB").resize((128, 128))
            img_array = np.expand_dims(img_to_array(img) / 255.0, axis=0)
        return img_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen: {e}")


# ==========================
# Entrenamiento incremental
# ==========================
logging.basicConfig(level=logging.INFO, format="%(message)s")

def train_on_new_image(contents: bytes, clase: str):
    """Entrena rápido con la nueva imagen y reemplaza el modelo guardado"""
    try:
        img_array = procesar_imagen_memoria(contents)
        clase_idx = clases.index(clase)
        y = np.array([clase_idx])

        with modelo_lock:
            modelo_manager.model.train_on_batch(img_array, y)
            # guardo en temporal en la misma carpeta que el modelo original
            save_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas_tmp.keras")
            modelo_manager.model.save(save_path, overwrite=True)
            # reemplazo el modelo original en la raíz del proyecto
            os.replace(save_path, os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras"))
            modelo_manager.reload_model()

        logging.info(f"Entrenamiento incremental completado para la clase {clase}")

    except Exception as e:
        logging.error(f"Error en entrenamiento incremental: {e}")

from conexion import guardar_diagnostico

# ==========================
# Endpoint predict + train
# ==========================
@app.post("/predict_and_train/")
async def predict_and_train(file: UploadFile = File(...), clase: str = Form(...)):
    if clase not in clases:
        raise HTTPException(status_code=400, detail=f"La clase debe ser una de {clases}")

    # predicción
    contents = await file.read()
    img_array = procesar_imagen_memoria(contents)
    with modelo_lock:
        prediccion = modelo_manager.predict(img_array)

    clase_idx = int(np.argmax(prediccion))
    probabilidad = float(np.max(prediccion))
    clase_detectada = clases[clase_idx]

    instrucciones_ai = recomendacion_gemini(clase_detectada)

    #  Guardar en bd
    guardar_diagnostico(
        tipo="imagen",
        clase=clase_detectada,
        instrucciones=instrucciones_ai
    )

    # entrenamiento incremental
    train_on_new_image(contents, clase)

    # regreso todo lo importante
    return {
        "clase": clase_detectada,
        "probabilidad": probabilidad,
        "instrucciones": instrucciones_ai,
        "mensaje": f"Entrenamiento incremental realizado para la clase {clase}"
    }

from pydantic import BaseModel

# ==========================
# Modelo para la solicitud de análisis de síntomas por texto
# ==========================
class SymptomRequest(BaseModel):
    symptoms: str


# ==========================
# Endpoint para recomendaciones basadas en texto
# ==========================
@app.post("/analyze-symptoms/")
async def analyze_symptoms(request: SymptomRequest):
    texto = request.symptoms.strip().lower()

    # Validar que mencione extremidad y tipo de lesión
    extremidad_valida = any(x in texto for x in ["brazo", "pierna"])
    tipo_valido = any(x in texto for x in ["cortada", "corte", "quemadura"])

    if not (extremidad_valida and tipo_valido):
        raise HTTPException(
            status_code=400, 
            detail="Solo se permiten descripciones de cortadas o quemaduras en brazos o piernas."
        )

    try:
        prompt = f"""
        Actúa como un experto en primeros auxilios. Un estudiante presenta la siguiente herida:
        {request.symptoms}

        Proporciona:
        1. Breve descripción de la lesión
        2. Tres pasos cruciales de acción inmediata
        3. Advertencias claras de lo que NO se debe hacer
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        respuesta = model.generate_content(prompt)

        # =========================
        # Determinar clase detectada
        # =========================
        if "quemadura" in texto:
            clase_detectada = "quemaduras"
        elif "cortada" in texto or "corte" in texto:
            clase_detectada = "cortadas"
        else:
            clase_detectada = "desconocida"

        # =========================
        # Guardar en base de datos
        # =========================
        guardar_diagnostico(
            tipo="texto",
            clase=clase_detectada,
            instrucciones=respuesta.text
        )

        return {"respuesta": respuesta.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la recomendación: {e}")
    
    # Endpoint para historial
@app.get("/historial/")
def historial():
    try:
        registros = obtener_historial()
        return registros
    except Exception as e:
        return {"error": str(e)}
