from datetime import datetime
from flask import Flask, flash,jsonify, render_template, request, make_response,render_template_string, redirect, url_for,session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import os
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'supersecretkey'
Admin=False

db_path = os.path.join('', 'Gestion_Penas.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
    return conn

# Ruta de prueba
@app.route('/', methods=['GET'])
def ping():
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
            return redirect(url_for('registration_pena'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('El nombre de usuario ya existe. Por favor, elige otro.')
            return redirect(url_for('registration_pena'))

        # Insertar en la tabla de peñas
        cursor.execute("INSERT INTO PENA (nombre) VALUES (?)", (nombre_peña,))
        id_peña = cursor.lastrowid  # Obtener el ID de la nueva peña

        # Insertar en la tabla de administradores con Idpena
        cursor.execute("INSERT INTO admins (username, password, Idpena) VALUES (?, ?, ?)",
                       (username, generate_password_hash(password), id_peña))

        flash('Admin registrado exitosamente. Ahora puedes iniciar sesión.')
        conn.commit()
        conn.close()
        return redirect(url_for('login'))  # Redirigir al login después del registro

    return render_template('registration_pena.html')  # Cargar el formulario de registro de peña

@app.route('/registration_jugador', methods=['GET', 'POST'])
def registration_jugador():
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
            return redirect(url_for('registration_jugador'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar en la tabla de jugadores
        cursor.execute("INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (?, ?, ?)",
                       (username, '', nacionalidad))  # Puedes personalizar Apellidos
        id_jugador = cursor.lastrowid  # Obtener el ID del nuevo jugador

        # Insertar en la tabla JUGADORPENA
        cursor.execute("INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (?, ?, ?, ?)",
                       (id_jugador, id_peña, mote, posicion))

        flash('Jugador registrado exitosamente. Ahora puedes iniciar sesión.')
        conn.commit()
        conn.close()
        return redirect(url_for('login'))  # Redirigir al login después del registro

    return render_template('registration_jugador.html')  # Cargar el formulario de registro de jugador
# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Conectar a la base de datos y buscar el usuario
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        # Convertir el objeto Row en un diccionario
        if user:
            user = dict(user)
        else:
            user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
            if user:
                user = dict(user)
                Admin=True
        
        conn.close()
        # Verificar si el usuario existe y la contraseña es correcta
        if user and check_password_hash(user['password'], password):
           
            
            if(Admin==True):
                session['username'] = user['username']
                session['name'] = user['username'] 
                session['Idpena']=user['Idpena']
                return redirect(url_for('admin_dashboard'))
            
            else:
                session['username'] = user['username']
                session['name'] = user['name'] 
                session['Idjugador'] = user['Idjugador']
                flash('Usuario no es admin funcionalidad aun no implementada.')
                return redirect(url_for('login'))
            
        else:
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.')
            return redirect(url_for('login'))
    
    return render_template('login.html')
# Ruta para el dashboard (página principal del usuario)
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session:
        # Si no hay sesión iniciada, redirigir al login
        flash('Por favor, inicia sesión primero.')
        return redirect(url_for('login'))
    
    # Puedes utilizar los datos del usuario almacenados en la sesión
    username = session.get('username')
    return render_template('admin_dashboard.html', username=username)
    
# Gestión de jugadores
@app.route('/admin/gestionar_jugadores')
def gestionar_jugadores():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    # Aquí puedes obtener los datos de jugadores desde la base de datos
    conn = get_db_connection()
    id=session['Idpena']
    jugadores = conn.execute('SELECT * FROM JUGADORPENA WHERE idpena = ?', (id,)).fetchall()
    conn.close()
    
    return render_template('gestionar_jugadores.html', jugadores=jugadores)

# Gestión de partidos
@app.route('/admin/gestionar_partidos')
def gestionar_partidos():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    # Aquí puedes obtener los datos de los partidos desde la base de datos
    conn = get_db_connection()
    partidos = conn.execute('SELECT * FROM partidos').fetchall()
    conn.close()

    return render_template('gestionar_partidos.html', partidos=partidos)

# Ruta para añadir jugador
@app.route('/admin/gestionar_jugadores/añadir_jugador', methods=['GET', 'POST'])
def añadir_jugador():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']
        
        # Insertar en la tabla JUGADOR y luego en JUGADORPENA
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES (?, ?, ?)",
                       (nombre, apellidos, nacionalidad))
        
        # Obtener el Idjugador recién insertado
        id_jugador = cursor.lastrowid
        id_pena = session['Idpena']
        
        cursor.execute("INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (?, ?, ?, ?)",
                       (id_jugador, id_pena, mote, posicion))
        
        conn.commit()
        conn.close()
        
        flash('Jugador añadido exitosamente.')
        return redirect(url_for('gestionar_jugadores'))
    
    return render_template('añadir_jugador.html')

@app.route('/admin/gestionar_jugadores/editar/<int:jugador_id>', methods=['GET', 'POST'])
def editar_jugador(jugador_id):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Si el formulario ha sido enviado, actualizar el jugador en la base de datos
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        nacionalidad = request.form['nacionalidad']
        mote = request.form['mote']
        posicion = request.form['posicion']

        # Actualizar los datos del jugador
        conn.execute("""
            UPDATE JUGADOR
            SET Nombre = ?, Apellidos = ?, Nacionalidad = ?
            WHERE Idjugador = ?
        """, (nombre, apellidos, nacionalidad, jugador_id))
        
        # Actualizar los datos en la tabla JUGADORPENA
        conn.execute("""
            UPDATE JUGADORPENA
            SET Mote = ?, Posicion = ?
            WHERE Idjugador = ? AND Idpena = ?
        """, (mote, posicion, jugador_id, session['Idpena']))
        
        conn.commit()
        conn.close()
        
        flash('Jugador actualizado correctamente.')
        return redirect(url_for('gestionar_jugadores'))

    # Obtener los datos actuales del jugador
    jugador = conn.execute("""
        SELECT JUGADOR.*, JUGADORPENA.Mote, JUGADORPENA.Posicion
        FROM JUGADOR
        JOIN JUGADORPENA ON JUGADOR.Idjugador = JUGADORPENA.Idjugador
        WHERE JUGADOR.Idjugador = ? AND JUGADORPENA.Idpena = ?
    """, (jugador_id, session['Idpena'])).fetchone()

    conn.close()

    if jugador is None:
        flash('Jugador no encontrado.')
        return redirect(url_for('gestionar_jugadores'))

    return render_template('editar_jugador.html', jugador=jugador)

@app.route('/admin/gestionar_jugadores/eliminar/<int:jugador_id>', methods=['POST'])
def eliminar_jugador(jugador_id):
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    # Eliminar el jugador de ambas tablas
    conn.execute("DELETE FROM JUGADORPENA WHERE Idjugador = ? AND Idpena = ?", (jugador_id, session['Idpena']))
    conn.execute("DELETE FROM JUGADOR WHERE Idjugador = ?", (jugador_id,))
    
    conn.commit()
    conn.close()
    
    flash('Jugador eliminado correctamente.')
    return redirect(url_for('gestionar_jugadores'))


@app.route('/admin/gestionar_temporadas', methods=['GET'])
def gestionar_temporadas():
    if 'Idpena' not in session:
        flash('Por favor, inicia sesión como administrador.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Obtener todas las temporadas asociadas a la peña del administrador
    temporadas = conn.execute("""
        SELECT * FROM TEMPORADA
        WHERE Idpena = ?
        ORDER BY Idt DESC
    """, (session['Idpena'],)).fetchall()
    conn.close()

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
    # Eliminar la temporada asociada a la peña
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
            J.Nombre,
            JT.VICT,
            JT.EMP,
            JT.DERR,
            (JT.VICT * 3 + JT.EMP * 2 + JT.DERR * 1) AS Puntos,
            ROUND(CAST(JT.VICT AS FLOAT) / NULLIF(JT.VICT + JT.EMP + JT.DERR, 0) * 100, 2) AS Porcentaje_victorias
        FROM JUGADORTEMPORADA JT
        JOIN JUGADOR J ON JT.Idjugador = J.Idjugador
        WHERE JT.Idt = ? AND JT.Idpena = ?
        ORDER BY Puntos DESC, Porcentaje_victorias DESC
    """, (id_temporada, session['Idpena'])).fetchall()

    # Lista de partidos
    partidos = conn.execute("""
        SELECT Idp, Idpena, Idt
        FROM PARTIDO
        WHERE Idt = ? AND Idpena = ?
        ORDER BY Idp ASC
    """, (id_temporada, session['Idpena'])).fetchall()

    # Jugadores disponibles para añadir a la temporada
    jugadores_disponibles = conn.execute("""
        SELECT JP.Idjugador, J.Nombre
        FROM JUGADORPENA JP
        JOIN JUGADOR J ON JP.Idjugador = J.Idjugador
        WHERE JP.Idpena = ?
        AND JP.Idjugador NOT IN (
            SELECT Idjugador
            FROM JUGADORTEMPORADA
            WHERE Idt = ? AND Idpena = ?
        )
    """, (session['Idpena'], id_temporada, session['Idpena'])).fetchall()

    conn.close()

    return render_template('visualizar_temporada.html', temporada=temporada, jugadores=jugadores, partidos=partidos, jugadores_disponibles=jugadores_disponibles)

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
        # Crear el partido
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PARTIDO (Idpena, Idt)
            VALUES (?, ?)
        """, (session['Idpena'], id_temporada))
        id_partido = cursor.lastrowid

        # Crear equipos para el partido
        cursor.execute("""
            INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
            VALUES (1, ?, ?, ?)
        """, (id_partido, session['Idpena'], id_temporada))
        cursor.execute("""
            INSERT INTO EQUIPO (Ide, Idp, Idpena, Idt)
            VALUES (2, ?, ?, ?)
        """, (id_partido, session['Idpena'], id_temporada))

        # Asignar jugadores a los equipos
        jugadores_equipo_1 = request.form.getlist('equipo_1')
        jugadores_equipo_2 = request.form.getlist('equipo_2')

        for jugador_id in jugadores_equipo_1:
            cursor.execute("""
                INSERT INTO EJUGADOR (Ide, Idp, Idjugador)
                VALUES (1, ?, ?)
            """, (id_partido, jugador_id))

        for jugador_id in jugadores_equipo_2:
            cursor.execute("""
                INSERT INTO EJUGADOR (Ide, Idp, Idjugador)
                VALUES (2, ?, ?)
            """, (id_partido, jugador_id))

        conn.commit()
        conn.close()
        flash('Partido creado y jugadores asignados con éxito.')
        return redirect(url_for('gestionar_partidos'))

    # Obtener jugadores disponibles para asignar a equipos
    jugadores_disponibles = conn.execute("""
        SELECT JT.Idjugador, J.Nombre
        FROM JUGADORTEMPORADA JT
        JOIN JUGADOR J ON JT.Idjugador = J.Idjugador
        WHERE JT.Idpena = ? AND JT.Idt = ?
    """, (session['Idpena'], id_temporada)).fetchall()

    conn.close()

    return render_template('draft_partido.html', temporada=temporada, jugadores_disponibles=jugadores_disponibles)
# Manejo de errores personalizados
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "No encontrado"}), 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)


    