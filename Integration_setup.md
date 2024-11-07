# Documentación de Integración Continua 🔄

Después de confirmar que nuestras pruebas funcionan correctamente en local, es esencial elegir una herramienta de **integración continua (CI)** adecuada para automatizar la ejecución de pruebas y despliegue en nuestro proyecto Python.

## Principales Herramientas de Integración Continua para Proyectos Python

Las herramientas de CI permiten ejecutar automáticamente pruebas en cada cambio de código, ayudando a detectar errores a tiempo y garantizando la calidad del software. A continuación, se describen las herramientas más recomendadas para proyectos en Python:

### 1. **GitHub Actions**
   - **Descripción**: `GitHub Actions` es una plataforma de automatización de flujos de trabajo integrada en GitHub que permite ejecutar pruebas y procesos de CI/CD.
   - **Características**:
     - Integra fácilmente el CI/CD en el flujo de trabajo de GitHub.
     - Ofrece **máquinas virtuales gratuitas** para proyectos de código abierto.
     - Soporte para matrices de pruebas y ejecución en múltiples entornos y versiones de Python.
     - Gran cantidad de **acciones predefinidas** y personalizables.
   - **Uso**: Recomendado para proyectos que ya utilizan GitHub y desean una solución de CI/CD flexible, sin necesidad de configuración compleja.
   
### 2. **Travis CI**
   - **Descripción**: `Travis CI` es una herramienta de integración continua muy popular en la comunidad open-source.
   - **Características**:
     - Se integra fácilmente con repositorios de GitHub y ejecuta flujos de trabajo en cada commit y PR.
     - Ofrece una configuración simple mediante un archivo `.travis.yml`.
     - Ideal para proyectos de **código abierto**, ya que proporciona un plan gratuito para ellos.
   - **Uso**: Adecuado para proyectos que buscan una plataforma CI confiable y ya están alojados en GitHub o Bitbucket.

### 3. **CircleCI**
   - **Descripción**: `CircleCI` es una herramienta de CI/CD que soporta tanto GitHub como Bitbucket.
   - **Características**:
     - Ofrece **pipelines de CI/CD avanzados** y un control detallado de las tareas.
     - Configuración de flujos en archivos YAML.
     - Soporta ejecución en **contenedores Docker**, máquinas virtuales y entornos personalizados.
     - Buena opción para proyectos de código abierto y privados con alta personalización en CI.
   - **Uso**: Recomendado para equipos con necesidades avanzadas de CI/CD y que buscan optimizar el tiempo de ejecución de sus pipelines.

### 4. **GitLab CI/CD**
   - **Descripción**: `GitLab CI/CD` es el sistema de integración y entrega continua integrado en GitLab.
   - **Características**:
     - Configuración sencilla a través de archivos `.gitlab-ci.yml`.
     - Ejecuta pipelines de CI/CD de manera rápida y escalable en servidores de GitLab o en runners propios.
     - Amplia personalización en cada etapa del pipeline.
   - **Uso**: Ideal para proyectos alojados en GitLab, con soporte completo para CI/CD y flexibilidad en los pipelines.

### 5. **Jenkins**
   - **Descripción**: `Jenkins` es una de las herramientas de CI/CD más personalizables y ampliamente adoptadas.
   - **Características**:
     - Totalmente **open-source** y con soporte de plugins extensivo.
     - Flexibilidad para integrarse con casi cualquier entorno o sistema de control de versiones.
     - Requiere configuración y mantenimiento manual en servidores propios.
   - **Uso**: Recomendada para grandes proyectos con necesidades específicas de CI/CD y entornos propios.

---

### Selección de Herramienta para Nuestro Proyecto

Hemos optado por utilizar **GitHub Actions** para nuestro flujo de integración continua debido a su **integración nativa con GitHub**, su **simplicidad de configuración**, y el soporte para **máquinas virtuales gratuitas** en proyectos open-source. Además, su capacidad de configurar matrices de pruebas y ejecutar flujos de trabajo en paralelo facilita la gestión de nuestras pruebas en múltiples versiones de Python y sistemas operativos.



### Configuración Básica en GitHub Actions

Para implementar CI en GitHub Actions, hemos definido un archivo `.github/workflows/python-app.yml` en el cual configuramos los siguientes pasos:

1. **Configuración del Entorno**: Configuramos la versión de Python, el SO y las dependencias necesarias.
2. **Ejecución de Pruebas**: Usamos `pytest` para ejecutar todas las pruebas.
3. **Informes y Logs**: Capturamos el resultado de cada paso, verificando si el código pasa las pruebas antes de integrarlo.

Este flujo de trabajo se ejecuta en cada pull request y push, asegurando la calidad del código antes de su incorporación al proyecto principal.

```
name: Python application

on:
  push:
    branches: [ "dev","main" ]  # Cambiado a "dev" para ejecutarse en la rama dev
  pull_request:
    branches: [ "main","dev" ]

permissions:
  contents: read

jobs:
  build:

    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]  # Ejecuta en Ubuntu y Windows
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 pytest
          pip install -r requirements.txt
      
      - name: Lint with flake8
        run: |
          # Detiene el build si hay errores de sintaxis en Python o nombres no definidos
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # Usa exit-zero para tratar todos los errores como advertencias. El editor de GitHub tiene 127 caracteres de ancho
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      
      - name: Test with pytest
        run: |
          pytest
  
```
Una vez que hemos definido el archivo .yml, procedemos a realizar las pruebas mediante un commit y un push a nuestra rama dev.

Como podemos ver en la imagen siguiente, en el commit se vinculan automáticamente los tests, y podemos observar que todos los tests pasan correctamente para las versiones de Python y los sistemas operativos definidos en el flujo de trabajo.
![Dev](/docs/images/DEV.jpg)

En la siguiente imagen, vemos que al realizar un merge y un pull request, también se ejecutan las pruebas automáticamente, y el proceso muestra que los tests están pasando correctamente.
![Pull Request](/docs/images/EjemploMerge.jpg)
