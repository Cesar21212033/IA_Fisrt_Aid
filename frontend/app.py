# app.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# --- Configuración base ---
app = FastAPI(title="IA First Aid API")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelo de imágenes ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # IA-Convolucional/
modelo_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.h5")

if not os.path.exists(modelo_path):
    raise FileNotFoundError(f"No se encontró el modelo en {modelo_path}")

modelo = load_model(modelo_path, compile=False)
clases = ["quemaduras", "cortadas"]

TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Endpoint para predicción de imagen ---
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

        os.remove(ruta_temp)

        return {
            "clase": clases[clase_idx],
            "probabilidad": probabilidad
        }

    except Exception as e:
        print("ERROR EN /predict/:", e)
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {e}")
