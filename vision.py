"""Calibra la webcam con la linterna apagada y sigue el foco al encenderla."""

import cv2

from ajustes import (
    AREA_MINIMA, AUMENTO_BRILLO_MINIMO, BRILLO_MINIMO, CAMARA,
    CONTRASTE_FOCO_MINIMO, CUADROS_CONFIRMACION, CUADROS_PERDIDOS_CONFIRMACION,
    DESPLAZAMIENTO_CONFIRMACION, FACTOR_AREA_FOCO, FILTRO, FRACCION_MAXIMA,
    MARGEN_GUIA_LINTERNA, TOLERANCIA_BRILLO_FOCO, VENTANA_CONTRASTE,
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
        self.perfil = None
        self.candidato = None
        self.cuadro_valido = False

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
        self.perfil = None
        self.candidato = None
        self.cuadro_valido = False
        return True

    def detectar(self, en_misma_zona=False):
        """Devuelve el centro normalizado del nuevo foco, o None."""
        gris = leer_gris(self.cap)
        self.candidato = None
        self.cuadro_valido = (
            gris is not None and self.ambiente is not None and gris.shape == self.ambiente.shape
        )
        if not self.cuadro_valido:
            return None

        # El foco debe destacar sobre la referencia y sobre sus alrededores.
        # Compensamos ajustes de exposición que afectan toda la imagen.
        cambio_exposicion = max(0, round(cv2.mean(gris)[0] - cv2.mean(self.ambiente)[0]))
        aumento = cv2.subtract(gris, self.ambiente)
        contraste = cv2.subtract(gris, cv2.blur(gris, VENTANA_CONTRASTE))
        mascara = cv2.bitwise_and(
            cv2.inRange(gris, BRILLO_MINIMO, 255),
            cv2.inRange(aumento, min(255, AUMENTO_BRILLO_MINIMO + cambio_exposicion), 255),
        )
        mascara = cv2.bitwise_and(mascara, cv2.inRange(contraste, CONTRASTE_FOCO_MINIMO, 255))
        cantidad, _, datos, centros = cv2.connectedComponentsWithStats(mascara)
        alto, ancho = gris.shape
        area_maxima = alto * ancho * FRACCION_MAXIMA
        focos = []
        for i in range(1, cantidad):
            x, y, ancho_foco, alto_foco, area = datos[i]
            if not AREA_MINIMA <= area <= area_maxima:
                continue
            if max(ancho_foco, alto_foco) > 3 * min(ancho_foco, alto_foco):
                continue
            punto = (centros[i, 0] / ancho, centros[i, 1] / alto)
            if en_misma_zona and self.anterior is not None:
                if distancia2(punto, self.anterior) > DESPLAZAMIENTO_CONFIRMACION ** 2:
                    continue
            if self.perfil is None and not all(
                MARGEN_GUIA_LINTERNA <= valor <= 1 - MARGEN_GUIA_LINTERNA for valor in punto
            ):
                continue
            zona = gris[y:y + alto_foco, x:x + ancho_foco]
            brillo = int(zona.max())
            if self.perfil is not None:
                area_ref, brillo_ref = self.perfil
                if not area_ref / FACTOR_AREA_FOCO <= area <= area_ref * FACTOR_AREA_FOCO:
                    continue
                if brillo < brillo_ref - TOLERANCIA_BRILLO_FOCO:
                    continue
            focos.append((punto, area, brillo))

        if not focos:
            return None
        if self.anterior is None:
            elegido = max(focos, key=lambda foco: foco[2])
        else:
            elegido = min(focos, key=lambda foco: distancia2(foco[0], self.anterior))
        punto, area, brillo = elegido
        self.candidato = (area, brillo)
        return punto

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
        if self.consecutivos < CUADROS_CONFIRMACION:
            return False
        self.perfil = self.candidato
        return True

    def seguir(self, posicion):
        """Actualiza la referencia del último punto válido durante el vuelo."""
        if posicion is not None:
            self.anterior = posicion


def distancia2(primero, segundo):
    """Devuelve la distancia al cuadrado entre dos puntos normalizados."""
    return (primero[0] - segundo[0]) ** 2 + (primero[1] - segundo[1]) ** 2
