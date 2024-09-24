# CC.2024-2025.Gestion de penas de futbol
 Repositorio con el proyecto de gestión de peñas de fútbol para la asignatura Cloud Computing master UGR

-Se va a realizar un sistema de gestión de peñas de fútbol. En el se podrá identificar los siguientes usuarios: Administrador de la Peña, Usuario . 
El Administrador de la Peña será capaz de usar todos los elementos de los que dispondrá la aplicación, adicionalmente será el encargado de parametrizar  e insertar los resultados cada jornada este podrá entrar mediante un nombre de usuario contraseña y código de peña.
El Jugador : será capaz de editar su nombre en la peña su foto y descripción.Nombre de usuario contraseña y código de peña.
Usuario no registrado no necesita de login, únicamente mediante el código de peña será capaz de acceder a la clasificación, historial de partidos , estadísticas de goleadores y perfil de los jugadores .

La peña contará con un número indetermiando de jugadores añadidos por el Administrador de la Peña, cada Jugador será único para cada peña indistíntamente que exista en varias peñas.
-Será posible realizar de acuerdo a los jugadores "convocados" un draft recomendado de acuerdo a porcentaje de victorias y valoración de los atributos del jugador.
-Será posible empezar una nueva temporada importando los jugadores que existían previamente.
-Será posible tener un historial para poder ver peñas pasadas.
-Mostrar estadísticas interesantes y ordenadas.


La gestión de logs se realizará usando la libreria `logging` de `Python`.

## Historias de usuario
Para cada microservicio se ha definido un *milestone*. El primer *milestone* es para el [Administrador]de la peña y sus funciones más básicas el cual será capaz de :
- [[HU] Como administrador quiero poder darme de alta .]
- [[HU] Como administrador quiero dar de alta una peña.]
- [[HU] Como administrador quiero modificar una peña.]
- [[HU] Como administrador quiero dar de alta a un jugador de la peña.]
- Como segundo *milestone* se define las funciones más avanzadas del administrador
- [[HU] Como administrador quiero planificar un partido con su alineación.]
- [[HU] Como administrador quiero poder añadir/modificar el resultado de un partido .]
- [[HU] Como administrador quiero poder añadir/modificar las estadísticas de un jugador de un partido .]
- [[HU] Como administrador quiero poder añadir/modificar deudas de los jugadores de la peña.]
El tercer *milestone* es para los [Usuarios] en el se plantean las actividades que puede realizar un usuario normal que también se extienden al usuario.
- [[HU] Como usuario quiero poder darme de alta .]
- [[HU] Como usuario quiero poder ver la tabla de clasificación.]
- [[HU] Como usuario quiero poder ver la tabla de estadísticas de los jugadores.]
- [[HU] Como usuario quiero poder editar mi foto de perfil y mi apodo.]
- [[HU] Como usuario quiero poder consultar los resultados de los partidos.]
- [[HU] Como usuario quiero poder consultar mi deuda de las peñas a las que estoy asociado.]
