# ===========================
# Código optimizado para dataset pequeño (267 train, 64 val)
# Estrategias implementadas:
# 1. Transfer Learning (MobileNetV2)
# 2. Data Augmentation agresiva
# 3. Early Stopping
# 4. Learning Rate bajo
# 5. Batch size pequeño
# 6. Validación cruzada estilo
# ===========================

import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout, 
    BatchNormalization, GlobalAveragePooling2D, Activation,
    Input
)
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping, CSVLogger
import matplotlib.pyplot as plt
from PIL import Image
import os
import zipfile
import numpy as np
from collections import Counter
import glob
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
import seaborn as sns

# ===========================
# Configuración inicial
# ===========================
print("TensorFlow version:", tf.__version__)
print("GPU disponible:", len(tf.config.list_physical_devices('GPU')) > 0)

# Configurar para evitar sobrecarga de memoria
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# ===========================
# Descomprimir archivo zip si existe
# ===========================
zip_path = '/content/data.zip'
extract_path = '/content/'

if not os.path.exists(os.path.join(extract_path, 'data')):
    if os.path.exists(zip_path):
        print(f"Descomprimiendo {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print("✓ Descompresión completada!")
    else:
        print(f"⚠ No se encontró {zip_path}. Continuando...")
else:
    print(f"✓ Directorio '{os.path.join(extract_path, 'data')}' ya existe.")

# ===========================
# Configuración de rutas (ESTRUCTURA SIMPLIFICADA)
# ===========================
BASE_DATA_DIR = os.path.join(os.getcwd(), 'data')
TRAIN_DIR = os.path.join(BASE_DATA_DIR, "train")
VAL_DIR = os.path.join(BASE_DATA_DIR, "val")

print(f"\n📍 Directorio de entrenamiento: {TRAIN_DIR}")
print(f"📍 Directorio de validación: {VAL_DIR}")

# ===========================
# Verificar estructura SIMPLIFICADA (solo cortadas/quemaduras)
# ===========================
def verificar_estructura_simple():
    clases_esperadas = ['cortadas', 'quemaduras', 'cortes', 'quemaduras']
    
    for data_type, path in [("train", TRAIN_DIR), ("val", VAL_DIR)]:
        print(f"\nVerificando {data_type}...")
        
        if not os.path.exists(path):
            print(f"  ❌ No existe: {path}")
            return False
        
        # Buscar clases disponibles (acepta variaciones)
        subfolders = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        
        if len(subfolders) < 2:
            print(f"  ⚠ Solo {len(subfolders)} clases encontradas. Necesitamos al menos 2.")
            print(f"  📂 Carpetas encontradas: {subfolders}")
            
            # Verificar si hay imágenes directamente en la carpeta
            archivos_img = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if archivos_img:
                print(f"  ⚠ Hay {len(archivos_img)} imágenes sin organizar en subcarpetas.")
            
            return False
        
        print(f"  ✅ {len(subfolders)} clases encontradas: {subfolders}")
        
        # Contar imágenes por clase
        for clase in subfolders:
            clase_path = os.path.join(path, clase)
            imagenes = [f for f in os.listdir(clase_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"     {clase}: {len(imagenes)} imágenes")
    
    return True

if not verificar_estructura_simple():
    print("\n❌ Estructura incorrecta. Asegúrate de tener:")
    print("   data/train/cortadas/")
    print("   data/train/quemaduras/")
    print("   data/val/cortadas/")
    print("   data/val/quemaduras/")
    exit()

# ===========================
# Limpiar y preparar imágenes
# ===========================
def limpiar_imagenes_carpeta(carpeta):
    """Limpia y convierte todas las imágenes a JPG"""
    total_procesadas = 0
    total_eliminadas = 0
    
    for root, dirs, files in os.walk(carpeta):
        for archivo in files:
            if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                ruta_completa = os.path.join(root, archivo)
                try:
                    with Image.open(ruta_completa) as img:
                        img.verify()
                    
                    # Convertir a JPG si no lo es
                    if not archivo.lower().endswith('.jpg'):
                        img = Image.open(ruta_completa).convert('RGB')
                        nuevo_nombre = os.path.splitext(ruta_completa)[0] + ".jpg"
                        img.save(nuevo_nombre, "JPEG", quality=95)
                        os.remove(ruta_completa)
                        print(f"  🔄 Convertido: {archivo} -> {os.path.basename(nuevo_nombre)}")
                    
                    total_procesadas += 1
                except Exception as e:
                    print(f"  ❌ Eliminado (corrupto): {archivo}")
                    try:
                        os.remove(ruta_completa)
                        total_eliminadas += 1
                    except:
                        pass
    
    return total_procesadas, total_eliminadas

print("\n🧹 Limpiando imágenes...")
proc_train, elim_train = limpiar_imagenes_carpeta(TRAIN_DIR)
proc_val, elim_val = limpiar_imagenes_carpeta(VAL_DIR)
print(f"✓ Train: {proc_train} procesadas, {elim_train} eliminadas")
print(f"✓ Val: {proc_val} procesadas, {elim_val} eliminadas")

# ===========================
# Configuración de hiperparámetros optimizados
# ===========================
IMG_SIZE = 224  # Tamaño para MobileNetV2
BATCH_SIZE = 8  # Batch pequeño para pocos datos
EPOCHS = 50
LEARNING_RATE = 0.0001  # Learning rate bajo
PATIENCE_EARLY_STOP = 15  # Paciencia para early stopping
PATIENCE_REDUCE_LR = 8    # Paciencia para reducir LR

print(f"\n⚙️  Hiperparámetros:")
print(f"  • Tamaño imagen: {IMG_SIZE}x{IMG_SIZE}")
print(f"  • Batch size: {BATCH_SIZE} (pequeño para dataset reducido)")
print(f"  • Épocas máximas: {EPOCHS}")
print(f"  • Learning rate: {LEARNING_RATE}")
print(f"  • Early stopping patience: {PATIENCE_EARLY_STOP}")

# ===========================
# Data Augmentation AGRESIVA (para pocos datos)
# ===========================
print("\n🎨 Configurando Data Augmentation...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=45,           # Aumentado de 30 a 45
    width_shift_range=0.3,       # Aumentado de 0.2 a 0.3
    height_shift_range=0.3,      # Aumentado de 0.2 a 0.3
    shear_range=0.3,             # Aumentado de 0.2 a 0.3
    zoom_range=0.3,              # Aumentado de 0.2 a 0.3
    horizontal_flip=True,
    vertical_flip=False,         # Mantener False para imágenes médicas
    brightness_range=[0.6, 1.4], # Rango más amplio
    channel_shift_range=30.0,    # Nuevo: variar canales de color
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(
    rescale=1./255  # Solo normalización para validación
)

print("✓ Data augmentation configurada de forma agresiva")

# ===========================
# Crear generadores de datos
# ===========================
print("\n📂 Creando generadores de datos...")

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',  # Cambiado a binary para 2 clases
    shuffle=True,
    seed=42
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',  # Cambiado a binary para 2 clases
    shuffle=False
)

# Mostrar información
num_classes = len(train_generator.class_indices)
class_names = list(train_generator.class_indices.keys())

print(f"✓ Clases detectadas: {class_names}")
print(f"✓ Mapeo de clases: {train_generator.class_indices}")
print(f"✓ Imágenes de entrenamiento: {train_generator.samples}")
print(f"✓ Imágenes de validación: {val_generator.samples}")

# ===========================
# Calcular pesos de clases para balancear
# ===========================
print("\n⚖️ Calculando pesos de clases...")

# Obtener distribución real
train_class_counts = Counter(train_generator.classes)
val_class_counts = Counter(val_generator.classes)

print(f"Distribución en train:")
for class_idx, count in train_class_counts.items():
    class_name = class_names[class_idx]
    percentage = (count / train_generator.samples) * 100
    print(f"  {class_name}: {count} imágenes ({percentage:.1f}%)")

print(f"\nDistribución en val:")
for class_idx, count in val_class_counts.items():
    class_name = class_names[class_idx]
    percentage = (count / val_generator.samples) * 100
    print(f"  {class_name}: {count} imágenes ({percentage:.1f}%)")

# Calcular class_weight automáticamente
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)

class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
print(f"\n✓ Pesos calculados: {class_weight_dict}")

# ===========================
# Crear modelo con TRANSFER LEARNING
# ===========================
print("\n🏗️ Construyendo modelo con Transfer Learning...")

# Opción 1: MobileNetV2 (más rápido, menos parámetros)
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Opción 2: EfficientNetB0 (más preciso pero más lento)
# base_model = EfficientNetB0(
#     weights='imagenet',
#     include_top=False,
#     input_shape=(IMG_SIZE, IMG_SIZE, 3)
# )

# Congelar capas base inicialmente
base_model.trainable = False
print(f"✓ Modelo base: {base_model.name}")
print(f"✓ Capas congeladas: {len(base_model.layers)}")

# Construir modelo completo
inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = GlobalAveragePooling2D()(x)
x = Dropout(0.5)(x)  # Dropout alto para evitar overfitting
x = Dense(128, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
outputs = Dense(1, activation='sigmoid')(x)  # 1 neurona para clasificación binaria

model = Model(inputs, outputs)

print(f"\n📊 Resumen del modelo:")
print(f"  • Total parámetros: {model.count_params():,}")
print(f"  • Parámetros entrenables: {sum([w.shape.num_elements() for w in model.trainable_weights]):,}")
print(f"  • Parámetros no entrenables: {sum([w.shape.num_elements() for w in model.non_trainable_weights]):,}")

# ===========================
# Compilar modelo
# ===========================
optimizer = Adam(
    learning_rate=LEARNING_RATE,
    beta_1=0.9,
    beta_2=0.999,
    epsilon=1e-07
)

model.compile(
    optimizer=optimizer,
    loss='binary_crossentropy',
    metrics=[
        'accuracy',
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.AUC(name='auc')
    ]
)

print("\n✅ Modelo compilado con métricas adicionales (Precision, Recall, AUC)")

# ===========================
# Callbacks (ESENCIALES para evitar overfitting)
# ===========================
print("\n🔔 Configurando callbacks...")

# 1. Guardar el mejor modelo
checkpoint = ModelCheckpoint(
    'mejor_modelo_cortadas_quemaduras.keras',
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    save_weights_only=False,
    verbose=1
)

# 2. Reducir learning rate si se estanca
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=PATIENCE_REDUCE_LR,
    min_lr=1e-7,
    verbose=1
)

# 3. Early stopping para evitar overfitting
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=PATIENCE_EARLY_STOP,
    restore_best_weights=True,
    verbose=1,
    mode='min'
)

