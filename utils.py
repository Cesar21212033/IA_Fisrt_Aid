import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.metrics import classification_report, confusion_matrix

# ================================
# 1. Cargar imágenes de un directorio
# ================================
def cargar_imagenes(ruta, tamaño=(128,128)):
    """
    Carga imágenes desde carpetas organizadas por clase.
    
    Args:
        ruta (str): Ruta al directorio base (train o val)
        tamaño (tuple): Tamaño a redimensionar cada imagen
    
    Returns:
        X (np.array): Array de imágenes
        y (np.array): Array de etiquetas
        clases (list): Lista de nombres de clases
    """
    X, y = [], []
    clases = sorted(os.listdir(ruta))
    
    for idx, clase in enumerate(clases):
        clase_path = os.path.join(ruta, clase)
        if not os.path.isdir(clase_path):
            continue
        for img_name in os.listdir(clase_path):
            img_path = os.path.join(clase_path, img_name)
            try:
                img = load_img(img_path, target_size=tamaño)
                X.append(img_to_array(img))
                y.append(idx)
            except Exception as e:
                print(f"No se pudo cargar {img_path}: {e}")
    
    return np.array(X), np.array(y), clases

# ================================
# 2. Mostrar imágenes con etiquetas
# ================================
def mostrar_imagenes(X, y, clases, n=9):
    plt.figure(figsize=(10,10))
    for i in range(min(n, len(X))):
        plt.subplot(3,3,i+1)

        # grayscale
        if X[i].shape[-1] == 1:
            plt.imshow(X[i].squeeze(), cmap='gray')
        else:
            # RGB, normalizado 0-1
            plt.imshow(X[i] / 255.0 if X[i].max() > 1 else X[i])

        plt.title(clases[y[i]])
        plt.axis('off')
    plt.show()

# ================================
# 3. Reporte de evaluación del modelo
# ================================
def reporte_modelo(modelo, X_val, y_val, clases):
    """
    Genera reporte de clasificación y matriz de confusión.
    
    Args:
        modelo: Modelo entrenado (Keras)
        X_val (np.array): Imágenes de validación
        y_val (np.array): Etiquetas de validación
        clases (list): Nombres de clases
    """
    y_pred = np.argmax(modelo.predict(X_val), axis=1)
    print("=== Classification Report ===")
    print(classification_report(y_val, y_pred, target_names=clases))
    print("\n=== Confusion Matrix ===")
    print(confusion_matrix(y_val, y_pred))
