from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import google.generativeai as genai  # ✅ Importación correcta

# === CONFIGURACIÓN DE GEMINI ===
GEMINI_API_KEY = "AIzaSyBcy89im5JOLDfQKLaEN9G2eTUBhl1YNzo"
genai.configure(api_key=GEMINI_API_KEY)


def recomendacion_gemini(clase_detectada: str) -> str:
    """Genera una recomendación de primeros auxilios usando Gemini."""
    try:
        prompt = f"""
        Actúa como un experto asistente de primeros auxilios. 
        La lesión ha sido clasificada por un modelo de visión artificial como: **{clase_detectada}**.

        Genera una respuesta profesional, fácil de entender, clara y concisa sobre los primeros auxilios.
        Incluye:
        1. Una breve descripción de la lesión.
        2. Tres pasos cruciales de acción inmediata (qué hacer).
        3. Una advertencia clara (qué NO hacer).

        Usa saltos de línea para mejorar la legibilidad.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")  # ✅ modelo correcto
        respuesta = model.generate_content(prompt)

        return respuesta.text  # ✅ devuelve solo el texto
    except Exception as e:
        return f"Error al generar la recomendación: {e}"


# --- Configuración base ---
app = FastAPI(title="IA First Aid API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cargar modelo de imagen ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # IA-Convolucional/
modelo_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras")

if not os.path.exists(modelo_path):
    raise FileNotFoundError(f"No se encontró el modelo en {modelo_path}")

modelo = load_model(modelo_path, compile=False)
clases = ["quemaduras", "cortadas"]

TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)


# --- Endpoint de predicción ---
@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    try:
        ruta_temp = os.path.join(TEMP_DIR, file.filename)
        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img = load_img(ruta_temp, target_size=(128, 128))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediccion = modelo.predict(img_array, verbose=0)
        clase_idx = int(np.argmax(prediccion))
        probabilidad = float(np.max(prediccion))
        clase_detectada = clases[clase_idx]

        # ✅ Llamada a Gemini
        instrucciones_ai = recomendacion_gemini(clase_detectada)

        os.remove(ruta_temp)  # eliminar imagen temporal

        return {
            "clase": clase_detectada,
            "probabilidad": probabilidad,
            "instrucciones": instrucciones_ai
        }

    except Exception as e:
        print("ERROR EN /predict/:", e)
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {e}")
