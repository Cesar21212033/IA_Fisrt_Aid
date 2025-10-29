import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# ================================
# 0. Importar ModelManager
# ================================
from model import ModelManager  # Asegúrate de que model_manager.py esté en la misma carpeta

# ================================
# 1. Inicializar ModelManager
# ================================
modelo_manager = ModelManager("modelo_quemaduras_cortadas.keras")

# ================================
# 2. Definir clases
# ================================
clases = ["quemaduras", "cortadas"]

# ================================
# 3. Función de predicción
# ================================
def predecir_lesion(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        return {"error": f"No se encontró la imagen: {ruta_imagen}"}

    try:
        # Procesar imagen
        img = load_img(ruta_imagen, target_size=(128,128))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predicción usando ModelManager
        pred = modelo_manager.predict(img_array)
        clase_idx = np.argmax(pred)
        prob = np.max(pred)

        return {"prediction": clases[clase_idx], "confidence": float(prob)}

    except Exception as e:
        return {"error": str(e)}


# ================================
# 4. Ejecutar desde CLI si se quiere
# ================================
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python predict.py <ruta_de_la_imagen>")
        sys.exit(1)

    ruta = sys.argv[1]
    resultado = predecir_lesion(ruta)
    
    if "error" in resultado:
        print(resultado["error"])
    else:
        print(f"La lesión probablemente es: {resultado['prediction']} con {resultado['confidence']*100:.2f}% de confianza")
