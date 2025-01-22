import logging
from logging.handlers import RotatingFileHandler
import os
import graypy  # Asegúrate de tener instalado graypy con `pip install graypy`

def setup_logging(name):
    """
    Configura el logger con rotación de archivos, consola y envío a Graylog.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Ajusta el nivel según tus necesidades

    # Handler para rotación de archivos
    file_handler = RotatingFileHandler('app/logs/application.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)

    # Handler para Graylog (GELF UDP)
    graylog_host = os.getenv('GRAYLOG_HOST', 'localhost')  # Cambia si es necesario
    graylog_port = int(os.getenv('GRAYLOG_PORT', 12201))   # Cambia si es necesario
    gelf_handler = graypy.GELFUDPHandler(graylog_host, graylog_port)
    gelf_handler.setLevel(logging.DEBUG)
    logger.addHandler(gelf_handler)

    return logger