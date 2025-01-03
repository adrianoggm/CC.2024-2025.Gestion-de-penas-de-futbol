from datetime import datetime
from flask import Flask, flash,jsonify, render_template, request, make_response,render_template_string, redirect, url_for,session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import os
from logging_config import setup_logging

#app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'
Admin=False


# Configuración del logger
logger = setup_logging("app")
db_logger = setup_logging("db")

db_path = os.path.join('', 'Gestion_Penas.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
        db_logger.info("Conexión a la base de datos establecida.")
        return conn
    except sqlite3.Error as e:
        db_logger.error(f"Error al conectar a la base de datos: {e}")
        raise

@app.route('/', methods=['GET'])
def ping():
    logger.info("Ruta raíz accesada.")
    #print("Ruta raíz accesada.")
    return render_template('index.html')


@app.route('/registration_pena', methods=['GET', 'POST'])
def registration_pena():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        nombre_peña = request.form['nombre_peña']

        # Validaciones simples
        if password != confirm_password:
            flash('Las contraseñas no coinciden. Por favor, intenta de nuevo.')
            logger.warning(f"Error de coincidencia de contraseñas para el usuario: {username}.")
            return redirect(url_for('registration_pena'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            logger.warning(f"Intento de registro fallido. El nombre de usuario '{username}' ya existe.")
            flash('El nombre de usuario ya existe. Por favor, elige otro.')
            return redirect(url_for('registration_pena'))

        # Insertar en la tabla de peñas
        cursor.execute("INSERT INTO PENA (nombre) VALUES (?)", (nombre_peña,))
        id_peña = cursor.lastrowid  # Obtener el ID de la nueva peña
        db_logger.info(f"Peña '{nombre_peña}' creada con ID {id_peña}.")
        # Insertar en la tabla de administradores con Idpena
        cursor.execute("INSERT INTO admins (username, password, Idpena) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), id_peña))
        db_logger.info(f"Administrador '{username}' registrado para la peña con ID {id_peña}.")
        flash('Admin registrado exitosamente. Ahora puedes iniciar sesión.')
        logger.info(f"Registro exitoso del administrador '{username}'.")
        conn.commit()
        conn.close()
        logger.debug("Conexión a la base de datos cerrada.")
        return redirect(url_for('login'))  # Redirigir al login después del registro
    logger.info("Formulario de registro de peña accedido mediante GET.")
    return render_template('registration_pena.html')  # Cargar el formulario de registro de peña
@app.route('/registration_jugador', methods=['GET', 'POST'])
def registration_jugador():
    logger.info("Acceso al formulario de registro de jugador.")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        id_peña = request.form['id_peña']  # ID de la peña a la que se unirá el jugador
        mote = request.form['mote']
        posicion = request.form['posicion']
        nacionalidad = request.form['nacionalidad']

        # Validaciones simples
        if password != confirm_password:
            flash('Las contraseñas no coinciden. Por favor, intenta de nuevo.')
            logger.warning(f"Error de coincidencia de contraseñas para el jugador: {username}.")
            return redirect(url_for('registration_jugador'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            logger.debug("Conexión a la base de datos establecida.")

            # Insertar en la tabla de jugadores
            cursor.execute("INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (?, ?, ?)",
                           (username, '', nacionalidad))
            id_jugador = cursor.lastrowid  # Obtener el ID del nuevo jugador
            db_logger.info(f"Jugador '{username}' creado con ID {id_jugador}.")

            # Insertar en la tabla JUGADORPENA
            cursor.execute("INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (?, ?, ?, ?)",
                           (id_jugador, id_peña, mote, posicion))
            db_logger.info(f"Jugador '{username}' asociado a la peña ID {id_peña} con mote '{mote}' y posición '{posicion}'.")

            flash('Jugador registrado exitosamente. Ahora puedes iniciar sesión.')
            logger.info(f"Jugador '{username}' registrado exitosamente.")
            
            conn.commit()
            logger.debug("Transacciones de la base de datos confirmadas.")
        except sqlite3.Error as e:
            logger.error(f"Error en la base de datos durante el registro de jugador '{username}': {e}", exc_info=True)
            flash("Ocurrió un error en el registro. Por favor, inténtalo más tarde.")
            return redirect(url_for('registration_jugador'))
        finally:
            if conn:
                conn.close()
                logger.debug("Conexión a la base de datos cerrada.")

        return redirect(url_for('login'))  # Redirigir al login después del registro

    return render_template('registration_jugador.html')  # Cargar el formulario de registro de jugador


@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Acceso al formulario de inicio de sesión.")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Intento de inicio de sesión con el nombre de usuario: {username}.")

        conn = get_db_connection()

        try:
            # Conectar a la base de datos y buscar el usuario
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            # Convertir el objeto Row en un diccionario
            if user:
                user = dict(user)
                logger.info(f"Usuario encontrado: {username}. Tipo: Jugador.")
                Admin = False
            else:
                user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
                if user:
                    user = dict(user)
                    db_logger.info(f"Usuario encontrado: {username}. Tipo: Administrador.")
                    Admin = True
                else:
                    logger.warning(f"Intento de inicio de sesión fallido. Usuario '{username}' no encontrado.")
                    flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.')
                    return redirect(url_for('login'))
        except sqlite3.Error as e:
            logger.error(f"Error durante la búsqueda del usuario '{username}': {e}", exc_info=True)
            flash('Ocurrió un error. Inténtalo de nuevo.')
            return redirect(url_for('login'))
        finally:
            conn.close()
            logger.debug("Conexión a la base de datos cerrada.")

        # Verificar si el usuario existe y la contraseña es correcta
        if user and check_password_hash(user['password'], password):
            if Admin:
                session['username'] = user['username']
                session['name'] = user['username']
                session['Idpena'] = user['Idpena']
                logger.info(f"Administrador '{username}' inició sesión exitosamente.")
                return redirect(url_for('admin_dashboard'))
            else:
                session['username'] = user['username']
                session['name'] = user['name']
                session['Idjugador'] = user['Idjugador']
                logger.info(f"Jugador '{username}' intentó iniciar sesión, pero la funcionalidad no está implementada.")
                flash('Usuario no es admin funcionalidad aún no implementada.')
                return redirect(url_for('login'))
        else:
            logger.warning(f"Intento de inicio de sesión fallido para el usuario '{username}'. Contraseña incorrecta.")
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session:
        logger.warning("Intento de acceso al dashboard sin iniciar sesión.")
        flash('Por favor, inicia sesión primero.')
        return redirect(url_for('login'))

    username = session.get('username')
    logger.info(f"Acceso al dashboard por el usuario: {username}.")
    return render_template('admin_dashboard.html', username=username)

    
@app.route('/admin/gestionar_jugadores')
def gestionar_jugadores():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado a la gestión de jugadores.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        id = session['Idpena']
        jugadores = conn.execute('SELECT * FROM JUGADORPENA WHERE idpena = ?', (id,)).fetchall()
        logger.info(f"Gestión de jugadores accedida por el administrador de la peña ID {id}.")
    except sqlite3.Error as e:
        logger.error(f"Error al obtener los jugadores para la peña ID {id}: {e}", exc_info=True)
        jugadores = []
    finally:
        conn.close()
        logger.debug("Conexión a la base de datos cerrada.")

    return render_template('gestionar_jugadores.html', jugadores=jugadores)

# Gestión de partidos
@app.route('/admin/gestionar_partidos')
def gestionar_partidos():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    # Aquí puedes obtener los datos de los partidos desde la base de datos
    conn = get_db_connection()
    partidos = conn.execute('SELECT * FROM PARTIDO').fetchall()
    conn.close()

    return render_template('gestionar_partidos.html', partidos=partidos)
@app.route('/admin/gestionar_jugadores/añadir_jugador', methods=['GET', 'POST'])
def añadir_jugador():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado a la funcionalidad de añadir jugador.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']

        logger.info(f"Intento de añadir jugador. Nombre: {nombre}, Mote: {mote}, Posición: {posicion}, Peña ID: {session.get('Idpena')}")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Insertar en la tabla JUGADOR
            cursor.execute("INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (?, ?, ?)",
                           (nombre, apellidos, nacionalidad))
            id_jugador = cursor.lastrowid
            db_logger.info(f"Jugador '{nombre}' creado con ID {id_jugador}.")

            # Insertar en la tabla JUGADORPENA
            id_pena = session['Idpena']
            cursor.execute("INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (?, ?, ?, ?)",
                           (id_jugador, id_pena, mote, posicion))
            db_logger.info(f"Jugador ID {id_jugador} asociado a la peña ID {id_pena} como '{mote}' ({posicion}).")

            conn.commit()
            flash('Jugador añadido exitosamente.')
            logger.info(f"Jugador '{nombre}' añadido exitosamente.")
        except sqlite3.Error as e:
            logger.error(f"Error al añadir jugador '{nombre}': {e}", exc_info=True)
            flash('Error al añadir el jugador. Por favor, inténtalo de nuevo.')
        finally:
            conn.close()
            logger.debug("Conexión a la base de datos cerrada.")

        return redirect(url_for('gestionar_jugadores'))
    
    logger.info("Formulario para añadir jugador accedido mediante GET.")
    return render_template('añadir_jugador.html')


@app.route('/admin/gestionar_jugadores/editar/<int:jugador_id>', methods=['GET', 'POST'])
def editar_jugador(jugador_id):
    if 'Idpena' not in session:
        logger.warning(f"Acceso no autorizado a la edición del jugador ID {jugador_id}.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']

        logger.info(f"Intento de edición para el jugador ID {jugador_id}. Nuevos datos: Nombre={nombre}, Apellidos={apellidos}, Nacionalidad={nacionalidad}, Mote={mote}, Posición={posicion}")

        try:
            # Actualizar los datos del jugador en la tabla JUGADOR
            conn.execute("""
                UPDATE JUGADOR
                SET Nombre = ?, Apellidos = ?, Nacionalidad = ?
                WHERE Idjugador = ?
            """, (nombre, apellidos, nacionalidad, jugador_id))
            db_logger.info(f"Jugador ID {jugador_id} actualizado en la tabla JUGADOR.")

            # Actualizar los datos en la tabla JUGADORPENA
            conn.execute("""
                UPDATE JUGADORPENA
                SET Mote = ?, Posicion = ?
                WHERE Idjugador = ? AND Idpena = ?
            """, (mote, posicion, jugador_id, session['Idpena']))
            db_logger.info(f"Jugador ID {jugador_id} actualizado en la tabla JUGADORPENA.")

            conn.commit()
            flash('Jugador actualizado correctamente.')
            logger.info(f"Jugador ID {jugador_id} actualizado exitosamente.")
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar el jugador ID {jugador_id}: {e}", exc_info=True)
            flash('Error al actualizar el jugador. Por favor, inténtalo de nuevo.')
        finally:
            conn.close()
            logger.debug("Conexión a la base de datos cerrada.")

        return redirect(url_for('gestionar_jugadores'))

    try:
        # Obtener los datos actuales del jugador
        jugador = conn.execute("""
            SELECT JUGADOR.*, JUGADORPENA.Mote, JUGADORPENA.Posicion
            FROM JUGADOR
            JOIN JUGADORPENA ON JUGADOR.Idjugador = JUGADORPENA.Idjugador
            WHERE JUGADOR.Idjugador = ? AND JUGADORPENA.Idpena = ?
        """, (jugador_id, session['Idpena'])).fetchone()

        if jugador is None:
            logger.warning(f"Intento de editar jugador no encontrado. ID: {jugador_id}, Peña ID: {session['Idpena']}.")
            flash('Jugador no encontrado.')
            return redirect(url_for('gestionar_jugadores'))
        
        logger.info(f"Datos cargados para edición del jugador ID {jugador_id}.")
    except sqlite3.Error as e:
        logger.error(f"Error al cargar los datos del jugador ID {jugador_id}: {e}", exc_info=True)
        flash('Error al cargar los datos del jugador. Por favor, inténtalo de nuevo.')
        return redirect(url_for('gestionar_jugadores'))
    finally:
        conn.close()
        logger.debug("Conexión a la base de datos cerrada.")

    return render_template('editar_jugador.html', jugador=jugador)

@app.route('/admin/gestionar_jugadores/eliminar/<int:jugador_id>', methods=['POST'])
def eliminar_jugador(jugador_id):
    if 'Idpena' not in session:
        logger.warning(f"Acceso no autorizado al intento de eliminación del jugador ID {jugador_id}.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    try:
        # Eliminar el jugador de ambas tablas
        conn.execute("DELETE FROM JUGADORPENA WHERE Idjugador = ? AND Idpena = ?", (jugador_id, session['Idpena']))
        db_logger.info(f"Jugador ID {jugador_id} eliminado de la tabla JUGADORPENA (Peña ID: {session['Idpena']}).")

        conn.execute("DELETE FROM JUGADOR WHERE Idjugador = ?", (jugador_id,))
        db_logger.info(f"Jugador ID {jugador_id} eliminado de la tabla JUGADOR.")

        conn.commit()
        flash('Jugador eliminado correctamente.')
        logger.info(f"Jugador ID {jugador_id} eliminado exitosamente.")
    except sqlite3.Error as e:
        logger.error(f"Error al eliminar el jugador ID {jugador_id}: {e}", exc_info=True)
        flash('Error al eliminar el jugador. Por favor, inténtalo de nuevo.')
    finally:
        conn.close()
        logger.debug("Conexión a la base de datos cerrada.")

    return redirect(url_for('gestionar_jugadores'))


@app.route('/admin/gestionar_temporadas', methods=['GET'])
def gestionar_temporadas():
    if 'Idpena' not in session:
        logger.warning("Acceso no autorizado a la gestión de temporadas.")
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    try:
        # Obtener todas las temporadas asociadas a la peña del administrador
        temporadas = conn.execute("""
            SELECT * FROM TEMPORADA
            WHERE Idpena = ?
            ORDER BY Idt DESC
        """, (session['Idpena'],)).fetchall()
        logger.info(f"Se recuperaron {len(temporadas)} temporadas para la Peña ID {session['Idpena']}.")
    except sqlite3.Error as e:
        logger.error(f"Error al recuperar temporadas para Peña ID {session['Idpena']}: {e}", exc_info=True)
        flash('Error al recuperar las temporadas. Por favor, inténtalo de nuevo.')
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()
        logger.debug("Conexión a la base de datos cerrada.")

    return render_template('gestionar_temporadas.html', temporadas=temporadas)

@app.route('/admin/gestionar_temporadas/añadir', methods=['GET', 'POST'])
def añadir_temporada():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        fechaini = request.form['fechaini']
        fechafin = request.form['fechafin']

        try:
            # Convertir fechas del formato DD/MM/YYYY al formato ISO (YYYY-MM-DD)
            print(fechaini)
            fecha_ini_iso = fechaini
            fecha_fin_iso = fechafin

            # Validar que la fecha de inicio sea anterior a la fecha de fin
            if fecha_ini_iso >= fecha_fin_iso:
                flash('La fecha de inicio debe ser anterior a la fecha de fin.')
                return redirect(url_for('añadir_temporada'))
        except ValueError:
            flash('Fecha inválida. Por favor, introduce fechas válidas en formato DD/MM/YYYY.')
            return redirect(url_for('añadir_temporada'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar nueva temporada asociada a la peña
        cursor.execute("""
            INSERT INTO TEMPORADA (Idpena, Fechaini, Fechafin)
            VALUES (?, ?, ?)
        """, (session['Idpena'], fecha_ini_iso, fecha_fin_iso))
        conn.commit()
        conn.close()

        flash('Temporada añadida exitosamente.')
        return redirect(url_for('gestionar_temporadas'))

    return render_template('añadir_temporada.html')

@app.route('/admin/gestionar_temporadas/eliminar/<int:id_temporada>', methods=['POST'])
def eliminar_temporada(id_temporada):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Verificar y eliminar la temporada
    conn.execute("""
        DELETE FROM TEMPORADA
        WHERE Idt = ? AND Idpena = ?
    """, (id_temporada, session['Idpena']))
    conn.commit()
    conn.close()

    flash('Temporada eliminada correctamente.')
    return redirect(url_for('gestionar_temporadas'))


@app.route('/admin/visualizar_temporada/<int:id_temporada>', methods=['GET', 'POST'])
def visualizar_temporada(id_temporada):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Obtener la información básica de la temporada
    temporada = conn.execute("""
        SELECT Idt, Fechaini, Fechafin
        FROM TEMPORADA
        WHERE Idt = ? AND Idpena = ?
    """, (id_temporada, session['Idpena'])).fetchone()

    if not temporada:
        flash('Temporada no encontrada.')
        return redirect(url_for('gestionar_temporadas'))

    if request.method == 'POST':
        jugador_id = request.form.get('jugador_id')

        # Validar si el jugador ya está en la temporada
        existe = conn.execute("""
            SELECT 1 FROM JUGADORTEMPORADA
            WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
        """, (jugador_id, session['Idpena'], id_temporada)).fetchone()

        if existe:
            flash('El jugador ya está asociado a esta temporada.')
        else:
            # Añadir jugador a la temporada
            conn.execute("""
                INSERT INTO JUGADORTEMPORADA (Idjugador, Idpena, Idt)
                VALUES (?, ?, ?)
            """, (jugador_id, session['Idpena'], id_temporada))
            conn.commit()
            flash('Jugador añadido a la temporada con éxito.')

    # Clasificación de jugadores
    jugadores = conn.execute("""
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
        WHERE JT.Idt = ? AND JT.Idpena = ?
        ORDER BY Puntos DESC, Porcentaje_victorias DESC
    """, (id_temporada, session['Idpena'])).fetchall()

    # Lista de partidos con resultados
    partidos = conn.execute("""
        SELECT 
            P.Idp, 
            COALESCE(SUM(EJ1.Goles), 0) AS Goles_Equipo1,
            COALESCE(SUM(EJ2.Goles), 0) AS Goles_Equipo2
        FROM PARTIDO P
        LEFT JOIN EQUIPO E1 ON P.Idp = E1.Idp AND E1.Ide = 1
        LEFT JOIN EQUIPO E2 ON P.Idp = E2.Idp AND E2.Ide = 2
        LEFT JOIN EJUGADOR EJ1 ON EJ1.Idp = E1.Idp AND EJ1.Ide = E1.Ide
        LEFT JOIN EJUGADOR EJ2 ON EJ2.Idp = E2.Idp AND EJ2.Ide = E2.Ide
        WHERE P.Idt = ? AND P.Idpena = ?
        GROUP BY P.Idp
        ORDER BY P.Idp ASC
    """, (id_temporada, session['Idpena'])).fetchall()

    # Estadísticas avanzadas de jugadores
    estadisticas_jugadores = conn.execute("""
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
        WHERE P.Idt = ? AND JP.Idpena = ?
        GROUP BY JP.Idjugador, JP.Mote
        ORDER BY JP.Mote
    """, (id_temporada, session['Idpena'])).fetchall()

    # Convertir las filas en diccionarios para manipulación
    jugadores = [dict(row) for row in jugadores]
    estadisticas_jugadores = [dict(row) for row in estadisticas_jugadores]

    # Agregar estadísticas avanzadas a los jugadores
    for jugador in jugadores:
        estadisticas = next(
            (e for e in estadisticas_jugadores if e['Idjugador'] == jugador['Idjugador']),
            None
        )
        if estadisticas:
            jugador['Goles'] = estadisticas['Total_Goles']
            jugador['Asistencias'] = estadisticas['Total_Asistencias']
            jugador['Valoracion'] = estadisticas['Valoracion_Promedio']
        else:
            jugador['Goles'] = 0
            jugador['Asistencias'] = 0
            jugador['Valoracion'] = "N/A"

    # Jugadores disponibles para añadir a la temporada
    jugadores_disponibles = conn.execute("""
        SELECT JP.Idjugador, JP.Mote
        FROM JUGADORPENA JP
        WHERE JP.Idpena = ?
        AND JP.Idjugador NOT IN (
            SELECT Idjugador
            FROM JUGADORTEMPORADA
            WHERE Idt = ? AND Idpena = ?
        )
    """, (session['Idpena'], id_temporada, session['Idpena'])).fetchall()

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

    # Validar que la temporada exista
    temporada = conn.execute("""
        SELECT Idt, Fechaini, Fechafin
        FROM TEMPORADA
        WHERE Idt = ? AND Idpena = ?
    """, (id_temporada, session['Idpena'])).fetchone()

    if not temporada:
        flash('Temporada no encontrada.')
        return redirect(url_for('gestionar_temporadas'))

    if request.method == 'POST':
        if 'convocar' in request.form:
            # Lista de convocados seleccionados
            convocados = request.form.getlist('convocados')
            session['convocados'] = convocados
            print(convocados)
            flash(f'{len(convocados)} jugadores convocados.')
            return redirect(url_for('draft_partido', id_temporada=id_temporada))

        elif 'crear_partido' in request.form:  # Aseguramos que esta acción es reconocida
            # Obtener jugadores asignados a cada equipo
            jugadores_equipo_1 = request.form.getlist('equipo_1')
            jugadores_equipo_2 = request.form.getlist('equipo_2')
            print(jugadores_equipo_1)
            print(jugadores_equipo_2)
            # Validaciones de equipos (ya existentes en tu código)
            jugadores_repetidos = set(jugadores_equipo_1).intersection(set(jugadores_equipo_2))
            if jugadores_repetidos:
                flash(f"Los siguientes jugadores están en ambos equipos: {', '.join(jugadores_repetidos)}. Corrige esto antes de continuar.")
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            if len(jugadores_equipo_1) < 1 or len(jugadores_equipo_2) < 1:
                flash("Cada equipo debe tener al menos un jugador.")
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            if len(jugadores_equipo_1) != len(jugadores_equipo_2):
                flash("Ambos equipos deben tener el mismo número de jugadores.")
                return redirect(url_for('draft_partido', id_temporada=id_temporada))

            # Crear el partido
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO PARTIDO (Idpena, Idt)
                VALUES (?, ?)
            """, (session['Idpena'], id_temporada))
            id_partido = cursor.lastrowid

                    # Crear equipos para el partido
            cursor.execute("""
                INSERT INTO EQUIPO (Idp, Idpena, Idt)
                VALUES (?, ?, ?)
            """, (id_partido, session['Idpena'], id_temporada))

            cursor.execute("""
                INSERT INTO EQUIPO (Idp, Idpena, Idt)
                VALUES (?, ?, ?)
            """, (id_partido, session['Idpena'], id_temporada))

                        # Inicializar los totales de goles para cada equipo
            total_goles_equipo_1 = 0
            total_goles_equipo_2 = 0

            # Asignar estadísticas a jugadores del equipo 1
            for jugador_id in jugadores_equipo_1:
                goles = int(request.form.get(f'goles_{jugador_id}_equipo-1', 0))
                asistencias = request.form.get(f'asistencias_{jugador_id}_equipo-1', 0)
                valoracion = request.form.get(f'valoracion_{jugador_id}_equipo-1', 5)
                
                # Sumar los goles al total del equipo 1
                total_goles_equipo_1 += goles
                
                # Insertar las estadísticas en la base de datos
                cursor.execute("""
                    INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                    VALUES (1, ?, ?, ?, ?, ?)
                """, (id_partido, jugador_id, goles, asistencias, valoracion))

            # Asignar estadísticas a jugadores del equipo 2
            for jugador_id in jugadores_equipo_2:
                goles = int(request.form.get(f'goles_{jugador_id}_equipo-2', 0))
                asistencias = request.form.get(f'asistencias_{jugador_id}_equipo-2', 0)
                valoracion = request.form.get(f'valoracion_{jugador_id}_equipo-2', 5)
                
                # Sumar los goles al total del equipo 2
                total_goles_equipo_2 += goles
                
                # Insertar las estadísticas en la base de datos
                cursor.execute("""
                    INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                    VALUES (2, ?, ?, ?, ?, ?)
                """, (id_partido, jugador_id, goles, asistencias, valoracion))
                
              # Determinar el resultado del partido
            resultado_equipo_1 = 0  # 1 = victoria, 0 = empate, -1 = derrota
            resultado_equipo_2 = 0

            if total_goles_equipo_1 > total_goles_equipo_2:
                resultado_equipo_1 = 1
                resultado_equipo_2 = -1
            elif total_goles_equipo_1 < total_goles_equipo_2:
                resultado_equipo_1 = -1
                resultado_equipo_2 = 1

            # Actualizar JUGADORTEMPORADA para cada jugador
            for jugador_id in jugadores_equipo_1:
                if resultado_equipo_1 == 1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET VICT = VICT + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))
                elif resultado_equipo_1 == -1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET DERR = DERR + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))
                else:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET EMP = EMP + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))

            for jugador_id in jugadores_equipo_2:
                if resultado_equipo_2 == 1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET VICT = VICT + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))
                elif resultado_equipo_2 == -1:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET DERR = DERR + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))
                else:
                    cursor.execute("""
                        UPDATE JUGADORTEMPORADA
                        SET EMP = EMP + 1
                        WHERE Idjugador = ? AND Idpena = ? AND Idt = ?
                    """, (jugador_id, session['Idpena'], id_temporada))
                    

            conn.commit()
            session.pop('convocados', None)
            flash('Partido creado y jugadores asignados con éxito.')
            return redirect(url_for('visualizar_temporada', id_temporada=id_temporada))

    # Obtener jugadores disponibles para asignar a equipos
    jugadores_disponibles = conn.execute("""
        SELECT JT.Idjugador, JP.Mote, JP.Posicion
        FROM JUGADORTEMPORADA JT
        JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
        WHERE JT.Idpena = ? AND JT.Idt = ?
    """, (session['Idpena'], id_temporada)).fetchall()

    convocados = session.get('convocados', [])
    jugadores_convocados = [j for j in jugadores_disponibles if str(j['Idjugador']) in convocados]

    conn.close()

    return render_template('draft_partido.html', temporada=temporada, jugadores_disponibles=jugadores_disponibles, jugadores_convocados=jugadores_convocados)

@app.route('/admin/ver_estadisticas_partido/<int:id_partido>', methods=['GET'])
def ver_estadisticas_partido(id_partido):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Obtener información básica del partido
    partido = conn.execute("""
        SELECT Idp, Idpena, Idt
        FROM PARTIDO
        WHERE Idp = ? AND Idpena = ?
    """, (id_partido, session['Idpena'])).fetchone()

    if not partido:
        flash('Partido no encontrado.')
        return redirect(url_for('gestionar_partidos'))

        # Obtener estadísticas de los jugadores
    estadisticas = conn.execute("""
        SELECT 
            E.Ide AS Equipo,
            JP.Mote AS Jugador,
            EJ.Goles,
            EJ.Asistencias,
            EJ.Val
        FROM EJUGADOR EJ
        JOIN EQUIPO E ON EJ.Ide = E.Ide
        JOIN JUGADORPENA JP ON EJ.Idjugador = JP.Idjugador AND JP.Idpena = E.Idpena
        WHERE EJ.Idp = ?
        ORDER BY E.Ide, JP.Mote
    """, (id_partido,)).fetchall()

    conn.close()

    return render_template('ver_estadisticas_partido.html', partido=partido, estadisticas=estadisticas)



app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return "✅ Base de datos conectada correctamente", 200
    except Exception as e:
        return f"❌ Error al conectar con la base de datos: {e}", 500
    
# Manejo de errores personalizados
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


    