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
from conexion import guardar_conversacion
from conexion import obtener_conversaciones



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
async def predict_and_train(
    file: UploadFile = File(...), 
    clase: str = Form(...),
    numero_control: str = Form(...),
    nombre_completo: str = Form(...)
):
    if clase not in clases:
        raise HTTPException(status_code=400, detail=f"La clase debe ser una de {clases}")

    # Validar que los campos obligatorios estén presentes
    if not numero_control or not numero_control.strip():
        raise HTTPException(status_code=400, detail="El número de control es obligatorio")
    if not nombre_completo or not nombre_completo.strip():
        raise HTTPException(status_code=400, detail="El nombre completo es obligatorio")

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
    resultado_bd = guardar_diagnostico(
        tipo="imagen",
        clase=clase_detectada,
        instrucciones=instrucciones_ai,
        numero_control=numero_control.strip(),
        nombre_completo=nombre_completo.strip(),
        probabilidad=probabilidad
    )
    
    # Log del resultado de guardado
    if "error" in resultado_bd:
        print(f"ERROR al guardar en BD: {resultado_bd['error']}")
    else:
        print(f"Guardado exitoso en BD: {resultado_bd.get('mensaje', 'OK')}")

    # entrenamiento incremental
    train_on_new_image(contents, clase)

    # regreso todo lo importante (incluyendo el ID del diagnóstico guardado)
    return {
        "clase": clase_detectada,
        "probabilidad": probabilidad,
        "instrucciones": instrucciones_ai,
        "diagnostico_id": resultado_bd.get("id"),  # ID del diagnóstico guardado
        "mensaje": f"Entrenamiento incremental realizado para la clase {clase}"
    }

from pydantic import BaseModel

# ==========================
# Modelo para la solicitud de análisis de síntomas por texto
# ==========================
class SymptomRequest(BaseModel):
    symptoms: str
    numero_control: str
    nombre_completo: str


# ==========================
# Endpoint para recomendaciones basadas en texto
# ==========================
@app.post("/analyze-symptoms/")
async def analyze_symptoms(request: SymptomRequest):
    texto = request.symptoms.strip().lower()

    # Validar que los campos obligatorios estén presentes
    if not request.numero_control or not request.numero_control.strip():
        raise HTTPException(status_code=400, detail="El número de control es obligatorio")
    if not request.nombre_completo or not request.nombre_completo.strip():
        raise HTTPException(status_code=400, detail="El nombre completo es obligatorio")

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
        # Para análisis de texto, no hay probabilidad, se guarda como NULL
        resultado_bd = guardar_diagnostico(
            tipo="texto",
            clase=clase_detectada,
            instrucciones=respuesta.text,
            numero_control=request.numero_control.strip(),
            nombre_completo=request.nombre_completo.strip(),
            probabilidad=None  # No hay probabilidad en análisis de texto
        )
        
        # Log del resultado de guardado
        if "error" in resultado_bd:
            print(f"ERROR al guardar en BD: {resultado_bd['error']}")
        else:
            print(f"Guardado exitoso en BD: {resultado_bd.get('mensaje', 'OK')}")

        return {
            "respuesta": respuesta.text,
            "diagnostico_id": resultado_bd.get("id")  # ID del diagnóstico guardado
        }

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

# ==========================
# Modelo para pregunta sobre diagnóstico
# ==========================
class PreguntaRequest(BaseModel):
    diagnostico_id: int
    pregunta: str
    numero_control: str
    clase_detectada: str
    instrucciones_originales: str

# ==========================
# Endpoint para hacer preguntas sobre el diagnóstico
# ==========================
@app.post("/preguntar-diagnostico/")
async def preguntar_diagnostico(request: PreguntaRequest):
    try:
        # Crear contexto para Gemini con el diagnóstico original
        contexto = f"""
        Contexto del diagnóstico:
        - Clase detectada: {request.clase_detectada}
        - Recomendaciones originales: {request.instrucciones_originales}
        
        Pregunta del usuario: {request.pregunta}
        
        Responde la pregunta del usuario basándote en el contexto del diagnóstico proporcionado.
        Mantén un tono profesional y médico. Si la pregunta no está relacionada con el diagnóstico,
        indícalo educadamente y ofrece ayuda relacionada con primeros auxilios.
        """
        
        # Generar respuesta con Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        respuesta_obj = model.generate_content(contexto)
        respuesta_texto = respuesta_obj.text

        # Guardar la conversación en la BD
        resultado_guardado = guardar_conversacion(
            diagnostico_id=request.diagnostico_id,
            numero_control=request.numero_control,
            pregunta=request.pregunta,
            respuesta=respuesta_texto
        )

        if "error" in resultado_guardado:
            print(f"Error guardando conversación: {resultado_guardado['error']}")

        return {
            "respuesta": respuesta_texto,
            "conversacion_id": resultado_guardado.get("id")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {e}")

# ==========================
# Endpoint para obtener conversaciones de un diagnóstico
# ==========================
@app.get("/conversaciones/{diagnostico_id}")
def obtener_conversaciones_endpoint(diagnostico_id: int):
    try:
        conversaciones = obtener_conversaciones(diagnostico_id)
        return conversaciones
    except Exception as e:
        return {"error": str(e)}
