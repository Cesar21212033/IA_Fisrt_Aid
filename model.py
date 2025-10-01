import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers import RandomFlip, RandomRotation
import matplotlib.pyplot as plt
from utils import cargar_imagenes, mostrar_imagenes, reporte_modelo

# ================================
# 1. Cargar datasets usando utils.py
# ================================
X_train, y_train, clases = cargar_imagenes("data/train_augmented")
X_val, y_val, _ = cargar_imagenes("data/val")

# Normalización
X_train = X_train / 255.0
X_val = X_val / 255.0

# Opcional: mostrar algunas imágenes
mostrar_imagenes(X_train, y_train, clases, n=9)

# ================================
# 2. Definir el modelo CNN
# ================================
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
    Dense(len(clases), activation='softmax')  # Número de clases dinámico
])

# ================================
# 3. Compilar modelo
# ================================
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# ================================
# 4. Entrenar
# ================================
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=10,
    batch_size=32
)

# ================================
# 5. Guardar modelo
# ================================
model.save("modelo_lesiones_brazos.h5")

# ================================
# 6. Graficar entrenamiento
# ================================
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.legend()
plt.show()

# ================================
# 7. Evaluación con utils.py
# ================================
reporte_modelo(model, X_val, y_val, clases)
