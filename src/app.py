from flask import Flask, jsonify
from src.config import Config
from src.logging_config import setup_logging
from src.routes.auth_routes import auth_bp
from src.routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG

    # Logger principal
    logger = setup_logging("main_app")
    logger.info("Inicializando aplicación Flask como API...")

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.route('/api', methods=['GET'])
    def index():
        #send_log_to_service("Acceso a la página principal.")
        return jsonify({
            "message": "Bienvenido a la API de Gestión de Peñas",
            "status": "OK"
        }), 200

    # Manejo de errores global
    @app.errorhandler(404)
    def not_found(error):
        logger.warning("Error 404: Ruta no encontrada.")
        #send_log_to_service("Error 404: Ruta no encontrada.")
        return jsonify({"error": "No encontrado "}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Error 500: {error}")
        #send_log_to_service(f"Error 500: {error}")
        return jsonify({"error": "Error interno del servidor"}), 500

    return app

if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(host='0.0.0.0', port=5000)
