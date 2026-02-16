from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from io import BytesIO
from PIL import Image
import threading
import google.generativeai as genai
import logging
# Importaciones de conexion - usando importación directa ya que están en el mismo directorio
try:
    from conexion import obtener_historial, guardar_diagnostico, guardar_conversacion, obtener_conversaciones
except ImportError:
    # Fallback: importación relativa si la directa falla
    from .conexion import obtener_historial, guardar_diagnostico, guardar_conversacion, obtener_conversaciones



# ==========================
# Config FastAPI y CORS
# ==========================
app = FastAPI(title="IA First Aid API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Rutas y proyecto
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)
sys.path.append(BASE_DIR)  # Agregar el directorio frontend al path

from model import ModelManager  # traigo el modelo y las clases

clases = ModelManager.clases

# ==========================
# Endpoint raíz para verificar conexión
# ==========================
@app.get("/")
def root():
    return {"mensaje": "Servidor FastAPI funcionando correctamente", "status": "ok"}

# ==========================
# Config Gemini API
# ==========================
# IMPORTANTE: Usa variables de entorno para la API key
# Crea un archivo .env en la raíz del proyecto o en frontend/ con: GEMINI_API_KEY=tu_api_key_aqui
# O exporta la variable: export GEMINI_API_KEY=tu_api_key_aqui

# Intentar cargar python-dotenv si está disponible
try:
    from dotenv import load_dotenv
    # Buscar .env en la raíz del proyecto primero, luego en frontend/
    env_path_root = os.path.join(PROJECT_ROOT, '.env')
    env_path_frontend = os.path.join(BASE_DIR, '.env')
    
    if os.path.exists(env_path_root):
        load_dotenv(env_path_root)
        print(f"✓ Archivo .env cargado desde: {env_path_root}")
    elif os.path.exists(env_path_frontend):
        load_dotenv(env_path_frontend)
        print(f"✓ Archivo .env cargado desde: {env_path_frontend}")
    else:
        # Intentar cargar desde ubicación por defecto
        load_dotenv()
except ImportError:
    print("⚠️  python-dotenv no está instalado. Instala con: pip install python-dotenv")
    print("   O configura GEMINI_API_KEY como variable de entorno del sistema.")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Lee de variable de entorno o .env

if not GEMINI_API_KEY:
    print("⚠️  ADVERTENCIA: GEMINI_API_KEY no está configurada.")
    print("   Las recomendaciones usarán el sistema de fallback.")
    print("   Para usar Gemini AI, crea un archivo .env con: GEMINI_API_KEY=tu_api_key")
    print("   Obtén una nueva API key en: https://makersuite.google.com/app/apikey")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"✓ API Key de Gemini configurada correctamente (primeros 10 caracteres: {GEMINI_API_KEY[:10]}...)")

def obtener_modelos_gemini_texto():
    """
    Obtiene modelos de Gemini para texto (sin visión)
    Usa modelos que sabemos que funcionan para texto
    """
    # Modelos que funcionan para texto (sin visión)
    modelos_texto = ["gemini-pro", "models/gemini-pro"]
    
    # Intentar listar modelos disponibles
    try:
        modelos_disponibles = genai.list_models()
        nombres_modelos = []
        for m in modelos_disponibles:
            if 'generateContent' in m.supported_generation_methods:
                nombre_completo = m.name
                nombre_corto = nombre_completo.split('/')[-1]
                # Solo modelos de texto (sin visión)
                if 'gemini' in nombre_corto.lower() and 'vision' not in nombre_corto.lower():
                    nombres_modelos.append(nombre_corto)
        
        if nombres_modelos:
            # Priorizar gemini-pro si está disponible
            if 'gemini-pro' in nombres_modelos:
                modelos_texto = ['gemini-pro'] + [m for m in nombres_modelos if m != 'gemini-pro']
            else:
                modelos_texto = nombres_modelos
            logging.info(f"Modelos Gemini texto disponibles: {modelos_texto[:3]}...")
            return modelos_texto
    except Exception as e:
        logging.warning(f"No se pudieron listar modelos Gemini: {e}")
    
    # Fallback: usar gemini-pro que es el más común y funciona
    return ["gemini-pro"]

def obtener_modelos_gemini_vision():
    """
    Obtiene modelos de Gemini para visión (análisis de imágenes)
    """
    # Modelos que funcionan para visión
    modelos_vision = ["gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"]
    
    # Intentar listar modelos disponibles
    try:
        modelos_disponibles = genai.list_models()
        nombres_modelos = []
        for m in modelos_disponibles:
            if 'generateContent' in m.supported_generation_methods:
                nombre_completo = m.name
                nombre_corto = nombre_completo.split('/')[-1]
                # Modelos con visión
                if 'gemini' in nombre_corto.lower() and ('vision' in nombre_corto.lower() or '1.5' in nombre_corto.lower()):
                    nombres_modelos.append(nombre_corto)
        
        if nombres_modelos:
            modelos_vision = nombres_modelos
            logging.info(f"Modelos Gemini visión disponibles: {modelos_vision[:3]}...")
            return modelos_vision
    except Exception as e:
        logging.warning(f"No se pudieron listar modelos Gemini visión: {e}")
    
    # Fallback
    return ["gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"]

