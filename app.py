# app.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# ================================
# FastAPI setup
# ================================
app = FastAPI()

# Permitir que el frontend haga peticiones (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# Cargar modelo
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(BASE_DIR, "modelo_quemaduras_cortadas.h5")
modelo = load_model(modelo_path)
clases = ["quemaduras", "cortadas"]

# ================================
# Carpeta temporal para imágenes
# ================================
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# ================================
# Endpoint de predicción
# ================================
@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    try:
        # Guardar imagen temporal
        ruta_temp = os.path.join(TEMP_DIR, file.filename)
        with open(ruta_temp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Procesar imagen
        img = load_img(ruta_temp, target_size=(128,128))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predicción
        prediccion = modelo.predict(img_array, verbose=0)
        clase_idx = int(np.argmax(prediccion))
        probabilidad = float(np.max(prediccion))

        # Borrar imagen temporal
        os.remove(ruta_temp)

        return {
            "clase": clases[clase_idx],
            "probabilidad": probabilidad
        }

    except Exception as e:
        return {"error": f"Ocurrió un error al procesar la imagen: {e}"}
