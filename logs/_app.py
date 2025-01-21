from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, make_response, redirect, url_for, session
import psycopg2
import psycopg2.extras  # Para obtener cursores tipo diccionario
import os
from src.logging_config import setup_logging
from flask import Flask, flash, jsonify, render_template, request, make_response, render_template_string, redirect, url_for, session
import psycopg2          # CAMBIO: reemplaza import sqlite3
import psycopg2.extras   # Para cursores tipo diccionario
from werkzeug.security import check_password_hash, generate_password_hash


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
from flask import Blueprint, request, session, jsonify
import psycopg2
import psycopg2.extras
from psycopg2 import Error
from src.services.db_service import get_db_connection
from src.logging_config import setup_logging

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
logger = setup_logging("admin_routes")


def admin_required(f):
    """
    Decorador sencillo para verificar que existe 'Idpena' en la sesión
    (indicando que se ha iniciado sesión como admin).
    """
    def wrapper(*args, **kwargs):
        if 'Idpena' not in session:
            logger.warning("Intento de acceso sin tener sesión de admin.")
            return jsonify({"error": "No autorizado. Inicia sesión como administrador."}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ------------------------------------------------
#  GESTIÓN DE PARTIDOS
# ------------------------------------------------
@admin_bp.route('/gestionar_partidos', methods=['GET'])
@admin_required
def gestionar_partidos():
    """
    Devuelve la lista de todos los partidos (ejemplo).
    Puedes filtrarlos por Idpena si deseas.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Si quieres filtrar por la peña del admin, descomenta lo siguiente:
        # cursor.execute("SELECT * FROM PARTIDO WHERE Idpena = %s", (session['Idpena'],))
        cursor.execute("SELECT * FROM PARTIDO")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        partidos = [dict(r) for r in rows]
        logger.info(f"Obtenidos {len(partidos)} partidos.")
        return jsonify({"partidos": partidos}), 200

    except Error as e:
        logger.error(f"Error al obtener partidos: {e}", exc_info=True)
        return jsonify({"error": "Error al obtener partidos"}), 500


# ------------------------------------------------
#  GESTIÓN DE TEMPORADAS
# ------------------------------------------------
@admin_bp.route('/gestionar_temporadas', methods=['GET'])
@admin_required
def gestionar_temporadas():
    """
    Devuelve las temporadas para la peña actual (Idpena en sesión).
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("""
            SELECT * FROM TEMPORADA
            WHERE Idpena = %s
            ORDER BY Idt DESC
        """, (id_pena,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        temporadas = [dict(r) for r in rows]
        logger.info(f"Se recuperaron {len(temporadas)} temporadas para Peña ID={id_pena}.")
        return jsonify({"temporadas": temporadas}), 200

    except Error as e:
        logger.error(f"Error al recuperar temporadas para Peña ID={id_pena}: {e}", exc_info=True)
        return jsonify({"error": "Error al recuperar temporadas"}), 500


@admin_bp.route('/gestionar_temporadas/añadir', methods=['POST'])
@admin_required
def añadir_temporada():
    """
    Añade una nueva temporada.
    JSON esperado:
      {
        "fechaini": "2023-01-01",
        "fechafin": "2023-12-31"
      }
    """
    data = request.get_json() or {}
    fechaini = data.get('fechaini')
    fechafin = data.get('fechafin')

    if not fechaini or not fechafin:
        return jsonify({"error": "Faltan campos fechaini o fechafin"}), 400

    if fechaini >= fechafin:
        return jsonify({"error": "fechaini debe ser anterior a fechafin"}), 400

    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TEMPORADA (Idpena, Fechaini, Fechafin)
            VALUES (%s, %s, %s)
            RETURNING Idt
        """, (id_pena, fechaini, fechafin))

        id_temporada = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Temporada añadida exitosamente con ID={id_temporada}.")
        return jsonify({"message": "Temporada añadida", "id_temporada": id_temporada}), 201

    except Error as e:
        logger.error(f"Error al añadir temporada: {e}", exc_info=True)
        return jsonify({"error": "Error al añadir la temporada"}), 500


@admin_bp.route('/gestionar_temporadas/eliminar/<int:id_temporada>', methods=['DELETE'])
@admin_required
def eliminar_temporada(id_temporada):
    """
    Elimina una temporada (si pertenece a la peña del admin en sesión).
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM TEMPORADA
            WHERE Idt = %s AND Idpena = %s
        """, (id_temporada, id_pena))
        filas_afectadas = cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            logger.warning(f"No se encontró la temporada con ID={id_temporada} para la peña {id_pena}.")
            return jsonify({"error": "Temporada no encontrada"}), 404

        logger.info(f"Temporada ID={id_temporada} eliminada correctamente.")
        return jsonify({"message": "Temporada eliminada"}), 200

    except Error as e:
        logger.error(f"Error al eliminar temporada {id_temporada}: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar la temporada"}), 500


# ------------------------------------------------
#  VISUALIZAR TEMPORADA
# ------------------------------------------------
@admin_bp.route('/visualizar_temporada/<int:id_temporada>', methods=['GET', 'POST'])
@admin_required
def visualizar_temporada(id_temporada):
    """
    GET: Retorna la información detallada de la temporada, jugadores inscritos,
         clasificación y partidos.
    POST: Añade un jugador a la temporada (si no está ya).
           {
             "jugador_id": 123
           }
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Verificar si la temporada pertenece a la peña
        cursor.execute("""
            SELECT Idt, Fechaini, Fechafin
            FROM TEMPORADA
            WHERE Idt = %s AND Idpena = %s
        """, (id_temporada, id_pena))
        temporada = cursor.fetchone()
        if not temporada:
            cursor.close()
            conn.close()
            return jsonify({"error": "Temporada no encontrada"}), 404

        if request.method == 'POST':
            data = request.get_json() or {}
            jugador_id = data.get('jugador_id')
            if jugador_id:
                # Ver si el jugador ya está en la temporada
                cursor.execute("""
                    SELECT 1 FROM JUGADORTEMPORADA
                    WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                """, (jugador_id, id_pena, id_temporada))
                existe = cursor.fetchone()

                if existe:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Jugador ya asociado a la temporada"}), 400
                else:
                    # Insertar jugador en la temporada
                    cursor.execute("""
                        INSERT INTO JUGADORTEMPORADA (Idjugador, Idpena, Idt)
                        VALUES (%s, %s, %s)
                    """, (jugador_id, id_pena, id_temporada))
                    conn.commit()
                    # No cerramos aquí todavía, seguimos para devolver info actualizada

            # Pasamos a devolver al final la misma info en JSON

        # Cargar clasificación de jugadores
        cursor.execute("""
            SELECT
                J.Idjugador,
                JP.Mote,
                JT.VICT,
                JT.EMP,
                JT.DERR,
                (JT.VICT * 3 + JT.EMP * 2 + JT.DERR * 1) AS Puntos,
                ROUND((JT.VICT::numeric / NULLIF(JT.VICT + JT.EMP + JT.DERR, 0) * 100),2) AS Porcentaje_victorias
            FROM JUGADORTEMPORADA JT
            JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
            JOIN JUGADOR J ON JP.Idjugador = J.Idjugador
            WHERE JT.Idt = %s AND JT.Idpena = %s
            ORDER BY Puntos DESC, Porcentaje_victorias DESC
        """, (id_temporada, id_pena))
        jugadores_clasif = [dict(r) for r in cursor.fetchall()]

        # Partidos de la temporada (ejemplo de goles por partido)
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
        """, (id_temporada, id_pena))
        rows_partidos = cursor.fetchall()
        partidos = [dict(r) for r in rows_partidos]

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
        """, (id_temporada, id_pena))
        estadisticas_jugadores = [dict(r) for r in cursor.fetchall()]

        # Mezclar estadísticas avanzadas con la clasificación
        for jug in jugadores_clasif:
            e = next((x for x in estadisticas_jugadores if x['idjugador'] == jug['idjugador']), None)
            if e:
                jug['Total_Goles'] = e['total_goles']
                jug['Total_Asistencias'] = e['total_asistencias']
                jug['Valoracion_Promedio'] = e['valoracion_promedio']
            else:
                jug['Total_Goles'] = 0
                jug['Total_Asistencias'] = 0
                jug['Valoracion_Promedio'] = 0

        # Jugadores disponibles para añadir a la temporada
        cursor.execute("""
            SELECT JP.Idjugador, JP.Mote
            FROM JUGADORPENA JP
            WHERE JP.Idpena = %s
            AND JP.Idjugador NOT IN (
                SELECT Idjugador
                FROM JUGADORTEMPORADA
                WHERE Idt = %s AND Idpena = %s
            )
        """, (id_pena, id_temporada, id_pena))
        jugadores_disponibles = [dict(r) for r in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Respuesta final: info de la temporada, clasificación, partidos, jugadores disponibles
        temporada_json = {
            "Idt": temporada["Idt"],
            "Fechaini": str(temporada["Fechaini"]),
            "Fechafin": str(temporada["Fechafin"])
        }

        return jsonify({
            "temporada": temporada_json,
            "jugadores_clasificacion": jugadores_clasif,
            "partidos": partidos,
            "estadisticas_jugadores": estadisticas_jugadores,
            "jugadores_disponibles": jugadores_disponibles
        }), 200

    except Error as e:
        logger.error(f"Error en visualizar_temporada (ID={id_temporada}): {e}", exc_info=True)
        return jsonify({"error": "Error al cargar la temporada"}), 500


# ------------------------------------------------
#  DRAFT DE PARTIDO
# ------------------------------------------------
@admin_bp.route('/draft_partido/<int:id_temporada>', methods=['GET', 'POST'])
@admin_required
def draft_partido(id_temporada):
    """
    GET: Devuelve la lista de jugadores disponibles en la temporada (JUGADORTEMPORADA).
    POST:
      - Si 'convocar' en el payload, guarda la lista de convocados en session (no muy REST, pero ejemplo).
      - Si 'crear_partido', crea un partido con los dos equipos y sus stats.
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Verificar temporada
        cursor.execute("""
            SELECT Idt
            FROM TEMPORADA
            WHERE Idt = %s AND Idpena = %s
        """, (id_temporada, id_pena))
        temporada = cursor.fetchone()
        if not temporada:
            cursor.close()
            conn.close()
            return jsonify({"error": "Temporada no encontrada"}), 404

        if request.method == 'POST':
            data = request.get_json() or {}
            if data.get('convocar') is not None:
                convocados = data['convocar']  # lista de IDs de jugadores
                session['convocados'] = convocados
                logger.info(f"{len(convocados)} jugadores convocados.")
                cursor.close()
                conn.close()
                return jsonify({"message": "Jugadores convocados", "convocados": convocados}), 200

            elif data.get('crear_partido') is not None:
                jugadores_equipo_1 = data.get('equipo_1', [])
                jugadores_equipo_2 = data.get('equipo_2', [])

                # Validaciones
                repetidos = set(jugadores_equipo_1).intersection(set(jugadores_equipo_2))
                if repetidos:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": f"Jugadores repetidos en ambos equipos: {repetidos}"}), 400

                if len(jugadores_equipo_1) < 1 or len(jugadores_equipo_2) < 1:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Cada equipo debe tener al menos un jugador"}), 400

                if len(jugadores_equipo_1) != len(jugadores_equipo_2):
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Ambos equipos deben tener el mismo número de jugadores"}), 400

                # Crear el partido
                cursor.execute("""
                    INSERT INTO PARTIDO (Idpena, Idt)
                    VALUES (%s, %s)
                    RETURNING Idp
                """, (id_pena, id_temporada))
                id_partido = cursor.fetchone()[0]

                # Crear equipo 1
                cursor.execute("""
                    INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                    VALUES (1, %s, %s, %s)
                """, (id_partido, id_pena, id_temporada))
                # Crear equipo 2
                cursor.execute("""
                    INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                    VALUES (2, %s, %s, %s)
                """, (id_partido, id_pena, id_temporada))

                total_goles_equipo_1 = 0
                total_goles_equipo_2 = 0

                # Registrar stats equipo 1
                for j_id in jugadores_equipo_1:
                    goles = data.get(f'goles_{j_id}_equipo1', 0)
                    asistencias = data.get(f'asistencias_{j_id}_equipo1', 0)
                    val = data.get(f'valoracion_{j_id}_equipo1', 5)
                    total_goles_equipo_1 += goles

                    cursor.execute("""
                        INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                        VALUES (1, %s, %s, %s, %s, %s)
                    """, (id_partido, j_id, goles, asistencias, val))

                # Registrar stats equipo 2
                for j_id in jugadores_equipo_2:
                    goles = data.get(f'goles_{j_id}_equipo2', 0)
                    asistencias = data.get(f'asistencias_{j_id}_equipo2', 0)
                    val = data.get(f'valoracion_{j_id}_equipo2', 5)
                    total_goles_equipo_2 += goles

                    cursor.execute("""
                        INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                        VALUES (2, %s, %s, %s, %s, %s)
                    """, (id_partido, j_id, goles, asistencias, val))

                # Determinar resultado
                resultado_equipo_1 = 0
                resultado_equipo_2 = 0
                if total_goles_equipo_1 > total_goles_equipo_2:
                    resultado_equipo_1 = 1  # victoria
                    resultado_equipo_2 = -1 # derrota
                elif total_goles_equipo_1 < total_goles_equipo_2:
                    resultado_equipo_1 = -1
                    resultado_equipo_2 = 1

                # Actualizar JUGADORTEMPORADA para equipo 1
                for j_id in jugadores_equipo_1:
                    if resultado_equipo_1 == 1:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET VICT = VICT + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))
                    elif resultado_equipo_1 == -1:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET DERR = DERR + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))
                    else:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET EMP = EMP + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))

                # Actualizar JUGADORTEMPORADA para equipo 2
                for j_id in jugadores_equipo_2:
                    if resultado_equipo_2 == 1:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET VICT = VICT + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))
                    elif resultado_equipo_2 == -1:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET DERR = DERR + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))
                    else:
                        cursor.execute("""
                            UPDATE JUGADORTEMPORADA
                            SET EMP = EMP + 1
                            WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                        """, (j_id, id_pena, id_temporada))

                conn.commit()
                cursor.close()
                conn.close()

                session.pop('convocados', None)
                logger.info(f"Partido creado con Idp={id_partido}, temporada={id_temporada}.")
                return jsonify({"message": "Partido creado exitosamente", "id_partido": id_partido}), 201

        # GET: mostrar jugadores disponibles en la temporada
        cursor.execute("""
            SELECT JT.Idjugador, JP.Mote, JP.Posicion
            FROM JUGADORTEMPORADA JT
            JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
            WHERE JT.Idpena = %s AND JT.Idt = %s
        """, (id_pena, id_temporada))
        rows_jugadores = cursor.fetchall()
        jugadores_disponibles = [dict(r) for r in rows_jugadores]

        cursor.close()
        conn.close()

        # Si tenías 'session["convocados"]', lo devolvemos (aunque no es muy REST)
        convocados = session.get('convocados', [])

        return jsonify({
            "temporada": id_temporada,
            "jugadores_disponibles": jugadores_disponibles,
            "convocados": convocados
        }), 200

    except Error as e:
        logger.error(f"Error en draft_partido temporada={id_temporada}: {e}", exc_info=True)
        return jsonify({"error": "Error en el draft de partido"}), 500


# ------------------------------------------------
#  VER ESTADÍSTICAS PARTIDO
# ------------------------------------------------
@admin_bp.route('/ver_estadisticas_partido/<int:id_partido>', methods=['GET'])
@admin_required
def ver_estadisticas_partido(id_partido):
    """
    Devuelve las estadísticas de un partido (si pertenece a la peña actual).
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Info del partido
        cursor.execute("""
            SELECT Idp, Idpena, Idt
            FROM PARTIDO
            WHERE Idp = %s AND Idpena = %s
        """, (id_partido, id_pena))
        partido = cursor.fetchone()
        if not partido:
            cursor.close()
            conn.close()
            return jsonify({"error": "Partido no encontrado"}), 404

        # Estadísticas de jugadores
        cursor.execute("""
            SELECT
                E.Ide AS equipo,
                JP.Mote AS jugador,
                EJ.Goles,
                EJ.Asistencias,
                EJ.Val
            FROM EJUGADOR EJ
            JOIN EQUIPO E ON EJ.Ide = E.Ide
            JOIN JUGADORPENA JP ON EJ.Idjugador = JP.Idjugador AND JP.Idpena = E.Idpena
            WHERE EJ.Idp = %s
            ORDER BY E.Ide, JP.Mote
        """, (id_partido,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        estadisticas = []
        for r in rows:
            estadisticas.append({
                "equipo": r["equipo"],
                "jugador": r["jugador"],
                "goles": r["goles"],
                "asistencias": r["asistencias"],
                "valoracion": r["val"]
            })

        return jsonify({
            "partido": {
                "Idp": partido["idp"],
                "Idpena": partido["idpena"],
                "Idt": partido["idt"]
            },
            "estadisticas": estadisticas
        }), 200

    except Error as e:
        logger.error(f"Error en ver_estadisticas_partido (id_partido={id_partido}): {e}", exc_info=True)
        return jsonify({"error": "Error al ver estadísticas del partido"}), 500


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