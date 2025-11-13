import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout, 
    RandomFlip, RandomRotation, BatchNormalization,
    GlobalAveragePooling2D, Activation
)
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from PIL import Image
import os
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import time


# ===========================
# Función para limpiar imágenes
# ===========================
# Esta función recorre una carpeta y sus subcarpetas buscando imágenes.
# Verifica que los archivos sean válidos, los convierte al formato RGB y los guarda como .jpg.
# Si encuentra archivos corruptos o con formato no válido, los elimina.
def limpiar_y_convertir_carpeta(carpeta):
    for root, dirs, files in os.walk(carpeta):
        for archivo in files:
            ruta_archivo = os.path.join(root, archivo)
            try:
                img = Image.open(ruta_archivo)
                img.verify()
                img = Image.open(ruta_archivo).convert('RGB')
                nuevo_nombre = os.path.splitext(ruta_archivo)[0] + ".jpg"
                img.save(nuevo_nombre, "JPEG")
                if ruta_archivo != nuevo_nombre:
                    os.remove(ruta_archivo)
            except Exception:
                print(f" Archivo inválido eliminado: {ruta_archivo}")
                os.remove(ruta_archivo)

# Limpio las imágenes tanto de entrenamiento como de validación antes de usarlas
print(" Limpiando y convirtiendo imágenes de train...")
limpiar_y_convertir_carpeta("data/train")
print(" Limpiando y convirtiendo imágenes de val...")
limpiar_y_convertir_carpeta("data/val")

# ===========================
# Data Augmentation y Generadores
# ===========================
# Aquí preparo los generadores de datos para entrenamiento y validación.
# Al generador de entrenamiento le aplico aumentos mejorados para mayor variabilidad.
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,              # Aumentado de 20 a 30 grados
    width_shift_range=0.2,          # Aumentado de 0.1 a 0.2
    height_shift_range=0.2,         # Aumentado de 0.1 a 0.2
    zoom_range=0.2,                 # Aumentado de 0.1 a 0.2
    horizontal_flip=True,
    vertical_flip=True,             # Nuevo: flip vertical
    shear_range=0.2,                # Nuevo: transformación de cizalla
    brightness_range=[0.8, 1.2],    # Nuevo: variación de brillo
    fill_mode='nearest'
)

# El generador de validación solo reescala las imágenes, sin aplicar aumentos.
val_datagen = ImageDataGenerator(rescale=1./255)

# Creo los lotes de imágenes desde las carpetas correspondientes
#  Ruta base de este archivo model.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#  Rutas absolutas a los datos
TRAIN_DIR = os.path.join(BASE_DIR, "data/train")
VAL_DIR = os.path.join(BASE_DIR, "data/val")

# Aumentar resolución para mejor captura de detalles (opcional: usar 224x224 si tienes GPU)
IMG_SIZE = 224  # Aumentado de 128 a 224 para mejor precisión

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32,
    class_mode="sparse",  # las etiquetas se manejan como enteros
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32,
    class_mode="sparse"
)

# ===========================
# Definir modelo CNN mejorado
# ===========================
# Arquitectura más profunda y robusta con Batch Normalization y regularización L2
# para mejorar la precisión y reducir el overfitting.
model = Sequential([
    # Data augmentation en la capa del modelo
    RandomFlip("horizontal"),
    RandomRotation(0.1),
    
    # Bloque 1: Primera capa convolucional
    Conv2D(32, (3, 3), padding='same', kernel_regularizer=l2(0.001), input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    BatchNormalization(),
    Activation('relu'),
    Conv2D(32, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    MaxPooling2D(2, 2),
    Dropout(0.25),
    
    # Bloque 2: Segunda capa convolucional
    Conv2D(64, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    Conv2D(64, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    MaxPooling2D(2, 2),
    Dropout(0.25),
    
    # Bloque 3: Tercera capa convolucional (nuevo)
    Conv2D(128, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    Conv2D(128, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    MaxPooling2D(2, 2),
    Dropout(0.25),
    
    # Bloque 4: Cuarta capa convolucional (nuevo)
    Conv2D(256, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    Conv2D(256, (3, 3), padding='same', kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    MaxPooling2D(2, 2),
    Dropout(0.25),
    
    # Global Average Pooling en lugar de Flatten para reducir overfitting
    GlobalAveragePooling2D(),
    
    # Capas densas mejoradas
    Dense(512, kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    Dropout(0.5),
    
    Dense(256, kernel_regularizer=l2(0.001)),
    BatchNormalization(),
    Activation('relu'),
    Dropout(0.5),
    
    # Capa de salida
    Dense(2, activation='softmax')  # 2 clases: quemaduras y cortadas
])

# ===========================
# Compilar modelo
# ===========================
# Compilo el modelo usando Adam con learning rate ajustado y entropía 
# cruzada como función de pérdida.
# También mido la precisión para ver el rendimiento.
model.compile(
    optimizer=Adam(learning_rate=0.001),  # Learning rate inicial más bajo para mejor convergencia
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ===========================
# Callbacks mejorados
# ===========================
# EarlyStopping: Detiene el entrenamiento si no mejora la validación
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=15,  # Aumentado de 10 a 15 para dar más oportunidades
    restore_best_weights=True,
    verbose=1
)

# ModelCheckpoint: Guarda automáticamente el mejor modelo
checkpoint = ModelCheckpoint(
    "modelo_quemaduras_cortadas.keras",
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)

# ReduceLROnPlateau: Reduce el learning rate cuando el modelo deja de mejorar
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,      # Reduce el LR a la mitad
    patience=5,      # Espera 5 épocas sin mejora
    min_lr=0.00001,  # LR mínimo
    verbose=1
)


# ===========================
# Entrenar modelo
# ===========================
# Entreno el modelo con los datos de entrenamiento y validación, aplicando las callbacks configuradas.
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=200,
    callbacks=[early_stop, checkpoint, reduce_lr]  # Agregado reduce_lr
)
# ===========================
# Guardar modelo
# ===========================
# Guardo el modelo final entrenado en un archivo .keras
model.save("modelo_quemaduras_cortadas.keras")

# ===========================
# Clase para manejar el modelo guardado
# ===========================
# Esta clase me permite recargar el modelo si el archivo ha sido modificado
# y usarlo para hacer predicciones actualizadas.
class ModelManager:
    def __init__(self, path_model):
        self.path_model = path_model
        self.last_modified = 0
        self.model = None
        self.reload_model()

    def reload_model(self):
        """Cargar el modelo si cambió el archivo"""
        try:
            modified = os.path.getmtime(self.path_model)
            if modified > self.last_modified or self.model is None:
                self.model = load_model(self.path_model)
                self.last_modified = modified
                print(f" Modelo recargado: {time.ctime(modified)}") 
        except Exception as e:
            print(f" Error al cargar el modelo: {e}")
    
    def predict(self, img_array):
        """Asegurarse de usar el modelo actualizado"""
        self.reload_model()
        pred = self.model.predict(img_array, verbose=0)
        return pred
    

    # Lista de clases reconocidas por el modelo
clases = ["quemaduras", "cortadas"]


# ===========================
# Graficar entrenamiento
# ===========================
# Finalmente, grafico las curvas de precisión del entrenamiento y la validación
# para visualizar cómo fue el rendimiento del modelo.
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.xlabel("Épocas")
plt.ylabel("Precisión")
plt.title("CNN - Quemaduras vs Cortadas")
plt.legend()
plt.show()
