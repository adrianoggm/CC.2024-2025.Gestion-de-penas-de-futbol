# Hito 4: Composición de Servicios 🗰️

### Versión 1.4

Este documento corresponde al **Hito 4** del proyecto de **gestión de peñas y ligas individuales deportivas**. Durante este hito, se ha avanzado significativamente en la configuración, prueba y depuración de la infraestructura basada en contenedores para soportar la aplicación. Este proceso implicó ajustes iterativos para lograr una arquitectura funcional, escalable y que gestione adecuadamente los registros de logs.

---

## 🗋 1. Documentación y Justificación de la Estructura del Clúster de Contenedores

Se definieron cinco servicios principales que conforman la aplicación y permiten su correcta ejecución:

### **App (Contenedor de Aplicación)**

- **Descripción**: Ejecuta la lógica de la aplicación desarrollada en Flask.
- **Responsabilidad**: Gestiona las peticiones HTTP y realiza consultas a la base de datos.
- **Cambios Implementados**:
  - Se realizó una migración completa de SQLite a PostgreSQL, lo que implicó modificar todas las consultas debido a diferencias de sintaxis entre ambas bases de datos.
  - Se incorporó la biblioteca `psycopg2` para establecer la conexión con PostgreSQL.
  - Se implementó el uso de variables de entorno para configurar el acceso a la base de datos de manera dinámica.
- **Pruebas realizadas**:
  - Se verificó que todas las consultas modificadas fueran compatibles con PostgreSQL.
  - Se realizaron pruebas de estrés para confirmar la estabilidad y el manejo de concurrencia en la base de datos.

### **DB (Contenedor de Base de Datos)**

- **Descripción**: Implementado con PostgreSQL para el almacenamiento de información estructurada.
- **Cambios Implementados**:
  - Se configuró un script inicial para la creación y población de tablas.
  - La conexión a la base de datos ahora se realiza mediante un endpoint configurable a través de variables de entorno.
  - Se realizaron pruebas exhaustivas para garantizar la compatibilidad de las consultas y la integridad de los datos migrados desde SQLite.
- **Pruebas realizadas**:
  - Validación de integridad de datos tras la migración.
  - Simulación de fallos en el contenedor para verificar la recuperación mediante volúmenes persistentes.

### **Grafana (Contenedor de Monitorización)**

- **Descripción**: Proporciona un entorno visual para analizar métricas y logs.
- **Justificación**:
  - Se eligió Grafana por su capacidad de integración con múltiples fuentes de datos, incluidas Loki y Promtail.
  - Su interfaz amigable facilita el monitoreo en tiempo real.

### **Loki (Contenedor de Logs)**

- **Descripción**: Centraliza la recolección de logs enviados por la aplicación y otros servicios.
- **Justificación**:
  - Loki se seleccionó por su diseño ligero y su perfecta integración con Grafana.
  - Su configuración simple permitió reducir la complejidad respecto a otras soluciones como ELK.

### **Promtail (Agente de Logs)**

- **Descripción**: Recolecta logs locales y los envía a Loki para su almacenamiento y análisis.
- **Justificación**:
  - Promtail fue elegido por ser un agente oficial de Loki, asegurando compatibilidad nativa y menor esfuerzo de configuración.
- **Pruebas realizadas**:
  - Validación de recolección de logs desde el contenedor de aplicación.
  - Simulación de grandes volúmenes de logs para medir el rendimiento.

Esta configuración se desarrolló iterativamente, abordando problemas técnicos relacionados con permisos, conectividad de red y compatibilidad entre versiones.

---

## 🗋 2. Documentación y Justificación de la Configuración de los Contenedores

He optado por esta configuración tras explorar otras alternativas como la **pila ELK** y **Graylog**, las cuales presentaron múltiples problemas en la configuración de volúmenes y permisos de autenticación, haciendo inviable su implementación. A continuación, se detalla la justificación de la configuración seleccionada y una comparación con las alternativas consideradas.

### 2.1. Pila ELK

La **pila ELK** es un conjunto de herramientas de código abierto desarrollado por Elastic, utilizado para la búsqueda, análisis y visualización de datos en tiempo real. Es especialmente popular para la gestión de registros (logs) y el monitoreo de sistemas.

