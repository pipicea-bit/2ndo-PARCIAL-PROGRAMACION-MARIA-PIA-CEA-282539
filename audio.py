"""Carga y controla la música y los efectos de HIGHLIGHT."""

from pathlib import Path

import pygame

PISTAS = {
    "menú": "menu.wav",
    "Fácil": "facil.wav",
    "Normal": "normal.wav",
    "Difícil": "dificil.wav",
    "Extremo": "extremo.wav",
    "Survival": "survival.wav",
}


class Audio:
    """Cambia el audio al entrar a una pantalla o empezar una partida."""

    def __init__(self):
        """Carga los archivos una vez y reserva canales para música y finales."""
        carpeta = Path(__file__).resolve().parent / "sonidos"
        self.pistas = {
            modo: pygame.mixer.Sound(str(carpeta / archivo))
            for modo, archivo in PISTAS.items()
        }
        self.efectos = {
            "paso": pygame.mixer.Sound(str(carpeta / "paso.wav")),
            "derrota": pygame.mixer.Sound(str(carpeta / "fin.wav")),
            "victoria": pygame.mixer.Sound(str(carpeta / "victoria.wav")),
        }
        pygame.mixer.set_reserved(2)
        self.musica = pygame.mixer.Channel(0)
        self.musica.set_volume(0.32)
        self.resultado = pygame.mixer.Channel(1)
        self.resultado.set_volume(0.68)
        self.actual = None

    def actualizar(self, estado, nivel):
        """Mantiene la música en bucle o reproduce una sola vez el final."""
        if estado == "jugando":
            pista = nivel
        elif estado in ("victoria", "derrota"):
            pista = estado
        else:
            pista = "menú"
        if pista == self.actual:
            return

        self.actual = pista
        self.musica.stop()
        self.resultado.stop()
        if pista in self.pistas:
            self.musica.play(self.pistas[pista], loops=-1)
        else:
            self.resultado.play(self.efectos[pista])

    def paso(self):
        """Reproduce el efecto breve de cruzar o juntar una fruta."""
        self.efectos["paso"].play()
