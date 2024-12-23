# Imagen base con Python 3.12
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias, incluido SQLite
RUN apt-get update && apt-get install -y sqlite3 && apt-get clean

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar las dependencias
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos del código fuente y la base de datos
COPY src/ ./src/
COPY Gestion_Penas.db ./Gestion_Penas.db

# Verificar que la base de datos existe
RUN test -f /app/Gestion_Penas.db || echo "La base de datos no existe en el contenedor."

# Exponer el puerto que usará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "src/app.py"]