def determinar_gravedad_por_imagen(imagen_bytes: bytes, clase_detectada: str) -> str:
    """
    Determina la gravedad analizando características visuales de la imagen usando Gemini Vision
    Retorna: 'leve', 'moderado', o 'urgente'
    """
    if not GEMINI_API_KEY:
        # Si no hay API key, usar lógica conservadora
        return "moderado" if clase_detectada.lower() == "cortadas" else "moderado"
    
    try:
        import base64
        
        # Convertir imagen a base64
        imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        
        # Crear prompt para análisis visual
        prompt = f"""Analiza esta imagen de una lesión clasificada como: {clase_detectada}.

Evalúa las siguientes características visuales para determinar la GRAVEDAD:

1. PROFUNDIDAD: ¿La herida es superficial o profunda? ¿Se ve tejido interno (músculo, grasa, hueso)?
2. APERTURA: ¿La herida está abierta? ¿Qué tan ancha es la apertura?
3. SANGRADO: ¿Hay sangrado abundante, moderado o mínimo?
4. EXTENSIÓN: ¿Qué tan grande es la lesión?
5. NECESITA SUTURA: ¿La herida parece requerir sutura médica?

Responde SOLO con una de estas tres palabras (sin explicaciones):
- "leve" - si es superficial, mínima apertura, sangrado mínimo, no requiere sutura
- "moderado" - si es moderadamente profunda, apertura visible, sangrado moderado, podría necesitar sutura
- "urgente" - si es profunda, muestra tejido interno, sangrado abundante, apertura ancha, DEFINITIVAMENTE requiere sutura o atención médica inmediata

Responde SOLO con la palabra: leve, moderado, o urgente"""

        # Usar Gemini Vision para analizar
        modelos_a_intentar = obtener_modelos_gemini_vision()
        
        for modelo_nombre in modelos_a_intentar:
            try:
                model = genai.GenerativeModel(modelo_nombre)
                
                # Preparar imagen para Gemini
                import PIL.Image
                imagen_pil = PIL.Image.open(BytesIO(imagen_bytes))
                
                # Generar respuesta
                respuesta = model.generate_content([prompt, imagen_pil])
                texto_respuesta = respuesta.text.strip().lower()
                
                logging.info(f"Respuesta de Gemini Vision ({modelo_nombre}): {texto_respuesta[:100]}")
                
                # Extraer la gravedad de la respuesta
                if "urgente" in texto_respuesta:
                    return "urgente"
                elif "moderado" in texto_respuesta:
                    return "moderado"
                elif "leve" in texto_respuesta:
                    return "leve"
                else:
                    # Si no se puede determinar, ser conservador
                    logging.warning(f"Respuesta de Gemini no clara: {texto_respuesta}. Usando 'moderado' por seguridad.")
                    return "moderado"
                    
            except Exception as e:
                logging.warning(f"Error con modelo {modelo_nombre}: {e}, intentando siguiente...")
                continue
        
        # Si todos los modelos fallan, usar lógica conservadora
        logging.warning("No se pudo analizar imagen con Gemini. Usando lógica conservadora.")
        return "moderado"
        
    except Exception as e:
        logging.error(f"Error al analizar imagen con Gemini Vision: {e}")
        # En caso de error, usar lógica conservadora
        return "moderado"

