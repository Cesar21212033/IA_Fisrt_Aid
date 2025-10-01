import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from utils import cargar_imagenes, mostrar_imagenes

# ================================
# 1. Cargar el modelo entrenado
# ================================
modelo = load_model("modelo_lesiones_brazos.h5")

# ================================
# 2. Definir clases
# ================================
# Asegúrate que las clases coincidan con las carpetas de entrenamiento
clases = ["cortes", "quemaduras", "golpes"]

# ================================
# 3. Cargar imagen a predecir
# ================================
# Puedes cambiar esta ruta a cualquier imagen nueva
ruta_imagen = "data/nuevas/imagen1.jpg"

if not os.path.exists(ruta_imagen):
    print(f"No se encontró la imagen: {ruta_imagen}")
else:
    img = load_img(ruta_imagen, target_size=(128,128))  # Redimensionar
    img_array = img_to_array(img) / 255.0               # Normalizar
    img_array = np.expand_dims(img_array, axis=0)       # Añadir dimensión batch

    # ================================
    # 4. Hacer predicción
    # ================================
    prediccion = modelo.predict(img_array)
    clase_idx = np.argmax(prediccion)
    probabilidad = np.max(prediccion)

    print(f"La lesión probablemente es: {clases[clase_idx]} con {probabilidad*100:.2f}% de confianza")

# ================================
# 5. Predicciones de varias imágenes en una carpeta
# ================================
ruta_carpeta = "data/nuevas/"
imagenes = [f for f in os.listdir(ruta_carpeta) if f.endswith((".jpg", ".png", ".jpeg"))]

for img_name in imagenes:
    img_path = os.path.join(ruta_carpeta, img_name)
    img = load_img(img_path, target_size=(128,128))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    pred = modelo.predict(img_array)
    clase_idx = np.argmax(pred)
    prob = np.max(pred)
    
    print(f"{img_name} → {clases[clase_idx]} ({prob*100:.2f}%)")
