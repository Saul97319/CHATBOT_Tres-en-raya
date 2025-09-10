# UI Web para Cliente-Servidor (Flask + HTML + CSS) #

## Descripción del proyecto ##

Este proyecto implementa una interfaz web para interactuar con un sistema "Cliente-Servidor TCP".
El frontend está construido en HTML, CSS y JavaScript, mientras que el backend utiliza Flask (Python) para gestionar la comunicación entre la interfaz y los procesos cliente/servidor.

El sistema permite:

* Encender y apagar el servidor TCP.
* Conectar y desconectar un cliente.
* Enviar mensajes al servidor y obtener respuestas.
* Visualizar el historial de interacción en la interfaz web.


## Requisitos del sistema ##

* Python: versión 3.10 o superior
* Flask: instalar con `pip install flask`
* Navegador web moderno** (Chrome, Firefox, Edge, etc.)

## Instrucciones de ejecución ##

1. Abrir una terminal en la carpeta raíz del proyecto.
2. Instalar dependencias:

   ```bash
   pip install flask
   ```
3. Ejecutar el controlador principal:

   ```bash
   python controller.py
   ```
4. Abrir el navegador en:

   ```
   http://127.0.0.1:5000/
   ```

##  Endpoints disponibles ##

El archivo `controller.py` expone los siguientes endpoints HTTP:

* Servidor

  * `POST /server/start` → Enciende el servidor (`Servidor.py` como proceso).
  * `POST /server/stop` → Apaga el servidor.

* Cliente

  * `POST /client/connect` → Conecta el cliente TCP al servidor.
  * `POST /client/disconnect` → Envía `salir` y cierra la conexión.
  * `POST /client/send` → Envía un mensaje al servidor y devuelve la respuesta.

* Historial

  * `GET /history` → Devuelve el historial de mensajes en memoria.

* Finalización

  * `POST /exit` → Cierra cliente y servidor.

## Componentes principales ##

* `controller.py` → Controlador Flask que actúa como intermediario entre la UI y el Cliente-Servidor.
* `Servidor.py` → Implementa el servidor TCP.
* `Cliente.py` → Implementa el cliente TCP.
  *(Nota: en esta versión, el backend integra un cliente TCP propio para evitar bloqueos con `input()`/`print()`. Esto mejora la robustez del sistema).*
* `templates/index.html` → Interfaz principal en el navegador.
* `static/js/app.js` → Lógica de interacción cliente-web (AJAX/Fetch API).
* `static/css/styles.css` → Estilos de la interfaz web.

## Interfaz gráfica ##

La interfaz muestra:

* Botones para encender/apagar servidor y conectar/desconectar cliente.
* Un campo de texto para enviar preguntas/mensajes al servidor.
* Un panel para visualizar **respuestas y el historial**.

Los estilos se definen en `static/css/styles.css` y pueden personalizarse fácilmente.

## Ficha técnica del sistema ##

## Arquitectura ##

* Frontend: HTML, CSS, JavaScript
* Backend: Python (Flask)
* Comunicación interna: HTTP entre UI ↔ Flask, y TCP entre Cliente ↔ Servidor

## Tecnologías ##

* Lenguaje: Python 3.10+
* Framework web: Flask
* Sockets TCP: módulo estándar `socket` de Python
* Interfaz: HTML5, CSS3, JavaScript (vanilla)

## Flujo de trabajo ##

1. El usuario interactúa con la UI web.
2. Flask recibe las solicitudes HTTP y ejecuta acciones en cliente/servidor TCP.
3. El servidor TCP responde al cliente.
4. Flask envía la respuesta al navegador, actualizando el historial.

##  Notas finales ##

* Este proyecto está diseñado para **evitar bloqueos en la comunicación** mediante un cliente TCP integrado en el backend, en lugar de depender de procesos interactivos.
* Se puede extender fácilmente para:

  * Registrar historial en base de datos.
  * Mejorar la UI con frameworks frontend.
  * Implementar autenticación de usuarios.
