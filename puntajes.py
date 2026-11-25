"""Lee y guarda el mejor puntaje local de cada dificultad."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from ajustes import DIFICULTADES, META

ARCHIVO = Path(__file__).resolve().with_name("records.json")


def cargar():
    """Recupera récords válidos y usa cero para los faltantes."""
    try:
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = {}
    if not isinstance(datos, dict):
        datos = {}
    return {
        nivel: puntos if type(puntos) is int and 0 <= puntos <= META else 0
        for nivel in DIFICULTADES
        for puntos in (datos.get(nivel),)
    }


def guardar(records):
    """Reemplaza el archivo de récords solo cuando termina de escribirlo."""
    temporal = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=ARCHIVO.parent, delete=False
        ) as archivo:
            temporal = Path(archivo.name)
            json.dump(records, archivo, ensure_ascii=False)
        temporal.replace(ARCHIVO)
        return True
    except OSError:
        return False
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
