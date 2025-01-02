# Proyecto de Gestión de Peñas y Ligas Individuales Deportivas (2024-2025)

Este repositorio contiene el desarrollo del proyecto para la **gestión de peñas deportivas** y **ligas individuales**, llevado a cabo en la asignatura de **Cloud Computing** del Máster en la UGR.

---

## 📋 Descripción del Proyecto

El propósito del proyecto es construir un sistema que permita gestionar de manera eficiente **peñas deportivas** y **ligas individuales**. La aplicación distingue entre tres tipos de usuarios:

- **Administrador de la Peña**: Responsable de gestionar su peña, incluyendo jugadores, temporadas y partidos.
- **Usuario/Jugador**: Miembro de la peña que puede consultar estadísticas, resultados y participar en partidos.
- **Usuario no registrado**: Usuario externo con acceso limitado a información pública.

Este proyecto surge ante la necesidad de desarrollar aplicaciones específicas para **peñas deportivas** y **torneos individuales**, un ámbito con soluciones actuales limitadas o poco especializadas.

La documentación se organiza en los siguientes hitos:

---

## 📝 Descripción del Problema

En este apartado se definen los **alcances**, **objetivos**, **arquitectura**, **licencias** y el **entorno tecnológico** del proyecto.

📄 **Acceso a la documentación completa:**
- [Hito 1 - Documentación Base](docs/hitos/hito1.md)

---

## 🛠️ Integración Continua

Este hito se centra en el diseño e implementación de un flujo de **integración continua**, que incluye:

- **Automatización de pruebas** para asegurar la calidad del software.
- **Ejecución de pipelines** a través de herramientas como GitHub Actions.
- Estrategias de **detección temprana de errores** durante el ciclo de desarrollo.

📄 **Acceso a la documentación completa:**
- [Hito 2 - Integración Continua](docs/hitos/hito2.md)

---

## 🏗️ Diseño de Microservicios

En este hito se describe cómo el proyecto se ha concebido bajo una **arquitectura de microservicios**, incluyendo:

- **Descomposición de funcionalidades** en servicios independientes.
- Diseño de **interfaces claras y desacopladas**.
- Cambios clave respecto a la versión monolítica inicial.

📄 **Acceso a la documentación completa:**
- [Hito 3 - Diseño de Microservicios](docs/hitos/hito3.md)

---

## 📝 Hito 4: Composición de Servicios

En este hito se profundiza en cómo se realiza la **composición y orquestación de contenedores** para optimizar el despliegue y la escalabilidad de la aplicación. Se detalla la estructura del clúster y la configuración de cada contenedor, justificando las decisiones de diseño tomadas.

**Aspectos principales:**

1. **Estructura del clúster de contenedores**  
   - Se explica la **arquitectura general** y cómo se distribuyen las distintas funcionalidades en diferentes contenedores.  
   - Se justifica por qué cada servicio se ejecuta de forma separada, resaltando la modularidad y la escalabilidad.

2. **Configuración individual de los contenedores**  
   - Se documenta la **imagen base** elegida para cada contenedor.  
   - Se detallan las **dependencias**, **volúmenes** y **puertos** necesarios.  
   - Se explica cómo cada contenedor está configurado para cumplir con su función específica.

3. **Dockerfile de la aplicación**  
   - Se presenta el **Dockerfile principal** y se justifican cada una de las instrucciones empleadas.  
   - Se describen las dependencias y la lógica que permiten la ejecución del núcleo de la aplicación.

4. **Publicación en GitHub Packages**  
   - Se explica el **flujo de publicación** de los contenedores en GitHub Packages.  
   - Se muestra cómo se actualizan automáticamente las imágenes y se integra este proceso con la **integración continua**.

5. **Fichero de composición (`compose.yaml`)**  
   - Se ofrece la documentación del **archivo de orquestación** que conecta los distintos contenedores.  
   - Se detalla cómo se definen redes, volúmenes y la comunicación entre servicios.

6. **Validación y tests del clúster**  
   - Se muestra la **implementación de pruebas** que garantizan el correcto funcionamiento de la orquestación de contenedores.  
   - Se describen los **criterios de éxito** de los tests y la estrategia de verificación.

📄 **Acceso a la documentación completa:**
- [Hito 4 - Composición de Servicios](docs/hitos/hito4.md)
