# DOOM PDI: Doom controlado con la cámara

Proyecto del curso de **Procesamiento Digital de Imágenes (PDI)**. Se toma un clon de Doom hecho
en Python y se reemplazan el teclado y el mouse por **gestos captados con la webcam**, usando solo
técnicas clásicas de procesamiento de imágenes: umbralización, morfología, contornos y momentos.
**No se usa inteligencia artificial.**

## Juego original

El juego base es **[Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame/)** de
[Umang Lodaya](https://github.com/Umang-Lodaya). Es un motor de *raycasting* al estilo de
Wolfenstein 3D / Doom escrito con Pygame: tiene mapa, enemigos con búsqueda de caminos, escopeta,
sonidos y pantallas de victoria y derrota. Todo el crédito del juego es de su autor. Este
repositorio solo agrega la capa de control por visión.

## Qué hace este proyecto

La imagen de la cámara se divide en dos zonas, y cada una controla una parte del juego:

```
+----------------+---------------------------------+
|                |                                 |
|    CABEZA      +---------------------------------+
|    (1.5/4)     |      MANO (2.5/4, pecho)        |
+----------------+---------------------------------+
```

| Parte del cuerpo | Gesto | Acción en el juego |
|---|---|---|
| Mano | Moverla a la izquierda o a la derecha | Mover la mira (reemplaza el mouse) |
| Mano | Cerrarla (puño) | Disparar (reemplaza el clic) |
| Cabeza | Inclinarla hacia adelante o atrás (pitch) | Por definir |
| Cabeza | Inclinarla hacia un hombro (roll) | Por definir |

A grandes rasgos, el pipeline de cada frame es:

1. **Preprocesamiento:** redimensionar, espejar y aplicar un filtro Gaussiano.
2. **Segmentación de piel:** conversión a YCrCb y umbralización en los canales Cr y Cb.
3. **Morfología:** apertura para quitar ruido y cierre para rellenar huecos.
4. **Contornos:** se busca la mano y la cara, cada una dentro de su zona.
5. **Descriptores:**
   - Mano: centroide para la mira y solidez para distinguir la mano abierta del puño.
   - Cara: orientación por momentos centrales para el roll y desplazamiento vertical para el pitch.
6. **Comandos:** zona muerta y suavizado, para obtener valores en [−1, 1] que el juego usa en
   lugar del teclado y el mouse.

La explicación detallada de cada etapa está en **[vision/PIPELINE.md](vision/PIPELINE.md)**.

## Estado

- [x] Pipeline de visión: mira, disparo, roll y pitch, con pruebas automáticas
- [ ] Conectar el pipeline al juego
- [ ] Asignar acciones a los gestos de la cabeza

## Instalación

Requiere Python 3. Se probó con Python 3.14 y se usa `pygame-ce` porque `pygame` no tiene versión
para Python 3.14.

```bash
git clone https://github.com/LuisC645/DOOM_PDI.git
cd DOOM_PDI
python -m venv venv
source venv/Scripts/activate        # Windows (Git Bash). En PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso

```bash
python main.py                          # juego original (teclado y mouse)
python -m vision.main                   # prueba del control por cámara
python -m vision.tests.test_pipeline    # pruebas automáticas del pipeline (no necesitan cámara)
```

En la prueba por cámara, pon la cara en el recuadro morado y la mano en el verde, y pulsa `c`
para calibrar la posición neutra de la cabeza. `q` o `Esc` cierran la ventana.

### Controles originales del juego

- **W A S D:** moverse
- **Mouse:** mirar
- **Clic izquierdo:** disparar
- **Esc:** salir

## Estructura

```
├── main.py, player.py, ...   ← juego original (Doom-PyGame)
├── resources/                ← texturas, sprites y sonidos del juego original
└── vision/                   ← control por cámara (este proyecto)
    ├── config.py             ← parámetros
    ├── pipeline.py           ← une las etapas
    ├── main.py               ← prueba con cámara
    ├── processing/           ← segmentación, descriptores y comandos
    ├── utils/                ← dibujo y barras de ajuste
    └── tests/                ← pruebas con imágenes sintéticas
```
