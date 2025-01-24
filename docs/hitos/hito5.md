# ⚙️ Hito 5: Despliegue de la Aplicación

En este hito se documentan los pasos realizados para desplegar nuestra aplicación, incluyendo la investigación, pruebas con diferentes plataformas y la decisión final sobre la infraestructura utilizada.

## **Aspectos Principales**

### **Elección de la Plataforma de Despliegue**

#### **Análisis de Alternativas**  
Se analizaron diversas opciones para el despliegue de la aplicación, evaluando plataformas PaaS y IaaS según los siguientes criterios:

- **Escalabilidad:** La capacidad de la plataforma para gestionar incrementos en la carga de trabajo.
- **Costos:** Comparativa entre el coste de uso inicial y el presupuesto disponible para el proyecto.
- **Facilidad de Uso:** Interfaces y herramientas que simplifiquen el proceso de despliegue.
- **Soporte Técnico:** Documentación, foros y ayuda disponible para resolver problemas.

Durante esta fase, se probaron las plataformas **Fluent** y **Render** como opciones PaaS. Aunque en un primer momento Render parecía una buena solución, surgieron varios problemas:

1. **Problemas de conexión:**  
   Aunque el despliegue inicial fue exitoso, la conexión interna de los servicios y la carga de los logs fallaron, lo que limitaba su funcionalidad.
2. **Limitaciones con Grafana:**  
   No fue posible exponer correctamente el servicio de Grafana, una funcionalidad clave para nuestro proyecto.

Debido a estas limitaciones, se descartaron las opciones PaaS y se decidió probar con proveedores IaaS.
![MV](/docs/images/render.png)  
#### **Justificación de la Selección**  
Después de evaluar los principales servicios IaaS (AWS, Azure y Google Cloud), se optó por **Google Cloud** debido a:

- **Documentación de calidad:** Su guía detallada facilitó la configuración y el despliegue de servicios.
- **Incentivos económicos:** Ofrecen $300 en créditos gratuitos durante 90 días, lo que permitió realizar pruebas sin coste adicional.
- **Facilidad de integración:** Herramientas intuitivas y una interfaz de usuario amigable simplificaron el despliegue.

Aunque AWS y Azure también son opciones robustas, Google Cloud destacó por su equilibrio entre facilidad de uso y costos iniciales.

## **Configuración Necesaria para el Despliegue**

Para utilizar Google Cloud, fue necesario crear una nueva cuenta de Google, ya que:

- La cuenta actual ya había agotado el periodo de prueba gratuito.
- Las cuentas institucionales como **go.ugr.es** no permiten la domiciliación bancaria, lo que impedía el uso de estos servicios.

Una vez configurada la nueva cuenta, se procedió con la configuración de los servicios requeridos en Google Cloud, asegurando que la aplicación se desplegara correctamente.

## **Configuración de una Máquina Virtual en Google Cloud**

### 1. **Creación de la Máquina Virtual**

1. Accede a **Compute Engine** desde el panel de Google Cloud.
2. Selecciona la opción **"Crear instancia"**.
3. Utiliza los valores por defecto, asegurándote de que el servicio se configure en una ubicación europea.  
   - En este caso, se eligió la región **"EUW southwest (Madrid)"**.  
   ![MV](/docs/images/10.png)  
   ![MV2](/docs/images/11.png)

4. Espera a que la instancia se configure. Una vez creada, verifica su estado y edita los parámetros según sea necesario.

---

### 2. **Configuración Adicional**

1. Comprueba que el sistema operativo sea **Debian**.
2. Activa las opciones para permitir tráfico de **HTTP** y **HTTPS**.  
   ![Conf1](/docs/images/12.png)  
   ![Conf2](/docs/images/13.png)

---

### 3. **Conexión SSH y Prueba de Despliegue Manual**

1. Accede a la instancia a través de **SSH** desde la consola de Google Cloud. 
2. Realiza pruebas de configuración y despliegue manual para garantizar que el entorno está operativo. Para ello realizamos los siguientes comandos:
```bash
sudo apt install docker
sudo apt install git
git clone https://github.com/adrianoggm/CC.2024-2025.Gestion-de-penas-de-futbol
docker-compose build
docker-compose up
```

