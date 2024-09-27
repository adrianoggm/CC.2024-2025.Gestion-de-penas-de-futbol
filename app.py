from flask import Flask, flash,jsonify, render_template, request, make_response,render_template_string, redirect, url_for
from users import users 

app =Flask(__name__)
app.secret_key = 'supersecretkey'
@app.route('/',methods=['GET'])

def ping():
    return jsonify({"response ":"Hello world"})

@app.route('/users')
def usersHandler():
     return jsonify({"users ":users})

# Formulario de login HTML como plantilla dentro del código

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    
    if request.method == 'POST':
        # Recibir las credenciales del formulario (formulario POST)
        username = request.form.get('username')
        password = request.form.get('password')

        # Verificar si el usuario existe y si la contraseña es correcta
        if username in users and users[username]["password"] == password:
            # Redirigir al usuario a una página de éxito después del login
            return f"¡Bienvenido, {users[username]['name']}!"
        else:
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.')
            return redirect(url_for('login'))
    return render_template('login.html')


# Manejo de errores personalizados
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "No encontrado"}), 404)

if __name__=='__main__':
    app.run(host='0.0.0.0',port=4000,debug=True)

