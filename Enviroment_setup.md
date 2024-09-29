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

![setup](/docs/images/usermail.png)

### Posteriormente clonamos el repositorio:
```
$ git clone https://github.com/adrianoggm/CC.2024-2025.Gestion-de-penas-de-futbol
$ git pull origin master`
```
![setup](/docs/images/Clone.png)

En su defecto es posible realizar todo esto mediante GitHub Desktop la app de escritorio.
Para ello una vez autenticado será posible mediante la selección de la opción clone repository acceder al proyecto creado.

![setup](/docs/images/Clonegit.png)

Una vez clonado recomendamos crear una o varias ramas /dev en la que se realizará el desarrollo una rama main con el código funcional.
![setup](/docs/images/Createbranch.png)