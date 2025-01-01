# Gestión de Peñas y Ligas Individuales Deportivas - **Composición de Servicios** 🏗️

> **Versión 0.1**

Este documento corresponde al **Hito 4** del proyecto de **gestión de peñas y ligas individuales deportivas**. Durante este hito, el objetivo principal ha sido **contenedizar** la aplicación y orquestar los diferentes servicios que la componen, basándonos en la arquitectura de microservicios iniciada en el **Hito 3** y los avances en integración continua del **Hito 2**.

---

## 📋 1,5 puntos: Documentación y Justificación de la Estructura del Clúster de Contenedores

El clúster está compuesto por tres servicios principales, cada uno con una responsabilidad específica. La estructura del clúster está diseñada para facilitar la escalabilidad y el mantenimiento de la aplicación:

1. **App (Contenedor de Aplicación)**:
   - Ejecuta la lógica de la aplicación desarrollada en Flask, incluyendo la API y las vistas web.
   - Responsable de procesar solicitudes HTTP y realizar consultas a la base de datos.

2. **DB (Contenedor de Base de Datos)**:
   - Implementado con PostgreSQL para garantizar un sistema de almacenamiento fiable y persistente.
   - Utilizado para almacenar datos críticos como usuarios, partidos y estadísticas.

3. **Logs (Contenedor de Logs)**:
   - Encargado de gestionar y centralizar los logs generados por los otros contenedores.
   - Garantiza que los datos de logs estén organizados y accesibles para análisis.

El diseño modular asegura que cada servicio sea independiente, mejorando la mantenibilidad y permitiendo la reutilización de componentes.

---

## 📋 1,5 puntos: Documentación y Justificación de la Configuración de Cada Contenedor

### **App (Contenedor de Aplicación)**
- **Base**: Imagen `python:3.12-slim`.
- **Justificación**: Imagen ligera que incluye todo lo necesario para ejecutar aplicaciones en Python, reduciendo el tiempo de despliegue.
- **Configuración**:
  - Usa `requirements.txt` para instalar dependencias como Flask y SQLAlchemy.
  - Expone el puerto `5000` para servir las solicitudes HTTP.

### **DB (Contenedor de Base de Datos)**
- **Base**: Imagen oficial `postgres:15`.
- **Justificación**: Imagen optimizada y confiable para entornos de producción.
- **Configuración**:
  - Variables de entorno para configurar credenciales de usuario (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
  - Volumen asignado para garantizar la persistencia de datos.

### **Logs (Contenedor de Logs)**
- **Base**: Imagen `alpine`.
- **Justificación**: Su ligereza reduce el consumo de recursos y es ideal para operaciones básicas de logging.
- **Configuración**:
  - Montaje de volúmenes para almacenar logs generados por la aplicación y la base de datos.

---

## 📋 2 puntos: Documentación del Dockerfile del Contenedor con la Lógica de la Aplicación

El **Dockerfile** del contenedor de la aplicación define los pasos necesarios para construir y ejecutar el servicio:

1. **Imagen Base**:
   - Se utiliza `python:3.12-slim` para garantizar compatibilidad con Python 3.12 y optimizar el tamaño de la imagen.

2. **Instalación de Dependencias**:
   - Se copian los archivos `requirements.txt` al contenedor.
   - Se instalan las dependencias mediante `pip`.

3. **Copia del Código Fuente**:
   - El código fuente de la aplicación se copia al directorio `/app` del contenedor.

4. **Ejecución de la Aplicación**:
   - El contenedor inicia el servidor Flask utilizando el comando `python app.py`.

---

## 📋 1,5 puntos: Contenedor Subido Correctamente a GitHub Packages y Documentación de la Actualización Automática

### **Publicación Automática en GitHub Packages**
Se ha configurado un flujo CI/CD en GitHub Actions para automatizar la construcción y publicación del contenedor de la aplicación:

1. **Construcción de la Imagen**:
   - El workflow se ejecuta automáticamente con cada push a las ramas `main` o `dev`.

2. **Pruebas Automatizadas**:
   - Antes de publicar la imagen, se ejecutan pruebas para validar la funcionalidad del clúster.

3. **Publicación**:
   - La imagen se sube a **GitHub Container Registry (GHCR)** bajo el nombre:
     ```
     ghcr.io/<usuario>/cc.2024-2025.gestion-de-penas-de-futbol:latest
     ```

📄 **Documentación del flujo CI/CD**:
- Configurado en el archivo: `.github/workflows/docker-publish.yml`.

---

## 📋 2 puntos: Documentación del Fichero de Composición del Clúster de Contenedores (`docker-compose.yaml`)

El archivo `docker-compose.yaml` define la orquestación de los servicios. Sus principales características son:

1. **Servicios**:
   - `app`: Ejecuta la aplicación Flask y se conecta al servicio `db`.
   - `db`: Contenedor PostgreSQL para almacenamiento de datos.
   - `logs`: Contenedor para centralizar logs generados por `app` y `db`.

2. **Redes**:
   - Se define una red `bridge` para permitir la comunicación interna entre los contenedores.

3. **Volúmenes**:
   - Volumen persistente para la base de datos (`db_data`).
   - Directorio de logs montado en el contenedor `logs`.

4. **Dependencias**:
   - Uso de `depends_on` para garantizar que el contenedor de la base de datos esté listo antes de iniciar la aplicación.

---

## 📋 1,5 puntos: Correcta Implementación y Ejecución de los Tests para Validar el Clúster

Se han desarrollado pruebas específicas para garantizar el correcto despliegue del clúster:

1. **Test de Conexión a la Base de Datos**:
   - Verifica que la aplicación pueda conectarse al contenedor PostgreSQL y realizar consultas.

2. **Test de Logs**:
   - Comprueba que los logs generados por la aplicación y la base de datos son capturados correctamente por el contenedor de logs.

3. **Test de Endpoint Salud (`/health`)**:
   - Realiza una solicitud HTTP para confirmar que el servicio de la aplicación está operativo.

📄 **Ejecución de Tests**:
- Automatizados como parte del flujo CI/CD.
- Implementados en el script `test_cluster.py`.

---

## 🎯 Conclusión

Con este **Hito 4**, el proyecto ha evolucionado hacia un sistema completamente **contenedorizado**, lo que mejora la escalabilidad, el mantenimiento y la replicabilidad. La integración de pruebas automáticas y la publicación de imágenes en **GitHub Packages** refuerzan la calidad del sistema y facilitan su despliegue.

Este avance representa un paso importante en la implementación de conceptos clave de **Cloud Computing**, acercándonos a un sistema robusto y escalable para la gestión de peñas y ligas individuales deportivas.
