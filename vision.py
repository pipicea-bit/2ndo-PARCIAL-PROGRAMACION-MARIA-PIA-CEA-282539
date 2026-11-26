"""Calibra la webcam con la linterna apagada y sigue el foco al encenderla."""

import cv2

from ajustes import (
    AREA_MINIMA, AUMENTO_BRILLO_MINIMO, BRILLO_MINIMO, CAMARA,
    CONTRASTE_FOCO_MINIMO, CUADROS_CONFIRMACION, CUADROS_PERDIDOS_CONFIRMACION,
    DESPLAZAMIENTO_CONFIRMACION, FILTRO, FRACCION_MAXIMA, VENTANA_CONTRASTE,
)

KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, FILTRO)


def abrir_camara():
    """Abre la webcam una sola vez para toda la sesión."""
    return cv2.VideoCapture(CAMARA)


def leer_gris(cap):
    """Lee un cuadro en escala de grises y lo espeja, o devuelve None."""
    exito, cuadro = cap.read()
    if not exito:
        return None
    return cv2.cvtColor(cv2.flip(cuadro, 1), cv2.COLOR_BGR2GRAY)


class LectorLinterna:
    """Distingue una fuente puntual nueva de las luces que ya había en el cuadro."""

    def __init__(self, cap):
        """Usa la cámara abierta por el juego y empieza sin referencia."""
        self.cap = cap
        self.ambiente = None
        self.anterior = None
        self.consecutivos = 0
        self.perdidos = 0

    def registrar_ambiente(self):
        """Guarda la referencia que debe tomarse con la linterna apagada."""
        ambiente = leer_gris(self.cap)
        if ambiente is None:
            return False
        # Dilatar la referencia también descarta bordes brillantes de una ventana.
        self.ambiente = cv2.dilate(ambiente, KERNEL)
        self.anterior = None
        self.consecutivos = 0
        self.perdidos = 0
        return True

    def detectar(self):
        """Devuelve el centro normalizado del nuevo foco, o None."""
        gris = leer_gris(self.cap)
        if gris is None or self.ambiente is None or gris.shape != self.ambiente.shape:
            return None

        # El foco debe destacar sobre la referencia y sobre sus alrededores.
        aumento = cv2.subtract(gris, self.ambiente)
        contraste = cv2.subtract(gris, cv2.blur(gris, VENTANA_CONTRASTE))
        mascara = cv2.bitwise_and(
            cv2.inRange(gris, BRILLO_MINIMO, 255),
            cv2.inRange(aumento, AUMENTO_BRILLO_MINIMO, 255),
        )
        mascara = cv2.bitwise_and(mascara, cv2.inRange(contraste, CONTRASTE_FOCO_MINIMO, 255))
        cantidad, _, datos, centros = cv2.connectedComponentsWithStats(mascara)
        alto, ancho = gris.shape
        area_maxima = alto * ancho * FRACCION_MAXIMA
        focos = [
            i for i in range(1, cantidad)
            if AREA_MINIMA <= datos[i, cv2.CC_STAT_AREA] <= area_maxima
        ]
        if not focos:
            return None

        posiciones = {
            i: (centros[i, 0] / ancho, centros[i, 1] / alto) for i in focos
        }
        if self.anterior is None:
            foco = max(focos, key=lambda i: datos[i, cv2.CC_STAT_AREA])
        else:
            foco = min(focos, key=lambda i: distancia2(posiciones[i], self.anterior))
        return posiciones[foco]

    def confirmar(self, posicion):
        """Confirma el foco tras varios cuadros seguidos en la misma zona."""
        if posicion is None:
            self.perdidos += 1
            if self.perdidos > CUADROS_PERDIDOS_CONFIRMACION:
                self.anterior = None
                self.consecutivos = 0
            return False
        self.perdidos = 0
        limite = DESPLAZAMIENTO_CONFIRMACION ** 2
        if self.anterior is None or distancia2(posicion, self.anterior) > limite:
            self.consecutivos = 0
        self.anterior = posicion
        self.consecutivos += 1
        return self.consecutivos >= CUADROS_CONFIRMACION

    def seguir(self, posicion):
        """Actualiza la referencia del último punto válido durante el vuelo."""
        if posicion is not None:
            self.anterior = posicion


def distancia2(primero, segundo):
    """Devuelve la distancia al cuadrado entre dos puntos normalizados."""
    return (primero[0] - segundo[0]) ** 2 + (primero[1] - segundo[1]) ** 2
