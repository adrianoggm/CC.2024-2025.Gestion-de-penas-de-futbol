from .db import get_db_connection  # Importar la función de conexión si está en un módulo db.py

class User:
    def __init__(self, username):
        self.username = username

    def view_profile(self):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (self.username,)).fetchone()
        conn.close()
        return user