"""Lee y guarda el mejor puntaje local de cada dificultad."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from ajustes import METAS, PUNTOS_TURBO

ARCHIVO = Path(__file__).resolve().with_name("records.json")


def cargar():
    """Recupera récords válidos y usa cero para los faltantes."""
    try:
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = {}
    if not isinstance(datos, dict):
        datos = {}
    records = dict.fromkeys(METAS, 0)
    for nivel, meta in METAS.items():
        puntos = datos.get(nivel, 0)
        if type(puntos) is int and puntos >= 0:
            records[nivel] = puntos if meta is None else min(puntos, meta * PUNTOS_TURBO)
    return records


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
