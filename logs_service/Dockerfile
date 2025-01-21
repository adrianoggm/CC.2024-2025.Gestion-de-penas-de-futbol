FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el código fuente
COPY ./app.py /app/app.py

# Instalar Flask
RUN pip install --no-cache-dir flask

# Crear la carpeta de logs
RUN mkdir -p /logs

# Configurar el archivo de logs como variable de entorno
ENV LOG_FILE_PATH=/logs/service.log

# Exponer el puerto
EXPOSE 6000

# Comando para iniciar el servicio
CMD ["python", "app.py"]
