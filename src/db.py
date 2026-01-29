import sqlite3
from pathlib import Path

# Ruta correcta a la base de datos
DB_PATH = Path("src/data/app.db")


def get_connection():
    """
    Retorna una conexión SQLite con row_factory habilitado
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================
# MÉTRICAS PARA EL DASHBOARD
# ============================

def get_total_conversations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM conversations")
    result = cursor.fetchone()

    conn.close()
    return result["total"] if result else 0


def get_conversations_by_plan():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT plan_recomendado, COUNT(*) AS total
        FROM conversations
        GROUP BY plan_recomendado
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "plan": row["plan_recomendado"],
            "total": row["total"]
        }
        for row in rows
    ]


def get_average_consumption_and_budget():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            AVG(consumo_datos) AS consumo_promedio,
            AVG(presupuesto) AS presupuesto_promedio
        FROM conversations
    """)

    row = cursor.fetchone()
    conn.close()

    return {
        "consumo_promedio": round(row["consumo_promedio"], 2) if row["consumo_promedio"] else 0,
        "presupuesto_promedio": round(row["presupuesto_promedio"], 2) if row["presupuesto_promedio"] else 0
    }


def get_dashboard_metrics():
    """
    Retorna todas las métricas consolidadas para el dashboard
    """
    return {
        "total_conversaciones": get_total_conversations(),
        "planes_recomendados": get_conversations_by_plan(),
        "promedios": get_average_consumption_and_budget()
    }
