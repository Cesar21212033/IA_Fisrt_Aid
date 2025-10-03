import os
import hashlib
from PIL import Image

def eliminar_repetidas(carpeta):
    hashes = {}
    borradas = 0
    
    for root, dirs, files in os.walk(carpeta):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                ruta = os.path.join(root, file)
                
                try:
                    with Image.open(ruta) as img:
                        # Convertir imagen a bytes y crear hash
                        h = hashlib.md5(img.tobytes()).hexdigest()
                        
                        if h in hashes:
                            print(f"Imagen repetida encontrada: {ruta} -> se elimina")
                            os.remove(ruta)
                            borradas += 1
                        else:
                            hashes[h] = ruta
                except Exception as e:
                    print(f"No se pudo procesar {ruta}: {e}")
    
    print(f"\n✅ Proceso completado. Se eliminaron {borradas} imágenes repetidas en {carpeta}")

# Ejecutar en tus carpetas
eliminar_repetidas("data/train")
eliminar_repetidas("data/val")
