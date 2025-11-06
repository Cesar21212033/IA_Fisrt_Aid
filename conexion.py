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
def guardar_diagnostico(tipo, clase, instrucciones, numero_control=None, nombre_completo=None, probabilidad=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO historial_diagnosticos 
            (fecha, tipo, clase_detectada, probabilidad, numero_control, nombre_completo, instrucciones)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s)
        """

        values = (tipo, clase, probabilidad, numero_control, nombre_completo, instrucciones)
        
        print(f"Intentando guardar diagnóstico: tipo={tipo}, clase={clase}, probabilidad={probabilidad}, numero_control={numero_control}, nombre_completo={nombre_completo}")

        cursor.execute(query, values)
        conn.commit()
        
        print(f"Diagnóstico guardado exitosamente. ID: {cursor.lastrowid}")

        return {"mensaje": "Diagnóstico guardado correctamente", "id": cursor.lastrowid}

    except Error as e:
        print(f"Error guardando diagnóstico: {e}")
        print(f"Error completo: {type(e).__name__}: {str(e)}")
        if conn and conn.is_connected():
            conn.rollback()
        return {"error": str(e)}

    finally:
        if conn and conn.is_connected():
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
            SELECT  id, fecha, tipo, clase_detectada, probabilidad, numero_control, nombre_completo, instrucciones 
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
