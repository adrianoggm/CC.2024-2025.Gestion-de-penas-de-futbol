import logging
import os
from logging.handlers import RotatingFileHandler
def setup_logging(log_name):
    
    # Crear el directorio de logs si no existe
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Ruta del archivo de log
    log_file = os.path.join(log_dir, f"{log_name}.log")
    print(f"Configurando logger para: {log_file}")
    if not os.access(log_dir, os.W_OK):
        print(f"El directorio {log_dir} no tiene permisos de escritura.")
    if os.path.exists(log_file):
        print(f"El archivo {log_file} ya existe.")
    else:
        print(f"El archivo {log_file} no existe. Se intentará crear.")
    # Crear logger con el nombre especificado
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)  # Capturar todos los niveles

    # Revisar si el logger ya tiene handlers para evitar duplicados
    if logger.hasHandlers():
        logger.handlers.clear()

    # Crear un handler de archivo con rotación
    try:
        rotating_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,  # Guardar hasta 3 backups
            encoding='utf-8'
        )
        rotating_handler.setLevel(logging.DEBUG)  # Registrar todo
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        rotating_handler.setFormatter(formatter)

        # Agregar el handler al logger
        logger.addHandler(rotating_handler)
    except Exception as e:
        print(f"Error al configurar RotatingFileHandler: {e}")

    # Crear un handler para la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Agregar handler de consola al logger
    logger.addHandler(console_handler)

    return logger