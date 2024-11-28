# Documentación de los Logs 🛠️

Tras implementar las funcionalidades principales de nuestra aplicación, hemos diseñado e integrado un **sistema robusto de registro de logs** para garantizar un monitoreo eficiente de las operaciones, identificar errores rápidamente y facilitar el mantenimiento continuo. En esta sección, describimos las características y configuraciones empleadas para gestionar los logs.

---

## Principales Librerías de Logs en Python

Python incluye una poderosa librería estándar para manejar registros de eventos: **`logging`**. Esta herramienta permite capturar, almacenar y analizar eventos en diferentes niveles. Aquí destacamos las características más relevantes utilizadas en nuestro proyecto.

### **1. `logging`**
   - **Descripción**: Proporciona soporte integral para el registro de eventos y errores en aplicaciones Python.
   - **Características Principales**:
     - **Integrada**: No requiere instalación de librerías adicionales.
     - **Múltiples Handlers**: Soporta el envío de registros a varios destinos, como la consola y archivos de texto.
     - **Personalización Avanzada**: Configuración de niveles de registro, formato y rotación de archivos.
   - **Uso en este Proyecto**:
     - Captura tanto eventos de la lógica de negocio como operaciones relacionadas con la base de datos.
     - Separa los registros en **dos archivos independientes**:
       1. **`app.log`**: Almacena los eventos de la lógica de negocio y acciones de usuario.
       2. **`db.log`**: Registra las consultas SQL y transacciones realizadas.

---

## Sistema de Logs Implementado

El diseño del sistema de logs responde a los siguientes objetivos:

1. **Segregación de Logs**:
   - Separar los registros de la aplicación y de la base de datos en archivos específicos (`app.log` y `db.log`) para facilitar el análisis.
2. **Rotación de Archivos**:
   - Implementar **rotación de archivos** para limitar su tamaño a 5 MB, conservando hasta 3 copias de respaldo.
3. **Niveles de Registro**:
   - **DEBUG**: Información detallada para diagnóstico.
   - **INFO**: Seguimiento de eventos normales (ej., accesos exitosos a rutas).
   - **WARNING**: Eventos inesperados que no afectan el funcionamiento crítico.
   - **ERROR**: Problemas graves que requieren intervención inmediata.
4. **Formato Personalizado**:
   - Incluye detalles clave como fecha, hora, nombre del logger, nivel del evento y mensaje.

---

## Ejemplo de Logs Generados

A continuación, presentamos ejemplos de los registros generados al ejecutar pruebas en la aplicación:

### **Logs de la Aplicación**
![Logs App](/docs/images/logsapp.png)

### **Logs de la Base de Datos**
![Logs DB](/docs/images/logsdb.png)

---

## Configuración del Sistema de Logs

La configuración del sistema de logs se define en un archivo separado (`logging_config.py`), asegurando modularidad y fácil mantenimiento. Aquí está el código de configuración:

```python
def setup_logging(log_name):
    import os
    import logging
    from logging.handlers import RotatingFileHandler

    # Crear el directorio de logs si no existe
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Ruta del archivo de log
    log_file = os.path.join(log_dir, f"{log_name}.log")
    print(f"Configurando logger para: {log_file}")

    # Crear logger con el nombre especificado
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)  # Capturar todos los niveles

    # Limpiar handlers previos para evitar duplicados
    if logger.hasHandlers():
        logger.handlers.clear()

    # Configurar handler de archivo rotativo
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # Tamaño máximo: 5 MB
        backupCount=3,  # Guardar hasta 3 backups
        encoding='utf-8'
    )
    rotating_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotating_handler.setFormatter(formatter)

    # Agregar handler al logger
    logger.addHandler(rotating_handler)

    # Configurar handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Agregar handler de consola al logger
    logger.addHandler(console_handler)

    return logger
