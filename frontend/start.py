# start.py
import os
import subprocess
import threading
import sys
import signal
from fastapi import FastAPI

app = FastAPI()

# --- Detectar la raíz del proyecto ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # frontend/
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)               # IA-Convolucional/
MODEL_FILENAME = "modelo_quemaduras_cortadas.keras"
MODEL_PATH = os.path.join(PROJECT_ROOT, MODEL_FILENAME)

if not os.path.exists(MODEL_PATH):
    print(f"❌ No se encontró el modelo en: {MODEL_PATH}")
    sys.exit(1)
else:
    print(f"✅ Modelo encontrado en: {MODEL_PATH}")

# --- Función para ejecutar un comando y mostrar su salida en tiempo real ---
def run_command(cmd, name):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
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
    (f"uvicorn app:app --port 8000 --log-level info", "FastAPI"),
    ("npm run dev", "Vite")
]

# --- Crear un hilo por cada proceso ---
threads = []
for cmd, name in comandos:
    t = threading.Thread(target=run_command, args=(cmd, name))
    t.start()
    threads.append(t)

# --- Manejo de Ctrl+C para cerrar todo ---
def signal_handler(sig, frame):
    print("\n🛑 Deteniendo procesos...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# --- Esperar que terminen ---
for t in threads:
    t.join()
