"""Juego de vuelo controlado con la linterna del celular."""

from math import sin
from pathlib import Path
from random import randint

import pygame

import ajustes as a
from animales import dibujar_macaquito
from menu import Menu, dibujar_tarjeta, escribir
from puntajes import cargar, guardar
from vision import LectorLinterna, abrir_camara


class Obstaculo:
    """Dos paredes con un hueco que el macaquito debe atravesar."""

    def __init__(self, x, nivel, numero, anterior=None):
        """Reduce el hueco y lo mantiene al alcance desde el anterior."""
        self.x = x
        velocidad, aumento, inicial, minimo = a.DIFICULTADES[nivel]
        meta = a.METAS[nivel]
        minimo = max(minimo, 2 * a.RADIO + a.HOLGURA_HUECO)
        if meta is None:
            hueco = max(minimo, inicial - (numero - 1) * a.REDUCCION_SURVIVAL)
            velocidad_maxima = a.VELOCIDAD_MAXIMA_SURVIVAL
        else:
            hueco = round(inicial - (inicial - minimo) * (numero - 1) / (meta - 1))
            hueco = max(minimo, hueco)
            velocidad_maxima = velocidad + (meta - 1) * aumento

        mitad = hueco // 2
        desde = a.HUD + a.MARGEN_HUECO + mitad
        hasta = a.ALTO - a.MARGEN_HUECO - (hueco - mitad)
        if anterior is not None:
            # Usamos el tramo entre paredes y reservamos parte del tiempo para reaccionar.
            tramo = a.ESPACIO_ENTRE_OBSTACULOS - a.ANCHO_OBSTACULO - 2 * a.RADIO
            alcance = int(
                tramo * a.VELOCIDAD_VERTICAL * a.FRACCION_TRASLADO
                / (velocidad_maxima * a.FACTOR_TURBO)
            )
            desde = max(desde, anterior.centro - alcance)
            hasta = min(hasta, anterior.centro + alcance)

        self.centro = randint(desde, hasta)
        self.paso = self.centro - mitad
        self.fin_paso = self.paso + hueco
        self.contado = False
        primero = a.PRIMER_MURCIELAGO[nivel]
        intervalo = a.INTERVALO_MURCIELAGO[nivel]
        self.con_murcielago = numero >= primero and (numero - primero) % intervalo == 0
        self.con_fruta = numero % a.INTERVALO_FRUTA == 1 and not self.con_murcielago
        self.fase = 0.0

    def fruta(self):
        """Devuelve el centro de la fruta flotante detrás de la pared."""
        return (
            round(self.x + a.DISTANCIA_FRUTA),
            round((self.paso + self.fin_paso) / 2 + sin(self.fase) * a.AMPLITUD_FRUTA),
        )

    def actualizar(self, velocidad, dt):
        """Desplaza la pared y anima el vuelo del murciélago."""
        self.x -= velocidad * dt
        self.fase += a.FRECUENCIA_MURCIELAGO * dt

    def murcielago(self):
        """Devuelve el centro del murciélago asociado al desfiladero."""
        return (
            round(self.x + a.DISTANCIA_MURCIELAGO),
            round((self.paso + self.fin_paso) / 2 + sin(self.fase) * a.AMPLITUD_MURCIELAGO),
        )

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


def mover(y, objetivo, dt, turbo):
    """Acerca el personaje al objetivo con una velocidad máxima."""
    limite = a.VELOCIDAD_VERTICAL * dt * turbo
    return y + max(-limite, min(limite, objetivo - y))


def choca(y, pared):
    """Comprueba la distancia del macaquito al punto más cercano de la pared."""
    x = max(pared.left, min(a.X_MACAQUITO, pared.right))
    punto_y = max(pared.top, min(y, pared.bottom))
    return (a.X_MACAQUITO - x) ** 2 + (y - punto_y) ** 2 <= a.RADIO ** 2


def dibujar_murcielago(pantalla, x, y):
    """Dibuja alas angulares y ojos brillantes para distinguir el peligro."""
    pygame.draw.polygon(
        pantalla, a.COLOR_MURCIELAGO,
        [(x - 15, y - 7), (x - 7, y - 2), (x, y - 10),
         (x + 7, y - 2), (x + 15, y - 7), (x + 12, y + 5),
         (x + 5, y + 3), (x, y + 10), (x - 5, y + 3), (x - 12, y + 5)],
    )
    for ojo in (x - 3, x + 3):
        pygame.draw.circle(pantalla, a.OJOS_MURCIELAGO, (ojo, y - 1), 2)


