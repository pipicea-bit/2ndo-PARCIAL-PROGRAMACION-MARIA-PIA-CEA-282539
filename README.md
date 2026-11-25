# Macaquito · Vuelo nocturno

Guiá a tu piloto con la linterna del celular. Cruzá 12 desfiladeros en Fácil, 15 en Normal, 20 en Difícil o 25 en Extremo. En Survival, sumá todos los puntos que puedas hasta chocar con una pared o un murciélago. A medida que sumás puntos, las paredes avanzan más rápido y los próximos huecos se achican.

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
- Encendé la linterna del celular y mostrá el foco a la webcam. Cuando aparezca el macaquito a la izquierda, presioná Enter o Espacio.
- Subí la linterna para ascender y bajala para descender. La posición horizontal del piloto es fija. Los murciélagos suben y bajan entre las paredes y aparecen más seguido en las dificultades altas.
- Agarrá las frutas rojas para activar cinco segundos de turbo. Durante ese tiempo volás más rápido y cada desfiladero cruzado vale dos puntos. La barra inferior muestra cuánto turbo queda. Otra fruta recarga la barra.
- Si se pierde el foco, el juego se pausa. Volvé a mostrar la linterna para seguir.
- Tras una victoria o un choque, elegí Volver a jugar o Volver al menú principal con el mouse. También podés pulsar Enter, Espacio o R para repetir la ronda si la linterna está visible, y Esc o M para volver al menú. La X cierra el juego.

Usá un entorno con luz tenue y un fondo sin ventanas, lámparas ni reflejos dentro del cuadro. Empezá a unos 60 cm de la webcam y probá el recorrido vertical en la pantalla inicial. Si el foco llena una parte grande de la imagen, alejá el teléfono. Si tu cámara no detecta el foco, revisá el permiso y ajustá los umbrales en `ajustes.py`.

## Archivos

| Archivo | Contenido |
| --- | --- |
| `main.py` | Pantallas, bucle, vuelo, choques y puntaje. Incluye la clase `Obstaculo`. |
| `vision.py` | Abre la webcam, espeja el cuadro y devuelve el centro normalizado del foco como `(x, y)` o `None`. |
| `menu.py` | Selección de personaje, dificultad y vista de récords. |
| `animales.py` | Dibujos de los cinco pilotos. |
| `puntajes.py` | Lectura y escritura de los récords locales. |
| `ajustes.py` | Colores, dimensiones, velocidades, dificultad y umbrales de detección. |

Los WAV de `sonidos/` se sintetizaron para el proyecto a partir de ondas senoidales. Las figuras del juego se dibujan con Pygame y el póster se dibujó con Pillow. Los recursos visuales y sonoros son originales del proyecto.

## Uso de IA

Se usó OpenAI Codex para interpretar la consigna, implementar y verificar el código, sintetizar sonidos y preparar el README, el informe y el póster.

Prompts relevantes:

- «necesito hacer este parcial» (con la consigna en PDF adjunta).
- «yo quiero hacer algo asi, pero mas dificil. quiero hacer un flappy bird. con la linterna del celu se ,maneja el macaquito y va volando pasando obstaculos. se entiende ?»

OpenAI Codex. (2026). *Prompts utilizados para desarrollar Macaquito y sus materiales de entrega* [Generación de código y texto]. Recuperado de https://openai.com/codex/

## Repositorio

Enlace de GitHub pendiente de agregar cuando se publique el repositorio local.
