import logging
import requests
import os

def setup_logging(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Crear handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Añadir handler al logger
    logger.addHandler(console_handler)

    return logger

def send_log_to_service(message):
    """
    Envía un log al contenedor de logs mediante la API.
    """
    LOGS_API_URL = os.getenv('LOGS_API_URL', 'http://logs-container:6000/api/logs')
    try:
        response = requests.post(LOGS_API_URL, json={"message": message})
        if response.status_code != 200:
            print(f"Failed to send log: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception while sending log: {e}")