![Conf2](/docs/images/15.png)
![Conf2](/docs/images/16.png)
![Conf2](/docs/images/17.png)
Con esto pensaríamos que ya podemos acceder al servicio sin embargo si al ir a la dirección ip con el puerto que queremos probar obtendremos un el siguiente mensaje:
Al intentar acceder a la dirección IP pública con el puerto deseado, se obtiene el siguiente mensaje de error:

> *La página 34.175.121.121/puerto ha rechazado la conexión.*

Esto ocurre debido a una configuración incompleta en el firewall del usuario en Google Cloud, donde no se han definido correctamente las reglas para exponer los puertos necesarios para las peticiones TCP y UDP.

---

### **Solución: Configuración del Firewall**

#### **Pasos para Configurar las Reglas del Firewall**

1. Accede a **Seguridad de Red** en la consola de Google Cloud.
2. Selecciona la opción **"Crear regla de firewall"** para añadir las reglas necesarias.
3. Configura las siguientes reglas:

   - **Puerto 5000**: Utilizado por la aplicación principal.
   - **Puerto 3000**: Utilizado por el visualizador de logs de Grafana.

4. Asegúrate de que las reglas permitan el tráfico en los protocolos **TCP** y **UDP** según sea necesario.

   ![Firewall Configuración 1](/docs/images/15.png)  
   ![Firewall Configuración 2](/docs/images/16.png)  
   ![Firewall Configuración 3](/docs/images/17.png)

---

### **Verificación del Acceso**

Tras configurar las reglas del firewall, la aplicación estará accesible en las siguientes rutas:

