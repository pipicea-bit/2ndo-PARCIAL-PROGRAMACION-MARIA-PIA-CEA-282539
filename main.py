"""Juego de vuelo controlado con la linterna del celular."""

from pathlib import Path
from random import randint

import pygame

import ajustes as a
from vision import abrir_camara, detectar


class Obstaculo:
    """Dos paredes con un hueco que el macaquito debe atravesar."""

    def __init__(self, x, puntos):
        """Elige la posición vertical del hueco y lo ajusta al puntaje."""
        self.x = x
        hueco = max(a.HUECO_MINIMO, a.HUECO_INICIAL - puntos * a.REDUCCION_HUECO)
        self.paso = randint(a.HUD + a.MARGEN_HUECO, a.ALTO - a.MARGEN_HUECO - hueco)
        self.fin_paso = self.paso + hueco
        self.contado = False

    def paredes(self):
        """Devuelve los rectángulos que se dibujan y pueden causar un choque."""
        return (
            pygame.Rect(self.x, a.HUD, a.ANCHO_OBSTACULO, self.paso - a.HUD),
            pygame.Rect(self.x, self.fin_paso, a.ANCHO_OBSTACULO, a.ALTO - self.fin_paso),
        )


def altura_objetivo(posicion):
    """Traduce la altura del foco al área de juego."""
    _, y = posicion
    return a.HUD + a.RADIO + y * (a.ALTO - a.HUD - 2 * a.RADIO)


def mover(y, objetivo, dt):
    """Acerca el personaje al objetivo con una velocidad máxima."""
    limite = a.VELOCIDAD_VERTICAL * dt
    return y + max(-limite, min(limite, objetivo - y))


def choca(y, pared):
    """Comprueba la distancia del macaquito al punto más cercano de la pared."""
    x = max(pared.left, min(a.X_MACAQUITO, pared.right))
    punto_y = max(pared.top, min(y, pared.bottom))
    return (a.X_MACAQUITO - x) ** 2 + (y - punto_y) ** 2 <= a.RADIO ** 2


def cargar_sonidos():
    """Carga los dos efectos antes de iniciar el bucle."""
    carpeta = Path(__file__).resolve().parent / "sonidos"
    return tuple(
        pygame.mixer.Sound(str(carpeta / nombre))
        for nombre in ("paso.wav", "fin.wav")
    )


def escribir(pantalla, fuente, texto, y, color=a.TEXTO):
    """Dibuja una línea de texto centrada."""
    imagen = fuente.render(texto, True, color)
    pantalla.blit(imagen, imagen.get_rect(center=(a.ANCHO // 2, y)))


def dibujar_macaquito(pantalla, y):
    """Dibuja el personaje con su mochila amarilla."""
    x, y = a.X_MACAQUITO, round(y)
    pygame.draw.circle(pantalla, a.BOLSO, (x-18, y+7), 10)
    pygame.draw.circle(pantalla, a.PELAJE, (x, y), a.RADIO)
    pygame.draw.circle(pantalla, a.PELAJE, (x-15, y-17), 8)
    pygame.draw.ellipse(pantalla, a.CARA, (x-12, y-11, 32, 27))
    pygame.draw.circle(pantalla, a.FONDO, (x+9, y-4), 3)
    pygame.draw.circle(pantalla, a.FONDO, (x+17, y+6), 3)


def jugar(pantalla, reloj, cap, sonido_paso, sonido_fin):
    """Ejecuta la partida y permite reiniciar desde la pantalla final."""
    titulo = pygame.font.Font(None, 78)
    normal = pygame.font.Font(None, 29)
    estrellas = [(randint(0, a.ANCHO), randint(a.HUD, a.ALTO)) for _ in range(85)]
    estado = "inicio"
    y = (a.HUD + a.ALTO) / 2

    while True:
        dt = min(reloj.tick(a.FPS) / 1000, 0.05)
        empezar = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                empezar = estado != "jugando"

        posicion = detectar(cap)
        if empezar and posicion is not None:
            puntos = 0
            y = altura_objetivo(posicion)
            obstaculos = [Obstaculo(a.ANCHO, puntos)]
            estado = "jugando"

        # Al perder el foco se congela el vuelo y el avance de las paredes.
        if estado == "jugando" and posicion is not None:
            y = mover(y, altura_objetivo(posicion), dt)
            velocidad = a.VELOCIDAD_INICIAL + puntos * a.AUMENTO_VELOCIDAD
            for obstaculo in obstaculos:
                obstaculo.x -= velocidad * dt
                if any(choca(y, pared) for pared in obstaculo.paredes()):
                    estado = "derrota"
                    break
                # El paso cuenta una vez, cuando el personaje ya salió del hueco.
                if not obstaculo.contado and obstaculo.x + a.ANCHO_OBSTACULO < a.X_MACAQUITO - a.RADIO:
                    obstaculo.contado = True
                    puntos += 1
                    sonido_paso.play()
                    if puntos == a.META:
                        estado = "victoria"
                        break

            if obstaculos[-1].x <= a.ANCHO - a.ESPACIO_ENTRE_OBSTACULOS:
                obstaculos.append(Obstaculo(a.ANCHO, puntos))
            obstaculos = [o for o in obstaculos if o.x + a.ANCHO_OBSTACULO > 0]
            if estado != "jugando":
                sonido_fin.play()

        pantalla.fill(a.FONDO)
        for estrella in estrellas:
            pygame.draw.circle(pantalla, a.ESTRELLA, estrella, 2)
        if estado == "jugando":
            pygame.draw.line(pantalla, a.BORDE, (0, a.HUD), (a.ANCHO, a.HUD))
            escribir(pantalla, normal, f"Desfiladeros cruzados: {puntos}/{a.META}", 30)
            for obstaculo in obstaculos:
                for pared in obstaculo.paredes():
                    pygame.draw.rect(pantalla, a.ROCA, pared)
                    pygame.draw.rect(pantalla, a.BORDE, pared, 3)
            dibujar_macaquito(pantalla, y)
            if posicion is None:
                escribir(pantalla, normal, "Pausa · Mostrá la linterna a la cámara", a.ALTO - 27)
        else:
            encabezado = {"inicio": "Macaquito", "victoria": "¡Llegaste al otro lado!", "derrota": "¡Chocaste!"}[estado]
            escribir(pantalla, titulo, encabezado, 172, a.BOLSO)
            escribir(pantalla, normal, "Subí y bajá la linterna para cruzar 12 desfiladeros.", 245)
            aviso = "Mostrá la linterna a la cámara" if posicion is None else "Presioná Espacio para volar"
            escribir(pantalla, normal, aviso, 285)
            if posicion is not None:
                dibujar_macaquito(pantalla, altura_objetivo(posicion))
        pygame.display.flip()


def main():
    """Inicializa Pygame y libera la cámara al cerrar la ventana."""
    pygame.display.init()
    pygame.font.init()
    cap = None
    try:
        pygame.mixer.init()
        pantalla = pygame.display.set_mode((a.ANCHO, a.ALTO))
        pygame.display.set_caption(a.TITULO)
        sonidos = cargar_sonidos()
        cap = abrir_camara()
        jugar(pantalla, pygame.time.Clock(), cap, *sonidos)
    finally:
        if cap is not None:
            cap.release()
        pygame.quit()


if __name__ == "__main__":
    main()
