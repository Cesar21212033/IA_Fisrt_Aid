import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, RandomFlip, RandomRotation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from PIL import Image
import os

# ===========================
# Función para limpiar imágenes
# ===========================
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

# Limpiar carpetas
print("🔹 Limpiando y convirtiendo imágenes de train...")
limpiar_y_convertir_carpeta("data/train")
print("🔹 Limpiando y convirtiendo imágenes de val...")
limpiar_y_convertir_carpeta("data/val")

# ===========================
# Data Augmentation y Generadores
# ===========================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    "data/train",
    target_size=(128,128),
    batch_size=32,
    class_mode="sparse",  # etiquetas como enteros
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    "data/val",
    target_size=(128,128),
    batch_size=32,
    class_mode="sparse"
)

# ===========================
# Definir modelo CNN
# ===========================
model = Sequential([
    RandomFlip("horizontal"),
    RandomRotation(0.1),

    Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),

    Dense(2, activation='softmax')  # 2 clases: quemaduras y cortadas
])

# ===========================
# Compilar modelo
# ===========================
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ===========================
# Entrenar modelo
# ===========================
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=30  # aumenta número de épocas
)

# ===========================
# Guardar modelo
# ===========================
model.save("modelo_quemaduras_cortadas.h5")

# ===========================
# Graficar entrenamiento
# ===========================
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.xlabel("Épocas")
plt.ylabel("Precisión")
plt.title("CNN - Quemaduras vs Cortadas")
plt.legend()
plt.show()
