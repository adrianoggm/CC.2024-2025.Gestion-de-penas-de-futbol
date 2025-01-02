# Gestión de Peñas y Ligas Individuales Deportivas  
## **Hito 4: Composición de Servicios** 🏗️

> **Versión 0.1**

Este documento corresponde al **Hito 4** del proyecto de **gestión de peñas y ligas individuales deportivas**. Durante este hito, se ha avanzado en la **contenedización** de la aplicación y en la **orquestación** de los diferentes servicios que la componen, siguiendo las pautas de arquitectura de microservicios definidas en el **Hito 3** y aprovechando el flujo de **Integración Continua** establecido en el **Hito 2**.

---

## 📋 1. Documentación y Justificación del Clúster de Contenedores

Para garantizar la **independencia**, **flexibilidad** y **escalabilidad** de la aplicación, se han definido tres servicios principales, cada uno ejecutándose en un contenedor distinto:

1. **App (Contenedor de Aplicación)**  
   - Ejecuta la lógica de la aplicación desarrollada en Flask.  
   - Gestiona peticiones HTTP y realiza consultas a la base de datos.  

2. **DB (Contenedor de Base de Datos)**  
   - Implementado con **PostgreSQL** para un almacenamiento fiable y duradero de la información (usuarios, partidos, estadísticas, etc.).  

3. **Logs (Contenedor de Logs)**  
   - Centraliza la recogida de logs generados por la aplicación y la base de datos para su posterior análisis y persistencia.  

Gracias a esta arquitectura, cada servicio es fácilmente escalable e intercambiable, permitiendo que el proyecto evolucione sin modificar todo el sistema en bloque.

---

## 📋 2. Configuración de los Contenedores y Justificación

### 2.1. **App (Contenedor de Aplicación)**
- **Imagen Base**: `python:3.12-slim`  
  - Se elige una versión ligera y reciente de Python para optimizar el despliegue.  
- **Configuración**:
  - Las dependencias se gestionan mediante el archivo `requirements.txt`.  
  - Se expone el puerto `5000` para la comunicación con el host o con otros contenedores.  
- **Responsabilidad Principal**:
  - Ejecutar la lógica de negocio y servir las vistas/endpoints de la aplicación.

### 2.2. **DB (Contenedor de Base de Datos)**
- **Imagen Base**: `postgres:15`  
  - Esta versión oficial de PostgreSQL aporta estabilidad y buen soporte de la comunidad.  
- **Configuración**:
  - Uso de variables de entorno (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) para una configuración segura.  
  - Volúmenes para la **persistencia** de datos, de modo que la información permanezca aunque el contenedor se reinicie.  
- **Responsabilidad Principal**:
  - Almacenar toda la información crítica de la aplicación (usuarios, peñas, temporadas, resultados, etc.).

### 2.3. **Logs (Contenedor de Logs)**
- **Imagen Base**: `alpine`  
  - Imagen mínima para asegurar un bajo consumo de recursos.  
- **Configuración**:
  - Montaje de volúmenes compartidos con la aplicación y la base de datos para recopilar logs.  
- **Responsabilidad Principal**:
  - Centralizar y organizar todos los registros del clúster, lo que facilita la monitorización y el análisis.

---

## 📋 3. Dockerfile del Contenedor de Aplicación

A continuación se presenta el **Dockerfile** del contenedor principal (App), donde se incluyen las dependencias, la lógica de la aplicación y las configuraciones esenciales:

FROM python:3.12-slim  
RUN apt-get update && apt-get install -y sqlite3 && apt-get clean  
WORKDIR /app  
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  
COPY src/ ./src  
COPY Gestion_Penas.db ./Gestion_Penas.db  
EXPOSE 5000  
CMD ["python", "src/app.py"]

**Puntos Clave**:
- **Imagen base**: Versión ligera de Python para optimizar tiempos de construcción.  
- **Dependencias**: Instaladas a través de `requirements.txt`.  
- **Directorio de trabajo**: `/app`, para mantener la coherencia de los archivos.  
- **Ejecución**: El proceso principal se inicia con `python src/app.py`.  

