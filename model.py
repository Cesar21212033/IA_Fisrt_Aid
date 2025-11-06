import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, RandomFlip, RandomRotation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from PIL import Image
import os
from tensorflow.keras.models import Sequential, load_model
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
# Al generador de entrenamiento le aplico aumentos como rotaciones, desplazamientos y flips horizontales.
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
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

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(128,128),
    batch_size=32,
    class_mode="sparse",  # las etiquetas se manejan como enteros
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(128,128),
    batch_size=32,
    class_mode="sparse"
)

# ===========================
# Definir modelo CNN
# ===========================
# Defino una red neuronal convolucional secuencial.
# Uso capas de aumento de datos, convolución, pooling, y una densa final para clasificar entre 2 clases.
model = Sequential([
    RandomFlip("horizontal"),
    RandomRotation(0.1),

    Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),

    Dense(2, activation='softmax')  # 2 clases: quemaduras y cortadas
])

# ===========================
# Compilar modelo
# ===========================
# Compilo el modelo usando Adam como optimizador y entropía 
# cruzada como función de pérdida.
# También mido la precisión para ver el rendimiento.
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Uso EarlyStopping para detener el entrenamiento si no mejora la 
# validación después de cierto número de épocas.
early_stop = EarlyStopping(
    monitor='val_loss',  # también puedo usar 'val_accuracy'
    patience=10,
    restore_best_weights=True
)

# Uso ModelCheckpoint para guardar automáticamente el mejoR
#  modelo basado en la precisión de validación.
checkpoint = ModelCheckpoint(
    "modelo_quemaduras_cortadas.keras",  # mismo nombre que mi archivo actual
    monitor="val_accuracy",            # guarda cuando mejora la precisión en validación
    save_best_only=True,               # solo guarda el mejor modelo
    mode="max",                        # porque quiero maximizar la precisión
    verbose=1                          # muestra mensaje cuando se guarda
)


# ===========================
# Entrenar modelo
# ===========================
# Entreno el modelo con los datos de entrenamiento y validación, aplicando las callbacks configuradas.
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=200,
    callbacks=[early_stop, checkpoint]
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
