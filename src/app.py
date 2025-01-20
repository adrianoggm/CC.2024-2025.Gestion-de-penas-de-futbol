from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, make_response, redirect, url_for, session
import psycopg2
import psycopg2.extras  # Para obtener cursores tipo diccionario
import os
from logging_config import setup_logging
from flask import Flask, flash, jsonify, render_template, request, make_response, render_template_string, redirect, url_for, session
import psycopg2          # CAMBIO: reemplaza import sqlite3
import psycopg2.extras   # Para cursores tipo diccionario
from werkzeug.security import check_password_hash, generate_password_hash
import os
from logging_config import setup_logging

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'
Admin = False

# Configuración del logger
logger = setup_logging("app")
db_logger = setup_logging("db")

# Leemos la URL de conexión para Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/gestion_penas")

def get_db_connection():
    """
    Retorna una conexión a PostgreSQL usando psycopg2.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        db_logger.info("Conexión a la base de datos establecida.")
        return conn
    except psycopg2.Error as e:
        db_logger.error(f"Error al conectar a la base de datos PostgreSQL: {e}")
        raise

@app.route('/', methods=['GET'])
def ping():
    logger.info("Ruta raíz accesada.")
    return render_template('index.html')

# --- Ruta de prueba ---
@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Ejemplo: listar tablas en el schema 'public'
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"tables": [dict(row) for row in tables]})
    except Exception as e:
        logger.error(f"Error realizando consulta de prueba: {e}")
        return jsonify({"error": str(e)}), 500

# --- REGISTRO DE PEÑA ---
@app.route('/registration_pena', methods=['GET', 'POST'])
def registration_pena():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        nombre_peña = request.form['nombre_peña']

        if password != confirm_password:
            flash('Las contraseñas no coinciden.')
            logger.warning(f"Contraseñas no coinciden para usuario: {username}.")
            return redirect(url_for('registration_pena'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar si el nombre de usuario ya existe
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                logger.warning(f"Usuario '{username}' ya existe.")
                flash('El nombre de usuario ya existe.')
                return redirect(url_for('registration_pena'))

            # Insertar en la tabla de PENA, recuperando su ID con RETURNING
            cursor.execute("INSERT INTO PENA (nombre) VALUES (%s) RETURNING idpena", (nombre_peña,))
            id_peña = cursor.fetchone()[0]  # CAMBIO: en Postgres se obtiene con RETURNING

            db_logger.info(f"Peña '{nombre_peña}' creada con ID {id_peña}.")

            # Insertar en la tabla de admins
            cursor.execute(
                "INSERT INTO admins (username, password, Idpena) VALUES (%s, %s, %s)",
                (username, generate_password_hash(password), id_peña)
            )
            db_logger.info(f"Admin '{username}' registrado para la peña ID {id_peña}.")

            conn.commit()
            cursor.close()
            conn.close()

            flash('Admin registrado exitosamente. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))

        except psycopg2.Error as e:  # CAMBIO: psycopg2.Error
            logger.error(f"Error en la base de datos: {e}", exc_info=True)
            flash("Ocurrió un error en la base de datos.")
            return redirect(url_for('registration_pena'))

    logger.info("Formulario de registro de peña (GET).")
    return render_template('registration_pena.html')


# --- REGISTRO DE JUGADOR ---
@app.route('/registration_jugador', methods=['GET', 'POST'])
def registration_jugador():
    logger.info("Acceso al formulario de registro de jugador.")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        id_peña = request.form['id_peña']  # ID de la peña
        mote = request.form['mote']
        posicion = request.form['posicion']
        nacionalidad = request.form['nacionalidad']

        if password != confirm_password:
            flash('Las contraseñas no coinciden.')
            logger.warning(f"Contraseñas no coinciden para el jugador: {username}.")
            return redirect(url_for('registration_jugador'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar en la tabla JUGADOR, recuperar ID
            cursor.execute(
                "INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (%s, %s, %s) RETURNING Idjugador",
                (username, '', nacionalidad)
            )
            id_jugador = cursor.fetchone()[0]
            db_logger.info(f"Jugador '{username}' creado con ID {id_jugador}.")

            # Insertar en JUGADORPENA
            cursor.execute(
                "INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (%s, %s, %s, %s)",
                (id_jugador, id_peña, mote, posicion)
            )
            db_logger.info(f"Jugador '{username}' asociado a la peña {id_peña}.")

            conn.commit()
            cursor.close()
            conn.close()

            flash('Jugador registrado exitosamente. Ahora puedes iniciar sesión.')
            logger.info(f"Jugador '{username}' registrado.")
            return redirect(url_for('login'))

        except psycopg2.Error as e:  # CAMBIO: psycopg2.Error
            logger.error(f"Error durante registro del jugador '{username}': {e}", exc_info=True)
            flash("Ocurrió un error en el registro del jugador.")
            return redirect(url_for('registration_jugador'))

    return render_template('registration_jugador.html')


# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Acceso al formulario de inicio de sesión.")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Intento de inicio de sesión: {username}.")

        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Buscar en 'users'
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                Admin = False
                user = dict(user)  # Convertir en dict si queremos manipular campos
                logger.info(f"Usuario '{username}' encontrado en 'users'.")
            else:
                # Si no está en users, buscar en admins
                cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user:
                    Admin = True
                    user = dict(user)
                    logger.info(f"Usuario '{username}' encontrado en 'admins'.")
                else:
                    logger.warning(f"Usuario '{username}' no existe.")
                    flash('Usuario o contraseña incorrectos.')
                    return redirect(url_for('login'))

            cursor.close()
            conn.close()

            # Verificar contraseña
            if check_password_hash(user['password'], password):
                if Admin:
                    session['username'] = user['username']
                    session['Idpena'] = user['idpena']  # Ojo con mayúsculas
                    logger.info(f"Admin '{username}' inició sesión.")
                    return redirect(url_for('admin_dashboard'))
                else:
                    session['username'] = user['username']
                    session['name'] = user['name']
                    session['Idjugador'] = user['idjugador']
                    logger.info(f"Jugador '{username}' inició sesión (falta funcionalidad).")
                    flash('Usuario no es admin; funcionalidad en desarrollo.')
                    return redirect(url_for('login'))
            else:
                logger.warning(f"Contraseña incorrecta para '{username}'.")
                flash('Usuario o contraseña incorrectos.')
                return redirect(url_for('login'))

        except psycopg2.Error as e:
            logger.error(f"Error al buscar usuario '{username}': {e}", exc_info=True)
            flash('Ocurrió un error en la base de datos.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session:
        logger.warning("Intento de acceder al dashboard sin iniciar sesión.")
        flash('Por favor, inicia sesión primero.')
        return redirect(url_for('login'))

    username = session.get('username')
    logger.info(f"Acceso al dashboard por: {username}.")
    return render_template('admin_dashboard.html', username=username)


# --- GESTIONAR JUGADORES ---
@app.route('/admin/gestionar_jugadores')
def gestionar_jugadores():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado a gestionar jugadores.")
        flash('Inicia sesión como administrador.')
        return redirect(url_for('login'))

    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM JUGADORPENA WHERE idpena = %s", (id_pena,))
        jugadores = cursor.fetchall()
        cursor.close()
        conn.close()

        logger.info(f"Obtenidos jugadores de la peña {id_pena}.")
    except psycopg2.Error as e:
        logger.error(f"Error al obtener jugadores de la peña {id_pena}: {e}", exc_info=True)
        jugadores = []

    return render_template('gestionar_jugadores.html', jugadores=jugadores)


# --- GESTIONAR PARTIDOS ---
@app.route('/admin/gestionar_partidos')
def gestionar_partidos():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM PARTIDO")
        partidos = cursor.fetchall()
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"Error al obtener partidos: {e}", exc_info=True)
        partidos = []

    return render_template('gestionar_partidos.html', partidos=partidos)

# --- AÑADIR JUGADOR ---
@app.route('/admin/gestionar_jugadores/añadir_jugador', methods=['GET', 'POST'])
def añadir_jugador():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado para añadir jugador.")
        flash('Inicia sesión como administrador.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']

        id_pena = session['Idpena']

        logger.info(f"Añadir jugador: {nombre}, Mote: {mote}, Posición: {posicion}, Peña ID: {id_pena}")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar en JUGADOR y recuperar Idjugador
            cursor.execute(
                "INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (%s, %s, %s) RETURNING Idjugador",
                (nombre, apellidos, nacionalidad)
            )
            id_jugador = cursor.fetchone()[0]

            db_logger.info(f"Jugador '{nombre}' creado con ID {id_jugador}.")

            # Asociar en JUGADORPENA
            cursor.execute(
                "INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (%s, %s, %s, %s)",
                (id_jugador, id_pena, mote, posicion)
            )
            db_logger.info(f"Jugador {id_jugador} asociado a la peña {id_pena}.")
            conn.commit()

            cursor.close()
            conn.close()

            flash('Jugador añadido exitosamente.')
            logger.info(f"Jugador '{nombre}' añadido exitosamente.")
            return redirect(url_for('gestionar_jugadores'))

        except psycopg2.Error as e:
            logger.error(f"Error al añadir jugador '{nombre}': {e}", exc_info=True)
            flash('Error al añadir el jugador.')
            return redirect(url_for('añadir_jugador'))

    logger.info("Formulario para añadir jugador (GET).")
    return render_template('añadir_jugador.html')

# --- EDITAR JUGADOR ---
@app.route('/admin/gestionar_jugadores/editar/<int:jugador_id>', methods=['GET', 'POST'])
def editar_jugador(jugador_id):
    if 'Idpena' not in session:
        logger.warning(f"Acceso no autorizado para editar al jugador {jugador_id}.")
        flash('Inicia sesión como administrador.')
        return redirect(url_for('login'))

    id_pena = session['Idpena']

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']

        logger.info(f"Edición jugador {jugador_id}: Nombre={nombre}, Apellidos={apellidos}, Nacionalidad={nacionalidad}, Mote={mote}, Posición={posicion}")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # UPDATE en JUGADOR
            cursor.execute("""
                UPDATE JUGADOR
                SET Nombre = %s, Apellidos = %s, Nacionalidad = %s
                WHERE Idjugador = %s
            """, (nombre, apellidos, nacionalidad, jugador_id))

            # UPDATE en JUGADORPENA
            cursor.execute("""
                UPDATE JUGADORPENA
                SET Mote = %s, Posicion = %s
                WHERE Idjugador = %s AND Idpena = %s
            """, (mote, posicion, jugador_id, id_pena))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Jugador actualizado correctamente.')
            logger.info(f"Jugador ID {jugador_id} actualizado.")
            return redirect(url_for('gestionar_jugadores'))

        except psycopg2.Error as e:
            logger.error(f"Error al actualizar jugador {jugador_id}: {e}", exc_info=True)
            flash('Error al actualizar el jugador.')
            return redirect(url_for('gestionar_jugadores'))

    # GET: cargar datos del jugador
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT JUGADOR.*, JUGADORPENA.Mote, JUGADORPENA.Posicion
            FROM JUGADOR
            JOIN JUGADORPENA ON JUGADOR.Idjugador = JUGADORPENA.Idjugador
            WHERE JUGADOR.Idjugador = %s AND JUGADORPENA.Idpena = %s
        """, (jugador_id, id_pena))
        jugador = cursor.fetchone()
        cursor.close()
        conn.close()

        if not jugador:
            logger.warning(f"Jugador no encontrado. ID: {jugador_id}, Peña: {id_pena}.")
            flash('Jugador no encontrado.')
            return redirect(url_for('gestionar_jugadores'))

        logger.info(f"Datos cargados para edición del jugador {jugador_id}.")
    except psycopg2.Error as e:
        logger.error(f"Error al cargar datos del jugador {jugador_id}: {e}", exc_info=True)
        flash('Error al cargar los datos.')
        return redirect(url_for('gestionar_jugadores'))

    return render_template('editar_jugador.html', jugador=jugador)

