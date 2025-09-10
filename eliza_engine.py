import re

_REFLECT = {
    r"\byo\b": "tú",
    r"\bme\b": "te",
    r"\bmi\b": "tu",
    r"\bmío\b": "tuyo",
    r"\bmia\b": "tuya",
    r"\bmios\b": "tuyos",
    r"\bmias\b": "tuyas",
    r"\bconmigo\b": "contigo",
    r"\bsobre mí\b": "sobre ti",
    r"\bsoy\b": "eres",
    r"\bestoy\b": "estás",
    r"\bera\b": "eras",
    r"\bfui\b": "fuiste",
    r"\bpuedo\b": "puedes",
    r"\bquiero\b": "quieres",
    r"\bnecesito\b": "necesitas",
    r"\bpienso\b": "piensas",
    r"\bsiento\b": "sientes",
    r"\bmis\b": "tus",
}

def _strip_trailing_punct(s: str) -> str:
    return re.sub(r"[\s\.,;:!¿?]+$", "", s or "")

def _reflect(text: str) -> str:
    res = " " + _strip_trailing_punct(text.strip()) + " "
    for pat, repl in _REFLECT.items():
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    return res.strip()

_RULES = [
    (re.compile(r"^\s*estoy\s+.*\bporque\s+(.*)$", re.I),
     lambda m: f"¿Por qué crees que {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*estoy\s+(.*)$", re.I),
     lambda m: f"¿Por qué estás {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*(no\s+)?me\s+([a-záéíóúñ]+.*)$", re.I),
     lambda m: f"¿Qué te hace pensar que {('no te ' if m.group(1) else 'te ')}{_reflect(m.group(2))}?"),
    (re.compile(r"^\s*siento\s+(.*)$", re.I),
     lambda m: f"¿Desde cuándo sientes que {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*quiero\s+(.*)$", re.I),
     lambda m: f"¿Por qué quieres {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*porque\s+(.*)$", re.I),
     lambda m: "¿Esa es la razón principal? ¿Hay otras razones?"),
    (re.compile(r"^\s*pienso\s+que\s+(.*)$", re.I),
     lambda m: f"¿Qué te lleva a pensar que {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*no\s+([a-záéíóúñ]+.*)$", re.I),
     lambda m: f"¿Por qué no {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*(siempre|nunca)\s+(.*)$", re.I),
     lambda m: f"¿Realmente {m.group(1).lower()} {_reflect(m.group(2))}? ¿Puedes recordar alguna excepción?"),
    (re.compile(r"^\s*eres\s+(.*)$", re.I),
     lambda m: f"¿Por qué crees que soy {_reflect(m.group(1))}?"),
    (re.compile(r"^\s*soy\s+(.*)$", re.I),
     lambda m: f"¿Desde cuándo eres {_reflect(m.group(1))}?"),
    (re.compile(r".*\bque\s+no\s+me\s+([a-záéíóúñ]+.*)$", re.I),
     lambda m: f"¿Por qué crees que no te {_reflect(m.group(1))}?"),
]

def eliza_reply(text: str):
    if not text or text.strip() == "":
        return None
    t = text.strip()
    if "?" in t and not re.search(r"^\s*(estoy|soy|me|siento|quiero|porque|pienso)\b", t, flags=re.I):
        return None
    for pat, func in _RULES:
        m = pat.match(t)
        if m:
            try:
                resp = func(m)
            except Exception:
                continue
            resp = re.sub(r"\s{2,}", " ", resp).strip()
            resp = _strip_trailing_punct(resp)
            if not resp.endswith("?"):
                resp += "?"
            return resp
    if len(t.split()) >= 2:
        return "Entiendo. ¿Puedes contarme un poco más?"
    return None
