"""
Script para analizar la arquitectura del modelo y contar neuronas
"""
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# ===========================
# Definir el mismo modelo que en model.py
# ===========================
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    MaxPooling2D(2,2),
    
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    
    Flatten(),
    Dense(258, activation='relu'),
    Dropout(0.5),
    
    Dense(2, activation='softmax')  # 2 clases: quemaduras y cortadas
])

# Compilar el modelo (necesario para contar parámetros)
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ===========================
# Análisis del modelo
# ===========================
print("=" * 60)
print("ANÁLISIS DE LA ARQUITECTURA DEL MODELO")
print("=" * 60)
print("\n")

# Resumen del modelo
print("RESUMEN DEL MODELO:")
print("-" * 60)
model.summary()

print("\n" + "=" * 60)
print("CONTEO DE NEURONAS")
print("=" * 60)
print("\n")

# Contar neuronas en capas densas
neuronas_totales = 0
neuronas_por_capa = {}

for i, layer in enumerate(model.layers):
    layer_type = type(layer).__name__
    
    if layer_type == 'Dense':
        # Las capas Dense tienen neuronas
        neuronas = layer.units if hasattr(layer, 'units') else layer.output_shape[-1]
        neuronas_totales += neuronas
        neuronas_por_capa[f"Capas {i+1} ({layer.name})"] = neuronas
        print(f"Capas {i+1} ({layer.name}): {neuronas} neuronas")
    elif layer_type == 'Conv2D':
        # Las capas convolucionales tienen filtros, no neuronas tradicionales
        filtros = layer.filters if hasattr(layer, 'filters') else 0
        print(f"Capas {i+1} ({layer.name}): {filtros} filtros convolucionales (no son neuronas tradicionales)")

print("\n" + "-" * 60)
print(f"NEURONAS TOTALES EN CAPAS DENSAS: {neuronas_totales}")
print("-" * 60)

# Contar parámetros entrenables
parametros_totales = model.count_params()
print(f"\nPARÁMETROS TOTALES ENTRENABLES: {parametros_totales:,}")

# Desglose por capa
print("\n" + "=" * 60)
print("DESGLOSE DE PARÁMETROS POR CAPA")
print("=" * 60)
print("\n")

for i, layer in enumerate(model.layers):
    layer_type = type(layer).__name__
    params = layer.count_params()
    
    if params > 0:
        print(f"Capas {i+1} ({layer.name}) - Tipo: {layer_type}")
        print(f"  Parámetros: {params:,}")
        
        # Calcular tamaño de entrada y salida
        if hasattr(layer, 'input_shape') and layer.input_shape:
            print(f"  Input shape: {layer.input_shape}")
        if hasattr(layer, 'output_shape') and layer.output_shape:
            print(f"  Output shape: {layer.output_shape}")
        print()

print("=" * 60)

