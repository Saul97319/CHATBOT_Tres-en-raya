import socket
import threading
import unicodedata
import difflib
import eliza_engine

HOST = "127.0.0.1"
PORT = 65432

# ---------------- Normalización / Estándar de preguntas ----------------
def normaliza(txt: str) -> str:
    txt = txt.strip().lower()
    txt = "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )
    for ch in "¿?¡!.,;:-_()[]{}\"'":
        txt = txt.replace(ch, " ")
    txt = " ".join(txt.split())
    return txt

def estandariza_pregunta(txt: str) -> str:
    """
    Convierte a minúsculas y elimina signos como ¿? (y otros).
    Es un alias explícito que usa la lógica existente de normaliza().
    """
    return normaliza(txt)

# ---------------- Base de conocimiento  ----------------
def base_conocimiento():
    pares = {
        "como te llamas?": "Mi nombre es Diego.",
        "que edad tienes?": "Tengo la corta edad de 21.",
        "de donde eres?": "Vengo de Mexico wey.",
        "cual es tu color favorito?": "Azul.",
        "cual es tu comida favorita?": "Me encantan las enchiladas suizas.",
        "que musica te gusta?": "Banda, pop y rock.",
        "que idioma hablas?": "Principalmente español.",
        "quien es tu creador?": "Fui creado por un ser celestial que me gusta llamar Dios.",
        "que puedes hacer?": "Muchas cosas productivas e interesantes.",
        "como estas?": "Muy bien amigo gracias",
        "cuantos continentes hay?": "Siete.",
        "capital de mexico?": "Ciudad de México.",
        "capital de francia?": "París.",
        "quien escribio don quijote?": "Miguel de Cervantes.",
        "planeta mas cercano al sol?": "Mercurio.",
        "como se llama el planeta rojo?": "Marte.",
        "oceano mas grande?": "Océano Pacífico.",
        "animal terrestre mas rapido?": "Guepardo.",
        "mamifero mas grande?": "La ballena azul.",
        "metal liquido a temperatura ambiente?": "Mercurio.",
        "resultado de 2 + 2?": "4.",
        "cuantos dias tiene un ano bisiesto?": "366.",
        "formula quimica del agua?": "H2O.",
        "idioma oficial de brasil?": "Portugués.",
        "moneda de japon?": "Yen.",
        "capital de espana?": "Madrid.",
        "quien pinto la mona lisa?": "Leonardo da Vinci.",
        "en que continente esta egipto?": "África.",
        "punto de congelacion del agua en c?": "0 °C.",
        "quien fue albert einstein?": "Un físico teórico de renombre mundial.",
        "area de un triangulo?": "Base por altura dividido entre 2.",
        "cuantas horas tiene un dia?": "24.",
        "cuantos minutos tiene una hora?": "60.",
        "cuantos segundos tiene un minuto?": "60.",
        "que es la fotosintesis?": "Proceso por el que las plantas transforman luz en energia.",
        "que significa cpu?": "Unidad Central de Procesamiento.",
        "que es un byte?": "Conjunto de 8 bits.",
        "que es http?": "Un protocolo para transferir informacion en la web.",
        "que es la www?": "La World Wide Web, un sistema de documentos interconectados.",
        "quien fundo microsoft?": "Bill Gates y Paul Allen.",
        "quien fundo apple?": "Steve Jobs, Steve Wozniak y Ronald Wayne.",
        "capital de argentina?": "Buenos Aires.",
        "capital de colombia?": "Bogotá.",
        "capital de peru?": "Lima.",
        "capital de chile?": "Santiago.",
        "capital de italia?": "Roma.",
        "capital de alemania?": "Berlín.",
        "capital de canada?": "Ottawa.",
        "capital de estados unidos?": "Washington, D. C.",
        "montana mas alta del mundo?": "El Monte Everest.",
        "capa mas externa de la tierra?": "La corteza terrestre.",
        "que gas respiramos principalmente?": "Oxígeno (aprox. 21% del aire).",
        "cuantos huesos tiene el cuerpo humano adulto?": "206.",
        "simbolo quimico del oro?": "Au.",
        "que significa onu?": "Organizacion de las Naciones Unidas.",
        "que significa nasa?": "Administracion Nacional de Aeronautica y del Espacio.",
        "resultado de 9 x 9?": "81.",
        "numero pi aproximado?": "3.1416.",
        "en que pais esta la torre eiffel?": "Francia.",
    }
    assert len(pares) >= 50, f"Se esperaban 50 entradas, hay {len(pares)}"
    return {normaliza(k): v for k, v in pares.items()}

QA = base_conocimiento()
CLAVES = list(QA.keys())

# ---------------- Aritmética en lenguaje natural ----------------
def operar(a: float, op: str, b: float) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ZeroDivisionError("División entre cero")
        return a / b
    raise ValueError("Operador no soportado")

_UNIDADES = {
    "cero":0, "un":1, "uno":1, "una":1, "dos":2, "tres":3, "cuatro":4,
    "cinco":5, "seis":6, "siete":7, "ocho":8, "nueve":9
}
_ESPECIALES = {
    "diez":10, "once":11, "doce":12, "trece":13, "catorce":14, "quince":15,
    "dieciseis":16, "diecisiete":17, "dieciocho":18, "diecinueve":19,
    "veinte":20, "veintiuno":21, "veintidos":22, "veintitres":23,
    "veinticuatro":24, "veinticinco":25, "veintiseis":26, "veintisiete":27,
    "veintiocho":28, "veintinueve":29
}
_DECENAS = {
    "treinta":30, "cuarenta":40, "cincuenta":50, "sesenta":60,
    "setenta":70, "ochenta":80, "noventa":90
}
_CIENTOS = {
    "cien":100, "ciento":100, "doscientos":200, "trescientos":300,
    "cuatrocientos":400, "quinientos":500, "seiscientos":600,
    "setecientos":700, "ochocientos":800, "novecientos":900
}
_MULTIPLIERS = {"mil":1000}