# 4. Log de entrenamiento
csv_logger = CSVLogger(
    'entrenamiento_log.csv',
    separator=',',
    append=False
)

callbacks = [checkpoint, reduce_lr, early_stopping, csv_logger]
print("✓ Callbacks configurados: ModelCheckpoint, ReduceLROnPlateau, EarlyStopping, CSVLogger")

# ===========================
# Entrenamiento por ETAPAS
# ===========================
print("\n" + "="*60)
print("🚀 INICIANDO ENTRENAMIENTO POR ETAPAS")
print("="*60)

# ETAPA 1: Entrenar solo las capas densas
print("\n📈 ETAPA 1: Entrenando capas densas (capas base congeladas)")
history_stage1 = model.fit(
    train_generator,
    steps_per_epoch=max(1, train_generator.samples // BATCH_SIZE),
    validation_data=val_generator,
    validation_steps=max(1, val_generator.samples // BATCH_SIZE),
    epochs=20,  # Pocas épocas para la primera etapa
    callbacks=callbacks,
    class_weight=class_weight_dict,
    verbose=1
)

# ETAPA 2: Fine-tuning (descongelar algunas capas)
print("\n🎯 ETAPA 2: Fine-tuning (descongelando últimas capas del modelo base)")

# Descongelar las últimas 30 capas
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

# Recompilar con learning rate más bajo
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE / 10),
    loss='binary_crossentropy',
    metrics=['accuracy', 'precision', 'recall', 'auc']
)

