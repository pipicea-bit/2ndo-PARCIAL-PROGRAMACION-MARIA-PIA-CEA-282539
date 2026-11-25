"""Constantes de vuelo, presentación y detección de luz."""

ANCHO, ALTO = 860, 540
HUD = 58
FPS = 60
TITULO = "Macaquito · Vuelo nocturno"
FONDO = (14, 23, 45)
TEXTO = (255, 245, 216)
ESTRELLA = (75, 90, 124)
ROCA = (50, 73, 109)
BORDE = (114, 147, 174)
PELAJE = (156, 92, 66)
CARA = (252, 193, 132)
BOLSO = (255, 222, 110)
X_MACAQUITO = 180
RADIO = 22
VELOCIDAD_VERTICAL = 300
ANCHO_OBSTACULO = 70
ESPACIO_ENTRE_OBSTACULOS = 310
MARGEN_HUECO = 34
# Cada nivel define velocidad inicial, aumento, hueco inicial, mínimo y reducción.
DIFICULTADES = {
    "Fácil": (150, 7, 250, 200, 4),
    "Normal": (195, 13, 210, 148, 6),
    "Difícil": (235, 15, 178, 125, 6),
}
PERSONAJES = {
    "Coco": (PELAJE, CARA, BOLSO),
    "Nube": ((137, 145, 174), (239, 219, 197), (130, 222, 245)),
    "Chispa": ((175, 103, 112), (255, 210, 175), (245, 153, 196)),
}
META = 12
CAMARA = 0
BRILLO_MINIMO = 245
PISO_MASCARA = 225
DIFERENCIA_BRILLO = 15
AREA_MINIMA = 10
FRACCION_MAXIMA = 0.12
FILTRO = (3, 3)
