# start.py
import os
import subprocess
import threading
import sys
sys.stdout.reconfigure(encoding='utf-8')
import signal
import time
import requests

# --- Detectar la raíz del proyecto ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)               # IA-Convolucional/
MODEL_FILENAME = "modelo_quemaduras_cortadas.keras"
MODEL_PATH = os.path.join(PROJECT_ROOT, "modelo_quemaduras_cortadas.keras")


# --- Verificar que el modelo exista en PROJECT_ROOT ---
if os.path.exists(MODEL_PATH):
    print(f"✅ Modelo encontrado en {MODEL_PATH}")
else:
    print(f"⚠️  No se encontró el modelo en {MODEL_PATH}")
    print(f"   Por favor, entrena el modelo primero usando model.py o colab_train.ipynb")

# --- Función para ejecutar un comando y mostrar su salida en tiempo real ---
def run_command(cmd, name, cwd=None):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd  # <-- aquí se define la carpeta
    )

    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line}", end="")
    except Exception as e:
        print(f"[{name}] Error leyendo salida: {e}")
    finally:
        process.stdout.close()
        process.wait()

# --- Comandos a ejecutar ---
comandos = [
    # FastAPI sin --reload para evitar SpawnProcess en hilos de Windows
    # Usar python -m uvicorn para asegurar que funcione aunque uvicorn no esté en PATH
    (f"python -m uvicorn frontend.app:app --port 8001 --log-level info", "FastAPI"),
    ("npm run dev", "Vite")
]

# --- Crear un hilo por cada proceso ---
threads = []
for cmd, name in comandos:
    if name == "Vite":
        t = threading.Thread(target=run_command, args=(cmd, name, CURRENT_DIR))
    else:
        # FastAPI debe ejecutarse desde PROJECT_ROOT para encontrar el módulo 'frontend'
        t = threading.Thread(target=run_command, args=(cmd, name, PROJECT_ROOT))
    t.start()
    threads.append(t)

    # --- Esperar a que FastAPI esté listo antes de continuar ---
backend_url = "http://127.0.0.1:8001"
print(" Esperando a que FastAPI se inicie...")
for i in range(20):  # intenta hasta 20 veces (≈10 segundos)
    try:
        res = requests.get(backend_url)
        if res.status_code in [200, 404]:  # 404 es ok si la raíz no existe
            print(" FastAPI está listo")
            break
    except requests.exceptions.ConnectionError:
        print(".", end="", flush=True)
        time.sleep(0.5)
else:
    print("\n FastAPI no respondió a tiempo, verifica el servidor")


# --- Manejo de Ctrl+C para cerrar todo ---
def signal_handler(sig, frame):
    print("\n Deteniendo procesos...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# --- Esperar que terminen ---
for t in threads:
    t.join()
