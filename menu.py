"""Selección de personaje y dificultad en la pantalla de entrada."""

import pygame

import ajustes as a
from animales import ANIMALES, dibujar_macaquito


def escribir(pantalla, fuente, texto, y, color=a.TEXTO, x=a.ANCHO // 2):
    """Dibuja una línea centrada en las coordenadas indicadas."""
    imagen = fuente.render(texto, True, color)
    pantalla.blit(imagen, imagen.get_rect(center=(x, y)))


class Menu:
    """Mantiene las opciones elegidas y comparte sus áreas de clic y dibujo."""

    def __init__(self):
        """Prepara las tarjetas de las dos filas y el botón de inicio."""
        centros = (230, 430, 630)
        self.personajes = {
            nombre: pygame.Rect(x - 69, 157, 138, 98)
            for x, nombre in zip((126, 278, 430, 582, 734), ANIMALES)
        }
        self.niveles = {
            nivel: pygame.Rect(x-92, 306, 184, 77)
            for x, nivel in zip(centros, a.DIFICULTADES)
        }
        self.boton = pygame.Rect(310, 430, 240, 44)
        self.personaje = "Mono"
        self.nivel = "Normal"

    def pulsar(self, posicion):
        """Aplica la opción pulsada y devuelve si se pidió jugar."""
        for nombre, tarjeta in self.personajes.items():
            if tarjeta.collidepoint(posicion):
                self.personaje = nombre
        for nivel, tarjeta in self.niveles.items():
            if tarjeta.collidepoint(posicion):
                self.nivel = nivel
        return self.boton.collidepoint(posicion)

    def dibujar(self, pantalla, titulo, normal, records, posicion):
        """Muestra opciones, récords y estado de la linterna."""
        escribir(pantalla, titulo, "Macaquito", 63, a.BOLSO)
        escribir(pantalla, normal, "Vuelo nocturno", 106)
        escribir(pantalla, normal, "Elegí tu animal", 137)
        for nombre, tarjeta in self.personajes.items():
            dibujar_tarjeta(pantalla, tarjeta, nombre == self.personaje)
            dibujar_macaquito(pantalla, tarjeta.centerx, 190, nombre)
            escribir(pantalla, normal, nombre, 232, x=tarjeta.centerx)

        escribir(pantalla, normal, "Dificultad", 285)
        for nivel, tarjeta in self.niveles.items():
            dibujar_tarjeta(pantalla, tarjeta, nivel == self.nivel)
            escribir(pantalla, normal, nivel, 329, x=tarjeta.centerx)
            escribir(pantalla, normal, f"Récord {records[nivel]}/{a.META}", 358, x=tarjeta.centerx)

        listo = posicion is not None
        pygame.draw.rect(pantalla, a.BOLSO if listo else a.ROCA, self.boton, border_radius=9)
        escribir(pantalla, normal, "Jugar", self.boton.centery, a.FONDO if listo else a.TEXTO)
        aviso = "Linterna detectada · Clic en Jugar o Espacio" if listo else "Mostrá la linterna a la cámara para jugar"
        escribir(pantalla, normal, aviso, 500)


def dibujar_tarjeta(pantalla, tarjeta, elegida):
    """Resalta la opción actual con un borde amarillo."""
    pygame.draw.rect(pantalla, a.ROCA, tarjeta, border_radius=12)
    pygame.draw.rect(
        pantalla, a.BOLSO if elegida else a.BORDE, tarjeta, 2, border_radius=12
    )
