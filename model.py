import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers import RandomFlip, RandomRotation  # 👈 IMPORTAR ESTO
import matplotlib.pyplot as plt



# 1. Cargar datasets
train_dataset = tf.keras.utils.image_dataset_from_directory(
    "data/train_augmented",
    image_size=(128, 128),
    batch_size=32
)


val_dataset = tf.keras.utils.image_dataset_from_directory(
    "data/val",
    image_size=(128, 128),
    batch_size=32
)

# 2. Normalización
train_dataset = train_dataset.map(lambda x, y: (x/255.0, y))
val_dataset = val_dataset.map(lambda x, y: (x/255.0, y))

# 3. Definir el modelo CNN
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
    Dense(3, activation='softmax')  # 3 clases: cortes, quemaduras, golpes
])

# 4. Compilar
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 5. Entrenar
history = model.fit(train_dataset, validation_data=val_dataset, epochs=10)

# 6. Guardar modelo
model.save("modelo_lesiones_brazos.h5")

# 7. Graficar entrenamiento
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.legend()
plt.show()
