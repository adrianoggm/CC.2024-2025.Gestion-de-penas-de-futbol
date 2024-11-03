import pytest
import json
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'Gestion_Penas.db'  # Asegúrate de que esta sea la ruta correcta
    with app.test_client() as client:
        yield client

@pytest.fixture
def init_db():
    # Inicializa la base de datos para las pruebas
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS admins (username TEXT PRIMARY KEY, password TEXT, Idpena INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS JUGADOR (Idjugador INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Apellidos TEXT, Nacionalidad TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS JUGADORPENA (Idjugador INTEGER, Idpena INTEGER, Mote TEXT, Posicion TEXT, PRIMARY KEY (Idjugador, Idpena))')
    conn.commit()
    conn.close()

def test_ping(client):
    """Prueba la ruta de inicio."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gestionar Jugadores' in response.data

def test_registration(client, init_db):
    """Prueba el registro de usuarios."""
    response = client.post('/registration', data={'username': 'testuser', 'password': 'testpass', 'confirm_password': 'testpass'})
    assert response.status_code == 302  # Debe redirigir
    assert b'Usuario o contraseña incorrectos' not in response.data

def test_login(client, init_db):
    """Prueba el inicio de sesión."""
    client.post('/registration', data={'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass'})
    response = client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})
    assert response.status_code == 302  # Debe redirigir al dashboard
    assert b'Por favor, inicia sesión primero.' not in response.data

def test_gestionar_jugadores(client, init_db):
    """Prueba la gestión de jugadores."""
    client.post('/registration', data={'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass'})
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})
    
    # Añadir un jugador para probar la gestión
    client.post('/admin/gestionar_jugadores/añadir_jugador', data={
        'nombre': 'Juan',
        'apellidos': 'Pérez',
        'nacionalidad': 'Española',
        'mote': 'Juanito',
        'posicion': 'Delantero'
    })
    
    response = client.get('/admin/gestionar_jugadores')
    assert response.status_code == 200
    assert b'Juan' in response.data  # Comprobar que el jugador se muestra

def test_eliminar_jugador(client, init_db):
    """Prueba la eliminación de un jugador."""
    client.post('/registration', data={'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass'})
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})
    
    # Añadir un jugador para eliminar
    client.post('/admin/gestionar_jugadores/añadir_jugador', data={
        'nombre': 'Carlos',
        'apellidos': 'Gómez',
        'nacionalidad': 'Española',
        'mote': 'Carlitos',
        'posicion': 'Defensa'
    })

    # Ahora eliminar el jugador
    response = client.post('/admin/gestionar_jugadores/eliminar/1')  # Cambia el ID según sea necesario
    assert response.status_code == 302  # Debe redirigir después de eliminar

    # Verificar que el jugador ha sido eliminado
    response = client.get('/admin/gestionar_jugadores')
    assert b'Carlos' not in response.data

def test_editar_jugador(client, init_db):
    """Prueba la edición de un jugador."""
    client.post('/registration', data={'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass'})
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})

    # Añadir un jugador para editar
    client.post('/admin/gestionar_jugadores/añadir_jugador', data={
        'nombre': 'Andrés',
        'apellidos': 'Fernández',
        'nacionalidad': 'Española',
        'mote': 'Andresito',
        'posicion': 'Portero'
    })

    # Editar el jugador
    response = client.post('/admin/gestionar_jugadores/editar/1', data={
        'nombre': 'Andrés',
        'apellidos': 'Fernández',
        'nacionalidad': 'Española',
        'mote': 'Andresito Modificado',
        'posicion': 'Portero'
    })
    assert response.status_code == 302  # Debe redirigir después de editar

    # Verificar que los cambios se reflejan
    response = client.get('/admin/gestionar_jugadores')
    assert b'Andresito Modificado' in response.data  # Comprobar que el jugador editado se muestra