def determinar_gravedad(clase_detectada: str, probabilidad: float = None, imagen_bytes: bytes = None) -> str:
    """
    Determina el nivel de gravedad de la lesión
    Si se proporciona imagen_bytes, usa Gemini Vision para análisis visual
    Retorna: 'leve', 'moderado', o 'urgente'
    """
    # PRIORIDAD 1: Si tenemos la imagen, usar análisis visual con Gemini Vision
    if imagen_bytes is not None:
        return determinar_gravedad_por_imagen(imagen_bytes, clase_detectada)
    
    # PRIORIDAD 2: Si no hay probabilidad (análisis por texto), usar lógica basada solo en clase
    if probabilidad is None:
        # Por defecto, ser conservadores
        if clase_detectada.lower() == "quemaduras":
            return "moderado"
        elif clase_detectada.lower() == "cortadas":
            return "moderado"  # Cambiado de "leve" a "moderado" por seguridad
        else:
            return "urgente"  # Si no se puede determinar, mejor ser cauteloso
    
    # PRIORIDAD 3: Lógica basada en clase y probabilidad (fallback si no hay imagen)
    clase_lower = clase_detectada.lower()
    
    # Quemaduras: generalmente más graves
    if clase_lower == "quemaduras":
        if probabilidad < 0.6:  # Baja confianza
            return "urgente"
        elif probabilidad < 0.8:  # Confianza media
            return "moderado"
        else:  # Alta confianza
            return "moderado"  # Quemaduras siempre requieren atención
    
    # Cortadas: pueden ser leves, moderadas o urgentes
    # IMPORTANTE: La probabilidad solo indica confianza en el TIPO (cortada vs quemadura),
    # NO en la severidad. Una cortada profunda puede tener alta probabilidad pero ser grave.
    # Por seguridad, seremos más conservadores:
    elif clase_lower == "cortadas":
        if probabilidad < 0.6:  # Baja confianza - podría ser grave o mal clasificada
            return "urgente"
        elif probabilidad < 0.85:  # Confianza media-alta
            return "moderado"  # Por defecto moderado para ser conservadores
        else:  # Alta confianza (>= 0.85) - aún así, podría ser moderada
            # Ser conservador: alta confianza no significa que sea leve
            # Las cortadas profundas requieren atención médica
            return "moderado"  # Cambiado de "leve" a "moderado" por seguridad
    
    # Caso desconocido
    else:
        return "urgente"

def recomendacion_fallback(clase_detectada: str) -> str:
    """Recomendaciones predefinidas cuando Gemini no está disponible"""
    if clase_detectada.lower() == "quemaduras":
        return """QUEMADURAS - Primeros Auxilios:

1. DESCRIPCIÓN:
   Lesión en la piel causada por calor, productos químicos, electricidad o radiación.

2. TRES PASOS CRUCIALES:
   a) Enfriar inmediatamente: Aplicar agua fría (no hielo) durante 10-15 minutos
   b) Cubrir la herida: Usar gasa estéril o paño limpio, sin apretar
   c) Evaluar gravedad: Si es extensa, profunda o en cara/manos, buscar atención médica urgente

3. ADVERTENCIAS - NO HACER:
   ❌ NO romper ampollas
   ❌ NO aplicar cremas, mantequilla o remedios caseros
   ❌ NO quitar ropa adherida a la quemadura
   ❌ NO usar hielo directamente sobre la quemadura"""
    
    elif clase_detectada.lower() == "cortadas":
        return """CORTADAS - Primeros Auxilios:

1. DESCRIPCIÓN:
   Herida abierta en la piel causada por un objeto cortante.

2. TRES PASOS CRUCIALES:
   a) Limpiar la herida: Lavar con agua y jabón suave, eliminar suciedad visible
   b) Detener el sangrado: Aplicar presión directa con gasa estéril durante 5-10 minutos
   c) Proteger la herida: Cubrir con apósito estéril y cambiar diariamente

3. ADVERTENCIAS - NO HACER:
   ❌ NO usar alcohol directamente sobre la herida (causa más dolor)
   ❌ NO soplar sobre la herida (puede introducir bacterias)
   ❌ NO retirar objetos incrustados (buscar atención médica)
   ❌ NO ignorar signos de infección: enrojecimiento, pus, fiebre"""
    
    else:
        return f"""LESIÓN DETECTADA: {clase_detectada}

Recomendaciones generales:
1. Mantener la calma y evaluar la situación
2. Aplicar primeros auxilios básicos según el tipo de lesión
3. Buscar atención médica profesional si:
   - El sangrado no se detiene
   - La lesión es extensa o profunda
   - Hay signos de infección
   - La persona tiene dificultad para respirar

⚠️ IMPORTANTE: Estas son recomendaciones generales. Siempre consulta con un profesional médico para casos graves."""

def limpiar_markdown(texto: str) -> str:
    """Limpia formato markdown del texto para mostrar texto plano"""
    import re
    if not texto:
        return texto
    
    # Remover encabezados # ## ### (debe ir primero)
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    
    # Remover negritas **texto** o __texto__ (múltiples pasadas para casos anidados)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'__(.*?)__', r'\1', texto)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)  # Segunda pasada
    
    # Remover cursivas *texto* o _texto_ (pero no si están dentro de palabras)
    texto = re.sub(r'(?<!\w)\*(.*?)\*(?!\w)', r'\1', texto)
    texto = re.sub(r'(?<!\w)_(.*?)_(?!\w)', r'\1', texto)
    
    # Remover código `texto` o ```texto```
    texto = re.sub(r'```[\s\S]*?```', '', texto)  # Bloques de código
    texto = re.sub(r'`([^`]+)`', r'\1', texto)  # Código inline
    
    # Remover enlaces [texto](url) o [texto][ref]
    texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
    texto = re.sub(r'\[([^\]]+)\]\[[^\]]+\]', r'\1', texto)
    
    # Remover imágenes ![alt](url)
    texto = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', texto)
    
    # Remover listas con asteriscos o guiones al inicio (convertir a texto normal)
    texto = re.sub(r'^\s*[-*+]\s+', '', texto, flags=re.MULTILINE)
    
    # Remover números de lista (1. 2. etc) pero mantener el contenido
    texto = re.sub(r'^\s*\d+\.\s+', '', texto, flags=re.MULTILINE)
    
    # Limpiar espacios múltiples (pero mantener saltos de línea)
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        # Limpiar espacios múltiples en cada línea
        linea_limpia = re.sub(r' +', ' ', linea.strip())
        if linea_limpia:  # Solo agregar líneas no vacías
            lineas_limpias.append(linea_limpia)
    
    # Unir líneas y limpiar líneas vacías múltiples (máximo 2 líneas vacías)
    texto = '\n'.join(lineas_limpias)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()

