import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import seaborn as sns

# ===========================
# Configuración
# ===========================
MODELO_PATH = "modelo_quemaduras_cortadas.keras"
VAL_DIR = "data/val"
IMG_SIZE = 224
CLASES = ["quemaduras", "cortadas"]  # Índice 0: quemaduras, Índice 1: cortadas

# ===========================
# Función para cargar imágenes y etiquetas
# ===========================
def cargar_datos_validacion(val_dir):
    """
    Carga todas las imágenes de validación y sus etiquetas.
    Retorna: (imágenes, etiquetas)
    """
    imagenes = []
    etiquetas = []
    
    # Recorrer las carpetas de validación
    # Estructura esperada: data/val/Brazo/quemaduras/, data/val/Brazo/cortes/, etc.
    for parte_cuerpo in os.listdir(val_dir):
        parte_path = os.path.join(val_dir, parte_cuerpo)
        if not os.path.isdir(parte_path):
            continue
            
        # Recorrer las subcarpetas (quemaduras y cortes)
        for clase_nombre in os.listdir(parte_path):
            clase_path = os.path.join(parte_path, clase_nombre)
            if not os.path.isdir(clase_path):
                continue
            
            # Determinar el índice de la clase
            if "quemadura" in clase_nombre.lower():
                clase_idx = 0  # quemaduras
            elif "corte" in clase_nombre.lower():
                clase_idx = 1  # cortadas
            else:
                print(f"⚠️ Carpeta desconocida: {clase_path}")
                continue
            
            # Cargar todas las imágenes de esta carpeta
            archivos_imagen = [f for f in os.listdir(clase_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for archivo in archivos_imagen:
                ruta_imagen = os.path.join(clase_path, archivo)
                try:
                    # Cargar y preprocesar imagen
                    img = load_img(ruta_imagen, target_size=(IMG_SIZE, IMG_SIZE))
                    img_array = img_to_array(img) / 255.0  # Normalizar a [0, 1]
                    
                    imagenes.append(img_array)
                    etiquetas.append(clase_idx)
                except Exception as e:
                    print(f"⚠️ Error al cargar {ruta_imagen}: {e}")
                    continue
    
    return np.array(imagenes), np.array(etiquetas)

# ===========================
# Función principal
# ===========================
def generar_matriz_confusion():
    print("=" * 60)
    print("GENERADOR DE MATRIZ DE CONFUSIÓN")
    print("=" * 60)
    
    # 1. Cargar modelo
    print("\n📦 Cargando modelo...")
    if not os.path.exists(MODELO_PATH):
        print(f"❌ Error: No se encontró el modelo en {MODELO_PATH}")
        return
    
    try:
        modelo = load_model(MODELO_PATH)
        print(f"✅ Modelo cargado exitosamente")
        print(f"   Parámetros totales: {modelo.count_params():,}")
    except Exception as e:
        print(f"❌ Error al cargar el modelo: {e}")
        return
    
    # 2. Cargar datos de validación
    print("\n📂 Cargando datos de validación...")
    if not os.path.exists(VAL_DIR):
        print(f"❌ Error: No se encontró el directorio {VAL_DIR}")
        return
    
    imagenes, etiquetas_reales = cargar_datos_validacion(VAL_DIR)
    
    if len(imagenes) == 0:
        print("❌ No se encontraron imágenes de validación")
        return
    
    print(f"✅ {len(imagenes)} imágenes cargadas")
    print(f"   - Quemaduras: {np.sum(etiquetas_reales == 0)}")
    print(f"   - Cortadas: {np.sum(etiquetas_reales == 1)}")
    
    # 3. Hacer predicciones
    print("\n🔮 Realizando predicciones...")
    predicciones_prob = modelo.predict(imagenes, verbose=1)
    predicciones = np.argmax(predicciones_prob, axis=1)
    
    # 4. Calcular matriz de confusión
    print("\n📊 Calculando matriz de confusión...")
    matriz_conf = confusion_matrix(etiquetas_reales, predicciones)
    
    # 5. Mostrar resultados
    print("\n" + "=" * 60)
    print("MATRIZ DE CONFUSIÓN")
    print("=" * 60)
    print("\nMatriz (valores absolutos):")
    print(f"{'':15} {'Pred: Quemaduras':20} {'Pred: Cortadas':20}")
    print(f"{'Real: Quemaduras':15} {matriz_conf[0][0]:20} {matriz_conf[0][1]:20}")
    print(f"{'Real: Cortadas':15} {matriz_conf[1][0]:20} {matriz_conf[1][1]:20}")
    
    # Calcular métricas
    total = np.sum(matriz_conf)
    correctos = np.trace(matriz_conf)
    precision_total = correctos / total * 100
    
    print(f"\n📈 Métricas:")
    print(f"   Precisión total: {precision_total:.2f}%")
    print(f"   Aciertos: {correctos}/{total}")
    
    # Matriz normalizada (porcentajes)
    matriz_conf_norm = matriz_conf.astype('float') / matriz_conf.sum(axis=1)[:, np.newaxis]
    print("\nMatriz (porcentajes por fila):")
    print(f"{'':15} {'Pred: Quemaduras':20} {'Pred: Cortadas':20}")
    print(f"{'Real: Quemaduras':15} {matriz_conf_norm[0][0]*100:19.2f}% {matriz_conf_norm[0][1]*100:19.2f}%")
    print(f"{'Real: Cortadas':15} {matriz_conf_norm[1][0]*100:19.2f}% {matriz_conf_norm[1][1]*100:19.2f}%")
    
    # 6. Reporte de clasificación detallado
    print("\n" + "=" * 60)
    print("REPORTE DE CLASIFICACIÓN")
    print("=" * 60)
    reporte = classification_report(
        etiquetas_reales, 
        predicciones, 
        target_names=CLASES,
        digits=4
    )
    print(reporte)
    
    # 7. Visualizar matriz de confusión
    print("\n📊 Generando visualización...")
    
    # Crear figura con dos subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Matriz de confusión absoluta
    sns.heatmap(
        matriz_conf, 
        annot=True, 
        fmt='d', 
        cmap='Blues',
        xticklabels=CLASES,
        yticklabels=CLASES,
        ax=axes[0],
        cbar_kws={'label': 'Cantidad'}
    )
    axes[0].set_title('Matriz de Confusión (Valores Absolutos)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Predicción', fontsize=12)
    axes[0].set_ylabel('Real', fontsize=12)
    
    # Matriz de confusión normalizada
    sns.heatmap(
        matriz_conf_norm, 
        annot=True, 
        fmt='.2%', 
        cmap='Greens',
        xticklabels=CLASES,
        yticklabels=CLASES,
        ax=axes[1],
        cbar_kws={'label': 'Porcentaje'}
    )
    axes[1].set_title('Matriz de Confusión (Porcentajes)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Predicción', fontsize=12)
    axes[1].set_ylabel('Real', fontsize=12)
    
    plt.tight_layout()
    
    # Guardar figura
    nombre_archivo = "matriz_confusion.png"
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    print(f"✅ Matriz de confusión guardada en: {nombre_archivo}")
    
    # Mostrar figura
    plt.show()
    
    print("\n✅ Proceso completado!")

# ===========================
# Ejecutar si se llama directamente
# ===========================
if __name__ == "__main__":
    generar_matriz_confusion()