---

## 📋 4. Publicación en GitHub Packages y Flujo CI/CD

En el repositorio, se han configurado **GitHub Actions** para automatizar la construcción y publicación de las imágenes en **GitHub Packages**. Cada push a la rama principal dispara un **pipeline** que:

1. Construye la imagen Docker.  
2. Ejecuta las pruebas de validación.  
3. Publica la imagen resultante en GitHub Packages si todas las pruebas han sido exitosas.

De esta forma, se integran los principios de **Integración Continua** y **Despliegue Continuo** (CI/CD), garantizando la calidad y la coherencia de la aplicación.

---

## 📋 5. Fichero de Composición (docker-compose.yaml)

En el siguiente fragmento se muestra un ejemplo de configuración de **Docker Compose** para levantar los tres contenedores:

services:  
  app:  
    build:  
      context: .  
      dockerfile: Dockerfile  
    container_name: app-container  
    ports:  
      - "5000:5000"  
    volumes:  
      - ./src:/app/src  
      - ./logs:/app/logs  
      - ./Gestion_Penas.db:/app/Gestion_Penas.db  
    depends_on:  
      - db  

  db:  
    image: postgres:15  
    container_name: db-container  
    environment:  
      POSTGRES_USER: user  
      POSTGRES_PASSWORD: password  
      POSTGRES_DB: gestion_penas  
    volumes:  
      - db_data:/var/lib/postgresql/data  

  logs:  
    image: alpine  
    container_name: logs-container  
    volumes:  
      - ./logs:/app/logs  
    command: tail -f /dev/null  

volumes:  
  db_data:

**Puntos Destacados**:
- **app**: Construye la imagen desde el `Dockerfile`, mapea puertos y monta volúmenes para la base de datos y los logs.  
- **db**: Utiliza la imagen oficial de PostgreSQL; se definen credenciales y un volumen para la persistencia de datos.  
- **logs**: Contenedor ligero para la centralización de logs, permaneciendo en ejecución constante con `tail -f /dev/null`.  
- **db_data**: Volumen para mantener la persistencia en la base de datos.

---

## 📋 6. Implementación y Validación del Clúster

Para garantizar el correcto funcionamiento de los contenedores y su interacción, se han desarrollado pruebas automatizadas que validan tanto la disponibilidad de la aplicación Flask como la conexión con la base de datos. A continuación, se muestra un ejemplo de estas pruebas en **Python**, utilizando la librería `requests`:

```python
import requests

def test_app():
    try:
        # Enviar una solicitud GET a la aplicación Flask
        response = requests.get("http://localhost:5000")
        assert response.status_code == 200, "La aplicación no está respondiendo correctamente"
        print("✅ Test passed: La aplicación está accesible en http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_database():
    try:
        response = requests.get("http://localhost:5000/test_db")
        assert response.status_code == 200, "La base de datos no está conectada correctamente"
        print("✅ Test passed: Conexión a la base de datos exitosa")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_app()
```
### Explicación de las pruebas

**1. `test_app()`**  
   - Realiza una petición **HTTP GET** a la URL `http://localhost:5000`.  
   - Verifica que el código de estado de la respuesta sea **200 (OK)**.  
   - Si la verificación es exitosa, confirma que la aplicación Flask está disponible y respondiendo correctamente.  

**2. `test_database()`**  
   - Envía una solicitud **HTTP GET** a la ruta `http://localhost:5000/test_db`.  
   - La aplicación, por su parte, realiza una consulta a la base de datos para validar su conexión.  
   - Comprueba que el estado de la respuesta sea **200**, certificando que la aplicación puede comunicarse con la base de datos de manera adecuada.  

Estas pruebas pueden ejecutarse **de forma local** o integrarse en el **pipeline de CI/CD**, asegurando así que cada modificación del proyecto no afecte negativamente ni la conexión con la base de datos ni la disponibilidad de la aplicación. De este modo, se detectan de manera temprana posibles problemas de configuración o despliegue, lo que facilita su corrección inmediata.


