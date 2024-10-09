from flask import Flask, flash,jsonify, render_template, request, make_response,render_template_string, redirect, url_for,session
from users import users 
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
Admin=False
def get_db_connection():
    conn = sqlite3.connect('Gestion_Penas.db')
    conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
    return conn

# Ruta de prueba
@app.route('/', methods=['GET'])
def ping():
    return render_template('index.html')

# Registro
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Aquí iría la lógica para manejar el registro
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validaciones y lógica de registro aquí

        return redirect(url_for('login'))  # Redirigir al login después del registro
   
    return render_template('registration.html')
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
# Manejo de errores personalizados
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "No encontrado"}), 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)


    