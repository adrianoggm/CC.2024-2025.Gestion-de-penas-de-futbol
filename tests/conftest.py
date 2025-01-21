import os
import pytest
import psycopg2
import psycopg2.extras
import sys

# Insertamos la ruta del proyecto (un nivel arriba) al sys.path
# Ajusta si tu estructura de carpetas está en otro nivel
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import create_app  # Importa la función create_app, NO 'app'


def run_sql_script(conn, sql_path):
    """
    Lee y ejecuta el archivo .sql para crear/actualizar las tablas en PostgreSQL.
    Ajusta la ruta del fichero SQL a tu conveniencia.
    """
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    with conn.cursor() as cur:
        cur.execute(sql_script)
    conn.commit()


@pytest.fixture(scope="session")
def db_connection():
    """
    - Se conecta a la BD de test (usa TEST_DATABASE_URL o un valor por defecto).
    - (Opcional) Carga las tablas desde Gestion_Penas.sql, si así lo deseas.
    - Mantiene la conexión abierta durante toda la sesión de tests.
    """
    db_url = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@localhost:5432/gestion_penas")
    conn = psycopg2.connect(db_url)

    # Si necesitas crear o actualizar tu esquema, descomenta:
    # run_sql_script(conn, "Gestion_Penas.sql")

    yield conn

    conn.close()


@pytest.fixture(autouse=True)
def clean_db(db_connection):
    """
    Se ejecuta automáticamente antes de cada test:
      - Vacía todas las tablas para que cada test empiece con la BD limpia.
    """
    conn = db_connection
    with conn.cursor() as cur:
        # Obtener todas las tablas en la base de datos
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()

        # Desactivar restricciones de claves foráneas
        cur.execute("SET session_replication_role = 'replica';")

        # Vaciar todas las tablas
        for (table_name,) in tables:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")

        # Reactivar restricciones de claves foráneas
        cur.execute("SET session_replication_role = 'origin';")

    conn.commit()


@pytest.fixture
def client(db_connection, monkeypatch):
    """
    - Inyecta la variable de entorno DATABASE_URL para que tu app use la BD de test.
    - Crea la app con create_app().
    - Devuelve un test_client de Flask para hacer peticiones.
    """
    # Forzamos a usar la BD de test si no está definida la variable
    test_db_url = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@localhost:5432/gestion_penas")
    monkeypatch.setenv("DATABASE_URL", test_db_url)

    # Creamos la aplicación Flask con la factoría
    flask_app = create_app()
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as test_client:
        yield test_client
