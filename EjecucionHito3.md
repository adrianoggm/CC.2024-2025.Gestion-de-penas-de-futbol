# Ejecución de la Aplicación 🚀

Este documento detalla cómo ejecutar y explorar las nuevas funcionalidades implementadas en la aplicación de gestión de peñas y ligas deportivas. Para instrucciones sobre la configuración inicial y las funcionalidades básicas, puedes consultar la documentación del **Hito 2** en el siguiente enlace: **[Ejecución de la App](/Ejecucion.md)**.

En esta guía nos enfocaremos en las nuevas funcionalidades añadidas en el **Hito 3**, como la gestión de temporadas, el manejo de partidos y las mejoras en la experiencia del administrador.

---

## **Login Admin 🔑**

Al iniciar sesión como administrador, serás redirigido al **Admin Dashboard**, desde donde podrás gestionar jugadores, partidos y temporadas. 

Para acceder a la peña de demostración, utiliza las siguientes credenciales:
- **Usuario**: `admin`
- **Contraseña**: `1` (esta contraseña está cifrada en la base de datos, por lo que es fundamental recordarla, ya que actualmente no existe una opción de recuperación de contraseñas).

### Vista del Admin Dashboard
Al iniciar sesión correctamente, accederás a una vista como esta:
![Admin Dashboard](/docs/images/Panel-admin2.png)

Aquí puedes observar las opciones disponibles para gestionar jugadores, temporadas y partidos.

---

## **Gestionar Temporadas**

En esta sección, se muestra una lista de temporadas, ordenadas por las más recientes. Desde aquí, puedes:
- **Añadir Temporadas**: Definir nuevas temporadas con fechas de inicio y fin.
- **Eliminar Temporadas**: Gestionar temporadas existentes eliminándolas según sea necesario.

### Vista de Gestión de Temporadas
![Gestionar Temporadas](/docs/images/gestionar_temporadas.png)

---

## **Añadir Temporadas**

Al añadir una temporada, se debe definir:
- **Fecha de inicio**: Día en el que la temporada comienza.
- **Fecha de fin**: Día en el que la temporada termina.

Esta funcionalidad asegura que las temporadas queden registradas en la base de datos, listas para ser utilizadas en la planificación de partidos y visualización de estadísticas.

### Vista de Añadir Temporadas
![Añadir Temporadas](/docs/images/anadirtemp.png)

---

## **Visualización de Temporada**

Dentro de una temporada específica, puedes ver:
- **Clasificación de jugadores**: Tabla con estadísticas acumuladas como victorias, empates y derrotas.

### Vista de Clasificación
![Clasificación Temporada](/docs/images/Clasificacion.png)

---

## **Draft de Partido**

La funcionalidad de **Draft de Partido** permite:
- **Convocar jugadores** para un partido.
- **Dividir jugadores en equipos**.
- Definir **estadísticas básicas** de los jugadores (goles y asistencias) directamente desde la interfaz.

Actualmente, existe un problema conocido relacionado con la identificación de partidos asociados a una temporada específica. Este error será corregido en iteraciones futuras.

### Vista de Draft de Partido
#### Selección de Convocados
![Convocados](/docs/images/convocados.png)

#### Asignación de Equipos
![Partido](/docs/images/partido.png)

---

## **Visualización de Temporada Tras Partidos**

Tras la creación de partidos, la visualización de temporada permite:
- Observar el impacto de los resultados en la clasificación general.
- Analizar las estadísticas actualizadas.

### Vista Actualizada de Clasificación
![Clasificación Actualizada](/docs/images/Clasificacion2.png)

---

## **Visualización de un Partido**

En la sección de **Visualización de Partido**, se pueden ver:
- Detalles del partido jugado.
- Estadísticas registradas por jugador, como goles y asistencias.

Sin embargo, como se mencionó anteriormente, algunas estadísticas no se registran correctamente debido a un problema de identificación entre temporadas y partidos. Este problema está en proceso de resolución.

### Vista de Visualización de Partido
![Visualizar Partido](/docs/images/VisualizarPartido.png)

---

## **Conclusión**

El Hito 3 amplía significativamente las capacidades de la aplicación, introduciendo funcionalidades clave como la gestión de temporadas y partidos, así como mejoras en la experiencia del administrador. Aunque aún hay detalles por pulir, estas implementaciones sientan las bases para futuras mejoras y un sistema robusto de gestión de peñas deportivas.
