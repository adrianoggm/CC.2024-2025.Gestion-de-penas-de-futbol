import sqlite3

conn=sqlite3.connect("Gestion_Penas.db")
c=conn.cursor()
c.execute(""" CREATE TABLE IF NOT EXISTS PENA (
          Idpena TEXT PRIMARY KEY,
          Nombre TEXT,
          Admin  TEXT NOT NULL
          )""")

#c.execute("INSERT INTO PENA VALUES ('PENGR-001','Generalife','Genadmin')")

conn.commit()
c.execute("SELECT * FROM PENA ")
penas=c.fetchall()
print(penas)
conn.close()