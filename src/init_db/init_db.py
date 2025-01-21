# init_db.py
import os
import psycopg2

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/gestion_penas")

def main():
    # Lee tu archivo SQL desde el repositorio
    with open("Gestion_Penas.sql", "r", encoding="utf-8") as f:
        script_sql = f.read()

    # Conecta a la BD y ejecuta el script
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(script_sql)
    conn.commit()
    cur.close()
    conn.close()

    print("¡Base de datos inicializada correctamente!")

if __name__ == "__main__":
    main(