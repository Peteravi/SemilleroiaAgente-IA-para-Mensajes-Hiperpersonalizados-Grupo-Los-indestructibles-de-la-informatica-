from .db import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Historial de recomendaciones
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        name TEXT,
        city TEXT,
        plan TEXT,
        price REAL,
        budget REAL,
        match_percent INTEGER,
        risk TEXT
    )
    """)

    # Métricas simples
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        event TEXT
    )
    """)

    conn.commit()
    conn.close()
