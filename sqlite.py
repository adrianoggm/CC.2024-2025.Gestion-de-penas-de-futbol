import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
"""ACTUALMENTE ESTÁ EN PRUEBAS SOLO GENERA LA DB POSTERIORMENTE DEBERÁ DE FUNCIONAR COMO LISTENER DE LOS MÉTODOS QUE REALIZARÁN LAS CLASES ADMIN Y USUARIO."""

conn=sqlite3.connect("Gestion_Penas.db")
c=conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")
c.execute(""" CREATE TABLE IF NOT EXISTS PENA(
          Idpena INTEGER PRIMARY KEY AUTOINCREMENT,
          Nombre TEXT,
          Admin  TEXT NOT NULL
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
          PRIMARY KEY (Idjugador,Idpena,Idt),
          FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
          )""")
c.execute(""" CREATE TABLE IF NOT EXISTS PARTIDO (
          Idp INTEGER ,
          Idpena INTEGER,
          Idt INTEGER,
          PRIMARY KEY (Idp,Idpena,Idt),
          FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
          )""")
c.execute(""" CREATE TABLE IF NOT EXISTS EQUIPO (
          Ide INTEGER ,
          Idp INTEGER ,
          Idpena INTEGER,
          Idt INTEGER,
          PRIMARY KEY (Ide,Idp,Idpena,Idt),
          FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idpena) REFERENCES PENA(Idpena) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idt) REFERENCES TEMPORADA(Idt) ON UPDATE CASCADE ON DELETE CASCADE
          )""")
c.execute(""" CREATE TABLE IF NOT EXISTS EJUGADOR (
          Ide INTEGER ,
          Idp INTEGER ,
          Idjugador INTEGER,
          Goles INTEGER DEFAULT 0,
          Asistencias INTEGER DEFAULT 0,
          Val REAL DEFAULT 5 CHECK(Calidad BETWEEN 0 AND 10),
          PRIMARY KEY (Ide,Idp,Idjugador),
          FOREIGN KEY (Idp) REFERENCES PARTIDO(Idp) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Ide) REFERENCES EQUIPO(Ide) ON UPDATE CASCADE ON DELETE CASCADE,
          FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
          
          )""")
#c.execute("DELETE FROM users WHERE username = ?", ('adrianoggm',))
c.execute(""" CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,         -- Nombre de usuario único
    password TEXT NOT NULL,                -- Contraseña almacenada como hash
    name TEXT NOT NULL,                     -- Nombre del usuario
    Idjugador INTEGER,                      --Será 0 para los admins
    FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador) ON UPDATE CASCADE ON DELETE CASCADE
)""")

#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Generalife','Genadmin')")
#c.execute("INSERT INTO PENA VALUES ('0','Generalife','Genadmin')")
#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Churriana','CHadmin')")
#c.execute("INSERT INTO JUGADOR(Nombre,Apellidos,Nacionalidad) VALUES ('Adriano','García-Giralda Milena','ESPAÑOLA')")
#c.execute("INSERT INTO JUGADORPENA VALUES ('1','1','Adri jr','ATACANTE')")
#c.execute("INSERT INTO TEMPORADA(Fecha) VALUES ('2024/2025')")
#c.execute("INSERT INTO JUGADORTEMPORADA(Idjugador,Idpena,Idt) VALUES ('1','1','1')")
#password = generate_password_hash('1234')
#print(password)
#c.execute("INSERT INTO users(username,password,name,idjugador) VALUES (?, ?, ?, ?)",('adrianoggm', password, 'Adriano', '1'))
conn.commit()
c.execute("SELECT * FROM users ")
penas=c.fetchall()
print(penas)
conn.close()