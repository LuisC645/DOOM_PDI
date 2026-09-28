# DOOM PDI: Doom controlado con la cámara

Proyecto personal de **procesamiento digital de imágenes**. Toma un clon de Doom hecho en Python
y reemplaza el mouse por un **guante azul captado con la webcam**: con el guante se apunta y
se dispara, y con el teclado se camina. Solo usa técnicas clásicas de procesamiento de imágenes:
espacio de color HSV, umbralización, morfología, contornos y momentos.
**No usa inteligencia artificial.**

## Juego original

El juego base es **[Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame/)** de
[Umang Lodaya](https://github.com/Umang-Lodaya). Es un motor de *raycasting* al estilo de
Wolfenstein 3D / Doom escrito con Pygame: tiene mapa, enemigos con búsqueda de caminos, escopeta,
sonidos y pantallas de victoria y derrota. Todo el crédito del juego es de su autor. Este
repositorio agrega la capa de control por visión.

## Controles

Una línea vertical divide la imagen de la cámara. El guante se detecta en los 3/4 derechos:

```
+-----------+------------------------------------+
|           |                                    |
|   (1/4)   |          GUANTE (3/4)              |
|           |                                    |
+-----------+------------------------------------+
```

| Control | Acción |
|---|---|
| Guante a la izquierda o a la derecha | Girar la vista |
| Cerrar la mano (puño) | Disparar |
| **W A S D** | Moverse |
| **Esc** | Salir |

La vista **sigue la posición de la mano**, como un mouse: al mover la mano, la vista gira en ese
momento lo que corresponde y se detiene cuando la mano se detiene. Cruzar la zona completa equivale
a 120°. Para dar la vuelta completa, lleva la mano al borde: en el margen, la vista sigue girando
hacia ese lado.

## Cómo funciona

En cada frame de la cámara se hace lo siguiente:

1. **Preprocesamiento:** redimensionar, espejar y aplicar un filtro Gaussiano.
2. **Segmentación del guante:** conversión a HSV y umbralización con `cv2.inRange` en el rango
   de tono, saturación y brillo del azul.
3. **Morfología:** apertura para quitar ruido y cierre para rellenar huecos.
4. **Contorno:** se toma el contorno más grande dentro de la zona del guante.
5. **Descriptores:** el centroide da la posición de la mira, y la solidez (área del contorno /
   área del casco convexo) distingue la mano abierta del puño.
6. **Comandos:** margen y suavizado, para obtener la mira en [−1, 1] y el disparo, que el
   juego usa en lugar del mouse.

La visión corre en un hilo aparte para no frenar el juego, y el archivo
[vision/bridge.py](vision/bridge.py) comunica ambas partes. La explicación detallada de cada
etapa está en **[vision/PIPELINE.md](vision/PIPELINE.md)**.

## Instalación

Requiere Python 3 y una webcam. Se probó con Python 3.14 y se usa `pygame-ce` porque `pygame` no
tiene versión para Python 3.14.

```bash
git clone https://github.com/LuisC645/DOOM_PDI.git
cd DOOM_PDI
python -m venv venv
source venv/Scripts/activate        # Windows (Git Bash). En PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso

```bash
python main.py                          # jugar
python -m vision.main                   # ver la cámara y la máscara, y calibrar el color del guante
python -m vision.tests.test_pipeline    # pruebas automáticas del pipeline (no necesitan cámara)
```

Para jugar:
1. **Calibra el color una vez:** en `python -m vision.main`, pon la palma del guante sobre el
   recuadro amarillo, pulsa `c` y copia los valores `HSV_LOWER` y `HSV_UPPER` que se imprimen en
   [vision/config.py](vision/config.py).
2. Usa el guante a la derecha de la línea verde, con los dedos separados.
3. La vista de la cámara aparece en la esquina superior derecha del juego, con la línea y el estado
   de la mano (ABIERTA / CERRADA).

## Estructura

```
├── main.py, player.py, ...   ← juego (Doom-PyGame), con el mouse reemplazado por la cámara
├── resources/                ← texturas, sprites y sonidos del juego original
└── vision/                   ← control por cámara
    ├── bridge.py             ← puente entre la cámara y el juego
    ├── config.py             ← parámetros
    ├── pipeline.py           ← une las etapas
    ├── main.py               ← vista de la cámara para ajustar
    ├── processing/           ← segmentación, descriptores y comandos
    ├── utils/                ← dibujo de la vista previa
    └── tests/                ← pruebas con imágenes sintéticas
```
