"""Dibuja los cinco pilotos que se pueden elegir en el menú."""

import pygame

from ajustes import FONDO, RADIO

ANIMALES = {
    "Mono": ((156, 92, 66), (252, 193, 132), (255, 222, 110)),
    "Zorro": ((221, 115, 63), (255, 234, 195), (139, 224, 210)),
    "Conejo": ((202, 180, 211), (255, 225, 236), (245, 153, 196)),
    "Panda": ((242, 233, 216), (44, 51, 72), (160, 217, 119)),
    "Rana": ((112, 187, 103), (189, 231, 122), (255, 175, 106)),
}


def dibujar_macaquito(pantalla, x, y, personaje):
    """Dibuja un piloto con orejas, cara y colores propios."""
    cuerpo, detalle, mochila = ANIMALES[personaje]
    y = round(y)
    pygame.draw.circle(pantalla, mochila, (x - 18, y + 7), 10)

    # Las orejas quedan detrás de la cabeza, salvo los ojos saltones de la rana.
    if personaje == "Zorro":
        for oreja in (x - 13, x + 13):
            pygame.draw.polygon(
                pantalla, cuerpo, [(oreja - 9, y - 9), (oreja, y - 29), (oreja + 9, y - 9)]
            )
    elif personaje == "Conejo":
        for oreja in (x - 13, x + 3):
            pygame.draw.ellipse(pantalla, cuerpo, (oreja, y - 34, 10, 25))
            pygame.draw.ellipse(pantalla, detalle, (oreja + 3, y - 31, 4, 15))
    elif personaje in ("Panda", "Mono"):
        color = detalle if personaje == "Panda" else cuerpo
        pygame.draw.circle(pantalla, color, (x - 15, y - 16), 8)
        pygame.draw.circle(pantalla, color, (x + 13, y - 16), 8)

    pygame.draw.circle(pantalla, cuerpo, (x, y), RADIO)
    if personaje == "Panda":
        pygame.draw.ellipse(pantalla, detalle, (x - 12, y - 6, 12, 15))
        pygame.draw.ellipse(pantalla, detalle, (x + 5, y - 6, 12, 15))
        pygame.draw.circle(pantalla, cuerpo, (x - 6, y - 1), 2)
        pygame.draw.circle(pantalla, cuerpo, (x + 11, y - 1), 2)
    elif personaje == "Rana":
        for ojo in (x - 10, x + 10):
            pygame.draw.circle(pantalla, cuerpo, (ojo, y - 15), 9)
            pygame.draw.circle(pantalla, detalle, (ojo, y - 15), 6)
            pygame.draw.circle(pantalla, FONDO, (ojo + 2, y - 15), 3)
        pygame.draw.arc(pantalla, FONDO, (x - 10, y - 2, 22, 13), 3.4, 5.9, 2)
    else:
        pygame.draw.ellipse(pantalla, detalle, (x - 12, y - 9, 32, 25))
        pygame.draw.circle(pantalla, FONDO, (x + 7, y - 5), 3)
        pygame.draw.circle(pantalla, FONDO, (x + 17, y + 4), 3)
