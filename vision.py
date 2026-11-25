"""Lee la webcam y localiza el punto más brillante del cuadro."""

import cv2

from ajustes import (
    AREA_MINIMA, BRILLO_MINIMO, CAMARA, DIFERENCIA_BRILLO, FILTRO,
    FRACCION_MAXIMA, PISO_MASCARA,
)

KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, FILTRO)


def abrir_camara():
    """Abre la webcam una sola vez para toda la sesión."""
    return cv2.VideoCapture(CAMARA)


def detectar(cap):
    """Devuelve el centro normalizado del foco de luz o None."""
    exito, cuadro = cap.read()
    if not exito:
        return None

    # Espejar mantiene la correspondencia con el movimiento del jugador.
    cuadro = cv2.flip(cuadro, 1)
    gris = cv2.cvtColor(cuadro, cv2.COLOR_BGR2GRAY)
    _, maximo, _, _ = cv2.minMaxLoc(gris)
    if maximo < BRILLO_MINIMO:
        return None

    # Conservamos únicamente los píxeles cercanos al brillo máximo.
    umbral = max(PISO_MASCARA, int(maximo) - DIFERENCIA_BRILLO)
    mascara = cv2.inRange(gris, umbral, 255)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, KERNEL)
    contornos, _ = cv2.findContours(
        mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    foco = max(contornos, key=cv2.contourArea, default=None)
    alto, ancho = gris.shape
    if foco is None or not AREA_MINIMA <= cv2.contourArea(foco) <= alto * ancho * FRACCION_MAXIMA:
        return None

    momentos = cv2.moments(foco)
    return (
        momentos["m10"] / momentos["m00"] / ancho,
        momentos["m01"] / momentos["m00"] / alto,
    )
