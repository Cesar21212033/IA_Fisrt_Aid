# ===========================
# Código para entrenar modelo en Google Colab
# ===========================
# Este código está optimizado para ejecutarse en Google Colab con GPU
# Incluye visualización de gráficas de entrenamiento

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout, 
    BatchNormalization,
    GlobalAveragePooling2D, Activation
)
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from PIL import Image
import os
import zipfile
import numpy as np
from collections import Counter
import glob

# ===========================
# Descomprimir archivo zip si existe
# ===========================
zip_path = '/content/data.zip'
extract_path = '/content/'

# Crear el directorio de destino si no existe
if not os.path.exists(os.path.join(extract_path, 'data')):
    if os.path.exists(zip_path):
        print(f"Descomprimiendo {zip_path} en {extract_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(" Descompresión completada!")
    else:
        print(f" No se encontró el archivo {zip_path}. Continuando sin descomprimir...")
else:
    print(f"El directorio '{os.path.join(extract_path, 'data')}' ya existe. Saltando la descompresión.")

# Verificar que los directorios train y val existen después de la descompresión
expected_train_dir = os.path.join(extract_path, 'data', 'train')
expected_val_dir = os.path.join(extract_path, 'data', 'val')

if os.path.exists(expected_train_dir) and os.path.exists(expected_val_dir):
    print(f"Los directorios de entrenamiento ({expected_train_dir}) y validación ({expected_val_dir}) fueron encontrados.")
    print("Ahora puedes continuar con el entrenamiento.\n")
else:
    print(" Advertencia: Los directorios 'train' y/o 'val' no fueron encontrados después de la descompresión. Por favor, verifica la estructura del archivo zip.\n")

# ===========================
# Configuración de rutas
# ===========================
# Modifica estas rutas si tu carpeta 'data' está en una ubicación diferente a '/content/data'
# Por ejemplo, si descomprimiste 'my_data.zip' y tus carpetas train/val están directamente bajo /content/my_data/
# BASE_DATA_DIR = os.path.join(os.getcwd(), 'my_data')

# Por ahora, usamos la ruta por defecto que espera el modelo, asumiendo que has puesto tu carpeta 'data' en /content/
BASE_DATA_DIR = os.path.join(os.getcwd(), 'data')

# Estas variables se usarán en el código principal
# Asegúrate de que estas rutas existan y contengan las subcarpetas de clases (quemaduras, cortadas)
TRAIN_DIR = os.path.join(BASE_DATA_DIR, "train")
VAL_DIR = os.path.join(BASE_DATA_DIR, "val")

print(f"El código intentará encontrar las imágenes de entrenamiento en: {TRAIN_DIR}")
print(f"El código intentará encontrar las imágenes de validación en: {VAL_DIR}")

# ===========================
# Función para limpiar imágenes
# ===========================
def limpiar_y_convertir_carpeta(carpeta):
    """Limpia y convierte imágenes a formato RGB/JPG"""
    extensiones_validas = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif'}
    archivos_procesados = 0
    archivos_eliminados = 0
    
    for root, dirs, files in os.walk(carpeta):
        for archivo in files:
            ruta_archivo = os.path.join(root, archivo)
            extension = os.path.splitext(archivo)[1].lower()
            
            # Solo procesar archivos con extensiones de imagen válidas
            if extension not in extensiones_validas:
                continue
                
            try:
                img = Image.open(ruta_archivo)
                img.verify()
                img = Image.open(ruta_archivo).convert('RGB')
                nuevo_nombre = os.path.splitext(ruta_archivo)[0] + ".jpg"
                
                # Solo convertir y eliminar si la extensión es diferente a .jpg
                if extension != '.jpg':
                    img.save(nuevo_nombre, "JPEG")
                    os.remove(ruta_archivo)
                archivos_procesados += 1
            except Exception:
                print(f" Archivo inválido eliminado: {ruta_archivo}")
                try:
                    os.remove(ruta_archivo)
                    archivos_eliminados += 1
                except Exception:
                    pass
    
    return archivos_procesados, archivos_eliminados

# ===========================
# Verificar estructura de carpetas
# ===========================
# Verifica si las carpetas de clases existen dentro de TRAIN_DIR y VAL_DIR
def check_class_dirs(base_dir, data_type):
    if not os.path.exists(base_dir):
        print(f"¡Advertencia! La carpeta {data_type} no existe: {base_dir}")
        return False

    class_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not class_folders:
        print(f"¡Advertencia! La carpeta {data_type} no contiene ninguna subcarpeta de clases en: {base_dir}")
        print(f"Asegúrate de tener una estructura como: {base_dir}/quemaduras/, {base_dir}/cortadas/")
        return False
    else:
        print(f"Clases encontradas en {data_type}: {class_folders}")
        return True

print("\nVerificando estructura de entrenamiento:")
train_structure_ok = check_class_dirs(TRAIN_DIR, "entrenamiento")
print("\nVerificando estructura de validación:")
val_structure_ok = check_class_dirs(VAL_DIR, "validación")

if not (train_structure_ok and val_structure_ok):
    print("\nPor favor, revisa la estructura de tus carpetas y asegúrate de que las imágenes estén organizadas en subcarpetas de clases (ej. 'quemaduras', 'cortadas') dentro de tus directorios 'train' y 'val'.")
    print("Una vez que tus datos estén en la ubicación correcta y con la estructura esperada, vuelve a ejecutar la celda de entrenamiento.")
else:
    print("\n¡La estructura de carpetas parece correcta! Ahora puedes ejecutar la celda principal de entrenamiento.")
    
    # ===========================
    # Buscar y eliminar archivos .keras existentes
    # ===========================
    print("\n🔍 Buscando archivos .keras existentes...")
    keras_files = glob.glob('*.keras')
    
    if keras_files:
        print(f" Se encontraron {len(keras_files)} archivo(s) .keras existente(s):")
        for keras_file in keras_files:
            print(f"   - {keras_file}")
        print(" Estos archivos serán sobreescritos con el nuevo entrenamiento.\n")
        # Opcional: eliminar archivos antiguos antes del entrenamiento
        # Si prefieres mantenerlos hasta que se guarde el nuevo modelo, puedes comentar estas líneas
        for keras_file in keras_files:
            try:
                os.remove(keras_file)
                print(f"   ✓ Archivo eliminado: {keras_file}")
            except Exception as e:
                print(f"   ⚠ No se pudo eliminar {keras_file}: {e}")
    else:
        print(" No se encontraron archivos .keras existentes. Se creará un nuevo modelo.\n")
    
    # ===========================
    # Código de entrenamiento
    # ===========================
    print("\n🚀 Iniciando entrenamiento...\n")
    
    # ===========================
    # Limpiar y convertir imágenes
    # ===========================
    print("🧹 Limpiando imágenes de entrenamiento...")
    proc_train, elim_train = limpiar_y_convertir_carpeta(TRAIN_DIR)
    print(f" Procesadas: {proc_train}, Eliminadas: {elim_train}")
    
    print("🧹 Limpiando imágenes de validación...")
    proc_val, elim_val = limpiar_y_convertir_carpeta(VAL_DIR)
    print(f" Procesadas: {proc_val}, Eliminadas: {elim_val}\n")
    
    # ===========================
    # Data Augmentation y Generadores
    # ===========================
    IMG_SIZE = 224  # Tamaño optimizado para GPU
    BATCH_SIZE = 32  # Puedes aumentar si tienes GPU potente
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        # vertical_flip eliminado: incorrecto para imágenes médicas
        shear_range=0.2,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="sparse",
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="sparse"
    )
    
    print(f" Clases encontradas: {train_generator.class_indices}")
    print(f" Imágenes de entrenamiento: {train_generator.samples}")
    print(f" Imágenes de validación: {val_generator.samples}\n")
    
    # ===========================
    # Calcular class_weight para priorizar clase 'cortadas'
    # ===========================
    # Obtener la distribución de clases del generador de entrenamiento
    class_counts = Counter(train_generator.classes)
    total_samples = sum(class_counts.values())
    
    # Debug: mostrar qué clases se detectaron
    print(f" DEBUG - Nombres de clases detectadas: {list(train_generator.class_indices.keys())}")
    print(f" DEBUG - Distribución de clases: {dict(class_counts)}\n")
    
    # Contar imágenes reales en carpetas de cortes vs quemaduras
    print(f" Analizando estructura de carpetas para calcular pesos reales...")
    cortes_total = 0
    quemaduras_total = 0
    
    # Mapeo: para cada clase detectada (Brazo/Pierna), contar cortes y quemaduras
    clase_cortes_count = {}  # {class_idx: cantidad_de_cortes}
    clase_quemaduras_count = {}  # {class_idx: cantidad_de_quemaduras}
    
    for class_name, class_idx in train_generator.class_indices.items():
        clase_cortes_count[class_idx] = 0
        clase_quemaduras_count[class_idx] = 0
        
        # Buscar todas las subcarpetas de esta clase
        clase_path = os.path.join(TRAIN_DIR, class_name)
        if os.path.exists(clase_path):
            for root, dirs, files in os.walk(clase_path):
                rel_path = os.path.relpath(root, clase_path)
                # Buscar carpetas de cortes o quemaduras
                if 'corte' in rel_path.lower() or 'corte' in root.lower():
                    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    clase_cortes_count[class_idx] += len(image_files)
                    cortes_total += len(image_files)
                elif 'quemadura' in rel_path.lower() or 'quemadura' in root.lower():
                    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    clase_quemaduras_count[class_idx] += len(image_files)
                    quemaduras_total += len(image_files)
    
    print(f" DEBUG - Total imágenes: cortes={cortes_total}, quemaduras={quemaduras_total}")
    print(f" DEBUG - Por clase detectada:")
    for class_name, class_idx in train_generator.class_indices.items():
        print(f"   {class_name} (índice {class_idx}): cortes={clase_cortes_count[class_idx]}, quemaduras={clase_quemaduras_count[class_idx]}")
    
    # Calcular pesos basados en la proporción real de cortes vs quemaduras
    # Si cortes tiene menos imágenes, necesita más peso
    num_classes = len(train_generator.class_indices)
    class_weight = {}
    
    # Calcular pesos iniciales basados en distribución de clases detectadas
    for class_idx, count in class_counts.items():
        weight = total_samples / (num_classes * count)
        class_weight[class_idx] = weight
    
    # Ajustar pesos: dar más peso a las clases que tienen más cortes
    # Identificar qué clase tiene más cortes en proporción
    if cortes_total > 0 and quemaduras_total > 0:
        # Calcular proporción de cortes en cada clase
        for class_idx in class_weight.keys():
            total_clase = clase_cortes_count[class_idx] + clase_quemaduras_count[class_idx]
            if total_clase > 0:
                prop_cortes = clase_cortes_count[class_idx] / total_clase
                # Si esta clase tiene más del 50% de cortes, aumentar su peso
                if prop_cortes > 0.5:
                    # Aumentar peso proporcionalmente a cuántos cortes tiene
                    factor_ajuste = 1.0 + (prop_cortes - 0.5) * 2.0  # Máximo 1.5x si es 100% cortes
                    class_weight[class_idx] *= factor_ajuste
                    print(f" DEBUG - Ajustando peso de clase {class_idx}: prop_cortes={prop_cortes:.2%}, factor={factor_ajuste:.2f}")
        
        # También aplicar peso adicional global si cortes es minoritario
        if cortes_total < quemaduras_total:
            # Encontrar la clase con más cortes y darle peso adicional
            clase_con_mas_cortes = max(clase_cortes_count.items(), key=lambda x: x[1])
            if clase_con_mas_cortes[1] > 0:
                class_weight[clase_con_mas_cortes[0]] *= 1.5
                clase_nombre = [name for name, idx in train_generator.class_indices.items() if idx == clase_con_mas_cortes[0]][0]
                print(f" Class weights calculados: {class_weight}")
                print(f"   Priorizando clase '{clase_nombre}' (índice {clase_con_mas_cortes[0]}) con más cortes")
                print(f"   Peso final: {class_weight[clase_con_mas_cortes[0]]:.3f}\n")
            else:
                print(f" Class weights calculados: {class_weight}\n")
        else:
            print(f" Class weights calculados: {class_weight}\n")
    else:
        print(f" No se pudieron contar imágenes de cortes/quemaduras. Usando pesos balanceados.\n")
    
    # ===========================
    # Definir modelo CNN mejorado
    # ===========================
    print("🏗️ Construyendo modelo...")
    model = Sequential([
        # Bloque 1: Primera capa convolucional
        Conv2D(32, (3, 3), padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(32, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.10),
        
        # Bloque 2: Segunda capa convolucional
        Conv2D(64, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(64, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.10),
        
        # Bloque 3: Tercera capa convolucional
        Conv2D(128, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(128, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.10),
        
        # Bloque 4: Cuarta capa convolucional
        Conv2D(256, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(256, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.10),
        
        # Global Average Pooling
        GlobalAveragePooling2D(),
        
        # Capas densas con regularización L2
        Dense(512, kernel_regularizer=l2(0.001)),
        BatchNormalization(),
        Activation('relu'),
        Dropout(0.5),
        
        Dense(256, kernel_regularizer=l2(0.001)),
        BatchNormalization(),
        Activation('relu'),
        Dropout(0.5),
        
        # Capa de salida
        Dense(2, activation='softmax')
    ])
    
    # Compilar modelo
    model.compile(
        optimizer=Adam(learning_rate=0.002),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f" Modelo construido. Parámetros totales: {model.count_params():,}\n")
    
    # ===========================
    # Callbacks
    # ===========================
    checkpoint = ModelCheckpoint(
        'modelo_quemaduras_cortadas.keras',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=0.00001,
        verbose=1
    )
    
    # ===========================
    # Entrenar modelo
    # ===========================
    print(" Iniciando entrenamiento...")
    print(f" Batch size: {BATCH_SIZE}")
    print(f" Tamaño de imagen: {IMG_SIZE}x{IMG_SIZE}")
    print(f" Épocas máximas: 30\n")
    
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=30,
        callbacks=[checkpoint, reduce_lr],
        class_weight=class_weight,
        verbose=1
    )
    
    print("\n Entrenamiento completado!\n")
    
    # ===========================
    # Graficar entrenamiento
    # ===========================
    print(" Generando gráficas de entrenamiento...")
    
    # Crear figura con dos subplots
    plt.figure(figsize=(15, 5))
    
    # Gráfico 1: Precisión
    plt.subplot(1, 3, 1)
    plt.plot(history.history['accuracy'], label='Entrenamiento', marker='o', linewidth=2)
    plt.plot(history.history['val_accuracy'], label='Validación', marker='s', linewidth=2)
    plt.xlabel('Épocas', fontsize=12)
    plt.ylabel('Precisión', fontsize=12)
    plt.title('Precisión del Modelo', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Gráfico 2: Pérdida
    plt.subplot(1, 3, 2)
    plt.plot(history.history['loss'], label='Entrenamiento', marker='o', linewidth=2)
    plt.plot(history.history['val_loss'], label='Validación', marker='s', linewidth=2)
    plt.xlabel('Épocas', fontsize=12)
    plt.ylabel('Pérdida', fontsize=12)
    plt.title('Pérdida del Modelo', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Gráfico 3: Comparación Precisión (como en model.py)
    plt.subplot(1, 3, 3)
    plt.plot(history.history['accuracy'], label='Entrenamiento', linewidth=2)
    plt.plot(history.history['val_accuracy'], label='Validación', linewidth=2)
    plt.xlabel('Épocas', fontsize=12)
    plt.ylabel('Precisión', fontsize=12)
    plt.title('CNN - Quemaduras vs Cortadas', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Mostrar estadísticas finales
    best_val_acc = max(history.history['val_accuracy'])
    best_train_acc = max(history.history['accuracy'])
    final_val_acc = history.history['val_accuracy'][-1]
    final_train_acc = history.history['accuracy'][-1]
    
    print("\n" + "="*50)
    print(" RESULTADOS DEL ENTRENAMIENTO")
    print("="*50)
    print(f"Mejor precisión de validación: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")
    print(f"Mejor precisión de entrenamiento: {best_train_acc:.4f} ({best_train_acc*100:.2f}%)")
    print(f"Precisión final de validación: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
    print(f"Precisión final de entrenamiento: {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
    print("="*50)
    
    # Verificar que el modelo se guardó correctamente
    modelo_guardado = 'modelo_quemaduras_cortadas.keras'
    if os.path.exists(modelo_guardado):
        file_size = os.path.getsize(modelo_guardado) / (1024 * 1024)  # Tamaño en MB
        print(f"\n ✓ Modelo guardado exitosamente como: {modelo_guardado}")
        print(f"   Tamaño del archivo: {file_size:.2f} MB")
        if keras_files:
            print(f"   (Archivo .keras anterior fue sobreescrito con el nuevo entrenamiento)")
    else:
        print(f"\n ⚠ Advertencia: No se encontró el archivo {modelo_guardado} después del entrenamiento.")