- **App Principal**: [http://34.175.121.121:5000/api](http://34.175.121.121:5000/api)  
- **Grafana (Logs Visualizer)**: [http://34.175.121.121:3000/](http://34.175.121.121:3000/)  

   ![App Acceso](/docs/images/22.png)  
   ![Grafana Acceso](/docs/images/23.png)

---

### **Comprobación Adicional**

Para garantizar que el acceso es correcto, puedes realizar las siguientes verificaciones desde la terminal:

```bash
# Verificar conectividad al puerto 5000
curl http://34.175.121.121:5000/api

# Verificar conectividad al puerto 3000
curl http://34.175.121.121:3000/
```

## **Configuración para la Automatización del Despliegue**

Para realizar el despliegue automático, se creará un archivo `deploy.yml`. Este archivo permitirá que GitHub Actions se encargue de conectar, mediante SSH, con la máquina virtual (VM) en Google Cloud. 

### **Pasos Generales:**

1. Crear claves SSH para establecer una conexión segura.
2. Comprobar la conexión SSH con la VM.
3. Añadir la clave privada al repositorio de GitHub como un secreto en **GitHub Secrets**.
4. Configurar el archivo `deploy.yml` para automatizar el despliegue.

---

### **Creación y Configuración de Claves SSH**

#### **1. Generar las claves SSH en tu terminal local**
Ejecuta el siguiente comando en la terminal para crear un par de claves SSH:

```bash
ssh-keygen -t rsa -b 4096 -C "tu_correo@example.com"
```
Salida esperada: El comando generará dos archivos:


   - **Una clave privada (id_rsa).**
   - **Una clave pública (id_rsa.pub).**
![ssh-pub](/docs/images/25.png)
![ssh-priv](/docs/images/26.png)
![ssh-priv-en la MV](/docs/images/31.png)
Una vez añadida la clave pública a la MV en ~/.ssh/authorized_keys con un editor como nano podemos conectarnos con ssh la MV.
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub usuario@34.175.121.121
ssh -i ~/.ssh/id_rsa adrianogarciagiraldamilena@34.175.121.121 
```
---
### **Creación de `deploy.yml` y Configuración en GitHub Actions**

#### **1. Añadir la clave privada al repositorio**
Lo primero es agregar la clave privada SSH al repositorio como un secreto. Esto se realiza desde:

- **GitHub > Settings > Secrets and variables > Actions > New repository secret**.
- Nombre del secreto: `SSH_PRIVATE_KEY`.

   ![ssh-priv](/docs/images/27.png)

---

#### **2. Configurar el archivo `deploy.yml`**

A continuación, configuramos el archivo `.github/workflows/deploy.yml` para automatizar el despliegue. Este archivo realizará las siguientes acciones:

1. **Detectar cambios en la rama `main`**: El Action se ejecuta automáticamente al hacer un push a esta rama.
2. **Conexión SSH**: Se utiliza la clave privada almacenada en los secretos para establecer una conexión segura con la máquina virtual.
3. **Actualización del proyecto**: Se navega al directorio del proyecto, se realiza un `git pull` para traer los cambios y se actualizan los contenedores Docker.
4. **Reinicio del servicio**: Se reinician los contenedores con `docker-compose` para aplicar los últimos cambios.

El contenido del archivo es el siguiente:

```yaml
name: Deploy to Google Cloud VM

on:
  push:
    branches:
      - main  

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up SSH
      uses: webfactory/ssh-agent@v0.5.3
      with:
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

    - name: Deploy to VM
      run: |
        ssh -o StrictHostKeyChecking=no adrianogarciagiraldamilena@34.175.121.121 << 'EOF'
          cd ./CC.2024-2025.Gestion-de-penas-de-futbol
          git pull origin main
          docker-compose pull
          docker-compose down
          docker-compose up -d --build
        EOF

```
### **3. Explicación del Proceso**

#### **Seguridad mediante GitHub Secrets**
- Se utiliza la variable `${{ secrets.SSH_PRIVATE_KEY }}` para cargar la clave privada de forma segura.
- Esto garantiza que la clave privada no se exponga públicamente, preservando la confidencialidad y la seguridad del acceso SSH durante el despliegue.

#### **Pasos del Action**
El proceso automatizado sigue estos pasos clave:

1. **Establecer conexión SSH:**  
   El Action se conecta de forma segura a la máquina virtual utilizando la clave privada configurada en los secretos de GitHub.

2. **Acceso al directorio del proyecto:**  
   Navega al directorio de la aplicación en la máquina virtual.

3. **Actualizar el repositorio:**  
   Ejecuta el comando `git pull` para traer los últimos cambios desde la rama principal.

4. **Detener contenedores activos:**  
   Si hay servicios en ejecución, los detiene con `docker-compose down` para evitar conflictos durante el despliegue.

5. **Construir e iniciar servicios:**  
   Reconstruye e inicia los contenedores con el comando `docker-compose up -d --build`, aplicando los cambios más recientes.

#### **Resultado satisfactorio**
- Una vez completado el Action, los servicios se despliegan correctamente en la máquina virtual.
- La aplicación y sus dependencias estarán listas para ser utilizadas sin necesidad de intervención manual.

---

### **4. Verificación del Despliegue**

Para comprobar que el despliegue se realizó con éxito, verifica los siguientes indicadores:

- **Estado aprobado del Action en GitHub:**  
  Confirma que el workflow de GitHub Actions se completó correctamente.  
  ![Build-aproved](/docs/images/32.png)

- **Aplicación principal corriendo:**  
  Accede a la interfaz de la aplicación para verificar su funcionamiento.  
  ![App](/docs/images/22.png)

- **Grafana en funcionamiento:**  
  Comprueba que el visualizador de logs de Grafana está activo y accesible.  
  ![Grafana](/docs/images/33.png)

---
### **Pruebas de las Prestaciones de la Aplicación Desplegada en el IaaS**

Para evaluar las prestaciones de la aplicación desplegada en el IaaS, se realizarán las siguientes pruebas:

---

#### **1. Prueba de Respuesta HTTP**
Se utiliza la herramienta `curl` para comprobar que los endpoints de la aplicación responden correctamente:

```bash
# Probar el endpoint principal de la aplicación


# Salida esperada:
# HTTP/1.1 200 OK
# Content-Type: application/json
# Content-Length: ...
# Server: ...

# Probar el acceso a Grafana
curl -I http://34.175.121.121:3000

# Salida esperada:
# HTTP/1.1 200 OK
# Content-Type: text/html
```
  ![Curl app](/docs/images/55.png)
Observamos que efectivamente hay respuesta de la app web. 
---
## **Pruebas de Carga con Apache JMeter**

Para evaluar el rendimiento de nuestra aplicación bajo carga de trabajo, utilizaremos **Apache JMeter**, una herramienta robusta para pruebas de rendimiento. A continuación, se describen los pasos para realizar estas pruebas.

---

### **1. Preparar el Entorno**

#### **1.1 Instalar Apache JMeter**
1. Descarga la versión binaria de JMeter desde su página oficial:  
   [https://jmeter.apache.org/download_jmeter.cgi](https://jmeter.apache.org/download_jmeter.cgi).
2. Extrae el archivo `.zip` en una ubicación de tu preferencia (por ejemplo, `C:\JMeter`).
3. Navega al directorio `bin` y ejecuta el archivo `jmeter.bat` para iniciar la herramienta.

---

### **2. Configurar un Plan de Pruebas**

#### **2.1 Crear un Proyecto Nuevo**
1. Abre JMeter y crea un nuevo **Test Plan** desde el menú principal.
2. Haz clic derecho sobre el nodo raíz **Test Plan** y selecciona:
   **Add > Thread Group**.
![proyecto ](/docs/images/56.png)
#### **2.2 Configurar el Grupo de Hilos**
El **Thread Group** define la carga de trabajo que se aplicará a la aplicación. Configura los siguientes parámetros:
- **Number of Threads (Users):** Número de usuarios simulados (por ejemplo, `1000`).
- **Ramp-Up Period (in seconds):** Tiempo en segundos para lanzar todos los usuarios (por ejemplo, `100`).
- **Loop Count:** Número de veces que cada usuario repetirá la solicitud (puedes elegir `Forever` o un valor específico como `3`).
![hilos ](/docs/images/57.png)
#### **2.3 Añadir un Sampler HTTP**
1. Haz clic derecho en el **Thread Group** y selecciona:
   **Add > Sampler > HTTP Request**.
2. Configura el sampler con los detalles de tu aplicación:
   - **Server Name or IP:** Dirección del servidor (por ejemplo, `34.175.121.121`).
   - **Port Number:** Puerto donde está corriendo tu aplicación (por ejemplo, `5000` o `3000`).
   - **Path:** Ruta del endpoint (por ejemplo, `/api`).
![Peticiones ](/docs/images/58.png)
#### **2.4 Añadir un Listener**
1. Haz clic derecho en el **Test Plan** o en el **Thread Group** y selecciona:
   **Add > Listener > Summary Report** o **View Results Tree**.
2. Este componente permitirá visualizar los resultados de las pruebas.

---

### **3. Ejecutar la Prueba**
1. Haz clic en el botón de **Play** (triángulo verde) en la barra de herramientas.
2. Observa los resultados en tiempo real en el Listener configurado (por ejemplo, **Summary Report**).
![Listener ](/docs/images/59.png)
---

### **4. Interpretar los Resultados**

#### **4.1 Métricas Importantes en el "Summary Report"**
- **Throughput:** Solicitudes por segundo procesadas por el servidor.
- **Average Response Time:** Tiempo promedio de respuesta para las solicitudes.
- **Error Rate:** Porcentaje de solicitudes que fallaron durante la prueba.
- **Data Sent y Data Received:** Cantidad de datos enviados y recibidos durante la prueba.

#### **4.2 Análisis Detallado en "View Results Tree"**
- Observa las respuestas detalladas del servidor para cada solicitud, incluyendo:
  - Códigos HTTP (200, 404, etc.).
  - Contenido devuelto por el servidor.

---

### **5. Ajustar y Repetir**
- Si los resultados no cumplen con las expectativas (por ejemplo, alta latencia o errores), ajusta:
  - La configuración del servidor.
  - El número de usuarios o el tiempo de rampa.
- Repite la prueba hasta que el sistema responda dentro de los parámetros esperados.

---

### **6. Documentar los Resultados**
Para conservar un registro de las pruebas realizadas:
1. Haz clic derecho en el Listener (por ejemplo, **Summary Report**) y selecciona:
   **Save Table Data** para guardar los resultados en un archivo `.csv`.

---
Métrica de google cloud:
  ![Gcloud ](/docs/images/60.png)
### **Conclusión**
Apache JMeter es una herramienta eficiente para evaluar el rendimiento de nuestra aplicación. Las pruebas de carga nos permiten identificar posibles cuellos de botella y asegurar que la aplicación puede manejar el tráfico esperado. Si se detectan problemas, se ajustarán los parámetros del servidor y se repetirán las pruebas para garantizar la estabilidad del sistema.

