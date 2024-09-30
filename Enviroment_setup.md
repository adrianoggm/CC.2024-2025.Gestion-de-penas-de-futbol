## Preparación del entorno de trabajo

Aquí se podrá seguir el paso a paso para preparar el repositorio de las prácticas.

### Repositorios

- [Fork del Repositorio original de Cloud Computing 24-25](https://github.com/cvillalonga/CC-24-25.git): Fork realizado desde el repositorio original de la asignatura de Cloud Computing.

- [Repositorio de mi Proyecto](https://github.com/adrianoggm/CC.2024-2025.Gestion-de-penas-de-futbol.git): Contiene el proyecto a desarrollar durante el transcurso de la asignatura.

### Configuración de la cuenta personal de GitHub:

Se ha actualizado el perfil de github con una foto de perfil nueva y una descripción sobre mí además del nombre .

### Configuración de la conexión de Github con nuestro ordenador:

Para configurar Github en nuestro ordenador hemos realizado lo siguiente una vez creado en la web de Github nuestro repositorio hemos abierto una terminal en windows 
mediante cmd.
Aquí configuramos nuestro nombre de usuario y la dirección de correo usando los siguientes comandos.
Se configura un nombre de usuario y una dirección de correo via comandos Git para asociarlo a la cuenta GitHub:

```
$ git config --global user.name "Adriano"
$ git config --global user.email adrianoggm@correo.ugr.es
```

![usermail](/docs/images/usermail.PNG)

### Posteriormente clonamos el repositorio:
```
$ git clone https://github.com/adrianoggm/CC.2024-2025.Gestion-de-penas-de-futbol
$ git pull origin master`
```
![setup](/docs/images/Clone.PNG)

En su defecto es posible realizar todo esto mediante GitHub Desktop la app de escritorio.
Para ello una vez autenticado será posible mediante la selección de la opción clone repository acceder al proyecto creado.

![setup](/docs/images/Clonegit.PNG)

Una vez clonado recomendamos crear una o varias ramas /dev en la que se realizará el desarrollo una rama main con el código funcional.
![rama](/docs/images/Createbranch.PNG)


Ahora vamos a crear nuestro entorno de programación en python para ello instalamos nuestra versión deseada de python mediante el enlace :
nosotros hemos elegido Python 3.12.5 como versión inicial de desarrollo de nuestro proyecto.

Una vez instalado instalaremos las librerías mediante pip el cual es el instalador de paquetes de python. 
Mediante la orden pip install realizaremos las consecuentes instalaciones necesarias para nuestro proyecto .
Configuraremos nuestro entorno virtual mediante virtualenv para ello realizamos lo siguiente para el caso de SO Windows:
 pip install virtualenv 
 virtualenv venv
 
 Ahora activamos el entorno mediante la orden \venv\Scripts\Activate.ps1  
 ![entorno](/docs/images/entorno.PNG)
 Instalaremos las librerías necesarias pudiendo visualizar su instalación mediante pip list.
![entorno](/docs/images/List.PNG)

Una vez finalizado nuestro proyecto será necesario mediante freezze guardar las librerías y funciones en un fichero de tal forma que seamos capaces 
de replicar el comportamiento por parte de otros sistemas, como por ejemplo los contenedores.