**Componentes Principales de ELK:**
![pila ELK](/docs/images/ELK.png)

#### Elasticsearch
- **Descripción:**
  - Motor de búsqueda y análisis de datos basado en Lucene.
  - Almacena datos en formato estructurado (documentos JSON) y permite realizar búsquedas rápidas, agregaciones y análisis complejos.
  - Actúa como el núcleo de la pila, donde se almacenan los datos enviados por los otros componentes.

#### Logstash
- **Descripción:**
  - Herramienta de procesamiento y recolección de datos.
  - Recibe logs o datos de diversas fuentes, los transforma si es necesario y los envía a Elasticsearch para su almacenamiento.
  - Ofrece gran flexibilidad gracias a su sistema de plugins, permitiendo conectar múltiples fuentes de datos (archivos, bases de datos, etc.) y realizar transformaciones como filtrado, enmascarado y enriquecimiento.

#### Kibana
- **Descripción:**
  - Herramienta de visualización y análisis de datos.
  - Proporciona una interfaz gráfica para consultar y analizar los datos almacenados en Elasticsearch.
  - Permite crear dashboards personalizados, gráficos interactivos y visualizaciones en tiempo real.

**Problemas Encontrados con ELK:**
- Configuración compleja de volúmenes y permisos de autenticación.
- Dificultades para mantener la estabilidad del sistema, lo que llevó a fallos frecuentes durante la implementación.

### 2.2. Graylog

**Graylog** actúa como una solución centralizada de gestión de logs dentro de la infraestructura de contenedores. A continuación, se explica cómo funciona cada componente y cómo interactúan:
![Graylog](/docs/images/Graylog.png)
#### Componentes de la Configuración

