# UI web para tu Cliente-Servidor (HTML + CSS + Flask)

Este proyecto incluye:
- Botones para encender/apagar el servidor (`Servidor.py`).
- Botones para conectar/desconectar el cliente.
- Área de chat con burbujas.
- Historial de preguntas.
- Opción de Salir.

> Requisitos: Python 3.10+, `pip install flask`

## Cómo ejecutar

1. Copia `Servidor.py` y `Cliente.py` a esta misma carpeta.
2. En una terminal, ejecuta:

```bash
pip install flask
python controller.py
```

4. Abre en el navegador: `http://127.0.0.1:5000/`

## Notas técnicas

- Los endpoints HTTP están en `controller.py`:
  - `POST /server/start` – enciende el servidor (lanza `Servidor.py` como proceso).
  - `POST /server/stop` – apaga el servidor.
  - `POST /client/connect` – abre un socket TCP directo al servidor.
  - `POST /client/disconnect` – envía `"salir"` y cierra el socket.
  - `POST /client/send` – envía una pregunta y devuelve la respuesta.
  - `GET  /history` – historial en memoria.
  - `POST /exit` – cierra cliente y servidor.

- Por robustez, el backend actúa como cliente TCP integrado (sin usar `input()`/`print()`), lo que evita
  problemas con "pipes" bloqueantes típicos de procesos interactivos.
  Si necesitas forzar el uso exacto de `Cliente.py` como proceso, te puedo pasar una variación del
  controlador con ese modo.

- Los colores y estilos viven en `static/css/styles.css`.
- Toda la UI está en `index.html` y `static/js/app.js`.

¡Listo!