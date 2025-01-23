from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Ruta para almacenar los logs
LOG_FILE = os.getenv("LOG_FILE_PATH", "/logs/service.log")

@app.route('/api/logs', methods=['POST'])
def save_log():
    """
    Endpoint para guardar un log.
    Recibe un JSON con el mensaje del log.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Log message is required"}), 400

    log_message = data['message']
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_message + '\n')

    return jsonify({"status": "Log saved"}), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """
    Endpoint para obtener todos los logs.
    """
    if not os.path.exists(LOG_FILE):
        return jsonify({"logs": []}), 200

    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.readlines()

    return jsonify({"logs": logs}), 200

if __name__ == '__main__':
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    app.run(host='0.0.0.0', port=6000, debug=True)


