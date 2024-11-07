# Documentación del Testeo 🛠️

Tras desarrollar las primeras funcionalidades de nuestra aplicación, es fundamental realizar pruebas exhaustivas para garantizar su correcto funcionamiento y asegurar que cumple con los requisitos previstos. En esta sección, detallamos las principales librerías de Python para realizar pruebas, explicando sus enfoques, ventajas, y cuándo son más útiles para un proyecto de desarrollo.

## Principales Librerías de Testeo en Python

Python cuenta con un conjunto robusto de librerías para la realización de pruebas. A continuación, se presenta una descripción de las más destacadas:

### 1. **unittest**
   - **Descripción**: `unittest` es la librería estándar de Python para realizar pruebas unitarias, inspirada en el marco JUnit de Java.
   - **Características**:
     - Viene integrada con Python, por lo que no necesita instalación adicional.
     - Permite agrupar pruebas en clases y organiza su ejecución en diferentes métodos (`setUp`, `tearDown`).
     - Ideal para realizar pruebas de bajo nivel (unitarias).
   - **Uso**: Adecuado para proyectos que necesitan una estructura de pruebas sólida y están diseñados para llevar a cabo pruebas unitarias.

### 2. **pytest**
   - **Descripción**: `pytest` es una de las librerías más populares y flexibles para realizar pruebas en Python.
   - **Características**:
     - Soporte para pruebas unitarias, funcionales y de integración.
     - Ofrece una sintaxis simple y poderosa para escribir y organizar pruebas.
     - Permite el uso de fixtures para configurar el entorno de prueba de manera fácil.
     - Extensible mediante plugins, lo cual facilita la personalización.
   - **Uso**: Recomendado para proyectos de cualquier tamaño que busquen una sintaxis sencilla y funciones avanzadas para manejar tests.

### 3. **doctest**
   - **Descripción**: `doctest` permite incluir ejemplos de código en docstrings y ejecutarlos como pruebas.
   - **Características**:
     - Ideal para validar que los ejemplos en la documentación de las funciones son correctos.
     - Fácil de usar y útil para asegurar que la documentación esté alineada con la implementación.
   - **Uso**: Adecuado para proyectos donde la documentación detallada y precisa es importante, y para aplicaciones donde se quiera mantener la documentación y el código en sincronía.

### 4. **nose2**
   - **Descripción**: `nose2` es la segunda generación de la librería `nose`, diseñada para descubrir y ejecutar pruebas.
   - **Características**:
     - Fácil de usar y con una configuración mínima.
     - Soporta descubrimiento automático de pruebas, evitando la necesidad de importarlas manualmente.
     - Compatible con plugins y extensiones.
   - **Uso**: Útil en proyectos que requieren descubrir y ejecutar automáticamente un gran volumen de pruebas.

De todas estas opciones, hemos optado por utilizar **pytest** como la librería principal para nuestras pruebas. 

### ¿Por qué elegimos pytest?
`pytest` es ampliamente considerada una de las herramientas de testing más potentes y versátiles en el ecosistema Python. Esta elección se debe a varios factores clave:

- **Facilidad de Uso**: Su sintaxis intuitiva permite escribir y ejecutar pruebas con simplicidad, sin la complejidad de configuraciones adicionales.
- **Compatibilidad con Integración Continua**: `pytest` es ideal para su uso con plataformas de integración continua como GitHub Actions, Travis CI y Jenkins. La integración fluida asegura que nuestras pruebas se ejecuten automáticamente en cada cambio de código, mejorando la estabilidad y consistencia del proyecto.
- **Documentación Abundante y Comunidad Activa**: `pytest` cuenta con una extensa documentación y una comunidad activa que continuamente crea plugins y mejoras. Esto facilita resolver dudas y obtener soporte, así como acceder a recursos adicionales cuando el proyecto requiere personalizaciones avanzadas.
- **Extensibilidad**: La gran variedad de plugins disponibles y la posibilidad de crear nuestros propios fixtures y configuraciones hacen de `pytest` una herramienta extremadamente adaptable para diferentes necesidades.