##### Graylog (graylog-container)
- **Descripción:** Núcleo de la solución de logs.
- **Funciones:**
  - Recibe, almacena y permite consultar logs en tiempo real desde las aplicaciones y servicios configurados.
  - Proporciona una interfaz web accesible en [`http://localhost:9000`](http://localhost:9000) para buscar y analizar los logs.
- **Variables de Entorno Clave:**
  - `GRAYLOG_HTTP_EXTERNAL_URI`: URI para la interfaz externa de Graylog.
  - `GRAYLOG_ROOT_PASSWORD_SHA2`: Hash SHA256 de la contraseña del usuario root.
  - `GRAYLOG_PASSWORD_SECRET`: Cadena base64 que Graylog utiliza para la encriptación de contraseñas.

##### MongoDB (mongo-container)
- **Descripción:** Base de datos utilizada por Graylog.
- **Funciones:**
  - Almacena configuraciones, metadatos y otra información no relacionada con los logs.
  - Requisito imprescindible para el funcionamiento de Graylog.

##### Elasticsearch (elasticsearch-container)
- **Descripción:** Motor de búsqueda y almacenamiento de logs para Graylog.
- **Configuración:**
  - Configurado como un nodo único con los siguientes parámetros:
    - `discovery.type=single-node`: Indica que Elasticsearch funciona como una instancia independiente.
    - `ES_JAVA_OPTS=-Xms512m -Xmx512m`: Limita el uso de memoria de Elasticsearch a 512 MB.

##### Aplicación (app-container)
- **Descripción:** Fuente principal de los logs que Graylog procesará.
- **Funciones:**
  - Los logs generados en `./logs` pueden ser enviados a Graylog a través de entradas configuradas (por ejemplo, GELF, Syslog, etc.).

##### PostgreSQL (db-container)
- **Descripción:** Base de datos de la aplicación.
- **Funciones:**
  - No interactúa directamente con Graylog, pero almacena toda la información estructurada requerida por la aplicación.

#### Flujo de Trabajo de Graylog

1. **Recolección de Logs:**
   - Graylog recibe logs desde la aplicación o cualquier otra fuente configurada.
   - **Protocolos soportados:** GELF (Graylog Extended Log Format), Syslog, JSON, entre otros.
   - Los logs pueden ser enviados directamente desde la aplicación o mediante agentes intermedios (como Filebeat o Fluentd).

2. **Procesamiento y Almacenamiento:**
   - Los logs se procesan en Graylog y se almacenan en Elasticsearch para su posterior consulta.
   - Los mensajes son indexados para facilitar búsquedas rápidas y eficientes.

3. **Interfaz Web:**
   - Graylog expone una interfaz web en [`http://localhost:9000`](http://localhost:9000) para buscar, analizar y visualizar los logs.
   - Permite filtrar por campos, realizar búsquedas específicas y generar alertas basadas en los datos recibidos.

4. **Configuración y Gestión:**
   - MongoDB almacena información de configuraciones, usuarios y dashboards creados en Graylog.
   - La interfaz de Graylog permite configurar entradas (inputs), salidas (outputs) y pipelines para manipular los logs.

Aquí muestro un ejemplo de los contenedores de Graylog desplegados pero observamos como antes comentaba que pese a estar desplegados cuando 
intentamos acceder a los permisos no reconoce ni al usuario admin ni su contraseña. Pese a probar diferentes versioens del contenedor fue en vano. 
De todas formas se mantiene en el proyecto algunos archivos por si en el futuro se quisiera hacer una comparación.
![Contenedores Graylog](/docs/images/4.png)
![Fallo Graylog](/docs/images/6.png)
### 2.3. Configuración de los Contenedores

A continuación, se describen los contenedores utilizados en la configuración seleccionada, sus imágenes base, configuraciones esenciales y responsabilidades principales.

#### 2.3.1. App (Contenedor de Aplicación)

- **Base de Imagen:** `python:3.12-slim`
  - Imagen ligera, segura y adecuada para ejecutar aplicaciones modernas basadas en Python.
- **Configuración Esencial:**
  - Uso de variables de entorno para configurar la conexión a la base de datos y garantizar portabilidad.
  - Montaje del código fuente y los logs como volúmenes para facilitar el desarrollo y la depuración.
- **Responsabilidad Principal:** Proveer la lógica de negocio y los endpoints de la API REST.

#### 2.3.2. DB (Contenedor de Base de Datos)

- **Base de Imagen:** `postgres:15`
  - PostgreSQL es una base de datos confiable y ampliamente utilizada para aplicaciones empresariales.
- **Configuración Esencial:**
  - Uso de volúmenes para persistir datos entre reinicios.
  - Inclusión de un script inicial (`Gestion_Penas.sql`) para configurar tablas y datos iniciales.
- **Responsabilidad Principal:** Almacenar toda la información estructurada requerida por la aplicación.

#### 2.3.3. Grafana (Monitorización)

- **Base de Imagen:** `grafana/grafana-oss`
  - Herramienta de visualización de métricas y logs altamente personalizable.
- **Configuración Esencial:**
  - Conexión directa con Loki como fuente de datos para mostrar logs en tiempo real.
- **Responsabilidad Principal:** Ofrecer un panel visual para analizar datos de logs y métricas.

#### 2.3.4. Loki (Sistema de Logs)

- **Base de Imagen:** `grafana/loki:2.9.0`
  - Solución ligera y eficiente para gestionar logs centralizados.
- **Configuración Esencial:**
  - Uso de un archivo de configuración personalizado para especificar el formato y almacenamiento de logs.
- **Responsabilidad Principal:** Almacenar logs recolectados por Promtail y servirlos a Grafana.

#### 2.3.5. Promtail (Agente de Logs)

- **Base de Imagen:** `grafana/promtail:2.9.0`
  - Agente encargado de recolectar y enviar logs a Loki.
- **Configuración Esencial:**
  - Uso de un archivo de configuración personalizado para definir las fuentes y etiquetas de logs.
- **Responsabilidad Principal:** Recolectar logs desde el contenedor de la aplicación y otros servicios.

### 2.4. Justificación de la Configuración Seleccionada

La elección de esta configuración se basa en la estabilidad y facilidad de configuración comparada con las alternativas previamente consideradas:

- **Simplicidad en la Configuración:** A diferencia de la pila ELK, la configuración de Graylog junto con MongoDB y Elasticsearch simplifica la gestión de logs, evitando problemas complejos de volúmenes y permisos.
- **Eficiencia en el Monitoreo:** La integración con Grafana y Loki permite una visualización y monitoreo eficiente de los logs y métricas en tiempo real.
- **Escalabilidad y Flexibilidad:** La arquitectura modular facilita la escalabilidad y la adaptación a futuras necesidades sin comprometer la estabilidad del sistema.
- **Facilidad de Uso:** La interfaz web intuitiva de Graylog y Grafana facilita la búsqueda, análisis y visualización de los logs, mejorando la productividad del equipo de desarrollo y operaciones.

Esta configuración garantiza una gestión de logs robusta y eficiente, superando las limitaciones encontradas con otras soluciones como la pila ELK, y proporcionando una base sólida para el monitoreo y análisis continuo de la infraestructura de contenedores.
![Contenedores Grafana y Loki](/docs/images/1.png)
![Visualización Grafana](/docs/images/3.png)


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



## 📋 4. Fichero de Composición (`docker-compose.yaml`)

A continuación, se presenta un ejemplo de configuración de **Docker Compose** para desplegar los contenedores necesarios: `app`, `db`, `grafana`, `loki` y `promtail`. Este archivo facilita la orquestación y gestión de múltiples servicios en un entorno de contenedores.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: app-container
    ports:
      - "5000:5000"
    user: "${UID}:${GID}"
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs
    depends_on:
      - db
      - loki
      - promtail
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/gestion_penas
    networks:
      - grafana_network
    
  db:
    image: postgres:15
    container_name: db-container
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: gestion_penas
    volumes:
      - ./Gestion_Penas.sql:/docker-entrypoint-initdb.d/Gestion_Penas.sql
    ports:
      - "5432:5432"
    networks:
      - grafana_network

  grafana:
    image: grafana/grafana-oss
    container_name: grafana
    restart: unless-stopped
    ports:
      - '3000:3000'
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - grafana_network

  loki:
    image: grafana/loki:2.9.0
    container_name: grafana-loki
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
    ports:
      - "3100:3100"
    networks:
      - grafana_network

  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./logs:/var/log/nginx
      - ./promtail-config.yaml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
    networks:
      - grafana_network

volumes:
  grafana_data:

networks:
  grafana_network:
    driver: bridge
```
### **Puntos Destacados**

#### **app (Contenedor de Aplicación)**

- **Descripción:**  
  Contiene la aplicación principal desarrollada en Python.

- **Características:**
  - **Construcción Personalizada:**  
    Utiliza un `Dockerfile` para construir la imagen desde el contexto actual.
  - **Puertos:**  
    Mapea el puerto `5000` del contenedor al host para acceder a la aplicación.
  - **Volúmenes:**
    - Monta el directorio `./src` en `/app/src` para el código fuente.
    - Monta el directorio `./logs` en `/app/logs` para almacenar los logs generados.
  - **Dependencias:**  
    Depende de los servicios `db`, `loki` y `promtail` para funcionar correctamente.
  - **Variables de Entorno:**  
    Configura la conexión a la base de datos mediante `DATABASE_URL`.
  - **Redes:**  
    Conectado a la red `grafana_network` para comunicarse con otros servicios.

#### **db (Contenedor de Base de Datos)**

- **Descripción:**  
  Base de datos PostgreSQL para almacenar la información estructurada de la aplicación.

- **Características:**
  - **Imagen Oficial:**  
    Utiliza la imagen oficial de PostgreSQL versión `15`.
  - **Credenciales:**  
    Configura el usuario, contraseña y nombre de la base de datos a través de variables de entorno.
  - **Volúmenes:**
    - Monta el script `Gestion_Penas.sql` para inicializar la base de datos con las tablas y datos necesarios.
  - **Puertos:**  
    Expone el puerto `5432` para conexiones externas si es necesario.
  - **Redes:**  
    Conectado a la red `grafana_network`.

#### **grafana (Monitorización)**

- **Descripción:**  
  Herramienta de visualización para métricas y logs, proporcionando dashboards interactivos.

- **Características:**
  - **Imagen Oficial:**  
    Utiliza la versión open-source de Grafana.
  - **Reinicio Automático:**  
    Configurado para reiniciarse automáticamente a menos que se detenga manualmente.
  - **Puertos:**  
    Mapea el puerto `3000` para acceder a la interfaz web de Grafana.
  - **Volúmenes:**
    - Utiliza el volumen `grafana_data` para persistir la configuración y los dashboards creados.
  - **Redes:**  
    Conectado a la red `grafana_network`.

#### **loki (Sistema de Logs)**

- **Descripción:**  
  Solución ligera para la gestión y almacenamiento centralizado de logs.

- **Características:**
  - **Imagen Oficial:**  
    Utiliza la imagen de Loki versión `2.9.0`.
  - **Configuración Personalizada:**  
    Monta un archivo de configuración personalizado `loki-config.yaml`.
  - **Puertos:**  
    Expone el puerto `3100` para recibir logs.
  - **Redes:**  
    Conectado a la red `grafana_network`.

#### **promtail (Agente de Logs)**

- **Descripción:**  
  Agente encargado de recolectar y enviar logs a Loki.

- **Características:**
  - **Imagen Oficial:**  
    Utiliza la imagen de Promtail versión `2.9.0`.
  - **Configuración Personalizada:**  
    Monta el archivo `promtail-config.yaml` para definir las fuentes y etiquetas de logs.
  - **Volúmenes:**
    - Monta el directorio `./logs` para recolectar los logs generados por la aplicación.
  - **Redes:**  
    Conectado a la red `grafana_network`.

### **Consideraciones Adicionales**

- **Volúmenes Persistentes:**
  - **grafana_data:**  
    Asegura que los datos y configuraciones de Grafana persistan incluso si el contenedor se reinicia o elimina.

- **Redes:**
  - **grafana_network:**  
    Utiliza una red de tipo `bridge` para facilitar la comunicación entre los diferentes servicios sin exponerlos innecesariamente al exterior.

### **Ventajas de esta Configuración**

- **Orquestación Simplificada:**  
  Docker Compose gestiona múltiples contenedores, facilitando el despliegue y la gestión de dependencias entre servicios.

- **Persistencia de Datos:**  
  Mediante el uso de volúmenes, se garantiza que los datos críticos como logs y configuraciones se mantengan intactos entre reinicios.

- **Escalabilidad:**  
  La arquitectura modular permite añadir o eliminar servicios con facilidad según las necesidades del proyecto.

- **Aislamiento de Servicios:**  
  Cada contenedor opera de manera independiente, reduciendo riesgos de conflictos y facilitando el mantenimiento.

- **Configuraciones Personalizadas:**  
  La posibilidad de montar archivos de configuración personalizados (`loki-config.yaml`, `promtail-config.yaml`) permite adaptar cada servicio a requisitos específicos.

---


## 📋 5. Implementación y Validación del Clúster

Para garantizar el correcto funcionamiento de los contenedores y su interacción, se han desarrollado pruebas automatizadas que validan tanto la disponibilidad de la aplicación Flask como la conexión con la base de datos. A continuación, se detalla cómo se ha implementado este proceso utilizando **GitHub Actions** para automatizar el despliegue de los contenedores y la ejecución de las pruebas de la API.

### **Despliegue Automatizado de Contenedores en GitHub Actions**

En el flujo de trabajo de **GitHub Actions**, se ha configurado un job que se encarga de desplegar los contenedores definidos en el archivo `docker-compose.yml`. Este job realiza las siguientes acciones:

1. **Clonar el Repositorio**:
    ```yaml
    - name: Clonar el repositorio
      uses: actions/checkout@v4
    ```
    *Descripción*: Utiliza la acción oficial de GitHub para clonar el código fuente del repositorio.

2. **Instalar Docker y Docker Compose**:
    ```yaml
    - name: Instalar Docker
      run: |
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        docker --version

    - name: Instalar Docker Compose
      run: |
        sudo apt-get update
        sudo apt-get install -y docker-compose
        docker-compose --version
    ```
    *Descripción*: Instala Docker y Docker Compose en el runner de GitHub Actions, asegurando que las herramientas necesarias para contenerizar y gestionar los servicios estén disponibles.

3. **Iniciar y Habilitar el Servicio de Docker**:
    ```yaml
    - name: Iniciar Servicio de Docker
      run: |
        sudo systemctl start docker
        sudo systemctl enable docker
    ```
    *Descripción*: Inicia el servicio de Docker y lo habilita para que se inicie automáticamente en futuras sesiones.

4. **Construir y Desplegar los Contenedores**:
    ```yaml
    - name: Construir imágenes de Docker
      run: |
        docker-compose build --no-cache
      working-directory: './'

    - name: Iniciar Docker Compose
      run: docker-compose up -d
      working-directory: './'
    ```
    *Descripción*: Utiliza Docker Compose para construir las imágenes de los servicios definidos en `docker-compose.yml` y los despliega en modo desacoplado (`-d`), permitiendo que se ejecuten en segundo plano.

### **Validación del Funcionamiento del Clúster**

Una vez desplegados los contenedores, es crucial validar que todos los servicios están operativos y se comunican correctamente. Para ello, se han implementado pruebas automatizadas que se ejecutan después de asegurar que los servicios están activos.




1. **Configurar el Entorno Python**:
    ```yaml
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    ```
    *Descripción*: Configura el entorno Python con la versión especificada para ejecutar las pruebas.

2. **Cachear Dependencias de Pip**:
    ```yaml
    - name: Cachear dependencias de pip
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    ```
    *Descripción*: Utiliza la acción de caché de GitHub para almacenar y restaurar las dependencias de `pip`, acelerando el tiempo de instalación en ejecuciones futuras.

3. **Instalar Dependencias**:
    ```yaml
    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then
          pip install -r requirements.txt
        else
          pip install pytest requests
        fi
    ```
    *Descripción*: 
    - Actualiza `pip` a la última versión.
    - Instala las dependencias listadas en `requirements.txt`. Si el archivo no existe, instala paquetes predeterminados como `pytest` y `requests`.

4. **Ejecutar Pruebas Automatizadas**:
    ```yaml
    - name: Ejecutar Pruebas
      run: |
        sudo chown -R $USER:$USER logs
        chmod 777 logs
        ls -l 
        pytest tests/*
    ```
    *Descripción*: Ejecuta las pruebas utilizando `pytest`, buscando en el directorio `tests/`. Estas pruebas validan:
    - **Disponibilidad de la Aplicación Flask**: Comprueba que la API está en funcionamiento y responde a las solicitudes.
    - **Conexión con la Base de Datos**: Asegura que la aplicación puede establecer una conexión exitosa con la base de datos configurada.
    - **Implicitamente comprueban la conexión entre los logs si no da error**



## 📋 6. Publicación en GitHub Packages y Flujo CI/CD

En esta sección, se detalla cómo se ha configurado **GitHub Actions** para automatizar la construcción y publicación de imágenes Docker en **GitHub Packages**, integrando los principios de **Integración Continua** y **Despliegue Continuo** (CI/CD). Este proceso asegura la calidad y coherencia de la aplicación mediante la ejecución automática de pruebas y la publicación de imágenes solo si todas las pruebas son exitosas.

### **Descripción General del Flujo de Trabajo**

Cada vez que se realiza un _push_ a las ramas principales (`main` y `dev`), se activa un _pipeline_ que realiza las siguientes acciones:

1. **Construcción de la Imagen Docker**: Se construye la imagen Docker de la aplicación utilizando el `Dockerfile` proporcionado.
2. **Ejecución de Pruebas de Validación**: Se ejecutan pruebas automatizadas para verificar que la aplicación funciona correctamente.
3. **Publicación de la Imagen en GitHub Packages**: Si todas las pruebas pasan exitosamente, la imagen Docker se publica en GitHub Packages, asegurando que solo se desplieguen imágenes verificadas y de confianza.

### **Configuración en `docker-publish.yml`**

El archivo `docker-publish.yml` contiene la configuración necesaria para implementar este flujo de trabajo en **GitHub Actions**. A continuación, se presenta el contenido del archivo con una explicación de sus componentes principales.

```yaml
name: Build, Test, and Publish Docker Image 

on:
  push:
    branches:
      - main
      - dev

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest

    env:
      IMAGE_NAME: ghcr.io/adrianoggm/cc.2024-2025.gestion-de-penas-de-futbol
      IMAGE_TAG: ${{ github.sha }}

    steps:
      # Clonar el repositorio
      - name: Clonar el repositorio
        uses: actions/checkout@v4

      # Instalar Docker
      - name: Instalar Docker
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release

          # Agregar la clave GPG oficial de Docker
          curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

          # Configurar el repositorio estable de Docker
          echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

          sudo apt-get update
          sudo apt-get install -y docker-ce docker-ce-cli containerd.io

          # Verificar instalación de Docker
          docker --version

      # Instalar Docker Compose usando apt-get
      - name: Instalar Docker Compose
        run: |
          sudo apt-get update
          sudo apt-get install -y docker-compose
          docker-compose --version

      # Iniciar y habilitar el servicio de Docker
      - name: Iniciar Servicio de Docker
        run: |
          sudo systemctl start docker
          sudo systemctl enable docker

      # Construir las imágenes de Docker con 'docker-compose'
      - name: Construir imágenes de Docker
        run: |
          docker-compose build --no-cache
        working-directory: './'

      # Iniciar Docker Compose en modo desacoplado
      - name: Iniciar Docker Compose
        run: docker-compose up -d
        working-directory: './'

      # Esperar 20 segundos para que los servicios se inicien
      - name: Esperar a que los servicios estén listos
        run: |
          echo "Esperando 20 segundos para que los servicios se inicien..."
          sleep 20
          echo "Tiempo de espera completado. Asumiendo que los servicios están activos."
          docker-compose ps 
      # Configurar Python
      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      # Cachear dependencias de pip
      - name: Cachear dependencias de pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      # Instalar dependencias
      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            pip install pytest requests
          fi

      # Ejecutar Pruebas
      - name: Ejecutar Pruebas
        run: |
          sudo chown -R $USER:$USER logs
          chmod 777 logs
          ls -l 
          pytest 

      # Construir Imagen Docker
      - name: Construir Imagen Docker
        run: |
          docker build -t $IMAGE_NAME:$IMAGE_TAG .
          docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
        working-directory: './'

      # Iniciar Sesión en GitHub Container Registry
      - name: Iniciar Sesión en GitHub Container Registry
        run: echo ${{ secrets.GHCR_PASSWORD }} | docker login ghcr.io -u ${{ secrets.GHCR_USERNAME }} --password-stdin

      # Push de la Imagen Docker
      - name: Push de la Imagen Docker
        run: |
          docker push $IMAGE_NAME:$IMAGE_TAG
          docker push $IMAGE_NAME:latest

      # Desplegar y Limpiar Docker Compose
      - name: Desplegar y Limpiar Docker Compose
        if: always()
        run: docker-compose down
        working-directory: './'

```
---

### Componentes Clave del Flujo de Trabajo

#### Trigger del Flujo de Trabajo:

```yaml
on:
  push:
    branches:
      - main
      - dev
```
#### Variables de Entorno:
``` yaml
env:
  IMAGE_NAME: ghcr.io/adrianoggm/cc.2024-2025.gestion-de-penas-de-futbol
  IMAGE_TAG: ${{ github.sha }}

```
Descripción: Define las variables de entorno IMAGE_NAME y IMAGE_TAG que se utilizan para etiquetar las imágenes Docker.
### Pasos del Flujo de Trabajo:
#### Clonar el Repositorio: Obtiene el código fuente necesario para construir los contenedores.
```yaml
- name: Clonar el repositorio
  uses: actions/checkout@v4
```
#### Instalar Docker y Docker Compose: Prepara el entorno con las herramientas necesarias para manejar contenedores.
```yaml
- name: Instalar Docker
  run: |
    sudo apt-get update
    sudo apt-get install -y ...

- name: Instalar Docker Compose
  run: |
    sudo apt-get update
    sudo apt-get install -y docker-compose
    docker-compose --version
```
#### Iniciar el Servicio de Docker: Asegura que Docker está en funcionamiento.
```yaml
- name: Iniciar Servicio de Docker
  run: |
    sudo systemctl start docker
    sudo systemctl enable docker
  ```
#### Construir y Desplegar Contenedores: 
Utiliza Docker Compose para construir las imágenes y desplegar los servicios.
```yaml

- name: Construir imágenes de Docker
  run: |
    docker-compose build --no-cache
  working-directory: './'

- name: Iniciar Docker Compose
  run: docker-compose up -d
  working-directory: './'
```
#### Esperar y Verificar Servicios: Introduce una espera para permitir que los servicios se inicien y verifica su estado.
```yaml
- name: Esperar a que los servicios estén listos
  run: |
    echo "Esperando 20 segundos..."
    sleep 20
    echo "Tiempo de espera completado."
    docker-compose ps 
```
#### Configurar Python y Cachear Dependencias: Prepara el entorno Python y optimiza la instalación de dependencias.
``` yaml

- name: Configurar Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.12'

- name: Cachear dependencias de pip
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```
#### Instalar Dependencias: 
Actualiza pip y instala las dependencias necesarias para ejecutar las pruebas.
``` yaml
- name: Instalar dependencias
  run: |
    python -m pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    else
      pip install pytest requests
  ```
#### Ejecutar Pruebas Automatizadas: 
Realiza pruebas automatizadas para validar el funcionamiento de la aplicación.
``` yaml
- name: Ejecutar Pruebas
  run: |
    sudo chown -R $USER:$USER logs
    chmod 777 logs
    ls -l 
    pytest 
  ```
#### Construir y Publicar Imagen Docker: 
Construye la imagen final, la etiqueta y la publica en GitHub Container Registry.
``` yaml
- name: Construir Imagen Docker
  run: |
    docker build -t $IMAGE_NAME:$IMAGE_TAG .
    docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
  working-directory: './'

- name: Iniciar Sesión en GitHub Container Registry
  run: echo ${{ secrets.GHCR_PASSWORD }} | docker login ghcr.io -u ${{ secrets.GHCR_USERNAME }} --password-stdin

- name: Push de la Imagen Docker
  run: |
    docker push $IMAGE_NAME:$IMAGE_TAG
    docker push $IMAGE_NAME:latest
```
### Desplegar y Limpiar:
#### Detiene y elimina los contenedores desplegados, asegurando una limpieza adecuada.
```yaml
- name: Desplegar y Limpiar Docker Compose
  if: always()
  run: docker-compose down
  working-directory: './'
  ```
## Integración de CI/CD

Este flujo de trabajo implementa los principios de **Integración Continua** y **Despliegue Continuo** (CI/CD) al automatizar todo el proceso desde la construcción hasta la publicación de las imágenes Docker. Esto garantiza que cada cambio en el código fuente se pruebe y despliegue de manera consistente y confiable, manteniendo altos estándares de calidad y facilitando un desarrollo ágil y eficiente.

### Beneficios de Esta Configuración

- **Automatización Total**: Reduce la intervención manual, minimizando errores y acelerando el proceso de despliegue.
- **Validación Continua**: Asegura que cada push al repositorio pasa por un riguroso proceso de pruebas antes de ser desplegado.
- **Consistencia y Calidad**: Mantiene la coherencia en las versiones de las imágenes y la calidad del código mediante pruebas automatizadas.
- **Facilidad de Despliegue**: Simplifica el proceso de publicación de imágenes, permitiendo un despliegue rápido y seguro en diferentes entornos.

### Conclusión

La configuración de **GitHub Actions** para la construcción y publicación de imágenes Docker en **GitHub Packages** es una parte esencial del flujo de trabajo de CI/CD, garantizando que la aplicación se mantenga en un estado de alta calidad y esté siempre lista para ser desplegada en producción. Esta automatización no solo mejora la eficiencia del desarrollo, sino que también proporciona una capa adicional de confianza en la estabilidad y funcionalidad de la aplicación.

**Nota** (se ha eliminado el yml anterior que probaba en el entorno local la aplicación ya que eran pruebas redundantes que ya realiza este Action).