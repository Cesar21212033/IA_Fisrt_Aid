from datetime import datetime
import psycopg2
import psycopg2.extras
from psycopg2 import Error


def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",          # tu usuario de PostgreSQL
        password="adnatfhso4",  # tu contraseña
        database="IA"       # nombre de tu base de datos
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
            RETURNING id
        """

        values = (tipo, clase, probabilidad, numero_control, nombre_completo, instrucciones)
        
        cursor.execute(query, values)
        new_id = cursor.fetchone()[0]
        conn.commit()

        return {"mensaje": "Diagnóstico guardado correctamente", "id": new_id}

    except Error as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}

    finally:
        if conn:
            cursor.close()
            conn.close()
# ==========================
# Obtener historial
# ==========================
def obtener_historial():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT id, fecha, tipo, clase_detectada, probabilidad, numero_control, nombre_completo, instrucciones 
            FROM historial_diagnosticos 
            ORDER BY fecha DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        return {"error": str(e)}

    finally:
        if conn:
            cursor.close()
            conn.close()


# ==========================
# Guardar pregunta y respuesta
# ==========================
def guardar_conversacion(diagnostico_id, numero_control, pregunta, respuesta):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO conversaciones_diagnosticos
            (diagnostico_id, numero_control, pregunta, respuesta, fecha)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id;
        """

        values = (diagnostico_id, numero_control, pregunta, respuesta)

        cursor.execute(query, values)
        new_id = cursor.fetchone()[0]
        conn.commit()

        return {"mensaje": "Conversación guardada correctamente", "id": new_id}

    except Exception as e:
        print("Error guardando conversación:", e)
        if conn:
            conn.rollback()
        return {"error": str(e)}

    finally:
        if conn:
            cursor.close()
            conn.close()


# ==========================
# Obtener conversaciones de un diagnóstico
# ==========================
def obtener_conversaciones(diagnostico_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT id, pregunta, respuesta, fecha
            FROM conversaciones_diagnosticos
            WHERE diagnostico_id = %s
            ORDER BY fecha ASC
        """, (diagnostico_id,))

        return cursor.fetchall()

    except Exception as e:
        return {"error": str(e)}

    finally:
        if conn:
            cursor.close()
            conn.close()
