# Proyecto de gestión de peñas y ligas individuales deportivas (2024-2025)⚽🏀
> Versión 0.1

Este repositorio contiene el proyecto de *gestión de peñas y ligas individuales deportivas para la asignatura de **Cloud Computing** del máster de la UGR.

## Descripción del Proyecto

El objetivo del proyecto es desarrollar un sistema para la **gestión de peñas y ligas individuales deportivas**, donde se podrá identificar y gestionar tres tipos de usuarios: **Administrador de la Peña**, **Usuario/Jugador** y **Usuario no registrado**.
En la actualidad existen multitud de aplicaciones de ligas para equipos pero apenas ninguna para peñas deportivas o torneos individuales. Esta app busca dar una respuesta basándose en la siguiente propuesta:
### Tipos de Usuarios

1. **Administrador de la Peña**:
   - Tendrá acceso completo a todas las funcionalidades de la aplicación.
   - Será el responsable de parametrizar e insertar los resultados de cada jornada.
   - Para acceder a la plataforma, el administrador debe iniciar sesión con su **nombre de usuario**, **contraseña** y un **código de peña**.
   - Funciones principales:
     - Gestionar los jugadores de la peña.
     - Actualizar resultados de los partidos.
     - Configurar la peña y realizar ajustes generales.

2. **Usuario/Jugador**:
   - Puede editar su perfil personal, incluyendo su **nombre**, **foto** y **descripción**.
   - Requiere nombre de usuario, contraseña y código de peña para iniciar sesión.
   - Los jugadores pueden aportar su valoración del partido, lo que ayudará a actualizar estadísticas y equilibrar los equipos para futuros partidos mediante un sistema de **draft**.

3. **Usuario no registrado**:
   - No necesita iniciar sesión.
   - Podrá acceder a información pública de la peña mediante el **código de peña**, incluyendo:
     - Clasificación de la peña.
     - Historial de partidos.
     - Estadísticas de goleadores.
     - Perfiles públicos de los jugadores.

### Funcionalidades del Sistema

- **Gestión de jugadores**: Los jugadores son añadidos por el administrador, y cada jugador es único en cada peña (aunque puede estar en varias peñas diferentes).
- **Draft recomendado**: Basado en las valoraciones y el porcentaje de victorias de los jugadores convocados.
- **Historial de temporadas**: Se podrán importar jugadores de temporadas anteriores y acceder a un historial de temporadas pasadas.
- **Estadísticas detalladas**: El sistema mostrará estadísticas interesantes y organizadas de los jugadores y equipos.
- **Multipeña**: Un jugador puede ver a qué peñas está adscrito y sus estadísticas en cada una de ellas.

### Arquitectura del Sistema

La arquitectura propuesta para garantizar la modularidad, fiabilidad y rendimiento de la aplicación web incluirá tres componentes principales:
1. Aplicación web (basada en **Flask**).
2. Base de datos principal (usando **SQLite**).
3. Base de datos duplicada para asegurar la disponibilidad de los datos.

## Historias de Usuario (User Stories) 📖

Para cada microservicio del proyecto se ha definido un **milestone**.🌑

### Primer Milestone: Funciones Básicas del Administrador
- **[HU-01]** Como administrador quiero poder darme de alta en el sistema.
- **[HU-02]** Como administrador quiero dar de alta una peña para gestionar.
- **[HU-03]** Como administrador quiero modificar la información de una peña.
- **[HU-04]** Como administrador quiero dar de alta a un jugador en la peña.

### Segundo Milestone: Funciones Avanzadas del Administrador
- **[HU-05]** Como administrador quiero planificar un partido y definir su alineación.
- **[HU-06]** Como administrador quiero añadir o modificar el resultado de un partido.
- **[HU-07]** Como administrador quiero añadir o modificar las estadísticas de los jugadores tras un partido.
- **[HU-08]** Como administrador quiero poder gestionar las deudas de los jugadores.

### Tercer Milestone: Funciones del Usuario
- **[HU-09]** Como usuario quiero darme de alta en el sistema.
- **[HU-10]** Como usuario quiero ver la tabla de clasificación de la peña.
- **[HU-11]** Como usuario quiero ver las estadísticas de los jugadores de la peña.
- **[HU-12]** Como usuario quiero editar mi foto de perfil y apodo.
- **[HU-13]** Como usuario quiero consultar los resultados de los partidos jugados.
- **[HU-14]** Como usuario quiero consultar mi deuda en las peñas a las que estoy asociado.

## Tecnologías Utilizadas

- **Flask** para la creación de la aplicación web. 
- **SQLite** como base de datos relacional para el almacenamiento de datos.
- **HTML/CSS** para la creación de la interfaz de usuario.
- **Python** para la lógica de negocio y los microservicios.

## Arquitectura

La arquitectura está diseñada para garantizar modularidad y fiabilidad. Se basa en una arquitectura de 3 componentes:
1. **Aplicación Web (Flask)**.
2. **Base de Datos (SQLite)**.
3. **Base de Datos Duplicada** para respaldo.

![setup](docs/images/Arquictectura.png)
---

Este proyecto tiene como objetivo garantizar una gestión eficiente y equilibrada de las peñas de fútbol, ofreciendo un sistema dinámico, intuitivo y accesible tanto para administradores como para jugadores y usuarios no registrados.

## Documentación Adicional 📘

En esta sección irá todo lo referente a la configuración y licencia del proyecto.

1. [Licencia](/LICENSE)
2. [Configuración del entorno](/Enviroment_setup.md)
