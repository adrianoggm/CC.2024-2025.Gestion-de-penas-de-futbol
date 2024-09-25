import sqlite3

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
#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Generalife','Genadmin')")
#c.execute("INSERT INTO PENA VALUES ('0','Generalife','Genadmin')")
#c.execute("INSERT INTO PENA (Nombre,Admin) VALUES ('Churriana','CHadmin')")
#c.execute("INSERT INTO JUGADOR(Nombre,Apellidos,Nacionalidad) VALUES ('Adriano','García-Giralda Milena','ESPAÑOLA')")
#c.execute("INSERT INTO JUGADORPENA VALUES ('1','1','Adri jr','ATACANTE')")
conn.commit()
c.execute("SELECT * FROM JUGADORPENA ")
penas=c.fetchall()
print(penas)
conn.close()