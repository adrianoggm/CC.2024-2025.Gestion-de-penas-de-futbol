import pytest

def test_ping(client):
    """
    Prueba la ruta principal /api (o un /api/auth/ping, según hayas definido).
    Se asume que devuelves algo como {"message": "Bienvenido a la API...", "status": "OK"}.
    """
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'].startswith('Bienvenido')  # Ajusta según tu respuesta real
    assert data['status'] == 'OK'


def test_registration_admin_success(client):
    """
    Prueba el registro de un administrador de peña.
    POST /api/auth/registration_pena con JSON,
    se espera 201 y un mensaje de éxito.
    """
    response = client.post('/api/auth/registration_pena', json={
        'username': 'testadmin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    assert response.status_code == 201  # "Created"
    data = response.get_json()
    assert data.get('message') == 'Admin registrado exitosamente'
    assert 'id_peña' in data  # Devuelto desde el servidor


def test_registration_admin_unsuccess(client):
    """
    Prueba el registro de un administrador fallido. Por ejemplo,
    si el username ya existe, o si confirm_password no coincide.
    Ajusta el test a la lógica que quieras.
    """
    # Registramos por primera vez
    response = client.post('/api/auth/registration_pena', json={
        'username': 'testadmin2',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Test'
    })
    assert response.status_code == 201

    # Intento de registro con el mismo username
    response = client.post('/api/auth/registration_pena', json={
        'username': 'testadmin2',  # Repetido
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Otra'
    })
    # Se asume que devuelves 409 "Conflict" o similar
    assert response.status_code == 409
    data = response.get_json()
    assert 'error' in data


def test_registration_jugador_success(client):
    """
    Prueba el registro de un jugador en una peña existente.
    POST /api/auth/registration_jugador
    """
    # Primero, creamos el admin/peña
    response = client.post('/api/auth/registration_pena', json={
        'username': 'admin_for_jugador',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Jugadores'
    })
    assert response.status_code == 201
    data_admin = response.get_json()
    id_peña = data_admin['id_peña']

    # Crear jugador en esa peña
    response = client.post('/api/auth/registration_jugador', json={
        'username': 'testjugador',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'id_peña': id_peña,
        'mote': 'Jugadore',
        'posicion': 'Delantero',
        'nacionalidad': 'Española'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data.get('message') == "Jugador registrado exitosamente"
    assert 'id_jugador' in data


def test_registration_jugador_unsuccess(client):
    """
    Prueba un registro de jugador fallido, por ejemplo si no coinciden las contraseñas.
    """
    # Suponemos que la peña 999 no existe o no es válida
    response = client.post('/api/auth/registration_jugador', json={
        'username': 'jugador_fallo',
        'password': 'abc',
        'confirm_password': 'xyz',  # No coincide
        'id_peña': 999,
        'mote': 'Fallon',
        'posicion': 'Defensa',
        'nacionalidad': 'Uruguaya'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_login(client):
    """
    Prueba el inicio de sesión como admin.
    POST /api/auth/login => 200 + JSON con "message": "Admin logueado"
    """
    # Registrar admin
    response = client.post('/api/auth/registration_pena', json={
        'username': 'testadminlogin',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Login'
    })
    assert response.status_code == 201

    # Hacer login
    response = client.post('/api/auth/login', json={
        'username': 'testadminlogin',
        'password': 'testpass'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('message') == 'Admin logueado'
    assert 'Idpena' in data


def test_gestionar_jugadores(client):
    """
    Prueba la visualización y presencia de un jugador concreto
    en /api/admin/gestionar_jugadores.
    """
    # Registrar admin
    response = client.post('/api/auth/registration_pena', json={
        'username': 'admin_gj',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña GJ'
    })
    assert response.status_code == 201

    # Hacer login (el test_client guardará la cookie de sesión)
    response = client.post('/api/auth/login', json={
        'username': 'admin_gj',
        'password': 'testpass'
    })
    assert response.status_code == 200

    # Añadir un jugador
    response = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Juan',
        'apellidos': 'Pérez',
        'nacionalidad': 'Española',
        'mote': 'Juanito',
        'posicion': 'Delantero'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data.get('message') == 'Jugador añadido'

    # Obtener la lista de jugadores
    response = client.get('/api/admin/gestionar_jugadores')
    assert response.status_code == 200
    data = response.get_json()
    jugadores = data.get('jugadores', [])
    # Verificar si "Juanito" aparece
    assert any(j.get('mote') == 'Juanito' for j in jugadores)


def test_eliminar_jugador(client):
    """
    Prueba la eliminación de un jugador:
      1) Crear admin + login
      2) Añadir jugador
      3) DELETE jugador
      4) Comprobar que no aparece
    """
    # Crear admin
    response = client.post('/api/auth/registration_pena', json={
        'username': 'admin_eliminar_j',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Eliminar'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/api/auth/login', json={
        'username': 'admin_eliminar_j',
        'password': 'testpass'
    })
    assert response.status_code == 200

    # Añadir jugador
    response = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Carlos',
        'apellidos': 'Gómez',
        'nacionalidad': 'Española',
        'mote': 'Carlitos',
        'posicion': 'Defensa'
    })
    assert response.status_code == 201
    data_add = response.get_json()
    # Podrías devolver el Idjugador, aquí asumimos un "id_jugador" si lo implementas
    # id_jugador = data_add['id_jugador']

    # Para este ejemplo, supongamos que es 1. O haz un GET y busca "Carlitos" para saber su ID real
    # Si tu endpoint de añadir_jugador no devuelve ID, tendrás que listar jugadores y buscarlo
    # Para simplificar, re-listamos y buscamos a 'Carlitos'
    r_gestion = client.get('/api/admin/gestionar_jugadores')
    list_data = r_gestion.get_json()
    jugadores = list_data.get('jugadores', [])
    # Buscar al jugador que tenga 'mote' == 'Carlitos'
    target_id = None
    for j in jugadores:
        if j.get('mote') == 'Carlitos':
            target_id = j.get('idjugador')  # Ajusta el campo que tengas
            break
    assert target_id is not None, "No se encontró el jugador 'Carlitos' en la respuesta"

    # Eliminar jugador (DELETE)
    response = client.delete(f'/api/admin/gestionar_jugadores/eliminar/{target_id}')
    assert response.status_code == 200

    # Verificar que "Carlos" ya no aparece
    response = client.get('/api/admin/gestionar_jugadores')
    assert response.status_code == 200
    jugadores_after = response.get_json().get('jugadores', [])
    assert not any(j.get('idjugador') == target_id for j in jugadores_after), "El jugador no fue eliminado"


def test_editar_jugador(client):
    """
    Prueba la edición de un jugador.
    1) Crear admin + login
    2) Añadir jugador
    3) PUT/PATCH para editar (según tu implementación)
    4) GET y comprobar los cambios
    """
    # Crear admin
    response = client.post('/api/auth/registration_pena', json={
        'username': 'admin_editar_j',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Editar'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/api/auth/login', json={
        'username': 'admin_editar_j',
        'password': 'testpass'
    })
    assert response.status_code == 200

    # Añadir jugador
    response = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Andrés',
        'apellidos': 'Fernández',
        'nacionalidad': 'Española',
        'mote': 'Andresito',
        'posicion': 'Portero'
    })
    assert response.status_code == 201

    # Localizar ID del jugador 'Andresito'
    r_gestion = client.get('/api/admin/gestionar_jugadores')
    jugadores = r_gestion.get_json().get('jugadores', [])
    jugador_id = None
    for j in jugadores:
        if j.get('mote') == 'Andresito':
            jugador_id = j['idjugador']  # Ajusta si es otro nombre de campo
            break
    assert jugador_id is not None

    # Editar (asume PATCH o PUT en tu API; aquí supongo un PUT /editar/<id>)
    response = client.put(f'/api/admin/gestionar_jugadores/editar/{jugador_id}', json={
        'nombre': 'Andrés',
        'apellidos': 'Fernández',
        'nacionalidad': 'Española',
        'mote': 'Andresito Modificado',
        'posicion': 'Portero'
    })
    assert response.status_code == 200

    # Verificar
    r_gestion_after = client.get('/api/admin/gestionar_jugadores')
    jugadores_after = r_gestion_after.get_json().get('jugadores', [])
    # Comprobar que aparece 'Andresito Modificado'
    assert any(j.get('mote') == 'Andresito Modificado' for j in jugadores_after)


def test_crear_temporada(client):
    """
    Prueba la creación de una temporada:
    1) Crear admin + login
    2) POST /api/admin/gestionar_temporadas/añadir
    3) GET /api/admin/gestionar_temporadas => verificar
    """
    # Crear admin
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_temp',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña Temp'
    })
    assert r.status_code == 201

    # Login
    r = client.post('/api/auth/login', json={
        'username': 'admin_temp',
        'password': 'testpass'
    })
    assert r.status_code == 200

    # Añadir temporada
    response = client.post('/api/admin/gestionar_temporadas/añadir', json={
        'fechaini': '2023-01-01',
        'fechafin': '2023-12-31'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Temporada añadida'
    id_temporada = data['id_temporada']

    # Verificar con GET
    response = client.get('/api/admin/gestionar_temporadas')
    assert response.status_code == 200
    temporadas = response.get_json().get('temporadas', [])
    # Buscar la temporada con id_temporada
    assert any(t.get('idt') == id_temporada for t in temporadas)


def test_eliminar_temporada(client):
    """
    Prueba la eliminación de una temporada:
    1) Admin + login
    2) Crear temporada
    3) DELETE /gestionar_temporadas/eliminar/<id>
    4) GET y verificar que ya no está
    """
    # Crear admin
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_temp_del',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña TempDel'
    })
    assert r.status_code == 201

    # Login
    r = client.post('/api/auth/login', json={
        'username': 'admin_temp_del',
        'password': 'testpass'
    })
    assert r.status_code == 200

    # Crear temporada
    r = client.post('/api/admin/gestionar_temporadas/añadir', json={
        'fechaini': '2023-01-01',
        'fechafin': '2023-04-01'
    })
    assert r.status_code == 201
    data = r.get_json()
    id_temporada = data['id_temporada']

    # Eliminar
    r = client.delete(f'/api/admin/gestionar_temporadas/eliminar/{id_temporada}')
    assert r.status_code == 200  # Eliminada

    # Verificar
    r = client.get('/api/admin/gestionar_temporadas')
    assert r.status_code == 200
    temps = r.get_json().get('temporadas', [])
    assert not any(t.get('idt') == id_temporada for t in temps), "La temporada no fue eliminada"

def test_admin_required_protection(client):
    """
    Prueba que las rutas de admin devuelvan 401 si NO se ha iniciado sesión como admin.
    Intentamos llamar /api/admin/gestionar_jugadores sin login previo.
    """
    response = client.get('/api/admin/gestionar_jugadores')
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'No autorizado' in data['error']


def test_crear_temporada_invalida(client):
    """
    Prueba que no podamos crear una temporada con fechaini >= fechafin.
    """
    # Registrar y loguear admin
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_temp_invalid',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña TempInv'
    })
    assert r.status_code == 201

    r = client.post('/api/auth/login', json={
        'username': 'admin_temp_invalid',
        'password': 'testpass'
    })
    assert r.status_code == 200

    # Intentar crear temporada inválida
    response = client.post('/api/admin/gestionar_temporadas/añadir', json={
        'fechaini': '2023-12-31',
        'fechafin': '2023-01-01'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'inicio debe ser anterior' in data['error'] or 'La fecha de inicio debe ser anterior' in data['error']


def test_crear_jugador_con_datos_faltantes(client):
    """
    Prueba que no podamos crear un jugador si faltan campos obligatorios.
    """
    # Registrar y loguear admin
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_jugador_incompleto',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña JugInc'
    })
    assert r.status_code == 201

    r = client.post('/api/auth/login', json={
        'username': 'admin_jugador_incompleto',
        'password': 'testpass'
    })
    assert r.status_code == 200

    # Faltan algunos campos (ej. 'posicion')
    response = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'SinPos',
        'apellidos': '???',
        'nacionalidad': 'Española',
        'mote': 'Desconocido'
        # falta "posicion"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Faltan datos' in data['error']


def test_draft_partido_jugadores_repetidos(client):
    """
    Prueba que no podamos crear un partido (POST /api/admin/draft_partido/<id_temporada>)
    si hay jugadores repetidos en ambos equipos.
    """
    # 1) Crear admin + login
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_draft_rep',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña DraftRep'
    })
    assert r.status_code == 201

    r = client.post('/api/auth/login', json={
        'username': 'admin_draft_rep',
        'password': 'testpass'
    })
    assert r.status_code == 200
    data_login = r.get_json()
    id_pena = data_login.get('Idpena')

    # 2) Crear temporada
    r = client.post('/api/admin/gestionar_temporadas/añadir', json={
        'fechaini': '2023-01-01',
        'fechafin': '2023-12-31'
    })
    assert r.status_code == 201
    data_temp = r.get_json()
    id_temporada = data_temp['id_temporada']

    # 3) Registrar 2 jugadores
    j1 = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Jugador1',
        'apellidos': 'Test1',
        'nacionalidad': 'X',
        'mote': 'J1',
        'posicion': 'Delantero'
    })
    j2 = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Jugador2',
        'apellidos': 'Test2',
        'nacionalidad': 'X',
        'mote': 'J2',
        'posicion': 'Defensa'
    })
    assert j1.status_code == 201
    assert j2.status_code == 201

    # 4) Añadir esos jugadores a la temporada (POST /api/admin/visualizar_temporada/<id_temporada>)
    #    Con "jugador_id" en el body
    # Localizamos sus IDs
    list_jug = client.get('/api/admin/gestionar_jugadores').get_json()['jugadores']
    jug_1 = next(x for x in list_jug if x['mote'] == 'J1')
    jug_2 = next(x for x in list_jug if x['mote'] == 'J2')

    # Asignar a la temporada
    client.post(f'/api/admin/visualizar_temporada/{id_temporada}', json={'jugador_id': jug_1['idjugador']})
    client.post(f'/api/admin/visualizar_temporada/{id_temporada}', json={'jugador_id': jug_2['idjugador']})

    # 5) Crear un partido, pero usando el mismo jugador en ambos equipos
    #    (POST /api/admin/draft_partido/<id_temporada> con { "crear_partido": true, "equipo_1": [...], "equipo_2": [...] })
    response = client.post(f'/api/admin/draft_partido/{id_temporada}', json={
        "crear_partido": True,
        "equipo_1": [jug_1['idjugador']],
        "equipo_2": [jug_1['idjugador']]  # Repetido
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Jugadores repetidos' in data['error']


def test_draft_partido_equipos_desbalanceados(client):
    """
    Prueba que no se pueda crear un partido si los equipos no tienen el mismo número de jugadores,
    teniendo en cuenta que solo hay 2 jugadores registrados en total.
    """
    # 1) Crear admin + login
    r = client.post('/api/auth/registration_pena', json={
        'username': 'admin_draft_bal',
        'password': 'testpass',
        'confirm_password': 'testpass',
        'nombre_peña': 'Peña DraftBal'
    })
    assert r.status_code == 201

    r = client.post('/api/auth/login', json={
        'username': 'admin_draft_bal',
        'password': 'testpass'
    })
    assert r.status_code == 200

    # 2) Crear temporada
    r = client.post('/api/admin/gestionar_temporadas/añadir', json={
        'fechaini': '2023-05-01',
        'fechafin': '2023-06-01'
    })
    assert r.status_code == 201
    id_temporada = r.get_json()['id_temporada']

    # 3) Registrar 2 jugadores
    j1 = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Desbal1',
        'apellidos': 'DB1',
        'nacionalidad': 'X',
        'mote': 'DB1',
        'posicion': 'Mediocentro'
    })
    j2 = client.post('/api/admin/gestionar_jugadores/añadir_jugador', json={
        'nombre': 'Desbal2',
        'apellidos': 'DB2',
        'nacionalidad': 'X',
        'mote': 'DB2',
        'posicion': 'Portero'
    })
    assert j1.status_code == 201
    assert j2.status_code == 201

    # 4) Localizar ID y asignar a la temporada
    lista_j = client.get('/api/admin/gestionar_jugadores').get_json()['jugadores']
    jug_1 = next(x for x in lista_j if x['mote'] == 'DB1')
    jug_2 = next(x for x in lista_j if x['mote'] == 'DB2')

    # Asignar ambos a la temporada
    client.post(f'/api/admin/visualizar_temporada/{id_temporada}', json={'jugador_id': jug_1['idjugador']})
    client.post(f'/api/admin/visualizar_temporada/{id_temporada}', json={'jugador_id': jug_2['idjugador']})

    # 5) Intentar crear un partido con equipos desbalanceados:
    #    equipo_1 -> 1 jugador real; equipo_2 -> 1 jugador real + un id ficticio (999).
    #    => No habrá repetidos (jug_1 != jug_2 != 999) pero sí tamaños distintos (1 vs 2)
    response = client.post(f'/api/admin/draft_partido/{id_temporada}', json={
        "crear_partido": True,
        "equipo_1": [jug_1['idjugador']], 
        "equipo_2": [jug_2['idjugador'], 999]  
    })

    # Se espera un 400 y el mensaje de "mismo número de jugadores".
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'mismo número de jugadores' in data['error']

def test_clean_database(db_connection):
    """
    Limpia todas las tablas de la base de datos y verifica que estén vacías.
    Esto es un test adicional que revalida que la base de datos realmente se vacíe.
    """
    conn = db_connection
    with conn.cursor() as cur:
        # Obtener todas las tablas en la base de datos
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()

        # Limpiar las tablas
        for (table_name,) in tables:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
        conn.commit()

        # Verificar que cada tabla esté vacía
        for (table_name,) in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            assert count == 0, f"La tabla {table_name} no está vacía (contiene {count} filas)."
