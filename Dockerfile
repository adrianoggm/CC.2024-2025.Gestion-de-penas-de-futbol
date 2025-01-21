# Imagen base con Python 3.12
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para psycopg2 y SQLite (si lo necesitas)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    sqlite3 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar las dependencias (requirements.txt)
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/

# (Opcional) Eliminar la instalación de `sqlite3` si no lo usas

# Añadir /app al PYTHONPATH para que "from src..." funcione
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Exponer el puerto que usará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "src/app.py"]
