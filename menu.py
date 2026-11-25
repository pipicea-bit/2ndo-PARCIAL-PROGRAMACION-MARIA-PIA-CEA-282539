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
        self.personajes = {
            nombre: pygame.Rect(x - 69, 157, 138, 98)
            for x, nombre in zip((126, 278, 430, 582, 734), ANIMALES)
        }
        self.niveles = {
            nivel: pygame.Rect(x - 76, 313, 152, 77)
            for x, nivel in zip((108, 269, 430, 591, 752), a.DIFICULTADES)
        }
        self.boton = pygame.Rect(310, 430, 240, 44)
        self.personaje = "Mono"
        self.nivel = "Normal"
        self.fila_activa = "personajes"

    def pulsar(self, posicion):
        """Aplica la opción pulsada y devuelve si se pidió jugar."""
        for nombre, tarjeta in self.personajes.items():
            if tarjeta.collidepoint(posicion):
                self.personaje = nombre
                self.fila_activa = "personajes"
        for nivel, tarjeta in self.niveles.items():
            if tarjeta.collidepoint(posicion):
                self.nivel = nivel
                self.fila_activa = "niveles"
        return self.boton.collidepoint(posicion)

    def tecla(self, tecla):
        """Cambia de fila con arriba y abajo, y de opción con izquierda y derecha."""
        if tecla == pygame.K_UP:
            self.fila_activa = "personajes"
        elif tecla == pygame.K_DOWN:
            self.fila_activa = "niveles"
        elif tecla in (pygame.K_LEFT, pygame.K_RIGHT):
            paso = -1 if tecla == pygame.K_LEFT else 1
            if self.fila_activa == "personajes":
                opciones = tuple(self.personajes)
                self.personaje = opciones[(opciones.index(self.personaje) + paso) % len(opciones)]
            else:
                opciones = tuple(self.niveles)
                self.nivel = opciones[(opciones.index(self.nivel) + paso) % len(opciones)]


    def dibujar(self, pantalla, titulo, normal, chico, records):
        """Muestra opciones, récords y el objetivo del nivel elegido."""
        escribir(pantalla, titulo, "Macaquito", 63, a.BOLSO)
        escribir(pantalla, normal, "Vuelo nocturno", 106)
        escribir(pantalla, normal, "Elegí tu animal", 137, a.BOLSO if self.fila_activa == "personajes" else a.TEXTO)
        for nombre, tarjeta in self.personajes.items():
            dibujar_tarjeta(pantalla, tarjeta, nombre == self.personaje)
            dibujar_macaquito(pantalla, tarjeta.centerx, 190, nombre)
            escribir(pantalla, normal, nombre, 232, x=tarjeta.centerx)

        escribir(pantalla, normal, "Dificultad y modo", 277, a.BOLSO if self.fila_activa == "niveles" else a.TEXTO)
        meta = a.METAS[self.nivel]
        objetivo = "Jugá hasta chocar" if meta is None else f"Cruzá {meta} desfiladeros"
        escribir(pantalla, chico, f"{self.nivel} · {objetivo}", 300)
        for nivel, tarjeta in self.niveles.items():
            dibujar_tarjeta(pantalla, tarjeta, nivel == self.nivel)
            escribir(pantalla, normal, nivel, 334, x=tarjeta.centerx)
            escribir(pantalla, normal, f"Récord {records[nivel]} pts", 365, x=tarjeta.centerx)

        pygame.draw.rect(pantalla, a.BOLSO, self.boton, border_radius=9)
        escribir(pantalla, normal, "Jugar", self.boton.centery, a.FONDO)
        escribir(pantalla, chico, "Flechas para elegir · Enter o Espacio para continuar", 505)


def dibujar_tarjeta(pantalla, tarjeta, elegida):
    """Resalta la opción actual con un borde amarillo."""
    pygame.draw.rect(pantalla, a.ROCA, tarjeta, border_radius=12)
    pygame.draw.rect(
        pantalla, a.BOLSO if elegida else a.BORDE, tarjeta, 2, border_radius=12
    )
