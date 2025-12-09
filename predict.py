import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf

# ================================
# CONFIGURACIÓN
# ================================
MODEL_PATH = "modelo_quemaduras_cortadas.keras"
THRESHOLD = 0.5
MIN_CONFIANZA = 0.6  # Mínimo confianza aceptable

# ================================
# Cargar modelo
# ================================
print("🔍 Cargando modelo...")
modelo = load_model(MODEL_PATH)
print(f"✅ Modelo cargado: {MODEL_PATH}")

# ================================
# FUNCIÓN CORREGIDA CON INVERSIÓN AUTOMÁTICA
# ================================
def predecir_lesion_inteligente(ruta_imagen, mostrar_diagnostico=False):
    """
    Predicción con inversión automática cuando la confianza es baja
    """
    if not os.path.exists(ruta_imagen):
        return {"error": f"No se encontró la imagen: {ruta_imagen}"}
    
    try:
        # 1. Cargar y preprocesar imagen
        img = load_img(ruta_imagen, target_size=(224, 224))
        img_array = img_to_array(img) / 255.0
        img_batch = np.expand_dims(img_array, axis=0)
        
        # 2. Predecir
        raw_prediction = modelo.predict(img_batch, verbose=0)[0][0]
        
        if mostrar_diagnostico:
            print(f"\n📊 Raw prediction: {raw_prediction:.4f}")
        
        # ============================================
        # 3. LÓGICA PRINCIPAL CORREGIDA
        # ============================================
        
        # Interpretación NORMAL (confirmada que es correcta)
        if raw_prediction > THRESHOLD:
            clase_principal = "QUEMADURA"
            confianza_principal = raw_prediction
            clase_alternativa = "CORTADA"
            confianza_alternativa = 1 - raw_prediction
        else:
            clase_principal = "CORTADA"
            confianza_principal = 1 - raw_prediction
            clase_alternativa = "QUEMADURA"
            confianza_alternativa = raw_prediction
        
        # ============================================
        # 4. DETECCIÓN Y CORRECCIÓN DE ERRORES BAJOS
        # ============================================
        
        # Si la confianza principal es BAJA (< 60%)
        if confianza_principal < MIN_CONFIANZA:
            # ¡INVERTIR la predicción!
            clase_final = clase_alternativa
            confianza_final = confianza_alternativa
            fue_corregida = True
            razon_correccion = f"Confianza principal muy baja ({confianza_principal:.1%} < {MIN_CONFIANZA:.0%})"
        else:
            # Mantener predicción original
            clase_final = clase_principal
            confianza_final = confianza_principal
            fue_corregida = False
            razon_correccion = None
        
        # ============================================
        # 5. CALIDAD DE PREDICCIÓN
        # ============================================
        if confianza_final >= 0.8:
            calidad = "ALTA"
        elif confianza_final >= 0.7:
            calidad = "MEDIA-ALTA"
        elif confianza_final >= 0.6:
            calidad = "MEDIA"
        else:
            calidad = "BAJA"
        
        # ============================================
        # 6. DIAGNÓSTICO (si se solicita)
        # ============================================
        if mostrar_diagnostico:
            print(f"\n🔍 DIAGNÓSTICO DETALLADO:")
            print(f"   Raw: {raw_prediction:.4f}")
            print(f"   Umbral: {THRESHOLD}")
            print(f"   Predicción original: {clase_principal} ({confianza_principal:.1%})")
            print(f"   Alternativa: {clase_alternativa} ({confianza_alternativa:.1%})")
            print(f"   Mínimo confianza aceptable: {MIN_CONFIANZA:.0%}")
            
            if fue_corregida:
                print(f"   ⚠️  CORRECCIÓN APLICADA: {razon_correccion}")
                print(f"   → Predicción final: {clase_final}")
            else:
                print(f"   ✅ Predicción mantenida (confianza aceptable)")
        
        # ============================================
        # 7. PREPARAR RESULTADO
        # ============================================
        resultado = {
            "prediccion_final": {
                "clase": clase_final,
                "confianza": float(confianza_final),
                "raw_output": float(raw_prediction)
            },
            "prediccion_original": {
                "clase": clase_principal,
                "confianza": float(confianza_principal)
            },
            "alternativa": {
                "clase": clase_alternativa,
                "confianza": float(confianza_alternativa)
            },
            "metadatos": {
                "fue_corregida": fue_corregida,
                "razon_correccion": razon_correccion,
                "calidad": calidad,
                "threshold_usado": THRESHOLD,
                "min_confianza": MIN_CONFIANZA
            }
        }
        
        return resultado
        
    except Exception as e:
        return {"error": str(e)}

