import pytest
import json
from app import app, get_db_connection
import sqlite3
import pytest
import json
from app import app, get_db_connection
import sqlite3
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'  # Usar base de datos en memoria para pruebas
    with app.test_client() as client:
        yield client

@pytest.fixture
def init_db():
    # Crea una conexión a una base de datos temporal en memoria
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    
    # Aquí se crean las tablas necesarias para las pruebas
    c.execute(""" CREATE TABLE IF NOT EXISTS PENA (
        Idpena INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT,
        Admin TEXT 
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS JUGADOR (
        Idjugador INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT,
        Apellidos TEXT,
        Nacionalidad TEXT
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS JUGADORPENA (
        Idjugador INTEGER,
        Idpena INTEGER,
        Mote TEXT,
        Posicion TEXT,
        PRIMARY KEY (Idjugador, Idpena),
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS TEMPORADA (
        Idt INTEGER PRIMARY KEY AUTOINCREMENT,
        Fecha TEXT
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS JUGADORTEMPORADA (
        Idjugador INTEGER,
        Idpena INTEGER,
        Idt INTEGER,
        VICT INTEGER DEFAULT 0,
        DERR INTEGER DEFAULT 0,
        EMP INTEGER DEFAULT 0,
        Calidad REAL DEFAULT 5 CHECK(Calidad BETWEEN 0 AND 10),
        PRIMARY KEY (Idjugador, Idpena, Idt),
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS PARTIDO (
        Idp INTEGER,
        Idpena INTEGER,
        Idt INTEGER,
        PRIMARY KEY (Idp, Idpena, Idt),
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS EQUIPO (
        Ide INTEGER,
        Idp INTEGER,
        Idpena INTEGER,
        Idt INTEGER,
        PRIMARY KEY (Ide, Idp, Idpena, Idt),
        FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS EJUGADOR (
        Ide INTEGER,
        Idp INTEGER,
        Idjugador INTEGER,
        Goles INTEGER DEFAULT 0,
        Asistencias INTEGER DEFAULT 0,
        Val REAL DEFAULT 5 CHECK(Val BETWEEN 0 AND 10),
        PRIMARY KEY (Ide, Idp, Idjugador),
        FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Ide) REFERENCES EQUIPO(Ide) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        Idjugador INTEGER,
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS admins (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        Idpena TEXT,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    
    conn.commit()  # Asegúrate de guardar los cambios
    app.config['DATABASE'] = conn  # Conectar la aplicación a esta base de datos temporal

    yield  # Aquí se ejecutan las pruebas

    conn.close()  # Cierra la conexión después de las pruebas

def test_ping(client):
    """Prueba la ruta de inicio."""
    response = client.get('/')
    assert response.status_code == 200  # Asegúrate de que la página se carga correctamente
    assert 'Inicia Sesión o Regístrate' in response.get_data(as_text=True)  # Verifica que el texto está presente
    assert 'inicia sesión' in response.get_data(as_text=True)  # Verifica que el enlace de inicio de sesión está presente
    assert 'Regístrate aquí' in response.get_data(as_text=True)  # Verifica que el enlace de registro está presente

def test_registration_admin(client, init_db):
    """Prueba el registro de un administrador de peña."""
    response = client.post('/registration_pena', data={
        'user_type': 'admin',
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    assert response.status_code == 302  # Debe redirigir
    assert 'Usuario o contraseña incorrectos' not in response.get_data(as_text=True)

def test_registration_jugador(client, init_db):
    """Prueba el registro de un jugador."""
    # Primero, se necesita registrar un admin para que un jugador pueda registrarse
  
    
    # Ahora registrar un jugador
    response = client.post('/registration_jugador', data={
        'user_type': 'jugador',
        'username': 'testjugador',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'id_peña': 1,  # ID de la peña a la que se unirá el jugador
        'mote': 'Jugadore',
        'posicion': 'Delantero',
        'nacionalidad': 'Española'
    })
    assert response.status_code == 302  # Debe redirigir
    assert 'Usuario o contraseña incorrectos' not in response.get_data(as_text=True)

def test_login(client, init_db):
    """Prueba el inicio de sesión."""
    client.post('/registration', data={'user_type': 'admin', 'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass', 'nombre_peña': 'Peña Test'})
    response = client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})
    assert response.status_code == 302  # Debe redirigir al dashboard
    assert 'Por favor, inicia sesión primero.' not in response.get_data(as_text=True)

def test_gestionar_jugadores(client, init_db):
    """Prueba la gestión de jugadores."""
    client.post('/registration', data={'user_type': 'admin', 'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass', 'nombre_peña': 'Peña Test'})
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
    assert 'Juan' in response.get_data(as_text=True)  # Comprobar que el jugador se muestra

def test_eliminar_jugador(client, init_db):
    """Prueba la eliminación de un jugador."""
    client.post('/registration', data={'user_type': 'admin', 'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass', 'nombre_peña': 'Peña Test'})
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
    assert 'Carlos' not in response.get_data(as_text=True)

def test_editar_jugador(client, init_db):
    """Prueba la edición de un jugador."""
    client.post('/registration', data={'user_type': 'admin', 'username': 'testadmin', 'password': 'testpass', 'confirm_password': 'testpass', 'nombre_peña': 'Peña Test'})
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
    response = client.post('/admin/gestionar_jugadores/editar/4', data={
        'nombre': 'Andrés',
        'apellidos': 'Fernández',
        'nacionalidad': 'Española',
        'mote': 'Andresito Modificado',
        'posicion': 'Portero'
    })
    assert response.status_code == 302  # Debe redirigir después de editar

    # Verificar que los cambios se reflejan
    response = client.get('/admin/gestionar_jugadores')
    assert 'Andresito Modificado' in response.get_data(as_text=True)  # Comprobar que el jugador editado se muestra