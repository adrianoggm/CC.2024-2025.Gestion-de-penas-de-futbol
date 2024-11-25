
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from src.app import app
import sqlite3
import pytest
import json

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
    c.execute(""" CREATE TABLE IF NOT EXISTS PENA(
            Idpena INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT,
            Admin  TEXT 
            )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS JUGADOR(
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
            PRIMARY KEY (Idjugador,Idpena),
            FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE
            )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS TEMPORADA (
        Idpena INTEGER,
        Idt INTEGER PRIMARY KEY AUTOINCREMENT,
        Fechaini DATE,
        Fechafin DATE,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS JUGADORTEMPORADA (
            Idjugador INTEGER,
            Idpena INTEGER,
            Idt INTEGER,
            VICT INTEGER DEFAULT 0,
            DERR INTEGER DEFAULT 0,
            EMP INTEGER DEFAULT 0,
            Calidad REAL DEFAULT 5 CHECK(Calidad BETWEEN 0 AND 10),
            PRIMARY KEY (Idjugador,Idpena,Idt),
            FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS PARTIDO (
        Idp INTEGER PRIMARY KEY AUTOINCREMENT,
        Idpena INTEGER,
        Idt INTEGER,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS EQUIPO (
        Ide INTEGER PRIMARY KEY AUTOINCREMENT,
        Idp INTEGER,
        Idpena INTEGER,
        Idt INTEGER,
        FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    c.execute(""" CREATE TABLE IF NOT EXISTS EJUGADOR (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Ide INTEGER,
        Idp INTEGER,
        Idjugador INTEGER,
        Goles INTEGER DEFAULT 0,
        Asistencias INTEGER DEFAULT 0,
        Val REAL DEFAULT 5 CHECK(Val BETWEEN 0 AND 10),
        FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Ide) REFERENCES EQUIPO(Ide) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    #c.execute("DELETE FROM users WHERE username = ?", ('adrianoggm',))
    c.execute(""" CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,         -- Nombre de usuario único
        password TEXT NOT NULL,                -- Contraseña almacenada como hash
        name TEXT NOT NULL,                     -- Nombre del usuario
        Idjugador INTEGER,                      
        FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    #c.execute("DELETE FROM admins WHERE username = ?", ('Genadmin',))
    #c.execute("DROP TABLE  admins ")
    c.execute(""" CREATE TABLE IF NOT EXISTS admins (
        username TEXT PRIMARY KEY,         -- Nombre de usuario único
        password TEXT NOT NULL,                -- Contraseña almacenada como hash
        Idpena TEXT ,                      
        FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE
    )""")
    
    conn.commit()  # Asegúrate de guardar los cambios
    app.config['DATABASE'] = conn  # Conectar la aplicación a esta base de datos temporal

    yield  conn# Aquí se ejecutan las pruebas

    conn.close()  # Cierra la conexión después de las pruebas

def test_ping(client):
    """Prueba la ruta de inicio."""
    response = client.get('/')
    assert response.status_code == 200  # Asegúrate de que la página se carga correctamente
    assert 'Inicia Sesión o Regístrate' in response.get_data(as_text=True)  # Verifica que el texto está presente
    assert 'inicia sesión' in response.get_data(as_text=True)  # Verifica que el enlace de inicio de sesión está presente
    assert 'Regístrate aquí' in response.get_data(as_text=True)  # Verifica que el enlace de registro está presente

def test_registration_admin_success(client, init_db):
    """Prueba el registro de un administrador de peña."""
    response = client.post('/registration_pena', data={
        'user_type': 'admin',
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    assert response.status_code == 302  # Debe redirigir

def test_registration_admin_unsuccess(client, init_db):
    """Prueba el registro de un administrador de peña."""
    response = client.post('/registration_pena', data={
        'user_type': 'admin',
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    
    assert 'Usuario o contraseña incorrectos' not in response.get_data(as_text=True)

def test_registration_jugador_success(client, init_db):
    """Prueba el registro de un jugador."""
  
    
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
    
def test_registration_jugador_unsuccess(client, init_db):
        """Prueba el registro de un jugador."""
    
        
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



    ##TEST HITO 3 
def test_crear_temporada(client, init_db):
    """Prueba la creación de una temporada."""
    # Registrar y autenticar al administrador
    client.post('/registration', data={
        'user_type': 'admin',
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})

    # Crear una temporada
    response = client.post('/admin/gestionar_temporadas/añadir', data={
        'fechaini': '2023-01-01',
        'fechafin': '2023-12-31'
    })
    assert response.status_code == 302  # La creación redirige a la lista de temporadas

    # Verificar que la temporada aparece en la lista
    response = client.get('/admin/gestionar_temporadas')
    assert response.status_code == 200  # La página debe cargarse correctamente
    data = response.get_data(as_text=True)
    assert '2023-01-01' in data  # Verifica que la fecha de inicio se muestra
    assert '2023-12-31' in data  # Verifica que la fecha de fin se muestra
def test_eliminar_temporada(client, init_db):
    """Prueba la eliminación de una temporada."""
    # Registrar y autenticar al administrador
    client.post('/registration', data={
        'user_type': 'admin',
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})

    # Crear una temporada para eliminar
    client.post('/admin/gestionar_temporadas/añadir', data={
        'fechaini': '2023-01-01',
        'fechafin': '2023-04-01'
    })

    # Obtener la lista de temporadas y verificar que contiene la temporada creada
    response = client.get('/admin/gestionar_temporadas')
    assert response.status_code == 200
    data = response.get_data(as_text=True)

    # Extraer el ID de la temporada basado en el formato del HTML
    id_temporada = None
    for line in data.splitlines():
        if '<td>' in line and 'Temporada:' in data:  # Línea que contiene el ID de la temporada
            try:
                id_temporada = line.split('<td>')[1].split('</td>')[0].strip()
                break
            except IndexError:
                continue

    assert id_temporada is not None, "No se encontró el ID de la temporada en la respuesta"
    
    # Eliminar la temporada
    response = client.post(f'/admin/gestionar_temporadas/eliminar/{id_temporada}')
    assert response.status_code == 302  # Redirige después de eliminar

    # Verificar que el ID de la temporada fue eliminado
    response = client.get('/admin/gestionar_temporadas')
    data = response.get_data(as_text=True)
    assert id_temporada not in data
"""
def test_añadir_jugador_a_temporada(client, init_db):
   
    conn = init_db  # Usar la conexión compartida
    cursor = conn.cursor()

    # Registrar una peña
    cursor.execute("INSERT INTO PENA (Nombre, Admin) VALUES ('Peña Test', 'testadmin')")
    id_pena = cursor.lastrowid

    # Crear un jugador
    cursor.execute("INSERT INTO JUGADOR (Nombre, Apellidos, Nacionalidad) VALUES ('Juan', 'Pérez', 'Española')")
    id_jugador = cursor.lastrowid
    cursor.execute("INSERT INTO JUGADORPENA (Idjugador, Idpena, Mote, Posicion) VALUES (?, ?, 'Juanito', 'Delantero')", (id_jugador, id_pena))

    # Crear una temporada
    cursor.execute("INSERT INTO TEMPORADA (Idpena, Fechaini, Fechafin) VALUES (?, '2023-01-01', '2023-12-31')", (id_pena,))
    id_temporada = cursor.lastrowid

    conn.commit()

    # Autenticar como administrador
    client.post('/login', data={'username': 'testadmin', 'password': 'testpass'})

    # Añadir el jugador a la temporada
    response = client.post(f'/admin/visualizar_temporada/{id_temporada}', data={
        'jugador_id': id_jugador
    })
    #assert response.status_code == 302  # Redirige después de añadir

    # Verificar que el jugador aparece en la temporada
    response = client.get(f'/admin/visualizar_temporada/{id_temporada}')
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert 'Juanito' in data  # Verificar que el mote del jugador aparece en la clasificación
"""