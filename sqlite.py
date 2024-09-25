import sqlite3

conn=sqlite3.connect("Gestion_Penas.db")
c=conn.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS PENA(
          Idpena TEXT PRIMARY KEY,
          Nombre TEXT,
          Admin  TEXT NOT NULL
          )""")
c.execute(""" CREATE TABLE IF NOT EXISTS JUGADOR(
          Idjugador TEXT PRIMARY KEY,
          Nombre TEXT,
          Apellidos TEXT,
          Nacionalidad TEXT
          )""")
c.execute(""" CREATE TABLE IF NOT EXISTS JUGADORPENA (
          Idjugadorp TEXT,
          Idjugador TEXT,
          Idpena TEXT,
          Mote TEXT,
          Posicion TEXT,
          PRIMARY KEY (Idjugadorp,Idjugador,Idpena),
          FOREIGN KEY (Idjugador) REFERENCES JUGADOR(Idjugador),
          FOREIGN KEY (Idpena) REFERENCES PENA(Idpena)
          )""")
#c.execute("INSERT INTO PENA VALUES ('PENGR-001','Generalife','Genadmin')")
#c.execute("INSERT INTO JUGADOR VALUES ('PENGEN-001','Adriano','García-Giralda Milena','ESPAÑOLA')")
#c.execute("INSERT INTO JUGADORPENA VALUES ('JPGEN-001','PENGEN-001','PENGR-001','Adri jr','ATACANTE')")
conn.commit()
c.execute("SELECT * FROM JUGADORPENA ")
penas=c.fetchall()
print(penas)
conn.close()