@app.route('/admin/gestionar_jugadores/eliminar/<int:jugador_id>', methods=['POST'])
def eliminar_jugador(jugador_id):
    if 'Idpena' not in session:
        logger.warning(f"Acceso no autorizado al intento de eliminación del jugador ID {jugador_id}.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Eliminar de JUGADORPENA
        cursor.execute(
            "DELETE FROM JUGADORPENA WHERE Idjugador = %s AND Idpena = %s",
            (jugador_id, session['Idpena'])
        )
        db_logger.info(f"Jugador ID {jugador_id} eliminado de JUGADORPENA (Peña ID: {session['Idpena']}).")

        # Eliminar de JUGADOR
        cursor.execute(
            "DELETE FROM JUGADOR WHERE Idjugador = %s",
            (jugador_id,)
        )
        db_logger.info(f"Jugador ID {jugador_id} eliminado de JUGADOR.")

        conn.commit()
        cursor.close()
        conn.close()

        flash('Jugador eliminado correctamente.')
        logger.info(f"Jugador ID {jugador_id} eliminado exitosamente.")

    except psycopg2.Error as e:  # CAMBIO: psycopg2.Error
        logger.error(f"Error al eliminar el jugador ID {jugador_id}: {e}", exc_info=True)
        flash('Error al eliminar el jugador. Por favor, inténtalo de nuevo.')

    return redirect(url_for('gestionar_jugadores'))


@app.route('/admin/gestionar_temporadas', methods=['GET'])
def gestionar_temporadas():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado a la gestión de temporadas.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    temporadas = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("""
            SELECT * FROM TEMPORADA
            WHERE Idpena = %s
            ORDER BY Idt DESC
        """, (session['Idpena'],))
        temporadas = cursor.fetchall()

        logger.info(f"Se recuperaron {len(temporadas)} temporadas para Peña ID {session['Idpena']}.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        logger.error(f"Error al recuperar temporadas para Peña ID {session['Idpena']}: {e}", exc_info=True)
        flash('Error al recuperar las temporadas. Por favor, inténtalo de nuevo.')
        return redirect(url_for('admin_dashboard'))

    return render_template('gestionar_temporadas.html', temporadas=temporadas)


@app.route('/admin/gestionar_temporadas/añadir', methods=['GET', 'POST'])
def añadir_temporada():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        fechaini = request.form['fechaini']
        fechafin = request.form['fechafin']

        # Validaciones de fechas simples
        if fechaini >= fechafin:
            flash('La fecha de inicio debe ser anterior a la fecha de fin.')
            return redirect(url_for('añadir_temporada'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar nueva temporada en TEMPORADA
            cursor.execute("""
                INSERT INTO TEMPORADA (Idpena, Fechaini, Fechafin)
                VALUES (%s, %s, %s)
            """, (session['Idpena'], fechaini, fechafin))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Temporada añadida exitosamente.')
            return redirect(url_for('gestionar_temporadas'))

        except psycopg2.Error as e:
            logger.error(f"Error al añadir temporada: {e}", exc_info=True)
            flash('Error al añadir la temporada. Por favor, inténtalo de nuevo.')
            return redirect(url_for('añadir_temporada'))

    return render_template('añadir_temporada.html')


@app.route('/admin/gestionar_temporadas/eliminar/<int:id_temporada>', methods=['POST'])
def eliminar_temporada(id_temporada):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Eliminar la temporada
        cursor.execute("""
            DELETE FROM TEMPORADA
            WHERE Idt = %s AND Idpena = %s
        """, (id_temporada, session['Idpena']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Temporada eliminada correctamente.')
        return redirect(url_for('gestionar_temporadas'))

    except psycopg2.Error as e:
        logger.error(f"Error al eliminar temporada {id_temporada}: {e}", exc_info=True)
        flash('Error al eliminar la temporada.')
        return redirect(url_for('gestionar_temporadas'))


@app.route('/admin/visualizar_temporada/<int:id_temporada>', methods=['GET', 'POST'])
def visualizar_temporada(id_temporada):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Obtener info de la temporada
    cursor.execute("""
        SELECT Idt, Fechaini, Fechafin
        FROM TEMPORADA
        WHERE Idt = %s AND Idpena = %s
    """, (id_temporada, session['Idpena']))
    temporada = cursor.fetchone()

    if not temporada:
        cursor.close()
        conn.close()
        flash('Temporada no encontrada.')
        return redirect(url_for('gestionar_temporadas'))

    if request.method == 'POST':
        jugador_id = request.form.get('jugador_id')
        if jugador_id:
            # Ver si el jugador ya está en la temporada
            cursor.execute("""
                SELECT 1 FROM JUGADORTEMPORADA
                WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
            """, (jugador_id, session['Idpena'], id_temporada))
            existe = cursor.fetchone()

            if existe:
                flash('El jugador ya está asociado a esta temporada.')
            else:
                # Insertar jugador en la temporada
                cursor.execute("""
                    INSERT INTO JUGADORTEMPORADA (Idjugador, Idpena, Idt)
                    VALUES (%s, %s, %s)
                """, (jugador_id, session['Idpena'], id_temporada))
                conn.commit()
                flash('Jugador añadido a la temporada con éxito.')

    # Clasificación de jugadores
    cursor.execute("""
        SELECT
            J.Idjugador,
            JP.Mote,
            JT.VICT,
            JT.EMP,
            JT.DERR,
            (JT.VICT * 3 + JT.EMP * 2 + JT.DERR * 1) AS Puntos,
            ROUND(CAST(JT.VICT AS FLOAT) / NULLIF(JT.VICT + JT.EMP + JT.DERR, 0) * 100, 2) AS Porcentaje_victorias
        FROM JUGADORTEMPORADA JT
        JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
        JOIN JUGADOR J ON JP.Idjugador = J.Idjugador
        WHERE JT.Idt = %s AND JT.Idpena = %s
        ORDER BY Puntos DESC, Porcentaje_victorias DESC
    """, (id_temporada, session['Idpena']))
    jugadores = [dict(row) for row in cursor.fetchall()]

    # Lista de partidos con resultados (ejemplo)
    cursor.execute("""
        SELECT
            P.Idp,
            COALESCE(SUM(EJ1.Goles), 0) AS Goles_Equipo1,
            COALESCE(SUM(EJ2.Goles), 0) AS Goles_Equipo2
        FROM PARTIDO P
        LEFT JOIN EQUIPO E1 ON P.Idp = E1.Idp AND E1.Ide = 1
        LEFT JOIN EQUIPO E2 ON P.Idp = E2.Idp AND E2.Ide = 2
        LEFT JOIN EJUGADOR EJ1 ON EJ1.Idp = E1.Idp AND EJ1.Ide = E1.Ide
        LEFT JOIN EJUGADOR EJ2 ON EJ2.Idp = E2.Idp AND EJ2.Ide = E2.Ide
        WHERE P.Idt = %s AND P.Idpena = %s
        GROUP BY P.Idp
        ORDER BY P.Idp ASC
    """, (id_temporada, session['Idpena']))
    partidos = cursor.fetchall()

    # Estadísticas avanzadas de jugadores
    cursor.execute("""
        SELECT
            JP.Idjugador,
            JP.Mote,
            COALESCE(SUM(EJ.Goles), 0) AS Total_Goles,
            COALESCE(SUM(EJ.Asistencias), 0) AS Total_Asistencias,
            COALESCE(ROUND(AVG(EJ.Val), 2), 0) AS Valoracion_Promedio
        FROM JUGADORPENA JP
        LEFT JOIN EJUGADOR EJ ON JP.Idjugador = EJ.Idjugador
        LEFT JOIN EQUIPO E ON EJ.Ide = E.Ide
        LEFT JOIN PARTIDO P ON E.Idp = P.Idp AND JP.Idpena = P.Idpena
        WHERE P.Idt = %s AND JP.Idpena = %s
        GROUP BY JP.Idjugador, JP.Mote
        ORDER BY JP.Mote
    """, (id_temporada, session['Idpena']))
    estadisticas_jugadores = [dict(row) for row in cursor.fetchall()]

    # Mezclar estadísticas avanzadas en la lista `jugadores`
    for jug in jugadores:
        e = next((x for x in estadisticas_jugadores if x['Idjugador'] == jug['Idjugador']), None)
        if e:
            jug['Goles'] = e['Total_Goles']
            jug['Asistencias'] = e['Total_Asistencias']
            jug['Valoracion'] = e['Valoracion_Promedio']
        else:
            jug['Goles'] = 0
            jug['Asistencias'] = 0
            jug['Valoracion'] = "N/A"

    # Jugadores disponibles para añadir
    cursor.execute("""
        SELECT JP.Idjugador, JP.Mote
        FROM JUGADORPENA JP
        WHERE JP.Idpena = %s
        AND JP.Idjugador NOT IN (
            SELECT Idjugador
            FROM JUGADORTEMPORADA
            WHERE Idt = %s AND Idpena = %s
        )
    """, (session['Idpena'], id_temporada, session['Idpena']))
    jugadores_disponibles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'visualizar_temporada.html',
        temporada=temporada,
        jugadores=jugadores,
        partidos=partidos,
        estadisticas_jugadores=estadisticas_jugadores,
        jugadores_disponibles=jugadores_disponibles
    )


@app.route('/admin/draft_partido/<int:id_temporada>', methods=['GET', 'POST'])
def draft_partido(id_temporada):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Validar que la temporada exista
    cursor.execute("""
        SELECT Idt, Fechaini, Fechafin
        FROM TEMPORADA
        WHERE Idt = %s AND Idpena = %s
    """, (id_temporada, session['Idpena']))
    temporada = cursor.fetchone()

    if not temporada:
        cursor.close()
        conn.close()
        flash('Temporada no encontrada.')
        return redirect(url_for('gestionar_temporadas'))

    if request.method == 'POST':
        if 'convocar' in request.form:
            # Jugadores seleccionados
            convocados = request.form.getlist('convocados')
            session['convocados'] = convocados
            flash(f'{len(convocados)} jugadores convocados.')
            cursor.close()
            conn.close()
            return redirect(url_for('draft_partido', id_temporada=id_temporada))

        elif 'crear_partido' in request.form:
            # Obtener jugadores de cada equipo
            jugadores_equipo_1 = request.form.getlist('equipo_1')
            jugadores_equipo_2 = request.form.getlist('equipo_2')

            # Validaciones...
            jugadores_repetidos = set(jugadores_equipo_1).intersection(set(jugadores_equipo_2))
            if jugadores_repetidos:
                flash(f"Estos jugadores están en ambos equipos: {', '.join(jugadores_repetidos)}.")
                cursor.close()
                conn.close()
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            if len(jugadores_equipo_1) < 1 or len(jugadores_equipo_2) < 1:
                flash("Cada equipo debe tener al menos un jugador.")
                cursor.close()
                conn.close()
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            if len(jugadores_equipo_1) != len(jugadores_equipo_2):
                flash("Ambos equipos deben tener el mismo número de jugadores.")
                cursor.close()
                conn.close()
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            # Crear partido, recuperando su Idp
            cursor.execute("""
                INSERT INTO PARTIDO (Idpena, Idt)
                VALUES (%s, %s)
                RETURNING Idp
            """, (session['Idpena'], id_temporada))
            id_partido = cursor.fetchone()[0]

            # Crear dos equipos para el partido
            # Asumimos Ide=1 y Ide=2 para equipo 1 y 2 (si tu lógica lo requiere de otra manera, ajusta)
            cursor.execute("""
                INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                VALUES (1, %s, %s, %s)
            """, (id_partido, session['Idpena'], id_temporada))

            cursor.execute("""
                INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                VALUES (2, %s, %s, %s)
            """, (id_partido, session['Idpena'], id_temporada))

            total_goles_equipo_1 = 0
            total_goles_equipo_2 = 0

            # Equipo 1 stats
            for jugador_id in jugadores_equipo_1:
                goles = int(request.form.get(f'goles_{jugador_id}_equipo-1', 0))
                asistencias = int(request.form.get(f'asistencias_{jugador_id}_equipo-1', 0))
                valoracion = float(request.form.get(f'valoracion_{jugador_id}_equipo-1', 5))

                total_goles_equipo_1 += goles

                cursor.execute("""
                    INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                    VALUES (1, %s, %s, %s, %s, %s)
                """, (id_partido, jugador_id, goles, asistencias, valoracion))

            # Equipo 2 stats
            for jugador_id in jugadores_equipo_2:
                goles = int(request.form.get(f'goles_{jugador_id}_equipo-2', 0))
                asistencias = int(request.form.get(f'asistencias_{jugador_id}_equipo-2', 0))
                valoracion = float(request.form.get(f'valoracion_{jugador_id}_equipo-2', 5))

                total_goles_equipo_2 += goles

                cursor.execute("""
                    INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                    VALUES (2, %s, %s, %s, %s, %s)
                """, (id_partido, jugador_id, goles, asistencias, valoracion))

            # Determinar resultado
            resultado_equipo_1 = 0
            resultado_equipo_2 = 0

            if total_goles_equipo_1 > total_goles_equipo_2:
                resultado_equipo_1 = 1  # victoria
                resultado_equipo_2 = -1 # derrota
            elif total_goles_equipo_1 < total_goles_equipo_2:
                resultado_equipo_1 = -1
                resultado_equipo_2 = 1

            # Actualizar JUGADORTEMPORADA
            for jugador_id in jugadores_equipo_1:
                if resultado_equipo_1 == 1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET VICT = VICT + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))
                elif resultado_equipo_1 == -1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET DERR = DERR + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))
                else:
                    # empate
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET EMP = EMP + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))

            for jugador_id in jugadores_equipo_2:
                if resultado_equipo_2 == 1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET VICT = VICT + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))
                elif resultado_equipo_2 == -1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET DERR = DERR + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))
                else:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET EMP = EMP + 1
                        WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                    """, (jugador_id, session['Idpena'], id_temporada))

            conn.commit()
            cursor.close()
            conn.close()

            session.pop('convocados', None)
            flash('Partido creado y jugadores asignados con éxito.')
            return redirect(url_for('visualizar_temporada', id_temporada=id_temporada))

    # GET: mostrar jugadores disponibles
    cursor.execute("""
        SELECT JT.Idjugador, JP.Mote, JP.Posicion
        FROM JUGADORTEMPORADA JT
        JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
        WHERE JT.Idpena = %s AND JT.Idt = %s
    """, (session['Idpena'], id_temporada))
    jugadores_disponibles = cursor.fetchall()

    convocados = session.get('convocados', [])
    jugadores_convocados = [j for j in jugadores_disponibles if str(j['idjugador']) in convocados]

    cursor.close()
    conn.close()

    return render_template('draft_partido.html',
                           temporada=temporada,
                           jugadores_disponibles=jugadores_disponibles,
                           jugadores_convocados=jugadores_convocados)


@app.route('/admin/ver_estadisticas_partido/<int:id_partido>', methods=['GET'])
def ver_estadisticas_partido(id_partido):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Info del partido
    cursor.execute("""
        SELECT Idp, Idpena, Idt
        FROM PARTIDO
        WHERE Idp = %s AND Idpena = %s
    """, (id_partido, session['Idpena']))
    partido = cursor.fetchone()

    if not partido:
        cursor.close()
        conn.close()
        flash('Partido no encontrado.')
        return redirect(url_for('gestionar_partidos'))

    # Estadísticas jugadores
    cursor.execute("""
        SELECT
            E.Ide AS Equipo,
            JP.Mote AS Jugador,
            EJ.Goles,
            EJ.Asistencias,
            EJ.Val
        FROM EJUGADOR EJ
        JOIN EQUIPO E ON EJ.Ide = E.Ide
        JOIN JUGADORPENA JP ON EJ.Idjugador = JP.Idjugador AND JP.Idpena = E.Idpena
        WHERE EJ.Idp = %s
        ORDER BY E.Ide, JP.Mote
    """, (id_partido,))
    estadisticas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('ver_estadisticas_partido.html',
                           partido=partido,
                           estadisticas=estadisticas)



# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Error 404: Ruta no encontrada. {request.path}")
    return make_response(jsonify({"error": "No encontrado"}), 404)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error 500: {error}")
    return make_response(jsonify({"error": "Error interno del servidor"}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)