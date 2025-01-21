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
    Retorna 401 en caso de no tener esa sesión.
    """
    def wrapper(*args, **kwargs):
        if 'Idpena' not in session:
            logger.warning("Intento de acceso sin tener sesión de admin.")
            return jsonify({"error": "No autorizado. Inicia sesión como administrador."}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# -----------------------------------------
# GESTIONAR JUGADORES
# -----------------------------------------
@admin_bp.route('/gestionar_jugadores', methods=['GET'])
@admin_required
def gestionar_jugadores():
    """
    Devuelve la lista de jugadores asociados a la peña del admin en sesión.
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM JUGADORPENA WHERE Idpena = %s", (id_pena,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        jugadores = [dict(r) for r in rows]
        logger.info(f"Obtenidos {len(jugadores)} jugadores para la peña {id_pena}.")
        return jsonify({"jugadores": jugadores}), 200
    except Error as e:
        logger.error(f"Error al obtener jugadores para la peña {id_pena}: {e}", exc_info=True)
        return jsonify({"error": "Error al obtener jugadores"}), 500


@admin_bp.route('/gestionar_jugadores/añadir_jugador', methods=['POST'])
@admin_required
def añadir_jugador():
    """
    Crea un nuevo jugador en JUGADOR y lo asocia a la peña (JUGADORPENA).
    JSON esperado:
    {
        "nombre": "Juan",
        "apellidos": "Pérez",
        "nacionalidad": "Española",
        "mote": "Juanito",
        "posicion": "Delantero"
    }
    """
    id_pena = session['Idpena']
    data = request.get_json() or {}

    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    nacionalidad = data.get('nacionalidad')
    mote = data.get('mote')
    posicion = data.get('posicion')

    if not all([nombre, apellidos, nacionalidad, mote, posicion]):
        return jsonify({"error": "Faltan datos para crear el jugador"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insertar en JUGADOR
        cursor.execute(
            "INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (%s, %s, %s) RETURNING Idjugador",
            (nombre, apellidos, nacionalidad)
        )
        id_jugador = cursor.fetchone()[0]

        # Asociar al jugador en JUGADORPENA
        cursor.execute(
            "INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (%s, %s, %s, %s)",
            (id_jugador, id_pena, mote, posicion)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Jugador '{nombre}' (ID={id_jugador}) añadido a la peña {id_pena}.")
        return jsonify({"message": "Jugador añadido", "id_jugador": id_jugador}), 201

    except Error as e:
        logger.error(f"Error al añadir jugador: {e}", exc_info=True)
        return jsonify({"error": "Error al añadir jugador"}), 500


@admin_bp.route('/gestionar_jugadores/eliminar/<int:jugador_id>', methods=['DELETE'])
@admin_required
def eliminar_jugador(jugador_id):
    """
    Elimina un jugador de JUGADORPENA y JUGADOR.
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Eliminar de JUGADORPENA
        cursor.execute(
            "DELETE FROM JUGADORPENA WHERE Idjugador = %s AND Idpena = %s",
            (jugador_id, id_pena)
        )
        # Eliminar de JUGADOR
        cursor.execute(
            "DELETE FROM JUGADOR WHERE Idjugador = %s",
            (jugador_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Jugador ID={jugador_id} eliminado correctamente de la peña {id_pena}.")
        return jsonify({"message": "Jugador eliminado"}), 200
    except Error as e:
        logger.error(f"Error al eliminar el jugador ID={jugador_id}: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar el jugador"}), 500


@admin_bp.route('/gestionar_jugadores/editar/<int:jugador_id>', methods=['PUT', 'PATCH'])
@admin_required
def editar_jugador(jugador_id):
    """
    Edita un jugador (campos de JUGADOR y JUGADORPENA).
    JSON esperado:
    {
        "nombre": "Andrés",
        "apellidos": "Fernández",
        "nacionalidad": "Española",
        "mote": "Andresito Modificado",
        "posicion": "Portero"
    }
    """
    data = request.get_json() or {}
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    nacionalidad = data.get('nacionalidad')
    mote = data.get('mote')
    posicion = data.get('posicion')

    if not all([nombre, apellidos, nacionalidad, mote, posicion]):
        return jsonify({"error": "Faltan campos para editar el jugador"}), 400

    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Actualizar JUGADOR
        cursor.execute("""
            UPDATE JUGADOR
            SET Nombre = %s, Apellidos = %s, Nacionalidad = %s
            WHERE Idjugador = %s
        """, (nombre, apellidos, nacionalidad, jugador_id))

        # Actualizar JUGADORPENA
        cursor.execute("""
            UPDATE JUGADORPENA
            SET Mote = %s, Posicion = %s
            WHERE Idjugador = %s AND Idpena = %s
        """, (mote, posicion, jugador_id, id_pena))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Jugador ID={jugador_id} editado correctamente.")
        return jsonify({"message": "Jugador actualizado"}), 200

    except Error as e:
        logger.error(f"Error al actualizar jugador {jugador_id}: {e}", exc_info=True)
        return jsonify({"error": "Error al actualizar jugador"}), 500


# -----------------------------------------
# GESTIONAR PARTIDOS
# -----------------------------------------
@admin_bp.route('/gestionar_partidos', methods=['GET'])
@admin_required
def gestionar_partidos():
    """
    Devuelve la lista de partidos (podrías filtrar por Idpena si quieres).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Opcional: filtra con: WHERE Idpena = session['Idpena']
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


@admin_bp.route('/ver_estadisticas_partido/<int:id_partido>', methods=['GET'])
@admin_required
def ver_estadisticas_partido(id_partido):
    """
    Devuelve estadísticas de un partido (EJUGADOR, goles, asistencias, etc.).
    Solo si el partido pertenece a la peña en sesión.
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Comprobar que el partido pertenece a la peña
        cursor.execute("""
            SELECT Idp, Idpena, Idt
            FROM PARTIDO
            WHERE Idp = %s AND Idpena = %s
        """, (id_partido, id_pena))
        partido = cursor.fetchone()
        if not partido:
            cursor.close()
            conn.close()
            return jsonify({"error": "Partido no encontrado o no pertenece a esta peña"}), 404

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


# -----------------------------------------
# GESTIONAR TEMPORADAS
# -----------------------------------------
@admin_bp.route('/gestionar_temporadas', methods=['GET'])
@admin_required
def gestionar_temporadas():
    """
    Devuelve la lista de temporadas para la peña del admin.
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT *
            FROM TEMPORADA
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
        return jsonify({"error": "Error al recuperar las temporadas"}), 500


@admin_bp.route('/gestionar_temporadas/añadir', methods=['POST'])
@admin_required
def añadir_temporada():
    """
    Crea una nueva temporada para la peña.
    JSON esperado:
    {
        "fechaini": "2023-01-01",
        "fechafin": "2023-12-31"
    }
    """
    id_pena = session['Idpena']
    data = request.get_json() or {}
    fechaini = data.get('fechaini')
    fechafin = data.get('fechafin')

    if not fechaini or not fechafin:
        return jsonify({"error": "Faltan fechaini o fechafin"}), 400
    if fechaini >= fechafin:
        return jsonify({"error": "La fecha de inicio debe ser anterior a la fecha de fin"}), 400

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

        logger.info(f"Temporada añadida exitosamente (ID={id_temporada}).")
        return jsonify({"message": "Temporada añadida", "id_temporada": id_temporada}), 201
    except Error as e:
        logger.error(f"Error al añadir temporada: {e}", exc_info=True)
        return jsonify({"error": "Error al añadir la temporada"}), 500


@admin_bp.route('/gestionar_temporadas/eliminar/<int:id_temporada>', methods=['DELETE'])
@admin_required
def eliminar_temporada(id_temporada):
    """
    Elimina una temporada de la peña.
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


# -----------------------------------------
# VISUALIZAR TEMPORADA (detalle jugadores, partidos...)
# -----------------------------------------
@admin_bp.route('/visualizar_temporada/<int:id_temporada>', methods=['GET', 'POST'])
@admin_required
def visualizar_temporada(id_temporada):
    """
    GET: Retorna info detallada de la temporada (clasificación, partidos, etc.).
    POST: Añade un jugador a la temporada.
          JSON = {"jugador_id": 123}
    """
    id_pena = session['Idpena']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Verificar temporada
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
                # ¿Jugador ya en la temporada?
                cursor.execute("""
                    SELECT 1 FROM JUGADORTEMPORADA
                    WHERE Idjugador = %s AND Idpena = %s AND Idt = %s
                """, (jugador_id, id_pena, id_temporada))
                existe = cursor.fetchone()
                if existe:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Jugador ya asociado a esta temporada"}), 400
                else:
                    cursor.execute("""
                        INSERT INTO JUGADORTEMPORADA (Idjugador, Idpena, Idt)
                        VALUES (%s, %s, %s)
                    """, (jugador_id, id_pena, id_temporada))
                    conn.commit()

        # Clasificación de jugadores
        cursor.execute("""
            SELECT
                J.Idjugador,
                JP.Mote,
                JT.VICT,
                JT.EMP,
                JT.DERR,
                (JT.VICT * 3 + JT.EMP * 2 + JT.DERR * 1) AS Puntos,
                ROUND(
                    CAST(JT.VICT AS FLOAT)
                    / NULLIF(JT.VICT + JT.EMP + JT.DERR, 0) * 100,
                    2
                ) AS Porcentaje_victorias
            FROM JUGADORTEMPORADA JT
            JOIN JUGADORPENA JP ON JT.Idjugador = JP.Idjugador AND JT.Idpena = JP.Idpena
            JOIN JUGADOR J ON JP.Idjugador = J.Idjugador
            WHERE JT.Idt = %s AND JT.Idpena = %s
            ORDER BY Puntos DESC, Porcentaje_victorias DESC
        """, (id_temporada, id_pena))
        rows_clasif = cursor.fetchall()
        jugadores_clasif = [dict(r) for r in rows_clasif]

        # Partidos
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
        rows_stats = cursor.fetchall()
        estadisticas_jugadores = [dict(r) for r in rows_stats]

        # Mezclar estadísticas
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
        """, (id_pena, id_temporada, id_pena))
        rows_disponibles = cursor.fetchall()
        jugadores_disponibles = [dict(r) for r in rows_disponibles]

        cursor.close()
        conn.close()

        temporada_json = {
            "Idt": temporada["idt"],
            "Fechaini": str(temporada["fechaini"]),
            "Fechafin": str(temporada["fechafin"])
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


# -----------------------------------------
# DRAFT DE PARTIDO
# -----------------------------------------
@admin_bp.route('/draft_partido/<int:id_temporada>', methods=['GET', 'POST'])
@admin_required
def draft_partido(id_temporada):
    """
    GET: Retorna los jugadores disponibles en la temporada (lista de JUGADORTEMPORADA).
    POST: 
      - Si incluye "convocar", guarda la lista de convocados en session['convocados'] (no muy REST, pero ejemplo).
      - Si incluye "crear_partido", crea un partido con dos equipos y sus estadísticas.
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
            if 'convocar' in data:
                convocados = data['convocar']
                session['convocados'] = convocados
                logger.info(f"{len(convocados)} jugadores convocados.")
                cursor.close()
                conn.close()
                return jsonify({"message": "Jugadores convocados", "convocados": convocados}), 200

            elif 'crear_partido' in data:
                equipo_1 = data.get('equipo_1', [])
                equipo_2 = data.get('equipo_2', [])

                # Validaciones...
                repetidos = set(equipo_1).intersection(set(equipo_2))
                if repetidos:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": f"Jugadores repetidos en ambos equipos: {repetidos}"}), 400

                if len(equipo_1) < 1 or len(equipo_2) < 1:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Cada equipo debe tener al menos un jugador"}), 400

                if len(equipo_1) != len(equipo_2):
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

                # Crear equipo 1 y equipo 2
                cursor.execute("""
                    INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                    VALUES (1, %s, %s, %s)
                """, (id_partido, id_pena, id_temporada))
                cursor.execute("""
                    INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
                    VALUES (2, %s, %s, %s)
                """, (id_partido, id_pena, id_temporada))

                total_goles_equipo_1 = 0
                total_goles_equipo_2 = 0

                # Registrar stats de equipo_1
                for j_id in equipo_1:
                    goles = data.get(f'goles_{j_id}_equipo1', 0)
                    asistencias = data.get(f'asistencias_{j_id}_equipo1', 0)
                    val = data.get(f'valoracion_{j_id}_equipo1', 5)
                    total_goles_equipo_1 += goles

                    cursor.execute("""
                        INSERT INTO EJUGADOR (Ide, Idp, Idjugador, Goles, Asistencias, Val)
                        VALUES (1, %s, %s, %s, %s, %s)
                    """, (id_partido, j_id, goles, asistencias, val))

                # Registrar stats de equipo_2
                for j_id in equipo_2:
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
                    resultado_equipo_2 = -1
                elif total_goles_equipo_1 < total_goles_equipo_2:
                    resultado_equipo_1 = -1
                    resultado_equipo_2 = 1

                # Actualizar JUGADORTEMPORADA
                for j_id in equipo_1:
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

                for j_id in equipo_2:
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

        # GET: listar jugadores disponibles en la temporada
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

        convocados = session.get('convocados', [])
        return jsonify({
            "temporada": id_temporada,
            "jugadores_disponibles": jugadores_disponibles,
            "convocados": convocados
        }), 200

    except Error as e:
        logger.error(f"Error en draft_partido (temporada={id_temporada}): {e}", exc_info=True)
        return jsonify({"error": "Error en el draft de partido"}), 500

@admin_bp.route('/debug/ver_bd', methods=['GET'])
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