def cerca(y, centro, radio):
    """Indica si el piloto toca un objeto de centro y radio conocidos."""
    x_objeto, y_objeto = centro
    return (a.X_MACAQUITO - x_objeto) ** 2 + (y - y_objeto) ** 2 <= (a.RADIO + radio) ** 2


def dibujar_fruta(pantalla, x, y):
    """Dibuja una fruta roja con una hoja verde."""
    pygame.draw.circle(pantalla, a.COLOR_FRUTA, (x, y), a.RADIO_FRUTA)
    pygame.draw.circle(pantalla, a.TEXTO, (x - 4, y - 3), 2)
    pygame.draw.ellipse(pantalla, a.COLOR_HOJA, (x, y - 18, 12, 8))


def dibujar_turbo(pantalla, fuente, restante):
    """Muestra la duración del poder en una barra que se vacía."""
    barra = pygame.Rect(a.ANCHO // 2 - 135, a.ALTO - 20, 270, 9)
    pygame.draw.rect(pantalla, a.FONDO, barra.inflate(12, 30), border_radius=6)
    pygame.draw.rect(pantalla, a.ROCA, barra, border_radius=4)
    ancho = round(barra.width * restante / a.DURACION_TURBO)
    if ancho:
        lleno = pygame.Rect(barra.x, barra.y, ancho, barra.height)
        pygame.draw.rect(pantalla, a.COLOR_HOJA, lleno, border_radius=4)
    escribir(pantalla, fuente, "Turbo · Puntos x2", a.ALTO - 29, a.COLOR_HOJA)


def cargar_sonidos():
    """Carga los dos efectos antes de iniciar el bucle."""
    carpeta = Path(__file__).resolve().parent / "sonidos"
    return tuple(
        pygame.mixer.Sound(str(carpeta / nombre))
        for nombre in ("paso.wav", "fin.wav")
    )


def dibujar_calibracion(pantalla, titulo, normal, estado, boton, error):
    """Guía la toma de luz ambiente, la detección y el inicio del vuelo."""
    if estado == "ambiente":
        escribir(pantalla, titulo, "Apagá la linterna", 128, a.BOLSO)
        escribir(pantalla, normal, "Dejá la cámara apuntando al lugar de juego y registrá la luz ambiente.", 226)
        etiqueta = "Registrar luz ambiente"
    elif estado in ("encender", "buscar", "tapar", "destapar"):
        instrucciones = {
            "encender": ("Encendé la linterna", "Apuntala al centro de la webcam y mantené el celular quieto."),
            "buscar": ("Buscando la linterna", "Mantené el celular quieto un momento."),
            "tapar": ("Tapá la linterna", "Tapá la luz con la mano sin mover el celular."),
            "destapar": ("Destapá la linterna", "Dejá que la luz vuelva a verse en el mismo lugar."),
        }
        encabezado, indicacion = instrucciones[estado]
        escribir(pantalla, normal, "Luz ambiente registrada", 110, a.COLOR_HOJA)
        escribir(pantalla, titulo, encabezado, 190, a.BOLSO)
        escribir(pantalla, normal, indicacion, 263)
        etiqueta = "Linterna encendida" if estado == "encender" else None
    else:
        escribir(pantalla, titulo, "Prepará tu linterna", 128, a.BOLSO)
        x, y = a.ANCHO // 2, 184
        pygame.draw.circle(pantalla, a.COLOR_HOJA, (x, y), 22, 3)
        pygame.draw.lines(
            pantalla, a.COLOR_HOJA, False,
            [(x - 9, y), (x - 2, y + 7), (x + 11, y - 7)], 4,
        )
        escribir(pantalla, normal, "Linterna detectada correctamente", 226, a.COLOR_HOJA)
        escribir(pantalla, normal, "Mové el celular hacia arriba y abajo para controlar a tu animal.", 263)
        etiqueta = "Empezar a volar"

    if etiqueta is not None:
        dibujar_tarjeta(pantalla, boton, True)
        escribir(pantalla, normal, etiqueta, boton.centery)
    if error:
        escribir(pantalla, normal, "No se pudo leer la cámara. Revisá los permisos y volvé a intentar.", 415, a.BOLSO)
    ayuda = "R para recalibrar · Esc para volver" if etiqueta is None else "Enter o clic para confirmar · Esc para volver"
    escribir(pantalla, normal, ayuda, 481)


def jugar(pantalla, reloj, cap, sonido_paso, sonido_fin):
    """Ejecuta la partida y permite reiniciar desde la pantalla final."""
    familias = ("trebuchetms", "verdana", "arial", "dejavusans")
    titulo = pygame.font.SysFont(familias, 56, bold=True)
    normal = pygame.font.SysFont(familias, 20)
    chico = pygame.font.SysFont(familias, 16)
    estrellas = [(randint(0, a.ANCHO), randint(a.HUD, a.ALTO)) for _ in range(85)]
    estado = "menu"
    menu = Menu()
    lector = LectorLinterna(cap)
    pantallas_calibracion = ("ambiente", "encender", "buscar", "tapar", "destapar", "listo")
    cuadros_verificacion = 0
    confirmar = pygame.Rect(285, 321, 290, 48)
    error_camara = False
    records = cargar()
    guardado = True
    repetir = pygame.Rect(164, 294, 250, 52)
    principal = pygame.Rect(446, 294, 250, 52)
    y = (a.HUD + a.ALTO) / 2

    while True:
        dt = min(reloj.tick(a.FPS) / 1000, 0.05)
        empezar = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    estado = "menu"
                    empezar = False
                elif evento.key == pygame.K_r and estado in pantallas_calibracion:
                    estado = "ambiente"
                    error_camara = False
                    empezar = False
                elif estado == "menu":
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                        empezar = True
                    else:
                        menu.tecla(evento.key)
                elif estado in ("ambiente", "encender", "listo"):
                    empezar = evento.key in (pygame.K_SPACE, pygame.K_RETURN) or empezar
                elif estado in ("victoria", "derrota"):
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                        empezar = True
                    elif evento.key == pygame.K_m:
                        estado = "menu"
                        empezar = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if estado == "menu":
                    empezar = menu.pulsar(evento.pos) or empezar
                elif estado in ("ambiente", "encender", "listo"):
                    empezar = confirmar.collidepoint(evento.pos) or empezar
                elif estado in ("victoria", "derrota"):
                    if repetir.collidepoint(evento.pos):
                        empezar = True
                    elif principal.collidepoint(evento.pos):
                        estado = "menu"
                        empezar = False

        posicion = None
        if estado in ("buscar", "tapar", "destapar", "listo", "jugando"):
            posicion = lector.detectar(en_misma_zona=estado in ("tapar", "destapar"))
        if empezar and estado in ("menu", "victoria", "derrota"):
            estado = "ambiente"
            error_camara = False
        elif empezar and estado == "ambiente":
            error_camara = not lector.registrar_ambiente()
            if not error_camara:
                estado = "encender"
        elif empezar and estado == "encender":
            estado = "buscar"
        elif estado == "buscar" and lector.confirmar(posicion):
            estado = "tapar"
            cuadros_verificacion = 0
        elif estado in ("tapar", "destapar"):
            # Una lámpara fija no supera la prueba de desaparecer y volver.
            cumple_paso = posicion is None if estado == "tapar" else posicion is not None
            if lector.cuadro_valido and cumple_paso:
                cuadros_verificacion += 1
            else:
                cuadros_verificacion = 0
            if cuadros_verificacion >= a.CUADROS_CONFIRMACION:
                estado = "destapar" if estado == "tapar" else "listo"
                cuadros_verificacion = 0
        elif estado == "listo":
            lector.seguir(posicion)

        # Una vez confirmada, la calibración se conserva hasta empezar o salir.
        if empezar and estado == "listo":
            posicion_inicial = posicion if posicion is not None else lector.anterior
            puntos = 0
            cruces = 0
            restante_turbo = 0.0
            y = altura_objetivo(posicion_inicial)
            meta = a.METAS[menu.nivel]
            inicial, aumento, *_ = a.DIFICULTADES[menu.nivel]
            numero = 1
            obstaculos = [Obstaculo(a.ANCHO, menu.nivel, numero)]
            estado = "jugando"

        # Al perder el foco se congela el vuelo y el avance de las paredes.
        if estado == "jugando" and posicion is not None:
            lector.seguir(posicion)
            restante_turbo = max(0, restante_turbo - dt)
            turbo = a.FACTOR_TURBO if restante_turbo > 0 else 1
            y = mover(y, altura_objetivo(posicion), dt, turbo)
            velocidad = inicial + cruces * aumento
            if meta is None:
                # Survival sigue generando obstáculos a una velocidad que permite esquivarlos.
                velocidad = min(velocidad, a.VELOCIDAD_MAXIMA_SURVIVAL)
            velocidad *= turbo
            for obstaculo in obstaculos:
                obstaculo.actualizar(velocidad, dt)
                choque_murcielago = obstaculo.con_murcielago and cerca(
                    y, obstaculo.murcielago(), a.RADIO_MURCIELAGO
                )
                if choque_murcielago or any(choca(y, pared) for pared in obstaculo.paredes()):
                    estado = "derrota"
                    break
                if obstaculo.con_fruta and cerca(y, obstaculo.fruta(), a.RADIO_FRUTA):
                    obstaculo.con_fruta = False
                    restante_turbo = a.DURACION_TURBO
                    sonido_paso.play()
                # El poder duplica el puntaje de cada cruce, sin duplicar los desfiladeros cruzados.
                if not obstaculo.contado and obstaculo.x + a.ANCHO_OBSTACULO < a.X_MACAQUITO - a.RADIO:
                    obstaculo.contado = True
                    cruces += 1
                    puntos += a.PUNTOS_TURBO if restante_turbo > 0 else 1
                    if puntos > records[menu.nivel]:
                        records[menu.nivel] = puntos
                        guardado = guardar(records)
                    sonido_paso.play()
                    if cruces == meta:
                        estado = "victoria"
                        break

            if obstaculos[-1].x <= a.ANCHO - a.ESPACIO_ENTRE_OBSTACULOS:
                numero += 1
                anterior = obstaculos[-1]
                x_nuevo = anterior.x + a.ESPACIO_ENTRE_OBSTACULOS
                obstaculos.append(Obstaculo(x_nuevo, menu.nivel, numero, anterior))
            # Los objetos flotantes siguen activos después de que sale la pared.
            obstaculos = [
                o for o in obstaculos
                if o.x + a.ANCHO_OBSTACULO > 0
                or (o.con_murcielago and o.murcielago()[0] + a.RADIO_MURCIELAGO > 0)
                or (o.con_fruta and o.fruta()[0] + a.RADIO_FRUTA > 0)
            ]
            if estado != "jugando":
                sonido_fin.play()

        pantalla.fill(a.FONDO)
        for estrella in estrellas:
            pygame.draw.circle(pantalla, a.ESTRELLA, estrella, 2)
        if estado == "jugando":
            pygame.draw.line(pantalla, a.BORDE, (0, a.HUD), (a.ANCHO, a.HUD))
            avance = str(cruces) if meta is None else f"{cruces}/{meta}"
            escribir(pantalla, normal, f"{menu.nivel}    ·    Desfiladeros {avance}    ·    Puntos {puntos}", 30)
            for obstaculo in obstaculos:
                for pared in obstaculo.paredes():
                    pygame.draw.rect(pantalla, a.ROCA, pared)
                    pygame.draw.rect(pantalla, a.BORDE, pared, 3)
                if obstaculo.con_murcielago:
                    dibujar_murcielago(pantalla, *obstaculo.murcielago())
                if obstaculo.con_fruta:
                    dibujar_fruta(pantalla, *obstaculo.fruta())
            dibujar_macaquito(pantalla, a.X_MACAQUITO, y, menu.personaje)
            if restante_turbo > 0:
                dibujar_turbo(pantalla, normal, restante_turbo)
            if posicion is None:
                escribir(pantalla, normal, "Pausa · Mostrá la linterna a la cámara", a.ALTO - 57)
        elif estado == "menu":
            menu.dibujar(pantalla, titulo, normal, chico, records)
        elif estado in pantallas_calibracion:
            dibujar_calibracion(pantalla, titulo, normal, estado, confirmar, error_camara)
        else:
            encabezado = "¡Llegaste al otro lado!" if estado == "victoria" else "¡Chocaste!"
            escribir(pantalla, titulo, encabezado, 172, a.BOLSO)
            escribir(pantalla, normal, f"{menu.nivel} · Puntaje {puntos} · Récord {records[menu.nivel]}", 245)
            dibujar_tarjeta(pantalla, repetir, True)
            dibujar_tarjeta(pantalla, principal, False)
            escribir(pantalla, normal, "Volver a jugar", repetir.centery, x=repetir.centerx)
            escribir(pantalla, normal, "Volver al menú principal", principal.centery, x=principal.centerx)
            escribir(pantalla, normal, "Enter o R para repetir · Esc o M para volver al menú", 374)
            if not guardado:
                escribir(pantalla, normal, "El récord quedó guardado solo durante esta sesión", 438)
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
