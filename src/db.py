import sqlite3
import os

db_path = os.path.join('', 'Gestion_Penas.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
    return conn