def recomendacion_gemini(clase_detectada: str, gravedad: str = None) -> str:
    """Pido al AI que me diga qué hacer según la lesión"""
    # Verificar que la API key esté configurada
    if not GEMINI_API_KEY:
        return recomendacion_fallback(clase_detectada)
    
    # Determinar gravedad si no se proporciona
    if gravedad is None:
        gravedad = determinar_gravedad(clase_detectada)
    
    # Mensaje especial según gravedad
    mensaje_gravedad = ""
    if gravedad == "urgente":
        mensaje_gravedad = "\n\n⚠️ URGENTE: Esta lesión requiere atención médica inmediata. Después de aplicar primeros auxilios básicos, busque asistencia médica de emergencia de inmediato."
    elif gravedad == "moderado":
        mensaje_gravedad = "\n\n⚠️ MODERADO: Esta lesión requiere atención médica. Después de aplicar primeros auxilios, se recomienda consultar con un profesional de la salud para evaluación adecuada."
    
    prompt = f"""Actúa como un experto asistente de primeros auxilios. 
La lesión ha sido clasificada como: {clase_detectada}.
Nivel de gravedad estimado: {gravedad.upper()}

IMPORTANTE: Responde SOLO con texto plano, SIN formato markdown, SIN asteriscos, SIN negritas, SIN símbolos especiales.
Usa solo saltos de línea y texto normal.

Genera una respuesta profesional, clara y concisa sobre primeros auxilios con esta estructura:

1. DESCRIPCIÓN:
   [Breve descripción de la lesión y su severidad aparente]

2. TRES PASOS CRUCIALES:
   a) [Primer paso de acción inmediata]
   b) [Segundo paso de acción inmediata]
   c) [Tercer paso de acción inmediata]

3. ADVERTENCIAS - NO HACER:
   [Lista de cosas que NO se deben hacer]
{mensaje_gravedad}

IMPORTANTE: 
- Si la gravedad es URGENTE, DEBES incluir al final una recomendación clara y enfática de buscar asistencia médica inmediata.
- Si la gravedad es MODERADO, recomienda consultar con un profesional de la salud después de primeros auxilios.
- Si la lesión es profunda, abierta, muestra tejido interno, o sangra abundantemente, siempre recomienda atención médica profesional.

Responde directamente, sin introducciones ni explicaciones adicionales."""
    
    try:
        # Usar modelos de texto (sin visión)
        modelos_disponibles = obtener_modelos_gemini_texto()
        texto_respuesta = None
        
        for modelo_nombre in modelos_disponibles:
            try:
                model = genai.GenerativeModel(modelo_nombre)
                respuesta = model.generate_content(prompt)
                texto_respuesta = respuesta.text
                break  # Si funciona, salir del bucle
            except Exception as e:
                logging.warning(f"Error con modelo {modelo_nombre}: {e}, intentando siguiente...")
                continue
        
        if texto_respuesta:
            # Limpiar cualquier markdown que pueda venir
            texto_limpio = limpiar_markdown(texto_respuesta)
            return texto_limpio
        else:
            logging.warning("No se pudo conectar con ningún modelo de Gemini. Usando recomendaciones fallback.")
            return recomendacion_fallback(clase_detectada)
    except Exception as e:
        error_msg = str(e)
        # Si la API key está comprometida o inválida, usar recomendaciones fallback
        if "403" in error_msg or "API key" in error_msg or "leaked" in error_msg.lower():
            logging.warning(f"API key inválida o comprometida. Usando recomendaciones fallback.")
            return recomendacion_fallback(clase_detectada)
        return f"Error al generar la recomendación: {e}"


# ==========================
# Inicialización del modelo
# ==========================
modelo_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras")
modelo_manager = ModelManager(modelo_path)
modelo_lock = threading.Lock()  # bloqueo para evitar que varios entrenen a la vez

