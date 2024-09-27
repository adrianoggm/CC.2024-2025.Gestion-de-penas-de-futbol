from flask import Flask, flash,jsonify, render_template, request, make_response,render_template_string, redirect, url_for
from users import users 
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('Gestion_Penas.db')
    conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
    return conn

# Ruta de prueba
@app.route('/', methods=['GET'])
def ping():
    return jsonify({"response": "Hello world"})

# Ruta para mostrar todos los usuarios (solo como referencia)
@app.route('/users')
def usersHandler():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Conectar a la base de datos y buscar el usuario
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        print(user[0])
        print(user[1])
        # Convertir el objeto Row en un diccionario
        if user:
            user = dict(user)
        print(user['password'],password)
        # Verificar si el usuario existe y la contraseña es correcta
        if user and check_password_hash(user['password'], password):
            print("entras")
            return f"¡Bienvenido, {user['name']}!"
        else:
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Manejo de errores personalizados
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "No encontrado"}), 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

