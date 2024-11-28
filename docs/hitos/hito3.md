# Gestión de Peñas y Ligas Individuales Deportivas - **Integración Continua** ⚽🏀

> **Versión 0.1**

Este documento corresponde al **Hito 3** del proyecto de **gestión de peñas y ligas individuales deportivas**. Durante este hito se ha trabajado en la implementación de funcionalidades clave, continuando el flujo de trabajo definido en el **Hito 1** y ampliado en el **Hito 2**.

---

## 📋 Resumen de Actividades del Hito 2 🚀

En este hito, se ha desarrollado una **aplicación en Python** que abarca el *full stack* para la gestión de peñas y ligas deportivas, implementando las siguientes historias de usuario descritas en el **primer Milestone**: **Funciones Básicas del Administrador**.

---

## Historias de Usuario Implementadas  📌

Las funcionalidades incluidas en esta fase del proyecto corresponden a las siguientes historias de usuario:

### **Segundo Milestone: Funciones Avanzadas del Administrador**
- **[HU-05]**: Como administrador, quiero planificar un partido y definir su alineación.
- **[HU-06]**: Como administrador, quiero añadir o modificar el resultado de un partido.
- **[HU-07]**: Como administrador, quiero añadir o modificar las estadísticas de los jugadores tras un partido.

### **Tercer Milestone: Funciones del Usuario**
- **[HU-10]**: Como usuario, quiero ver la tabla de clasificación de la peña.
- **[HU-11]**: Como usuario, quiero ver las estadísticas de los jugadores de la peña.
- **[HU-13]**: Como usuario, quiero consultar los resultados de los partidos jugados.

Estas funcionalidades establecen una versión funcional que permite a los administradores gestionar peñas, jugadores y registros. La implementación de estas características puede verificarse en el documento: **[Ejecución de la App](/EjecucionHito2.md)**. Con estas mejoras, hemos iniciado el establecimiento de una lógica de negocio robusta en nuestra aplicación.

---

## 🔄 Testing e Integración Continua

Se ha ampliado el proceso de testing añadiendo dos casos adicionales, complementando las pruebas desarrolladas en el hito anterior. Esto se realiza sobre la base de que, al usar Flask como framework, ya se gestionaban tests para la API y las funcionalidades básicas.

### Tests Implementados en el Hito 3 🧪

En el **Hito 3**, se desarrollaron tests específicos para garantizar el correcto funcionamiento de las funcionalidades de gestión de temporadas. A continuación, se detallan los principales tests realizados:

---

### 1. `test_crear_temporada`
- **Propósito**: Probar la funcionalidad de creación de una nueva temporada.
- **Pruebas**:
  - Se registra y autentica un administrador.
  - Crea una nueva temporada con fechas específicas (ej., `"2023-01-01"` a `"2023-12-31"`).
  - Confirma que la solicitud de creación redirige correctamente (`302`).
  - Verifica que la nueva temporada aparece en la lista de temporadas disponibles.

---

### 2. `test_eliminar_temporada`
- **Propósito**: Probar la funcionalidad de eliminación de una temporada existente.
- **Pruebas**:
  - Se registra y autentica un administrador.
  - Crea una temporada específica (ej., `"2023-01-01"` a `"2023-04-01"`).
  - Obtiene el ID de la temporada creada desde el HTML de la lista de temporadas.
  - Solicita la eliminación de la temporada.
  - Confirma que la solicitud de eliminación redirige correctamente (`302`).
  - Verifica que la temporada eliminada no aparece en la lista de temporadas disponibles.


Aunque no se profundizó más en el testing debido a los avances en otras áreas, estos casos adicionales refuerzan la estabilidad de las funcionalidades.

---

## 🔍 Implementación de Logs

La implementación de un sistema de logs es uno de los cambios más significativos realizados en este hito. Se añadió un sistema de registro que permite separar los logs en un contenedor independiente, facilitando futuras implementaciones en una arquitectura **contenedorizada**.

### Características del Sistema de Logs
1. **Separación de contenedores:** Se planean tres contenedores futuros: **App**, **Logs** y **Base de Datos**.
2. **Almacenamiento centralizado:** Los logs se almacenan en archivos independientes para facilitar el análisis y el mantenimiento.
3. **Documentación:** La configuración y el uso de los logs están detallados en: **[Documentación Logs](/Logs.md)**.

---

## 🎯 Conclusión

Este hito marca un avance significativo en el proyecto, proporcionando una **base sólida** para la gestión de peñas deportivas. La combinación de nuevas funcionalidades, pruebas e integración de logs nos permite avanzar con confianza, manteniendo un enfoque en la calidad y la escalabilidad.

A medida que el proyecto evolucione, seguiremos añadiendo funcionalidades y mejoras para cumplir con los objetivos de usabilidad y rendimiento planteados en el **Hito 1**.
