# Gestión de Peñas y Ligas Individuales Deportivas - **Composición de Servicios** 🏗️

> **Versión 0.1**

Este documento corresponde al **Hito 4** del proyecto de **gestión de peñas y ligas individuales deportivas**. Durante este hito, el objetivo principal ha sido **contenedizar** la aplicación y orquestar los diferentes servicios que la componen, basándonos en la arquitectura de microservicios iniciada en el **Hito 3** y los avances en integración continua del **Hito 2**.

---

## 📋 Resumen de Actividades del Hito 4 🚀

En este hito, hemos llevado la aplicación **Python** existente —que abarca la lógica de negocio y los servicios básicos— a un entorno **contenedorizado**, haciendo uso de herramientas como **Docker** y **Docker Compose**. Este paso nos permite escalar la aplicación, simplificar la configuración y asegurar la coherencia de entornos entre desarrollo y producción.

Además, se ha reforzado la lógica de orquestación de los contenedores con un enfoque en **módulos independientes**:  
1. **Contenedor de la Aplicación (App Service)**  
2. **Contenedor de Logs (Logging Service)**  
3. **Contenedor de Base de Datos (DB Service)**  

Gracias a esta arquitectura, cada contenedor se encarga de una responsabilidad clara, permitiendo mayor flexibilidad y escalabilidad.

---

## Contenedores y Servicios Orquestados ⚙️

A continuación, se describen los contenedores y servicios incluidos en esta fase del proyecto, detallando su propósito y las tecnologías empleadas.

### 1. Contenedor de la Aplicación (App Service)
- **Propósito**: Ejecutar el núcleo de la aplicación (lógica de negocio, API y vistas web).  
- **Tecnología Base**:  
  - **Python 3.12** como entorno principal.  
  - **Flask** para la gestión de endpoints y vistas.  
- **Configuración Clave**:  
  - **Dockerfile** independiente que incluye dependencias específicas (`requirements.txt`).  
  - Exposición del puerto `5000` para el servicio HTTP, configurable con variables de entorno.

### 2. Contenedor de Logs (Logging Service)
- **Propósito**: Centralizar y gestionar los logs generados por el sistema.  
- **Tecnología Base**:  
  - **Alpine Linux**, utilizado para gestionar de forma eficiente los logs.  
- **Configuración Clave**:  
  - Montaje de volúmenes para recopilar logs desde los otros contenedores.  
  - Logs persistentes que se sincronizan con el entorno de desarrollo.

### 3. Contenedor de Base de Datos (DB Service)
- **Propósito**: Proveer una base de datos persistente y escalable para almacenar información de la aplicación (usuarios, peñas, partidos, resultados, etc.).  
- **Tecnología Base**:  
  - **PostgreSQL 15** como sistema de gestión de bases de datos.  
- **Configuración Clave**:  
  - Variables de entorno para definir credenciales seguras.  
  - Volumen dedicado para garantizar la persistencia de datos incluso en caso de reinicio del contenedor.

---

## Dockerfile y Publicación en GitHub Packages 📦

Para cada contenedor principal se ha creado un **Dockerfile** que define las dependencias, las variables de entorno y los pasos de compilación y ejecución. Algunos puntos esenciales:

1. **Imagen Base**  
   - Se seleccionó una imagen ligera y oficial (`python:3.12-slim`) para el contenedor de la aplicación.  
   - Para la base de datos, se utiliza la imagen oficial de **PostgreSQL** desde Docker Hub.  

2. **Instalación de Dependencias**  
   - Se utiliza `requirements.txt` para instalar librerías esenciales como Flask y SQLAlchemy.  

3. **Copia del Código Fuente**  
   - El código fuente de la aplicación se copia dentro del contenedor.  

4. **Ejecución de la Aplicación**  
   - El comando `CMD` ejecuta el servidor Flask, exponiendo el servicio en el puerto `5000`.

Adicionalmente, se configuró **GitHub Actions** para subir automáticamente estas imágenes a **GitHub Packages**. Este flujo CI/CD incluye los siguientes pasos:

- Construcción de las imágenes Docker para cada contenedor.  
- Ejecución de pruebas automatizadas para validar los servicios.  
- Publicación de las imágenes Docker en GitHub Packages tras pasar las validaciones.

---

## Fichero de Composición - `docker-compose.yaml` 🗄️

El archivo de composición (`docker-compose.yaml`) se encarga de orquestar los contenedores y definir cómo deben interactuar. Los puntos más relevantes incluyen:

1. **Redes**  
   - Uso de una red tipo `bridge` para permitir la comunicación entre contenedores (App ↔ DB ↔ Logs).  

2. **Volúmenes**  
   - Volumen persistente para la base de datos y almacenamiento de logs.

3. **Dependencias**  
   - Uso de `depends_on` para asegurar que la base de datos esté lista antes de iniciar la aplicación.

4. **Configuración de Variables de Entorno**  
   - Configuración de credenciales de la base de datos y personalización del puerto de la aplicación.

---

## Tests Implementados para Validar la Orquestación 🧪

Durante este hito, se han implementado pruebas específicas para garantizar el correcto despliegue y la comunicación entre contenedores:

1. **Test de Conexión a la Base de Datos**  
   - Verifica que la aplicación pueda conectarse al contenedor de PostgreSQL y realizar consultas básicas.  

2. **Test de Logs**  
   - Asegura que los logs generados por la aplicación se capturen correctamente en el contenedor de logs.

3. **Test de Endpoint de Salud**  
   - Comprueba que la ruta `/health` de la aplicación está accesible, indicando que el servicio se ejecuta correctamente.

Estos tests se ejecutan automáticamente como parte del pipeline de integración continua definido en el **Hito 2**.

---

## 📝 Implementación de Logs en la Arquitectura Contenedorizada

Se ha continuado el desarrollo iniciado en el hito anterior para centralizar la gestión de logs:

1. **Separación de Contenedores**  
   - Los logs de la aplicación y la base de datos se recopilan y gestionan en un contenedor independiente.  

2. **Persistencia y Análisis**  
   - Los datos de logs se almacenan en volúmenes persistentes para análisis posterior.  

3. **Documentación**  
   - La configuración y el análisis de logs están documentados en:  
     **[Documentación Logs](/LogsContenedores.md)**

---

## 🎯 Conclusión

Con el **Hito 4**, la aplicación se ha transformado en un sistema completamente **contenedorizado**, mejorando su escalabilidad, replicabilidad y mantenimiento. La orquestación mediante **Docker Compose** y la publicación automatizada en **GitHub Packages** refuerzan la integración continua y el despliegue continuo dentro del proyecto.

A medida que el sistema evolucione, se incluirán nuevos servicios y contenedores, manteniendo los principios de modularidad y escalabilidad planteados desde el inicio del proyecto.