Al elegir `pytest`, buscamos no solo asegurar la estabilidad y fiabilidad de nuestra aplicación, sino también optimizar el flujo de trabajo de desarrollo y pruebas, permitiéndonos crecer de manera eficiente y segura a medida que añadimos nuevas funcionalidades.
## Pytest
Para instalar `pytest` es tan sencillo como realizar:
```
$ pip install pytest
```

Una vez instalado hemos creado una carpeta \tests donde se encuentran los test.py . En nuestro caso constamos de un único archivo /tests/app_test.py.
Donde se encuentran los diferentes test que se han planteado.

### Resumen de Pruebas de la Aplicación ⚙️

Este documento detalla las pruebas realizadas para verificar las funcionalidades de la aplicación. Cada prueba se ha diseñado para asegurar el correcto funcionamiento de las funcionalidades de **registro**, **inicio de sesión**, **gestión de jugadores**, y más.
Estas se han realizado simulando la base de datos en memoria RAM.
---

#### 1. `test_ping`
- **Propósito**: Verificar que la página de inicio (`/`) se carga correctamente.
- **Pruebas**:
  - La respuesta tiene un código de estado `200` (OK).
  - **Textos esperados en la página**:
    - `"Inicia Sesión o Regístrate"`
    - Enlace para `"inicia sesión"`
    - Enlace para `"Regístrate aquí"`

---

#### 2. `test_registration_admin_success`
- **Propósito**: Probar el registro exitoso de un administrador de peña.
- **Pruebas**:
  - La solicitud `POST` al endpoint de registro redirige exitosamente (estado `302`), confirmando que el registro del administrador fue satisfactorio.

---

#### 3. `test_registration_admin_unsuccess`
- **Propósito**: Verificar que un intento de registro de administrador fallido no muestra mensajes de error indebidos.
- **Pruebas**:
  - Asegura que no aparece el mensaje `"Usuario o contraseña incorrectos"` en la respuesta.

---

#### 4. `test_registration_jugador_success`
- **Propósito**: Probar el registro exitoso de un jugador.
- **Pruebas**:
  - La solicitud `POST` para el registro del jugador redirige correctamente (estado `302`).
  - El mensaje `"Usuario o contraseña incorrectos"` no está presente en la respuesta.

---

#### 5. `test_registration_jugador_unsuccess`
- **Propósito**: Verificar que un intento fallido de registro de jugador no muestra mensajes de error indebidos.
- **Pruebas**:
  - Confirma que no se muestra el mensaje `"Usuario o contraseña incorrectos"` en la respuesta.

---

#### 6. `test_login`
- **Propósito**: Probar el inicio de sesión de un usuario administrador.
- **Pruebas**:
  - Después del registro de un administrador, la solicitud de `POST` al endpoint de inicio de sesión debe redirigir (estado `302`) al dashboard.
  - No debe aparecer el mensaje `"Por favor, inicia sesión primero."` en la respuesta.

---

#### 7. `test_gestionar_jugadores`
- **Propósito**: Probar la funcionalidad de gestión de jugadores en el panel de administración.
- **Pruebas**:
  - Después de iniciar sesión como administrador, la solicitud de `GET` para ver la lista de jugadores devuelve un estado `200`.
  - Confirma que un jugador recientemente añadido (ej., `"Juan"`) aparece en la lista de jugadores.

---

#### 8. `test_eliminar_jugador`
- **Propósito**: Probar la eliminación de un jugador.
- **Pruebas**:
  - Después de iniciar sesión como administrador, añade un jugador y luego lo elimina.
  - Confirma que la solicitud de eliminación redirige correctamente (estado `302`).
  - Verifica que el jugador eliminado (ej., `"Carlos"`) ya no aparece en la lista.

---

#### 9. `test_editar_jugador`
- **Propósito**: Probar la funcionalidad de edición de un jugador.
- **Pruebas**:
  - Después de iniciar sesión como administrador, añade un jugador y luego edita su información.
  - La solicitud de edición redirige correctamente (estado `302`).
  - Verifica que los cambios (ej., nombre modificado a `"Andresito Modificado"`) se reflejan en la lista de jugadores.

---
En la siguiente Imagen podemos observar las pruebas en pytest y como en local se ejecutan y pasan los test.
![Test](/docs/images/Tests.jpg)








