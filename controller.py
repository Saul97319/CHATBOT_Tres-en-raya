import os
import sys
import socket
import threading
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = BASE_DIR / "Servidor.py"
CLIENT_SCRIPT = BASE_DIR / "Cliente.py"

HOST, PORT = "127.0.0.1", 65432
try:
    # Dynamic import without executing main()
    import importlib.util
    spec = importlib.util.spec_from_file_location("ServidorModule", SERVER_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    HOST = getattr(mod, "HOST", HOST)
    PORT = getattr(mod, "PORT", PORT)
except Exception:
    pass

app = Flask(__name__, static_url_path="/static", static_folder=str(BASE_DIR / "static"))

# --- State ---
server_proc: subprocess.Popen | None = None

class TCPClientSession:
    """Lightweight client that talks to the TCP server directly (robust for web)."""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self.lock = threading.Lock()

    def connect(self):
        if self.sock:
            return "Ya conectado."
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.sock = s
        greeting = s.recv(4096).decode("utf-8", errors="ignore").strip()
        return greeting

    def send(self, text: str) -> str:
        if not self.sock:
            raise RuntimeError("Cliente no conectado.")
        with self.lock:
            self.sock.sendall((text + "\n").encode("utf-8"))
            data = self.sock.recv(4096)
            return data.decode("utf-8", errors="ignore").strip()

    def disconnect(self):
        if self.sock:
            try:
                self.sock.sendall(("salir\n").encode("utf-8"))
                try:
                    self.sock.recv(4096)
                except Exception:
                    pass
            except Exception:
                pass
            try:
                self.sock.close()
            finally:
                self.sock = None

client_session = TCPClientSession(HOST, PORT)
history:list[dict] = []

# --- Helpers ---
def process_alive(p: subprocess.Popen | None) -> bool:
    return bool(p) and (p.poll() is None)

def start_server_process():
    global server_proc
    if process_alive(server_proc):
        return True
    # Start unbuffered so logs flush
    server_proc = subprocess.Popen([sys.executable, "-u", str(SERVER_SCRIPT)],
                                  cwd=str(BASE_DIR),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  text=True)
    # Optional: read server log in background to avoid pipe filling
    def _drain(proc: subprocess.Popen):
        try:
            for _ in proc.stdout:  # type: ignore[attr-defined]
                pass
        except Exception:
            pass
    threading.Thread(target=_drain, args=(server_proc,), daemon=True).start()
    return True

def stop_server_process():
    global server_proc
    if not process_alive(server_proc):
        server_proc = None
        return
    try:
        server_proc.terminate()  # send SIGTERM / terminate on Windows
        server_proc.wait(timeout=2)
    except Exception:
        try:
            server_proc.kill()
        except Exception:
            pass
    finally:
        server_proc = None

# --- Routes ---
@app.get("/")
def index():
    return send_from_directory(str(BASE_DIR), "index.html")

BASE_DIR = Path(__file__).resolve().parent

@app.get("/game.html")
def serve_game_html():
    return send_from_directory(BASE_DIR, "game.html")

# Opcional: atajo /game
@app.get("/game")
def serve_game_short():
    return send_from_directory(BASE_DIR, "game.html")
@app.get("/status")
def status():
    return jsonify({
        "server_on": process_alive(server_proc),
        "client_on": client_session.sock is not None,
        "host": HOST, "port": PORT
    })

@app.post("/server/start")
def server_start():
    start_server_process()
    return jsonify({"ok": True, "server_on": True})

@app.post("/server/stop")
def server_stop():
    stop_server_process()
    return jsonify({"ok": True, "server_on": False})

@app.post("/client/connect")
def client_connect():
    try:
        greet = client_session.connect()
        return jsonify({"ok": True, "client_on": True, "greeting": greet})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/client/disconnect")
def client_disconnect():
    try:
        client_session.disconnect()
        return jsonify({"ok": True, "client_on": False, "message": "Cliente desconectado."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.post("/client/send")
def client_send():
    data = request.get_json(force=True, silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"ok": False, "error": "Mensaje vacío."}), 400
    try:
        reply = client_session.send(msg)
        history.append({"q": msg, "a": reply})
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/history")
def get_history():
    return jsonify({"items": history})

@app.post("/exit")
def exit_all():
    try:
        client_session.disconnect()
    except Exception:
        pass
    try:
        stop_server_process()
    except Exception:
        pass
    return jsonify({"ok": True})

# --- Static (already configured by Flask) ---

if __name__ == "__main__":
    # Print where the files are for convenience
    print(f"HOST={HOST} PORT={PORT}")
    app.run(host="127.0.0.1", port=5000, debug=True)
