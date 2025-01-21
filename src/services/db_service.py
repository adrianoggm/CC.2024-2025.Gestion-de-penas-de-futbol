import psycopg2
import psycopg2.extras
from src.logging_config import setup_logging
from src.config import Config

db_logger = setup_logging("db_service")

def get_db_connection():
    """
    Retorna una conexión a PostgreSQL usando psycopg2.
    """
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        db_logger.info("Conexión a la base de datos establecida.")
        return conn
    except psycopg2.Error as e:
        db_logger.error(f"Error al conectar a la base de datos PostgreSQL: {e}")
        raise