# ==========================
# Procesamiento de imagen
# ==========================
def procesar_imagen_memoria(contents: bytes):
    """Convierto la imagen a array listo para el modelo"""
    try:
        with Image.open(BytesIO(contents)) as img:
            img = img.convert("RGB").resize((224, 224))  # Actualizado a 224x224 para coincidir con el modelo mejorado
            img_array = np.expand_dims(img_to_array(img) / 255.0, axis=0)
        return img_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen: {e}")


# ==========================
# Entrenamiento incremental
# ==========================
logging.basicConfig(level=logging.INFO, format="%(message)s")

def train_on_new_image(contents: bytes, clase: str):
    """Entrena rápido con la nueva imagen y reemplaza el modelo guardado"""
    try:
        img_array = procesar_imagen_memoria(contents)
        
        # El modelo binario de Colab usa orden alfabético: ["cortadas", "quemaduras"]
        # - clase 0 = "cortadas"
        # - clase 1 = "quemaduras"
        # Pero ModelManager.clases = ["quemaduras", "cortadas"] (orden inverso)
        # Necesitamos mapear correctamente:
        if clase == "cortadas":
            clase_idx = 0  # clase 0 en modelo binario
        elif clase == "quemaduras":
            clase_idx = 1  # clase 1 en modelo binario
        else:
            raise ValueError(f"Clase desconocida: {clase}. Debe ser 'cortadas' o 'quemaduras'")
        
        y = np.array([clase_idx])

        with modelo_lock:
            modelo_manager.model.train_on_batch(img_array, y)
            # guardo en temporal en la misma carpeta que el modelo original
            save_path = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas_tmp.keras")
            modelo_manager.model.save(save_path, overwrite=True)
            # reemplazo el modelo original en la raíz del proyecto
            os.replace(save_path, os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras"))
            modelo_manager.reload_model()

        logging.info(f"Entrenamiento incremental completado para la clase {clase}")

    except Exception as e:
        logging.error(f"Error en entrenamiento incremental: {e}")

def train_on_new_image_async(contents: bytes, clase: str):
    """Ejecuta el entrenamiento incremental en un hilo separado para no bloquear"""
    def train_thread():
        train_on_new_image(contents, clase)
    
    thread = threading.Thread(target=train_thread, daemon=True)
    thread.start()

# ==========================
# Endpoint predict + train
# ==========================
@app.post("/predict_and_train/")
async def predict_and_train(
    file: UploadFile = File(...), 
    numero_control: str = Form(...),
    nombre_completo: str = Form(...)
):
    # Validar que los campos obligatorios estén presentes
    if not numero_control or not numero_control.strip():
        raise HTTPException(status_code=400, detail="El número de control es obligatorio")
    if not nombre_completo or not nombre_completo.strip():
        raise HTTPException(status_code=400, detail="El nombre completo es obligatorio")

    # predicción
    contents = await file.read()
    img_array = procesar_imagen_memoria(contents)
    with modelo_lock:
        prediccion = modelo_manager.predict(img_array)

    # El modelo de Colab usa Dense(1, sigmoid) - devuelve UN solo valor entre 0 y 1
    # prediccion es un array: [[valor]] o [valor]
    # Extraemos el valor único (igual que en colab.py línea 606: pred = model.predict(...)[0][0])
    if isinstance(prediccion, np.ndarray):
        if prediccion.ndim > 1:
            raw_value = float(prediccion[0][0])  # [[valor]] → valor
        else:
            raw_value = float(prediccion[0])  # [valor] → valor
    else:
        raw_value = float(prediccion)
    
    # El modelo de Colab usa clasificación binaria:
    # - flow_from_directory ordena clases alfabéticamente: ["cortadas", "quemaduras"]
    # - class_names[0] = "cortadas", class_names[1] = "quemaduras"
    # - Según colab.py línea 608: pred < 0.5 → class_names[0] ("cortadas"), pred >= 0.5 → class_names[1] ("quemaduras")
    # - raw_value representa probabilidad de clase positiva (quemaduras)
    # - Si raw_value < 0.5 → es más probable "cortadas"
    # - Si raw_value >= 0.5 → es más probable "quemaduras"
    
    if raw_value < 0.5:
        clase_detectada = "cortadas"
        probabilidad = 1.0 - raw_value  # confianza de que es cortada
    else:
        clase_detectada = "quemaduras"
        probabilidad = raw_value  # confianza de que es quemadura

    # Determinar gravedad usando análisis visual con Gemini Vision (si está disponible)
    # Esto analiza características reales como profundidad, apertura, sangrado, necesidad de sutura, etc.
    gravedad = determinar_gravedad(clase_detectada, probabilidad, contents)

    instrucciones_ai = recomendacion_gemini(clase_detectada, gravedad)

    #  Guardar en bd
    resultado_bd = guardar_diagnostico(
        tipo="imagen",
        clase=clase_detectada,
        instrucciones=instrucciones_ai,
        numero_control=numero_control.strip(),
        nombre_completo=nombre_completo.strip(),
        probabilidad=probabilidad
    )
    
    # Log del resultado de guardado
    if "error" in resultado_bd:
        print(f"ERROR al guardar en BD: {resultado_bd['error']}")
    else:
        print(f"Guardado exitoso en BD: {resultado_bd.get('mensaje', 'OK')}")

    # entrenamiento incremental - USAR LA CLASE DETECTADA, NO LA ENVIADA POR EL FRONTEND
    # Solo entrenar si la confianza es alta (>= 0.7) para evitar corrupción del modelo
    # Ejecutar en hilo separado para no bloquear la respuesta
    if probabilidad >= 0.7:
        train_on_new_image_async(contents, clase_detectada)
        mensaje_entrenamiento = f"Entrenamiento incremental iniciado para la clase {clase_detectada}"
    else:
        mensaje_entrenamiento = f"Entrenamiento omitido (confianza baja: {probabilidad:.2%})"

    # regreso todo lo importante (incluyendo el ID del diagnóstico guardado)
    return {
        "clase": clase_detectada,
        "probabilidad": probabilidad,
        "gravedad": gravedad,  # AGREGADO: Incluir gravedad en la respuesta
        "instrucciones": instrucciones_ai,
        "diagnostico_id": resultado_bd.get("id"),  # ID del diagnóstico guardado
        "mensaje": mensaje_entrenamiento
    }

from pydantic import BaseModel

# ==========================
# Modelo para la solicitud de análisis de síntomas por texto
# ==========================
class SymptomRequest(BaseModel):
    symptoms: str
    numero_control: str
    nombre_completo: str


# ==========================
# Endpoint para recomendaciones basadas en texto
# ==========================
@app.post("/analyze-symptoms")
@app.post("/analyze-symptoms/")
async def analyze_symptoms(request: SymptomRequest):
    try:
        texto = request.symptoms.strip().lower()

        # Validar que los campos obligatorios estén presentes
        if not request.numero_control or not request.numero_control.strip():
            raise HTTPException(status_code=400, detail="El número de control es obligatorio")
        if not request.nombre_completo or not request.nombre_completo.strip():
            raise HTTPException(status_code=400, detail="El nombre completo es obligatorio")

        # Permitir más variaciones de palabras y hacer la extremidad opcional
        
        # Palabras relacionadas con cortadas (más flexibles)
        palabras_cortadas = [
            "cortada", "corte", "me corté", "se cortó", "cortó", "cortar",
            "herida", "herido", "herida abierta", "laceración", "rasguño profundo",
            "sangra", "sangrado", "sangrando"
        ]
        
        # Palabras relacionadas con quemaduras (más flexibles)
        palabras_quemaduras = [
            "quemadura", "quemado", "me quemé", "se quemó", "quemó", "quemar",
            "ardor", "ardiendo", "quemazón", "escaldadura", "ampolla", "ampollas"
        ]
        
        # Palabras relacionadas con extremidades (opcional, más flexibles)
        palabras_extremidades = [
            "brazo", "pierna", "mano", "pie", "dedo", "dedos", "muñeca", "tobillo",
            "codo", "rodilla", "hombro", "cadera", "extremidad", "miembro"
        ]
        
        # Verificar si menciona algún tipo de lesión (cortada o quemadura)
        tiene_cortada = any(palabra in texto for palabra in palabras_cortadas)
        tiene_quemadura = any(palabra in texto for palabra in palabras_quemaduras)
        tiene_tipo_lesion = tiene_cortada or tiene_quemadura
        
        # Verificar si menciona alguna extremidad (opcional pero recomendado)
        tiene_extremidad = any(palabra in texto for palabra in palabras_extremidades)
        
        # Validación más flexible:
        # - DEBE mencionar tipo de lesión (cortada o quemadura)
        # - La extremidad es OPCIONAL pero se recomienda
        if not tiene_tipo_lesion:
            raise HTTPException(
                status_code=400, 
                detail="Por favor, describe una cortada o quemadura. Ejemplos: 'tengo una cortada en el brazo', 'me quemé la pierna', 'herida que sangra', etc."
            )
        
        # Advertencia (no error) si no menciona extremidad
        if not tiene_extremidad:
            logging.info("El texto no menciona una extremidad específica, pero se procesará igualmente.")
    except Exception as e:
         logging.error(f"Error al entrar: {e}")
    try:
        # =========================
        # Generar recomendación con Gemini
        # =========================
        # Determinar gravedad antes de generar el prompt
        if "quemadura" in texto:
            clase_temp = "quemaduras"
        elif "cortada" in texto or "corte" in texto:
            clase_temp = "cortadas"
        else:
            clase_temp = "desconocida"
        
        gravedad_temp = determinar_gravedad(clase_temp, None)
        
        mensaje_urgencia = ""
        if gravedad_temp == "urgente":
            mensaje_urgencia = "\n\n URGENTE: Esta lesión requiere atención médica inmediata. Después de aplicar primeros auxilios básicos, busque asistencia médica de emergencia de inmediato."
        
        prompt = f"""Actúa como un experto en primeros auxilios. Un estudiante presenta la siguiente herida:
        {request.symptoms}

Nivel de gravedad estimado: {gravedad_temp.upper()}

IMPORTANTE: Responde SOLO con texto plano, SIN formato markdown, SIN asteriscos, SIN negritas, SIN símbolos especiales.
Usa solo saltos de línea y texto normal.

Proporciona con esta estructura:

1. DESCRIPCIÓN:
   [Breve descripción de la lesión]

2. TRES PASOS CRUCIALES:
   a) [Primer paso de acción inmediata]
   b) [Segundo paso de acción inmediata]
   c) [Tercer paso de acción inmediata]

3. ADVERTENCIAS - NO HACER:
   [Lista de cosas que NO se deben hacer]
{mensaje_urgencia}

IMPORTANTE: Si la gravedad es URGENTE, DEBES incluir al final una recomendación clara y enfática de buscar asistencia médica inmediata.

Responde directamente, sin introducciones ni explicaciones adicionales."""

        try:
            # Intentar con diferentes modelos de Gemini (texto)
            modelos = obtener_modelos_gemini_texto()
            respuesta_texto = None
            for modelo_nombre in modelos:
                try:
                    model = genai.GenerativeModel(modelo_nombre)
                    respuesta_obj = model.generate_content(prompt)
                    respuesta_texto = limpiar_markdown(respuesta_obj.text)
                    break  # Si funciona, salir del bucle
                except Exception as e:
                    logging.warning(f"Error con modelo {modelo_nombre}: {e}, intentando siguiente...")
                    continue
            
            if respuesta_texto is None:
                # Si no se pudo conectar con Gemini, usar recomendaciones fallback
                logging.warning("No se pudo conectar con Gemini. Usando recomendaciones fallback.")
                texto_lower = texto.lower()
                if "quemadura" in texto_lower:
                    respuesta_texto = recomendacion_fallback("quemaduras")
                elif "cortada" in texto_lower or "corte" in texto_lower:
                    respuesta_texto = recomendacion_fallback("cortadas")
                else:
                    respuesta_texto = recomendacion_fallback("desconocida")
        except Exception as gemini_error:
            error_msg = str(gemini_error)
            # Si la API key está comprometida, usar fallback
            if "403" in error_msg or "API key" in error_msg or "leaked" in error_msg.lower():
                logging.warning("API key inválida. Usando recomendaciones fallback.")
                texto_lower = texto.lower()
                if "quemadura" in texto_lower:
                    respuesta_texto = recomendacion_fallback("quemaduras")
                elif "cortada" in texto_lower or "corte" in texto_lower:
                    respuesta_texto = recomendacion_fallback("cortadas")
                else:
                    respuesta_texto = recomendacion_fallback("desconocida")
            else:
                logging.error(f"Error con Gemini API: {gemini_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error al comunicarse con la API de Gemini: {str(gemini_error)}"
                )

        # =========================
        # Determinar clase detectada
        # =========================
        if "quemadura" in texto:
            clase_detectada = "quemaduras"
        elif "cortada" in texto or "corte" in texto:
            clase_detectada = "cortadas"
        else:
            clase_detectada = "desconocida"
        
        # Determinar gravedad (sin probabilidad para análisis por texto)
        gravedad = determinar_gravedad(clase_detectada, None)

        # =========================
        # Guardar en base de datos
        # =========================
        diagnostico_id = None
        try:
            resultado_bd = guardar_diagnostico(
                tipo="texto",
                clase=clase_detectada,
                instrucciones=respuesta_texto,
                numero_control=request.numero_control.strip(),
                nombre_completo=request.nombre_completo.strip(),
                probabilidad=None  # No hay probabilidad en análisis de texto
            )
            
            # Log del resultado de guardado
            if "error" in resultado_bd:
                logging.error(f"ERROR al guardar en BD: {resultado_bd['error']}")
                # No lanzar error, solo registrar - el diagnóstico ya se generó
            else:
                logging.info(f"Guardado exitoso en BD: {resultado_bd.get('mensaje', 'OK')}")
                diagnostico_id = resultado_bd.get("id")
        except Exception as bd_error:
            logging.error(f"Error al guardar en base de datos: {bd_error}")
            # No lanzar error, solo registrar - el diagnóstico ya se generó

        return {
            "respuesta": respuesta_texto,
            "gravedad": gravedad,  # AGREGADO: Incluir gravedad en la respuesta
            "clase_detectada": clase_detectada,  # También incluir clase detectada
            "diagnostico_id": diagnostico_id  # ID del diagnóstico guardado (puede ser None si falló)
        }

    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        logging.error(f"Error inesperado en analyze_symptoms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al generar la recomendación: {str(e)}")
    
    # Endpoint para historial
@app.get("/historial/")
def historial():
    try:
        registros = obtener_historial()
        return registros
    except Exception as e:
        return {"error": str(e)}

# ==========================
# Modelo para pregunta sobre diagnóstico
# ==========================
class PreguntaRequest(BaseModel):
    diagnostico_id: int
    pregunta: str
    numero_control: str
    clase_detectada: str
    instrucciones_originales: str

# ==========================
# Endpoint para hacer preguntas sobre el diagnóstico
# ==========================
@app.post("/preguntar-diagnostico/")
async def preguntar_diagnostico(request: PreguntaRequest):
    try:
        # Verificar que la API key esté configurada
        if not GEMINI_API_KEY:
            logging.warning("GEMINI_API_KEY no está configurada. No se puede usar Gemini para responder preguntas.")
            respuesta_texto = f"""No se pudo generar una respuesta personalizada con la IA porque la API key de Gemini no está configurada.

Basándome en el diagnóstico de {request.clase_detectada}, te recomiendo:

1. Revisar las recomendaciones originales proporcionadas
2. Consultar con un profesional médico si tienes dudas
3. Buscar atención médica inmediata si los síntomas empeoran

Para obtener respuestas más detalladas, configura una API key válida de Google Gemini en el archivo .env"""
        else:
            # Crear contexto para Gemini con el diagnóstico original
            contexto = f"""Contexto del diagnóstico:
- Clase detectada: {request.clase_detectada}
- Recomendaciones originales: {request.instrucciones_originales}

Pregunta del usuario: {request.pregunta}

IMPORTANTE: Responde SOLO con texto plano, SIN formato markdown, SIN asteriscos, SIN negritas, SIN símbolos especiales.
Usa solo saltos de línea y texto normal.

Responde la pregunta del usuario basándote en el contexto del diagnóstico proporcionado.
Mantén un tono profesional y médico. Si la pregunta no está relacionada con el diagnóstico,
indícalo educadamente y ofrece ayuda relacionada con primeros auxilios."""
            
            # Generar respuesta con Gemini - usar modelos de texto (sin visión)
            modelos = obtener_modelos_gemini_texto()
            respuesta_texto = None
            
            for modelo_nombre in modelos:
                try:
                    model = genai.GenerativeModel(modelo_nombre)
                    respuesta_obj = model.generate_content(contexto)
                    respuesta_texto = limpiar_markdown(respuesta_obj.text)
                    logging.info(f"Respuesta generada exitosamente con modelo: {modelo_nombre}")
                    break  # Si funciona, salir del bucle
                except Exception as e:
                    error_msg = str(e)
                    # Si es un error de API key, no intentar más modelos
                    if "API key" in error_msg or "403" in error_msg or "401" in error_msg:
                        logging.error(f"Error de autenticación con Gemini: {error_msg}")
                        break
                    logging.warning(f"Error con modelo {modelo_nombre}: {error_msg}, intentando siguiente...")
                    continue
            
            if respuesta_texto is None:
                # Si no se pudo conectar con Gemini, usar respuesta genérica
                logging.warning("No se pudo conectar con ningún modelo de Gemini. Usando respuesta genérica.")
                respuesta_texto = f"""No se pudo generar una respuesta personalizada con la IA.

Basándome en el diagnóstico de {request.clase_detectada}, te recomiendo:

1. Revisar las recomendaciones originales proporcionadas arriba
2. Consultar con un profesional médico si tienes dudas
3. Buscar atención médica inmediata si los síntomas empeoran o si hay sangrado abundante

Para obtener respuestas más detalladas, verifica que tu API key de Google Gemini esté configurada correctamente en el archivo .env"""

        # Guardar la conversación en la BD
        resultado_guardado = guardar_conversacion(
            diagnostico_id=request.diagnostico_id,
            numero_control=request.numero_control,
            pregunta=request.pregunta,
            respuesta=respuesta_texto
        )

        if "error" in resultado_guardado:
            print(f"Error guardando conversación: {resultado_guardado['error']}")

        return {
            "respuesta": respuesta_texto,
            "conversacion_id": resultado_guardado.get("id")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {e}")

# ==========================
# Endpoint para obtener conversaciones de un diagnóstico
# ==========================
@app.get("/conversaciones/{diagnostico_id}")
def obtener_conversaciones_endpoint(diagnostico_id: int):
    try:
        conversaciones = obtener_conversaciones(diagnostico_id)
        return conversaciones
    except Exception as e:
        return {"error": str(e)}