print(f"✓ Capas descongeladas: 30")
print(f"✓ Nuevo learning rate: {LEARNING_RATE / 10}")

# Continuar entrenamiento
history_stage2 = model.fit(
    train_generator,
    steps_per_epoch=max(1, train_generator.samples // BATCH_SIZE),
    validation_data=val_generator,
    validation_steps=max(1, val_generator.samples // BATCH_SIZE),
    epochs=EPOCHS - 20,  # Épocas restantes
    callbacks=callbacks,
    class_weight=class_weight_dict,
    initial_epoch=len(history_stage1.history['loss']),
    verbose=1
)

# Combinar historiales
history = {
    'loss': history_stage1.history['loss'] + history_stage2.history['loss'],
    'accuracy': history_stage1.history['accuracy'] + history_stage2.history['accuracy'],
    'val_loss': history_stage1.history['val_loss'] + history_stage2.history['val_loss'],
    'val_accuracy': history_stage1.history['val_accuracy'] + history_stage2.history['val_accuracy'],
    'precision': history_stage1.history['precision'] + history_stage2.history['precision'],
    'val_precision': history_stage1.history['val_precision'] + history_stage2.history['val_precision'],
    'recall': history_stage1.history['recall'] + history_stage2.history['recall'],
    'val_recall': history_stage1.history['val_recall'] + history_stage2.history['val_recall']
}

print("\n✅ Entrenamiento completado!")

# ===========================
# Visualización de resultados
# ===========================
print("\n📊 Generando visualizaciones...")

# Crear figura con múltiples gráficos
plt.figure(figsize=(20, 12))

# 1. Precisión
plt.subplot(2, 3, 1)
plt.plot(history['accuracy'], label='Train', linewidth=2, marker='o', markersize=4)
plt.plot(history['val_accuracy'], label='Val', linewidth=2, marker='s', markersize=4)
plt.axvline(x=20, color='r', linestyle='--', alpha=0.5, label='Inicio Fine-tuning')
plt.xlabel('Época')
plt.ylabel('Precisión')
plt.title('Precisión durante el entrenamiento', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 2. Pérdida
plt.subplot(2, 3, 2)
plt.plot(history['loss'], label='Train', linewidth=2, marker='o', markersize=4)
plt.plot(history['val_loss'], label='Val', linewidth=2, marker='s', markersize=4)
plt.axvline(x=20, color='r', linestyle='--', alpha=0.5, label='Inicio Fine-tuning')
plt.xlabel('Época')
plt.ylabel('Pérdida')
plt.title('Pérdida durante el entrenamiento', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 3. Precisión vs Recall
plt.subplot(2, 3, 3)
plt.plot(history['precision'], label='Precision Train', linewidth=2, alpha=0.7)
plt.plot(history['val_precision'], label='Precision Val', linewidth=2, alpha=0.7)
plt.plot(history['recall'], label='Recall Train', linewidth=2, alpha=0.7)
plt.plot(history['val_recall'], label='Recall Val', linewidth=2, alpha=0.7)
plt.xlabel('Época')
plt.ylabel('Métrica')
plt.title('Precisión y Recall', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 4. Comparación Train vs Val
plt.subplot(2, 3, 4)
epochs = range(1, len(history['accuracy']) + 1)
plt.plot(epochs, history['accuracy'], 'b-', label='Train Accuracy', linewidth=2)
plt.plot(epochs, history['val_accuracy'], 'r-', label='Val Accuracy', linewidth=2)
plt.fill_between(epochs, history['accuracy'], history['val_accuracy'], 
                 color='gray', alpha=0.2, label='Gap')
plt.xlabel('Época')
plt.ylabel('Precisión')
plt.title('Brecha entre Train y Val', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 5. Histograma de diferencias
plt.subplot(2, 3, 5)
diferencias = [a - v for a, v in zip(history['accuracy'], history['val_accuracy'])]
plt.hist(diferencias, bins=15, edgecolor='black', alpha=0.7)
plt.axvline(x=np.mean(diferencias), color='r', linestyle='--', linewidth=2, 
            label=f'Media: {np.mean(diferencias):.3f}')
plt.xlabel('Diferencia (Train - Val)')
plt.ylabel('Frecuencia')
plt.title('Distribución de diferencias', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 6. Matriz de confusión (predicciones finales)
plt.subplot(2, 3, 6)
# Generar predicciones
val_generator.reset()
y_true = val_generator.classes
y_pred_proba = model.predict(val_generator, verbose=0)
y_pred = (y_pred_proba > 0.5).astype(int).flatten()

from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicción')
plt.ylabel('Real')
plt.title('Matriz de Confusión Final', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('resultados_entrenamiento.png', dpi=150, bbox_inches='tight')
plt.show()

# ===========================
# Análisis de resultados
# ===========================
print("\n" + "="*60)
print("📈 ANÁLISIS DE RESULTADOS")
print("="*60)

# Estadísticas finales
best_val_acc = max(history['val_accuracy'])
best_val_acc_epoch = history['val_accuracy'].index(best_val_acc) + 1
final_val_acc = history['val_accuracy'][-1]
final_train_acc = history['accuracy'][-1]

# Calcular overfitting gap
overfitting_gap = final_train_acc - final_val_acc

print(f"\n🏆 Mejor precisión de validación: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")
print(f"   Logrado en la época: {best_val_acc_epoch}")
print(f"\n📊 Resultados finales:")
print(f"   • Precisión entrenamiento: {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
print(f"   • Precisión validación: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
print(f"   • Gap de overfitting: {overfitting_gap:.4f} ({overfitting_gap*100:.2f}%)")

# Interpretar resultados
if overfitting_gap > 0.15:
    print(f"\n⚠  ALERTA: Overfitting significativo (gap > 15%)")
    print("   Considera: Más aumentación de datos o más dropout")
elif overfitting_gap < 0.05:
    print(f"\n✅ Buen balance entre train y val")
else:
    print(f"\nℹ️  Overfitting moderado")

if final_val_acc < 0.6:
    print(f"\n🔴 BAJA PRECISIÓN: Considera recolectar más datos o revisar etiquetado")
elif final_val_acc < 0.75:
    print(f"\n🟡 PRECISIÓN MODERADA: Puede mejorar con más datos")
else:
    print(f"\n🟢 BUENA PRECISIÓN: ¡Excelente trabajo con datos limitados!")

# ===========================
# Guardar modelo final y reporte
# ===========================
print("\n💾 Guardando modelo y reporte...")

# Guardar modelo final
model.save('modelo_final_cortadas_quemaduras.keras')
print(f"✓ Modelo final guardado: modelo_final_cortadas_quemaduras.keras")

# Guardar reporte en texto
with open('reporte_entrenamiento.txt', 'w') as f:
    f.write("="*60 + "\n")
    f.write("REPORTE DE ENTRENAMIENTO - Cortadas vs Quemaduras\n")
    f.write("="*60 + "\n\n")
    f.write(f"Fecha: {pd.Timestamp.now()}\n")
    f.write(f"Modelo base: {base_model.name}\n")
    f.write(f"Total imágenes train: {train_generator.samples}\n")
    f.write(f"Total imágenes val: {val_generator.samples}\n")
    f.write(f"Clases: {class_names}\n")
    f.write(f"Mejor val accuracy: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)\n")
    f.write(f"Época del mejor modelo: {best_val_acc_epoch}\n")
    f.write(f"Final train accuracy: {final_train_acc:.4f}\n")
    f.write(f"Final val accuracy: {final_val_acc:.4f}\n")
    f.write(f"Overfitting gap: {overfitting_gap:.4f}\n")
    f.write(f"Class weights: {class_weight_dict}\n")

print("✓ Reporte guardado: reporte_entrenamiento.txt")

# ===========================
# Predicción de ejemplo
# ===========================
print("\n🔍 Realizando predicción de ejemplo...")

# Cargar una imagen aleatoria de validación
val_generator.reset()
batch = next(val_generator)
images, labels = batch

# Predecir primera imagen del batch
pred = model.predict(images[:1], verbose=0)[0][0]
true_label = labels[0]
pred_class = class_names[0] if pred < 0.5 else class_names[1]
true_class = class_names[0] if true_label < 0.5 else class_names[1]

print(f"✓ Predicción de ejemplo:")
print(f"   Imagen real: {true_class}")
print(f"   Predicción: {pred_class} (confianza: {max(pred, 1-pred):.2%})")

# ===========================
# Recomendaciones finales
# ===========================
print("\n" + "="*60)
print("💡 RECOMENDACIONES PARA MEJORAR")
print("="*60)

if final_val_acc < 0.70:
    print("\n1. 🔄 AUMENTAR DATOS:")
    print("   • Usar Roboflow (roboflow.com) para aumentar datos")
    print("   • Aplicar técnicas avanzadas de aumentación")
    print("   • Considerar web scraping controlado")
    
    print("\n2. 🎯 AJUSTAR MODELO:")
    print("   • Probar EfficientNetB0 en lugar de MobileNetV2")
    print("   • Aumentar dropout a 0.6-0.7")
    print("   • Reducir más el learning rate")
    
    print("\n3. 📊 MEJORAR DATOS:")
    print("   • Revisar etiquetado de imágenes")
    print("   • Eliminar imágenes de baja calidad")
    print("   • Balancear clases si hay desbalance > 60/40")

print("\n4. 📈 MONITOREO CONTINUO:")
print("   • Revisar matriz de confusión")
print("   • Verificar falsos positivos/negativos")
print("   • Ajustar umbral de clasificación si es necesario")

print("\n" + "="*60)
print("🎉 ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
print("="*60)