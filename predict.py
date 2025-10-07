import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# ================================
# 1. Cargar el modelo entrenado
# ================================
modelo = load_model("modelo_lesiones_brazos.h5")

# ================================
# 2. Definir clases
# ================================
clases = ["cortes", "quemaduras", "golpes"]

# ================================
# 3. Cargar imagen a predecir
# ================================
ruta_imagen = r"C:\Users\cesar\OneDrive\Desktop\IA-Convolucional\ejemplo.jpg"
 
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
