from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2 import Error
from src.services.db_service import get_db_connection
from src.logging_config import setup_logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = setup_logging("auth_routes")

@auth_bp.route('/ping', methods=['GET'])
def ping():
    """Endpoint de prueba para verificar el funcionamiento del auth_bp."""
    logger.info("Ping en auth_routes.")
    return jsonify({"message": "pong"}), 200

@auth_bp.route('/registration_pena', methods=['POST'])
def registration_pena():
    """
    Registra un administrador (admin) y crea una peña asociada.
    Espera un JSON con:
      {
        "username": "...",
        "password": "...",
        "confirm_password": "...",
        "nombre_peña": "..."
      }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    nombre_peña = data.get('nombre_peña')

    if not all([username, password, confirm_password, nombre_peña]):
        return jsonify({"error": "Faltan campos en la solicitud"}), 400

    if password != confirm_password:
        logger.warning(f"Contraseñas no coinciden para usuario: {username}.")
        return jsonify({"error": "Las contraseñas no coinciden"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            logger.warning(f"Usuario '{username}' ya existe.")
            return jsonify({"error": "El nombre de usuario ya existe"}), 409

        # Insertar en la tabla PENA y obtener su ID
        cursor.execute("INSERT INTO PENA (nombre) VALUES (%s) RETURNING idpena", (nombre_peña,))
        id_peña = cursor.fetchone()[0]

        # Insertar en la tabla de admins
        cursor.execute(
            "INSERT INTO admins (username, password, Idpena) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), id_peña)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Admin '{username}' registrado y peña '{nombre_peña}' creada con ID {id_peña}.")
        return jsonify({"message": "Admin registrado exitosamente", "id_peña": id_peña}), 201

    except Error as e:
        logger.error(f"Error en la base de datos: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error en la base de datos"}), 500

@auth_bp.route('/registration_jugador', methods=['POST'])
def registration_jugador():
    """
    Registra un jugador y lo asocia a una peña existente.
    Espera un JSON con:
      {
        "username": "...",
        "password": "...",
        "confirm_password": "...",
        "id_peña": 1,
        "mote": "...",
        "posicion": "...",
        "nacionalidad": "..."
      }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    id_peña = data.get('id_peña')
    mote = data.get('mote')
    posicion = data.get('posicion')
    nacionalidad = data.get('nacionalidad')

    if not all([username, password, confirm_password, id_peña, mote, posicion, nacionalidad]):
        return jsonify({"error": "Faltan campos en la solicitud"}), 400

    if password != confirm_password:
        logger.warning(f"Contraseñas no coinciden para el jugador: {username}.")
        return jsonify({"error": "Las contraseñas no coinciden"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar en la tabla JUGADOR y recuperar ID
        cursor.execute(
            "INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (%s, %s, %s) RETURNING Idjugador",
            (username, '', nacionalidad)
        )
        id_jugador = cursor.fetchone()[0]
        logger.info(f"Jugador '{username}' creado con ID {id_jugador}.")

        # Insertar en JUGADORPENA
        cursor.execute(
            "INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (%s, %s, %s, %s)",
            (id_jugador, id_peña, mote, posicion)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Jugador '{username}' asociado a la peña {id_peña}.")
        return jsonify({"message": "Jugador registrado exitosamente", "id_jugador": id_jugador}), 201

    except Error as e:
        logger.error(f"Error durante registro del jugador '{username}': {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error en el registro del jugador"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión como admin o jugador.
    Espera un JSON con:
      {
        "username": "...",
        "password": "..."
      }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Faltan username o password"}), 400

    logger.info(f"Intento de inicio de sesión: {username}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # 1) Buscar en 'users'
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            is_admin = False
            user = dict(user)
        else:
            # 2) Buscar en 'admins'
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                is_admin = True
                user = dict(user)
            else:
                logger.warning(f"Usuario '{username}' no existe en 'users' ni 'admins'.")
                return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

        cursor.close()
        conn.close()

        # Verificar contraseña
        if check_password_hash(user['password'], password):
            # Guardar en session (si deseas mantener la sesión en el servidor)
            session['username'] = user['username']
            if is_admin:
                session['Idpena'] = user.get('idpena')
                logger.info(f"Admin '{username}' inició sesión.")
                return jsonify({"message": "Admin logueado", "role": "admin", "Idpena": session['Idpena']}), 200
            else:
                session['Idjugador'] = user.get('idjugador')
                logger.info(f"Jugador '{username}' inició sesión.")
                return jsonify({"message": "Jugador logueado", "role": "jugador", "Idjugador": session['Idjugador']}), 200
        else:
            logger.warning(f"Contraseña incorrecta para '{username}'.")
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    except psycopg2.Error as e:
        logger.error(f"Error al buscar usuario '{username}': {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error en la base de datos"}), 500
    
@auth_bp.route('/debug/ver_bd', methods=['GET'])
def ver_bd_completa():
    """
    Endpoint para depurar: retorna en JSON todas las tablas (public)
    y el contenido de cada una. Este endpoint no está protegido.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener las tablas públicas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        all_tables = [row[0] for row in cursor.fetchall()]

        data_bd = {}
        # Por cada tabla, hacer SELECT * y almacenar resultado
        for table in all_tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            
            # Convertir cada fila en diccionario {columna: valor}
            table_data = []
            for row in rows:
                row_dict = {col: val for col, val in zip(colnames, row)}
                table_data.append(row_dict)
            
            data_bd[table] = table_data

        cursor.close()
        conn.close()

        logger.info(f"Consulta sin protección: tablas ({len(all_tables)}) consultadas.")
        return jsonify({
            "tables": all_tables,
            "data": data_bd
        }), 200

    except psycopg2.Error as e:
        logger.error(f"Error al consultar la BD completa: {e}", exc_info=True)
        return jsonify({"error": "Error al obtener las tablas de la BD"}), 500
