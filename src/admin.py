from .user import User
from .db import get_db_connection  # Importar la función de conexión si está en un módulo db.py

class Admin(User):
    def __init__(self, username, id_pena):
        super().__init__(username)
        self.id_pena = id_pena

    def add_pena(self, nombre):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO PENA (nombre) VALUES (?)", (nombre,))
        pena_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pena_id

    def get_players(self):
        conn = get_db_connection()
        players = conn.execute("SELECT * FROM JUGADORPENA WHERE Idpena = ?", (self.id_pena,)).fetchall()
        conn.close()
        return players

    def delete_player(self, jugador_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM JUGADORPENA WHERE Idjugador = ? AND Idpena = ?", (jugador_id, self.id_pena))
        conn.execute("DELETE FROM JUGADOR WHERE Idjugador = ?", (jugador_id,))
        conn.commit()
        conn.close()

    def update_player(self, jugador_id, nombre, apellidos, nacionalidad, mote, posicion):
        conn = get_db_connection()

        # Actualizar en la tabla JUGADOR
        conn.execute("""
            UPDATE JUGADOR
            SET Nombre = ?, Apellidos = ?, Nacionalidad = ?
            WHERE Idjugador = ?
        """, (nombre, apellidos, nacionalidad, jugador_id))

        # Actualizar en la tabla JUGADORPENA
        conn.execute("""
            UPDATE JUGADORPENA
            SET Mote = ?, Posicion = ?
            WHERE Idjugador = ? AND Idpena = ?
        """, (mote, posicion, jugador_id, self.id_pena))

        conn.commit()
        conn.close()