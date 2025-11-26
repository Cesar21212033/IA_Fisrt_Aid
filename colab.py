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
        print("✅ Descompresión completada!")
    else:
        print(f"⚠️ No se encontró el archivo {zip_path}. Continuando sin descomprimir...")
else:
    print(f"El directorio '{os.path.join(extract_path, 'data')}' ya existe. Saltando la descompresión.")

# Verificar que los directorios train y val existen después de la descompresión
expected_train_dir = os.path.join(extract_path, 'data', 'train')
expected_val_dir = os.path.join(extract_path, 'data', 'val')

if os.path.exists(expected_train_dir) and os.path.exists(expected_val_dir):
    print(f"Los directorios de entrenamiento ({expected_train_dir}) y validación ({expected_val_dir}) fueron encontrados.")
    print("Ahora puedes continuar con el entrenamiento.\n")
else:
    print("⚠️ Advertencia: Los directorios 'train' y/o 'val' no fueron encontrados después de la descompresión. Por favor, verifica la estructura del archivo zip.\n")

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
                print(f"⚠️ Archivo inválido eliminado: {ruta_archivo}")
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
    # Código de entrenamiento
    # ===========================
    print("\n🚀 Iniciando entrenamiento...\n")
    
    # ===========================
    # Limpiar y convertir imágenes
    # ===========================
    print("🧹 Limpiando imágenes de entrenamiento...")
    proc_train, elim_train = limpiar_y_convertir_carpeta(TRAIN_DIR)
    print(f"✅ Procesadas: {proc_train}, Eliminadas: {elim_train}")
    
    print("🧹 Limpiando imágenes de validación...")
    proc_val, elim_val = limpiar_y_convertir_carpeta(VAL_DIR)
    print(f"✅ Procesadas: {proc_val}, Eliminadas: {elim_val}\n")
    
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
    
    print(f"✅ Clases encontradas: {train_generator.class_indices}")
    print(f"✅ Imágenes de entrenamiento: {train_generator.samples}")
    print(f"✅ Imágenes de validación: {val_generator.samples}\n")
    
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
        Dropout(0.15),
        
        # Bloque 2: Segunda capa convolucional
        Conv2D(64, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(64, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.15),
        
        # Bloque 3: Tercera capa convolucional
        Conv2D(128, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(128, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.15),
        
        # Bloque 4: Cuarta capa convolucional
        Conv2D(256, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        Conv2D(256, (3, 3), padding='same'),
        BatchNormalization(),
        Activation('relu'),
        MaxPooling2D(2, 2),
        Dropout(0.15),
        
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
        optimizer=Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"✅ Modelo construido. Parámetros totales: {model.count_params():,}\n")
    
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
        patience=5,
        min_lr=0.00001,
        verbose=1
    )
    
    # ===========================
    # Entrenar modelo
    # ===========================
    print("🚀 Iniciando entrenamiento...")
    print(f"📊 Batch size: {BATCH_SIZE}")
    print(f"🖼️ Tamaño de imagen: {IMG_SIZE}x{IMG_SIZE}")
    print(f"📈 Épocas máximas: 30\n")
    
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=30,
        callbacks=[checkpoint, reduce_lr],
        verbose=1
    )
    
    print("\n✅ Entrenamiento completado!\n")
    
    # ===========================
    # Graficar entrenamiento
    # ===========================
    print("📊 Generando gráficas de entrenamiento...")
    
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
    print("📊 RESULTADOS DEL ENTRENAMIENTO")
    print("="*50)
    print(f"Mejor precisión de validación: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")
    print(f"Mejor precisión de entrenamiento: {best_train_acc:.4f} ({best_train_acc*100:.2f}%)")
    print(f"Precisión final de validación: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
    print(f"Precisión final de entrenamiento: {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
    print("="*50)
    print(f"\n✅ Modelo guardado como: modelo_quemaduras_cortadas.keras")
