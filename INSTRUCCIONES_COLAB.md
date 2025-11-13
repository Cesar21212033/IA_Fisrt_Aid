# 🚀 Guía para Entrenar el Modelo en Google Colab con GPU

Esta guía te ayudará a entrenar tu modelo CNN mejorado usando GPU gratuita de Google Colab.

## 📋 Pasos para usar el notebook en Colab

### Paso 1: Abrir Google Colab
1. Ve a [Google Colab](https://colab.research.google.com/)
2. Inicia sesión con tu cuenta de Google

### Paso 2: Subir el notebook
1. Haz clic en **File → Upload notebook**
2. Sube el archivo `colab_train.ipynb` que está en la raíz del proyecto
3. O simplemente copia y pega el contenido del notebook en un nuevo notebook de Colab

### Paso 3: Configurar GPU ⚡
**IMPORTANTE**: Antes de ejecutar cualquier celda, configura la GPU:

1. Ve a **Runtime → Change runtime type**
2. En **Hardware accelerator**, selecciona **GPU**
3. Opcionalmente selecciona **T4 GPU** o **A100 GPU** (si está disponible)
4. Haz clic en **Save**

### Paso 4: Ejecutar las celdas en orden

Ejecuta las celdas del notebook en orden (de arriba hacia abajo):

#### Celda 1: Verificar GPU
- Verifica que TensorFlow detecte la GPU
- Configura el crecimiento de memoria GPU

#### Celda 2: Instalar dependencias
- Instala TensorFlow, Pillow, Matplotlib y NumPy
- Esto puede tomar 1-2 minutos

#### Celda 3: Subir datos
Tienes **dos opciones**:

**Opción A: Subir manualmente (Recomendado para primera vez)**
1. En el panel izquierdo de Colab, haz clic en el ícono de carpeta 📁
2. Haz clic derecho en el área de archivos → **Upload folder**
3. Selecciona tu carpeta `data` completa (debe contener `train/` y `val/`)
4. Espera a que termine la carga
5. Ejecuta la celda para verificar

**Opción B: Usar Google Drive**
1. Sube tu carpeta `data` a Google Drive
2. Ejecuta la celda que monta Google Drive
3. Ajusta la ruta si es necesario: `/content/drive/MyDrive/IA-Convolucional/data`

#### Celda 4-8: Preparar y entrenar el modelo
- Estas celdas ejecutan todo el proceso:
  - Limpieza de imágenes
  - Configuración de generadores de datos
  - Construcción del modelo mejorado
  - Entrenamiento con GPU

**⏱️ Tiempo estimado de entrenamiento:**
- Con GPU T4: ~30-60 minutos (dependiendo del número de épocas)
- Con GPU A100: ~15-30 minutos
- Sin GPU: ~3-6 horas ⚠️

#### Celda 9: Visualizar resultados
- Muestra gráficos de precisión y pérdida
- Muestra estadísticas del entrenamiento

#### Celda 10: Descargar modelo
- Descarga el modelo entrenado (`modelo_quemaduras_cortadas.keras`)
- O guárdalo en Google Drive

## 📁 Estructura de datos requerida

Tu carpeta `data` debe tener esta estructura:

```
data/
├── train/
│   ├── Brazo/
│   │   ├── cortes/
│   │   │   ├── imagen1.jpg
│   │   │   ├── imagen2.jpg
│   │   │   └── ...
│   │   └── quemaduras/
│   │       ├── imagen1.jpg
│   │       └── ...
│   └── Pierna/
│       ├── cortes/
│       └── quemaduras/
└── val/
    ├── Brazo/
    │   ├── cortes/
    │   └── quemaduras/
    └── Pierna/
        ├── cortes/
        └── quemaduras/
```

## ⚙️ Configuraciones opcionales

### Aumentar batch size (si tienes GPU potente)
En la celda de configuración de generadores, puedes cambiar:
```python
BATCH_SIZE = 32  # Cambiar a 64 o 128 si tienes A100 GPU
```

### Ajustar tamaño de imagen
```python
IMG_SIZE = 224  # Puedes usar 256 o 512 si tienes GPU potente
```

## 🔧 Solución de problemas

### Error: "No se detectó GPU"
- Verifica que hayas seleccionado GPU en Runtime → Change runtime type
- A veces Colab no tiene GPUs disponibles (especialmente en horas pico)
- Intenta más tarde o usa CPU (será más lento)

### Error: "Out of memory"
- Reduce el `BATCH_SIZE` a 16 o 8
- Reduce el `IMG_SIZE` a 128
- Cierra otras pestañas de Colab que estén usando GPU

### Error: "No se encontraron los datos"
- Verifica que la carpeta `data` esté en la raíz del proyecto de Colab
- Verifica la estructura de carpetas
- Usa la opción de Google Drive si es más fácil

### El entrenamiento es muy lento
- Verifica que GPU esté activada: `Runtime → Change runtime type → GPU`
- Verifica que TensorFlow detecte la GPU en la primera celda
- Considera usar batch size más pequeño si hay problemas de memoria

## 📊 Monitoreo del entrenamiento

Durante el entrenamiento verás:
- **Loss**: Pérdida del modelo (debe disminuir)
- **Accuracy**: Precisión (debe aumentar)
- **Val_loss**: Pérdida en validación (debe disminuir)
- **Val_accuracy**: Precisión en validación (debe aumentar)

**Señales de buen entrenamiento:**
- ✅ Val_accuracy aumenta consistentemente
- ✅ Val_loss disminuye consistentemente
- ✅ No hay gran diferencia entre accuracy y val_accuracy (sin overfitting)

## 💾 Guardar y descargar el modelo

El modelo se guarda automáticamente durante el entrenamiento como `modelo_quemaduras_cortadas.keras`.

Para descargarlo:
1. Ejecuta la última celda del notebook
2. El archivo se descargará automáticamente
3. O guárdalo en Google Drive para acceso futuro

## 🎯 Próximos pasos después del entrenamiento

1. **Descarga el modelo** entrenado
2. **Reemplaza** el archivo `modelo_quemaduras_cortadas.keras` en tu proyecto local
3. **Prueba el modelo** con nuevas imágenes usando `predict.py`
4. **Integra** el modelo en tu aplicación FastAPI

## 📝 Notas importantes

- ⏰ Las sesiones de Colab tienen un límite de tiempo (12 horas máximo)
- 💾 Los archivos en Colab se eliminan cuando cierras la sesión (a menos que los guardes en Drive)
- 🆓 Colab ofrece GPU gratuita pero con límites de uso diario
- 🔄 Si el entrenamiento se interrumpe, puedes cargar el modelo guardado y continuar

## 🆘 ¿Necesitas ayuda?

Si encuentras problemas:
1. Revisa los mensajes de error en las celdas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que la estructura de datos sea correcta
4. Verifica que GPU esté activada

¡Buena suerte con el entrenamiento! 🚀

