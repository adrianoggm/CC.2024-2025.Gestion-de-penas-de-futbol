# Ejecución de la Aplicación 🚀

Para poder ejecutar la app será tan sencillo como ejecutar en el directorio raíz del proyecto los siguientes comandos: 

En Windows
```
$ py src\app.py

```
En Linux
```
$ python ./src/app.py

```
Una vez ejecutado el comando, se generará un enlace con el endpoint de la página principal de la aplicación web:

Running on: http://127.0.0.1:4000

![Ejecución](/docs/images/EjecucionApp.jpg)


### Acciones Disponibles 🔧
Una vez dentro, puedes realizar las siguientes acciones desde la interfaz web:

Registrar una Peña junto con su Administrador.
Registrar un Jugador.
Realizar un Login para acceder a diferentes perfiles.

![Index](/docs/images/Login.jpg)

## Registrar Peña y Administrador 🏟️
En este formulario podrás registrar una nueva Peña y su usuario Administrador correspondiente.
![Registro Peña](/docs/images/RegistroPena.jpg)
Si se presenta algún error en el registro o login, los mensajes de error se gestionan y se muestran correctamente en pantalla:
![Registro Peña unsucces](/docs/images/RegistroPenaFail.jpg)

Una vez registrada la Peña, el administrador podrá crear cuentas de jugadores para esa Peña, o bien, los jugadores podrán ser creados más tarde por el mismo administrador.

## Registrar Jugador 🧑‍💼
Similar al proceso de registro de Peñas, aquí podrás registrar un jugador para la Peña.
![Registro Jugador](/docs/images/Registrojugador.jpg)
Y nos redirigirá a la página de inicio para realizar un login.
![Registro Jugador correcto](/docs/images/Registrojugadorsucces.jpg)

Nota: Actualmente, el login de los jugadores no está completamente gestionado y puede devolver un error al intentar acceder con un perfil de jugador.

## Login Admin 🔑
Si inicias sesión con una cuenta de administrador, serás redirigido al Admin Dashboard, donde podrás gestionar jugadores y partidos. Para acceder, utiliza el usuario "admin" con la contraseña "1" (esta contraseña está cifrada en la base de datos, por lo que es importante recordarla, ya que no hay opción de recuperación).
Una vez dentro veremos la siguiente vista:
![Admin dashboard](/docs/images/Panel_admin.jpg)

Actualmente, solo está implementada la opción para Gestionar Jugadores.

## Gestionar Jugador 📝
En esta sección del dashboard del administrador, podrás gestionar y visualizar todos los jugadores inscritos en la Peña. Las acciones disponibles son:

Añadir un jugador.
Editar un jugador.
Eliminar un jugador.

![Gestionar Jugadores](/docs/images/Gestionarjugadore.jpg)
Nota: En el futuro, se implementará la posibilidad de vincular cuentas de jugador con jugadores, permitiendo una relación bidireccional (CuentaJugador ⇄ Jugador). Actualmente, la relación es unidireccional.

###  Añadir Jugador ➕
Si decides añadir un nuevo jugador a la Peña, simplemente completa el formulario de registro y este aparecerá en la lista de jugadores.
![Añadir Jugadores](/docs/images/Addjugador.jpg)
Posteriormente todos los jugadores que añadamos se verán reflejados en nuestra lista de jugadores. Para hacer las pruebas añadiremos 2 jugadores más.
![Gestionar Jugadores](/docs/images/Gestionarjugadore2.jpg)
### Borrar Jugador 🗑️
Si decides eliminar un jugador, selecciona la opción de borrar, confirma la acción y el jugador será eliminado de la Peña.
Observamos como borramos al jugador Lovi (Andrés) de la peña:
![Borrar Jugadores](/docs/images/Borrarjugadores.jpg)
### Editar Jugador ✏️
Para editar un jugador, selecciona el jugador a modificar y actualiza los campos requeridos.
Ahora editaremos los valores de Toñin(Antonio) por los de Sergi(Sergio).
![Añadir Jugadores](/docs/images/editar.jpg)
![Añadir Jugadores](/docs/images/Gestionarjugadore3.jpg)