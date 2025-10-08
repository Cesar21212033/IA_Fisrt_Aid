import os
import sys
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# ================================
# 1. Cargar el modelo entrenado
# ================================
modelo = load_model("modelo_quemaduras_cortadas.h5")

# ================================
# 2. Definir clases
# ================================
clases = ["quemaduras", "cortadas"]

# ================================
# 3. Obtener ruta de imagen desde argumentos
# ================================
if len(sys.argv) < 2:
    print("Uso: python predict.py <ruta_de_la_imagen>")
    sys.exit(1)

ruta_imagen = sys.argv[1]

if not os.path.exists(ruta_imagen):
    print(f"No se encontró la imagen: {ruta_imagen}")
    sys.exit(1)

# ================================
# 4. Procesar la imagen
# ================================
try:
    img = load_img(ruta_imagen, target_size=(128,128))  # Redimensionar
    img_array = img_to_array(img) / 255.0               # Normalizar
    img_array = np.expand_dims(img_array, axis=0)       # Añadir dimensión batch
except Exception as e:
    print(f"Error al procesar la imagen: {e}")
    sys.exit(1)

# ================================
# 5. Hacer predicción
# ================================
prediccion = modelo.predict(img_array, verbose=0)  # verbose=0 evita logs innecesarios
clase_idx = np.argmax(prediccion)
probabilidad = np.max(prediccion)

# ================================
# 6. Mostrar resultado
# ================================
print(f"La lesión probablemente es: {clases[clase_idx]} con {probabilidad*100:.2f}% de confianza")
