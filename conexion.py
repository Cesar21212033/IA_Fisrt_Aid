import mysql.connector
from mysql.connector import Error
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",             
        password="Baby20150531",  
        database="first_ai"
    )

# ==========================
# Guardar diagnóstico
# ==========================
def guardar_diagnostico(tipo, clase, instrucciones):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO historial_diagnosticos 
            (fecha, tipo, clase_detectada, instrucciones)
            VALUES (NOW(), %s, %s, %s)
        """

        values = (tipo, clase, instrucciones)

        cursor.execute(query, values)
        conn.commit()

        return {"mensaje": "Diagnóstico guardado correctamente"}

    except Error as e:
        print("Error guardando diagnóstico:", e)
        return {"error": str(e)}

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==========================
# Obtener historial
# ==========================
def obtener_historial():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT  fecha, tipo, clase_detectada, instrucciones 
            FROM historial_diagnosticos 
            ORDER BY fecha DESC
        """)
        return cursor.fetchall()

    except Error as e:
        return {"error": str(e)}

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