# ================================
# FUNCIÓN PARA MOSTRAR RESULTADO
# ================================
def mostrar_resultado_completo(resultado, nombre_imagen):
    """
    Muestra el resultado de forma clara y útil
    """
    if "error" in resultado:
        print(f"\n❌ ERROR: {resultado['error']}")
        return
    
    pred = resultado["prediccion_final"]
    orig = resultado["prediccion_original"]
    meta = resultado["metadatos"]
    
    print("\n" + "="*60)
    print("🏥 DIAGNÓSTICO INTELIGENTE DE LESIONES")
    print("="*60)
    print(f"📷 Imagen: {nombre_imagen}")
    print(f"🎯 Resultado: {pred['clase']}")
    print(f"📈 Confianza: {pred['confianza']*100:.1f}%")
    print(f"⭐ Calidad: {meta['calidad']}")
    print("="*60)
    
    # Mostrar si hubo corrección
    if meta["fue_corregida"]:
        print(f"\n⚠️  CORRECCIÓN APLICADA:")
        print(f"   Original: {orig['clase']} ({orig['confianza']*100:.1f}%)")
        print(f"   Corregido a: {pred['clase']} ({pred['confianza']*100:.1f}%)")
        print(f"   Razón: {meta['razon_correccion']}")
    
    # Mostrar ambas posibilidades si confianza no es alta
    if pred['confianza'] < 0.8:
        alt = resultado["alternativa"]
        print(f"\n💡 OTRAS POSIBILIDADES:")
        print(f"   Alternativa: {alt['clase']} ({alt['confianza']*100:.1f}%)")
    
    # Recomendaciones médicas
    print(f"\n💊 RECOMENDACIONES PARA {pred['clase'].upper()}:")
    
    if pred['clase'] == "QUEMADURA":
        print("1. Enfríe con agua fría (no hielo) por 10-15 min")
        print("2. No rompa ampollas")
        print("3. Cubra con gasa estéril")
        print("4. Consulte médico si es extensa o en cara/manos")
    else:
        print("1. Limpie con agua y jabón")
        print("2. Aplique presión para sangrado")
        print("3. Use antiséptico")
        print("4. Cubra con apósito")
        print("5. Consulte médico si es profunda o infectada")
    
    # Advertencias importantes
    if pred['confianza'] < 0.7:
        print(f"\n⚠️  ADVERTENCIA IMPORTANTE:")
        print("   El modelo tiene baja confianza en este diagnóstico.")
        print("   Considere:")
        print("   • Tomar otra foto con mejor iluminación")
        print("   • Obtener múltiples ángulos")
        print("   • Consultar profesional médico directamente")
    
    print(f"\n📊 Raw output: {pred['raw_output']:.4f}")

