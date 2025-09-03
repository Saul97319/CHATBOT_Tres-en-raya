import socket

HOST = "127.0.0.1"
PORT = 65432

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        bienvenida = s.recv(4096).decode("utf-8", errors="ignore")
        print(bienvenida, end="")
        while True:
            try:
                pregunta = input("> ")
            except (EOFError, KeyboardInterrupt):
                pregunta = "salir"
            s.sendall((pregunta + "\n").encode("utf-8"))
            data = s.recv(4096)
            if not data:
                break
            respuesta = data.decode("utf-8", errors="ignore")
            print(respuesta, end="")
            if "Adiós." in respuesta:
                break

if __name__ == "__main__":
    main()
