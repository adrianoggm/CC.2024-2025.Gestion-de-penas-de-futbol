import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
"""ACTUALMENTE ESTÁ EN PRUEBAS SOLO GENERA LA DB POSTERIORMENTE DEBERÁ DE FUNCIONAR COMO LISTENER DE LOS MÉTODOS QUE REALIZARÁN LAS CLASES ADMIN Y USUARIO."""

conn=sqlite3.connect("Gestion_Penas.db")
c=conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")
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

#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Generalife','Genadmin')")
#c.execute("INSERT INTO PENA VALUES ('0','Generalife','Genadmin')")
#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Churriana','CHadmin')")
#c.execute("INSERT INTO JUGADOR(Nombre,Apellidos,Nacionalidad) VALUES ('Adriano','García-Giralda Milena','ESPAÑOLA')")
#c.execute("INSERT INTO JUGADORPENA VALUES ('1','1','Adri jr','ATACANTE')")
#c.execute("INSERT INTO TEMPORADA(Fecha) VALUES ('2024/2025')")
#c.execute("INSERT INTO JUGADORTEMPORADA(Idjugador,Idpena,Idt) VALUES ('1','1','1')")
password = generate_password_hash('password') #1234 para adrianoggm
#print(password)
#c.execute("INSERT INTO users(username,password,name,idjugador) VALUES (?, ?, ?, ?)",('adrianoggm', password, 'Adriano', '1'))
#c.execute("INSERT INTO admins(username,password,Idpena) VALUES (?, ?, ?)",('Genadmin', password, '1'))
conn.commit()
c.execute("SELECT * FROM EJUGADOR ")
penas=c.fetchall()
print(penas)
conn.close()