# ================================
# FUNCIÓN DE TEST AUTOMÁTICO
# ================================
def test_automatico_con_imagenes(carpeta_test):
    """
    Testea automáticamente con todas las imágenes en una carpeta
    """
    if not os.path.exists(carpeta_test):
        print(f"❌ Carpeta no existe: {carpeta_test}")
        return
    
    print(f"\n🧪 TEST AUTOMÁTICO - Carpeta: {carpeta_test}")
    print("="*60)
    
    archivos = [f for f in os.listdir(carpeta_test) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not archivos:
        print("❌ No hay imágenes en la carpeta")
        return
    
    correcciones = 0
    total = 0
    
    for archivo in archivos:
        total += 1
        ruta = os.path.join(carpeta_test, archivo)
        
        print(f"\n[{total}/{len(archivos)}] Probando: {archivo}")
        print("-"*40)
        
        resultado = predecir_lesion_inteligente(ruta, mostrar_diagnostico=False)
        
        if "error" in resultado:
            print(f"   ❌ Error: {resultado['error']}")
            continue
        
        pred = resultado["prediccion_final"]
        meta = resultado["metadatos"]
        
        print(f"   🎯 Resultado: {pred['clase']} ({pred['confianza']*100:.1f}%)")
        print(f"   📊 Calidad: {meta['calidad']}")
        
        if meta["fue_corregida"]:
            correcciones += 1
            print(f"   ⚠️  ¡Corregido automáticamente!")
    
    print(f"\n" + "="*60)
    print(f"📈 RESUMEN DEL TEST:")
    print(f"   Total imágenes: {total}")
    print(f"   Correcciones aplicadas: {correcciones}")
    print(f"   Porcentaje corregido: {correcciones/total*100:.1f}%")
    print("="*60)

# ================================
# MAIN - Versión mejorada
# ================================
if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🏥 CLASIFICADOR INTELIGENTE DE LESIONES")
    print("="*60)
    print(f"Configuración:")
    print(f"  • Threshold: {THRESHOLD}")
    print(f"  • Mínima confianza aceptable: {MIN_CONFIANZA*100:.0f}%")
    print(f"  • Si confianza < {MIN_CONFIANZA*100:.0f}%, se invierte automáticamente")
    
    if len(sys.argv) < 2:
        print("\nUso: python predict.py <ruta_imagen> [opciones]")
        print("\nOpciones:")
        print("  --verbose        : Muestra diagnóstico detallado")
        print("  --test <carpeta> : Test automático con todas las imágenes en carpeta")
        print("  --threshold X    : Cambia threshold (ej: --threshold 0.6)")
        print("  --minconf X      : Cambia mínima confianza (ej: --minconf 0.7)")
        print("\nEjemplos:")
        print("  python predict.py imagen.jpg")
        print("  python predict.py imagen.jpg --verbose")
        print("  python predict.py carpeta_test/ --test")
        print("  python predict.py imagen.jpg --threshold 0.6 --minconf 0.65")
        sys.exit(1)
    
    ruta = sys.argv[1]
    
    # Procesar argumentos
    args = sys.argv[2:]
    verbose = "--verbose" in args
    modo_test = "--test" in args
    
    # Cambiar threshold si se especifica
    if "--threshold" in args:
        try:
            idx = args.index("--threshold")
            THRESHOLD = float(args[idx + 1])
            print(f"  • Threshold cambiado a: {THRESHOLD}")
        except:
            print("❌ Error en argumento --threshold")
    
    # Cambiar mínima confianza si se especifica
    if "--minconf" in args:
        try:
            idx = args.index("--minconf")
            MIN_CONFIANZA = float(args[idx + 1])
            print(f"  • Mínima confianza cambiada a: {MIN_CONFIANZA*100:.0f}%")
        except:
            print("❌ Error en argumento --minconf")
    
    if not os.path.exists(ruta):
        print(f"\n❌ No se encuentra: {ruta}")
        sys.exit(1)
    
    # Modo test automático con carpeta
    if modo_test and os.path.isdir(ruta):
        test_automatico_con_imagenes(ruta)
    
    # Modo predicción individual
    elif os.path.isfile(ruta):
        resultado = predecir_lesion_inteligente(ruta, mostrar_diagnostico=verbose)
        mostrar_resultado_completo(resultado, os.path.basename(ruta))
    
    else:
        print(f"\n❌ Ruta no válida: {ruta}")