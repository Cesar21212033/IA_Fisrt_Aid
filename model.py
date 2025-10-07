import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, RandomFlip, RandomRotation
import matplotlib.pyplot as plt
from PIL import Image
import os

# ===========================
# Funciones para limpiar imágenes
# ===========================
def limpiar_y_convertir_carpeta(carpeta):
    for root, dirs, files in os.walk(carpeta):
        for archivo in files:
            ruta_archivo = os.path.join(root, archivo)
            try:
                # Abrir imagen y verificar que no esté corrupta
                img = Image.open(ruta_archivo)
                img.verify()
                
                # Reabrir y convertir a RGB (por si no está en ese formato)
                img = Image.open(ruta_archivo).convert('RGB')
                nuevo_nombre = os.path.splitext(ruta_archivo)[0] + ".jpg"
                img.save(nuevo_nombre, "JPEG")
                
                # Si el archivo original no era .jpg, eliminarlo
                if ruta_archivo != nuevo_nombre:
                    os.remove(ruta_archivo)

            except Exception:
                print(f"❌ Archivo inválido eliminado: {ruta_archivo}")
                os.remove(ruta_archivo)

# ===========================
# Limpiar carpetas antes de cargar datasets
# ===========================
print("🔹 Limpiando y convirtiendo imágenes de train...")
limpiar_y_convertir_carpeta("data/train")
print("🔹 Limpiando y convirtiendo imágenes de val...")
limpiar_y_convertir_carpeta("data/val")

# ===========================
# 1. Cargar datasets
# ===========================
train_dataset = tf.keras.utils.image_dataset_from_directory(
    "data/train",
    image_size=(128, 128),
    batch_size=32,
    label_mode="int",
)

val_dataset = tf.keras.utils.image_dataset_from_directory(
    "data/val",
    image_size=(128, 128),
    batch_size=32,
    label_mode="int",
)

# ===========================
# 2. Normalización
# ===========================
train_dataset = train_dataset.map(lambda x, y: (x/255.0, y))
val_dataset = val_dataset.map(lambda x, y: (x/255.0, y))

# ===========================
# 3. Definir el modelo CNN
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
    Dense(3, activation='softmax')  # cambiar si no son 3 clases
])

# ===========================
# 4. Compilar
# ===========================
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# ===========================
# 5. Entrenar
# ===========================
history = model.fit(train_dataset, validation_data=val_dataset, epochs=10)

# ===========================
# 6. Guardar modelo
# ===========================
model.save("modelo_lesiones_brazos.h5")

# ===========================
# 7. Graficar entrenamiento
# ===========================
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.xlabel("Épocas")
plt.ylabel("Precisión")
plt.legend()
plt.show()