def _parse_num_palabras(tokens, i0):
    """
    Intenta leer un número en español empezando en tokens[i0].
    Devuelve (valor, consumidos) o (None, 0) si no hay número.
    Soporta 0..9999 aprox. (unidades, decenas con 'y', cientos y 'mil').
    """
    n = len(tokens)
    i = i0
    valor = 0
    actual = 0
    consumidos = 0

    while i < n:
        t = tokens[i]
        if t == "y":
            i += 1; consumidos += 1
            continue
        if t in _MULTIPLIERS:
            mult = _MULTIPLIERS[t]
            if actual == 0:
                actual = 1
            valor += actual * mult
            actual = 0
            i += 1; consumidos += 1
            continue
        if t in _CIENTOS:
            actual += _CIENTOS[t]
            i += 1; consumidos += 1
            continue
        if t in _DECENAS:
            actual += _DECENAS[t]
            i += 1; consumidos += 1
            continue
        if t in _ESPECIALES:
            actual += _ESPECIALES[t]
            i += 1; consumidos += 1
            continue
        if t in _UNIDADES:
            actual += _UNIDADES[t]
            i += 1; consumidos += 1
            continue
        break

    if consumidos == 0:
        return None, 0
    return valor + actual, consumidos

_OP_MAP = {
    "+": "+", "-": "-", "*": "*", "/": "/",
    "x": "*",
    "mas": "+", "menos": "-", "por": "*", "entre": "/", "dividido": "/", "multiplicado": "*",
    "sumar": "+", "restar": "-", "multiplicar": "*", "dividir": "/",
}

def _float_token(tok: str):
    t = tok.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None

def _extrae_operacion(k: str):
    """
    De un texto normalizado 'k' obtiene el primer patrón:
        número  operador  número
    Retorna (a, op, b) o None si no lo encuentra.
    """
    tokens = k.split()
    items = []  # mezcla de floats y ops str
    i = 0
    while i < len(tokens):
        t = tokens[i]
        # operador
        if t in _OP_MAP:
            items.append(_OP_MAP[t])
            i += 1
            continue
        # número en dígitos (acepta decimales . o ,)
        v = _float_token(t)
        if v is not None:
            items.append(v)
            i += 1
            continue
        # número en palabras (puede abarcar varios tokens)
        v2, used = _parse_num_palabras(tokens, i)
        if used > 0:
            items.append(float(v2))
            i += used
            continue
        # otro texto -> ignorar
        i += 1

    # Buscar el primer patrón número op número
    for j in range(len(items) - 2):
        if isinstance(items[j], (int, float)) and isinstance(items[j+2], (int, float)) and isinstance(items[j+1], str):
            return float(items[j]), items[j+1], float(items[j+2])
    return None

def _fmt_num(x: float) -> str:
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return f"{x:.10g}"

def intenta_aritmetica(k: str):
    trio = _extrae_operacion(k)
    if not trio:
        return None
    a, op, b = trio
    try:
        r = operar(a, op, b)
    except ZeroDivisionError:
        return "Error: división entre cero."
    except Exception:
        return None
    return f"Resultado: {_fmt_num(r)}"

# ---------------- Respuesta principal ----------------
def responder(pregunta_original: str) -> str:
    k = estandariza_pregunta(pregunta_original)
    if not k:
        return "Pregunta vacía. Intenta de nuevo."

    # 1) Intento de aritmética básica a partir de la frase
    posible = intenta_aritmetica(k)
    if posible is not None:
        return posible

    # 2) Preguntas de la base de conocimiento
    if k in QA:
        return QA[k]
    # 2.5) Intenta respuesta estilo terapeuta (patrones ELIZA)
    eliza = eliza_engine.eliza_reply(pregunta_original)
    if eliza is not None:
        return eliza

    sugerencias = difflib.get_close_matches(k, CLAVES, n=1, cutoff=0.82)
    if sugerencias:
        mejor = sugerencias[0]
        return f"No tengo esa exacta. ¿Quisiste decir: '{mejor}'?\nRespuesta: {QA[mejor]}"
    return "No sé esa. Intenta una pregunta corta y básica."

# ---------------- Servidor TCP (sin cambios) ----------------
def maneja_cliente(conn, addr):
    try:
        conn.sendall("Conectado al servidor de preguntas. Escribe 'salir' para terminar.\n".encode("utf-8"))
        while True:
            data = conn.recv(4096)
            if not data:
                break
            pregunta = data.decode("utf-8", errors="ignore").strip()
            if normaliza(pregunta) == "salir":
                conn.sendall("Adiós.\n".encode("utf-8"))
                break
            respuesta = responder(pregunta)
            conn.sendall((respuesta + "\n").encode("utf-8"))
    finally:
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT} (Ctrl+C para salir)")
        while True:
            conn, addr = s.accept()
            hilo = threading.Thread(target=maneja_cliente, args=(conn, addr), daemon=True)
            hilo.start()

if __name__ == "__main__":
    main()

