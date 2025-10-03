import tensorflow as tf
import matplotlib.pyplot as plt

# Función para cargar y preprocesar imágenes
def cargar_imagen(ruta, size=(128,128)):
    img = tf.keras.utils.load_img(ruta, target_size=size)
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) / 255.0
    return img_array

# Función para mostrar imágenes con sus etiquetas
def mostrar_imagenes(dataset, class_names, num=5):
    plt.figure(figsize=(10, 10))
    for images, labels in dataset.take(1):
        for i in range(num):
            ax = plt.subplot(1, num, i + 1)
            plt.imshow(images[i].numpy().astype("uint8"))
            plt.title(class_names[labels[i]])
            plt.axis("off")
    plt.show()
