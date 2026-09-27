# DOOM PDI: Doom controlado con la cámara

Proyecto personal de **procesamiento digital de imágenes**. Toma un clon de Doom hecho en Python
y reemplaza el teclado y el mouse por **gestos captados con la webcam**. Solo usa técnicas
clásicas de procesamiento de imágenes: umbralización, morfología, contornos y momentos.
**No usa inteligencia artificial.**

## Juego original

El juego base es **[Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame/)** de
[Umang Lodaya](https://github.com/Umang-Lodaya). Es un motor de *raycasting* al estilo de
Wolfenstein 3D / Doom escrito con Pygame: tiene mapa, enemigos con búsqueda de caminos, escopeta,
sonidos y pantallas de victoria y derrota. Todo el crédito del juego es de su autor. Este
repositorio agrega la capa de control por visión.

## Controles

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
| Mano | Moverla a la izquierda o a la derecha | Girar la vista |
| Mano | Cerrarla (puño) | Disparar |
| Cabeza | Inclinarla hacia adelante o atrás | Avanzar o retroceder |
| Cabeza | Inclinarla hacia un hombro | Moverse hacia ese lado |

Todos los movimientos son proporcionales: cuanto más se inclina la cabeza o se aleja la mano del
centro, más rápido se mueve o gira el jugador. En el centro hay una zona muerta para que la
postura de reposo no mueva nada.

- **C:** recalibra la posición neutra de la cabeza (hazlo sentado derecho y con la cabeza quieta).
- **Esc:** salir.

## Cómo funciona

En cada frame de la cámara se hace lo siguiente:

1. **Preprocesamiento:** redimensionar, espejar y aplicar un filtro Gaussiano.
2. **Segmentación de piel:** conversión a YCrCb y umbralización en los canales Cr y Cb.
3. **Morfología:** apertura para quitar ruido y cierre para rellenar huecos.
4. **Contornos:** se busca la mano y la cara, cada una dentro de su zona.
5. **Descriptores:**
   - Mano: centroide para la mira y solidez para distinguir la mano abierta del puño.
   - Cara: orientación por momentos centrales para la inclinación lateral y desplazamiento
     vertical para la inclinación adelante/atrás.
6. **Comandos:** zona muerta y suavizado, para obtener valores en [−1, 1] que el juego usa en
   lugar del teclado y el mouse.

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
python -m vision.main                   # ver solo la cámara, con la máscara y barras para ajustar umbrales
python -m vision.tests.test_pipeline    # pruebas automáticas del pipeline (no necesitan cámara)
```

Para jugar:
- Pon la cara en el recuadro morado y la mano derecha en el verde, a la altura del pecho.
- La vista de la cámara aparece en la esquina superior derecha del juego.
- Si la piel no se detecta bien con tu iluminación, usa `python -m vision.main` para encontrar
  los umbrales y cópialos en [vision/config.py](vision/config.py).

## Estructura

```
├── main.py, player.py, ...   ← juego (Doom-PyGame), con los controles reemplazados
├── resources/                ← texturas, sprites y sonidos del juego original
└── vision/                   ← control por cámara
    ├── bridge.py             ← puente entre la cámara y el juego
    ├── config.py             ← parámetros
    ├── pipeline.py           ← une las etapas
    ├── main.py               ← vista de la cámara para ajustar
    ├── processing/           ← segmentación, descriptores y comandos
    ├── utils/                ← dibujo y barras de ajuste
    └── tests/                ← pruebas con imágenes sintéticas
```
