# HIGHLIGHT

Guiá a tu piloto con la linterna del celular. Cruzá 12 desfiladeros en Fácil, 15 en Normal, 20 en Difícil o 25 en Extremo. En Survival, sumá todos los puntos que puedas hasta chocar con una pared o un murciélago. Cada barrera tiene un hueco más angosto que la anterior. En Survival los huecos se achican hasta un mínimo, y la altura del próximo hueco siempre queda al alcance desde el anterior.

## Instalación

Desde esta carpeta, con Python 3.10, 3.11 o 3.12:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows, activá el entorno con `.venv\Scripts\activate` en CMD. El programa usa Pygame, OpenCV y NumPy. Si macOS pide acceso a la cámara, concedéselo a la app desde la que ejecutás Python.

## Cómo jugar

- En el menú, elegí un mono, un zorro, un conejo, un panda o una rana y seleccioná la dificultad. Cada modo muestra su mejor puntaje guardado. Podés usar el mouse o las flechas (arriba/abajo para cambiar de fila, izquierda/derecha para cambiar la opción).
- Elegí Jugar. Con la linterna apagada, registrá la luz ambiente. Luego encendé la linterna del celular y apuntala al centro de la webcam y elegí Linterna encendida. Cuando te lo pida el juego, tapá la luz con la mano y destapala sin mover el celular para que la cámara verifique que ese foco desaparece y vuelve. Cuando aparezca «Linterna detectada correctamente», elegí Empezar a volar o presioná Enter.
- Subí la linterna para ascender y bajala para descender. La posición horizontal del piloto es fija. Los murciélagos suben y bajan entre las paredes y aparecen más seguido en las dificultades altas.
- Agarrá las frutas rojas para activar cinco segundos de turbo. Durante ese tiempo volás más rápido y cada desfiladero cruzado vale dos puntos. La barra inferior muestra cuánto turbo queda. Otra fruta recarga la barra.
- Si se pierde el foco, el juego se pausa. Volvé a mostrar la linterna para seguir.
- Tras una victoria o un choque, elegí Volver a jugar o Volver al menú principal con el mouse. También podés pulsar Enter, Espacio o R para repetir la ronda tras volver a calibrar, y Esc o M para volver al menú. La X cierra el juego.

La calibración toma de referencia la luz que ya está en el cuadro. Mantené la webcam fija durante la partida. Si una ventana muy clara tapa el recorrido del foco, corré la cámara para que la linterna tenga un fondo visible. Empezá a unos 60 cm y alejá el teléfono si su luz satura gran parte de la imagen.

## Archivos

| Archivo | Contenido |
| --- | --- |
| `main.py` | Pantallas, bucle, vuelo, choques y puntaje. Incluye la clase `Obstaculo`. |
| `vision.py` | Abre la webcam, registra la luz ambiente y devuelve el centro normalizado del foco como `(x, y)` o `None`. |
| `menu.py` | Selección de personaje, dificultad y vista de récords. |
| `audio.py` | Música del menú y de cada modo, efectos de cruce y sonidos de resultado. |
| `animales.py` | Dibujos de los cinco pilotos. |
| `puntajes.py` | Lectura y escritura de los récords locales. |
| `ajustes.py` | Colores, dimensiones, velocidades, dificultad y umbrales de detección. |

La música original del menú y de los cinco modos, y los efectos de paso, victoria y derrota, se sintetizaron para el proyecto y están en `sonidos/`. Las figuras del juego se dibujan con Pygame. El póster final es el flyer de HIGHLIGHT aportado por María Pía Cea.

## Uso de IA

Se usó OpenAI Codex para interpretar la consigna, implementar y verificar el código, sintetizar sonidos y preparar el README 


Prompts relevantes:

- «yo quiero hacer algo asi, pero mas dificil. quiero hacer un juego inspirado en flappy bird. 

OpenAI Codex. (2026). *Prompts utilizados para desarrollar HIGHLIGHT y sus materiales de entrega* [Generación de código y texto]. Recuperado de https://openai.com/codex/

## Repositorio

Enlace de GitHub pendiente de agregar cuando se publique el repositorio local.
