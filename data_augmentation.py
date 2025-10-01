import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img, save_img
import numpy as np

# Directorios
train_dir = "data/train"
output_dir = "data/train_augmented"

# Crear carpeta de salida si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Parámetros de aumento de datos
datagen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Recorrer cada clase
for class_name in os.listdir(train_dir):
    class_path = os.path.join(train_dir, class_name)
    output_class_path = os.path.join(output_dir, class_name)

    if not os.path.exists(output_class_path):
        os.makedirs(output_class_path)

    # Procesar cada imagen
    for img_name in os.listdir(class_path):
        img_path = os.path.join(class_path, img_name)
        img = load_img(img_path)                  # Cargar imagen
        x = img_to_array(img)                     # Convertir a array
        x = x.reshape((1,) + x.shape)             # Reshape para el datagen

        # Generar 5 imágenes nuevas por cada original
        i = 0
        for batch in datagen.flow(x, batch_size=1, save_to_dir=output_class_path, save_prefix='aug', save_format='jpg'):
            i += 1
            if i >= 5:  # Cambia el número para generar más/menos imágenes
                break

print("✅ Aumento de datos completado. Revisa la carpeta data/train_augmented")
