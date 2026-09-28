# Control de Doom con un guante azul: pipeline de procesamiento de imágenes

Con un **guante azul** frente a la webcam se apunta y se dispara, y con el teclado (W A S D) se
camina. Solo se usan técnicas básicas de procesamiento digital de imágenes: conversión al espacio
de color HSV, umbralización con `cv2.inRange`, morfología, contornos y momentos de imagen. No se
usa IA.

| Gesto | Valor que se obtiene | Acción en el juego |
|---|---|---|
| Mover el guante a la izquierda o a la derecha | `aim` ∈ [−1, 1] | Girar |
| Cerrar la mano (puño) | `shoot` | Disparar |

## Zona de la mano

```
+-----------+------------------------------------+
|           |            MANO (3/4)              |
|           |                                    |
|   (1/4)   |  |←margen                 margen→| |
+-----------+------------------------------------+
            ↑ línea que separa la pantalla
```

- El guante se busca solo en los **3/4 derechos** de la imagen, con todo el alto.
- **Margen:** la mira llega a ±1 a una distancia del 15 % del ancho antes de cada borde, porque
  el centroide nunca toca el borde de la zona y cerca de los bordes la detección falla más.
  Pasado el margen, la mira se mantiene en ±1.

Las proporciones se cambian en [config.py](config.py) con `HAND_X` y `AIM_MARGIN`.

**Vista previa:** muestra solo la imagen de la cámara, la línea que separa la pantalla y el estado
de la mano: ABIERTA, CERRADA o SIN MANO. En `vision.main` se ve además la máscara del guante.

## Estructura de archivos

```
vision/
├── bridge.py              ← puente con el juego: hilo de la cámara + get_controls()
├── config.py              ← parámetros: zona, rango HSV del guante, puño, margen, suavizado
├── pipeline.py            ← une las etapas: frame → mira, puño, disparo
├── main.py                ← prueba con la cámara: vista previa + máscara + calibración
├── processing/            ← las etapas de procesamiento de imágenes
│   ├── segmentation.py    ← 1-4. redimensionar, espejo, Gaussiano, HSV, umbral, morfología, calibración
│   ├── features.py        ← 5-6. contorno, quitar el brazo, centroide, solidez
│   └── controls.py        ← 7. mira (margen, suavizado)
├── utils/
│   └── drawing.py         ← vista previa: línea divisoria + ABIERTA / CERRADA
└── tests/                 ← pruebas sin cámara
    ├── synthetic.py       ← genera imágenes de prueba (guante, piel, cara, brazo doblado)
    └── test_pipeline.py   ← 13 pruebas de cada etapa
```

## Pipeline

```
Cámara → [1] Preprocesamiento → [2] BGR → HSV → [3] Umbralización (inRange) → [4] Morfología
       → [5] Contorno del guante → [5b] Quitar el brazo → [6] Centroide y solidez → [7] Mira y disparo
```

**1. Preprocesamiento** — [processing/segmentation.py](processing/segmentation.py)
- La imagen se reduce a 320x240 y se voltea horizontalmente para que funcione como un espejo.
- Se suaviza con un **filtro Gaussiano 5x5**, que reduce el ruido del sensor.

**2. Espacio de color HSV**
- En RGB, el brillo y el color están mezclados: un guante con sombra y uno iluminado tienen
  valores RGB muy distintos.
- HSV separa el **tono** (H, qué color es), la **saturación** (S, qué tan puro es) y el **brillo**
  (V). El azul ocupa un rango estrecho de H aunque cambie la luz.

**3. Umbralización**
- `cv2.inRange` deja en blanco los píxeles que cumplen las tres condiciones y en negro el resto:
  - H ∈ [100, 130]: tono azul.
  - S ≥ 80: descarta grises y blancos.
  - V ≥ 40: descarta sombras muy oscuras.
- El resultado es una **imagen binaria** con el guante en blanco. La piel, la cara y el fondo
  quedan fuera porque no son azules.
- **Calibración** (tecla `c` en `vision.main`): se miden los píxeles del guante dentro de un
  recuadro y el rango pasa a ser `[percentil 5 − holgura, percentil 95 + holgura]` en cada canal.
  Los valores se imprimen para copiarlos en [config.py](config.py).

**4. Morfología**
- **Apertura** (erosión y luego dilatación) con un elemento de 3x3: quita puntos blancos sueltos.
- **Cierre** (dilatación y luego erosión) con un elemento de 9x9: rellena huecos dentro del guante,
  como pliegues o reflejos.

**5. Contorno del guante** — [processing/features.py](processing/features.py)
- `cv2.findContours` busca contornos solo dentro de la zona de la mano, que funciona como región
  de interés, y se toma el de mayor área.
- Si el área es menor a 1500 píxeles, se considera que no hay mano.

**5b. Quitar el brazo** (`remove_arm`)
- Si el guante es largo o la manga es del mismo color, el brazo entra en el contorno. Con el
  brazo doblado, eso crea una concavidad que baja la solidez, y un puño parecería una mano abierta.
- **Transformada de distancia** (`cv2.distanceTransform`): a cada píxel le asigna su distancia al
  borde. El máximo es el **centro de la palma** y su valor es el **radio de la palma** *r*. Se busca
  en el 75 % superior del blob, porque el brazo está abajo.
- Se borra todo lo que está más de **1.1·r** por debajo del centro de la palma.

**6. Descriptores**
- **Centroide** a partir de los momentos de imagen: `cx = M10 / M00`.
- **Solidez** = área del contorno / área del casco convexo (`cv2.convexHull`):
  - Con la mano **abierta**, hay espacio vacío entre los dedos y la solidez es baja (≈ 0.72).
  - Con el **puño**, la forma es casi convexa y la solidez es alta (≈ 0.96).
  - Si la solidez es ≥ 0.84 (`FIST_SOLIDITY`), se considera puño.

**7. Mira y disparo** — [processing/controls.py](processing/controls.py)
- **Mira:** `(cx − centro) / alcance`, limitado a [−1, 1], donde el alcance es la distancia del
  centro al margen. Es lineal: 0 en el centro, ±1 en el margen y ±1 más allá.
  - Suavizado exponencial: `0.4·nuevo + 0.6·anterior`. Quita el temblor.
  - Si la mano desaparece y vuelve, el primer valor se toma sin suavizar.
- **Disparo:** solo en el frame en que la mano pasa de abierta a cerrada.

## Cálculos matemáticos

| # | Cálculo | Fórmula | Para qué |
|---|---|---|---|
| 1 | **Filtro Gaussiano** | `G(x,y) = (1 / 2πσ²) · e^(−(x² + y²) / 2σ²)`, convolución con un kernel de 5x5 | Reducir el ruido antes de umbralizar |
| 2 | **BGR → HSV** | `V = max(R,G,B)`<br>`S = (V − min) / V`<br>`H = 60° · (4 + (R − G)/(V − min))` si V = B (el caso del azul)<br>En OpenCV, H se divide entre 2 (0–179) y S, V se escalan a 0–255 | Separar el color del brillo |
| 3 | **Umbralización** | `M(x,y) = 255` si `Hmin ≤ H ≤ Hmax` y `Smin ≤ S ≤ Smax` y `Vmin ≤ V ≤ Vmax`; `0` si no | Imagen binaria del guante |
| 4 | **Calibración** | `min = P₅ − holgura`, `max = P₉₅ + holgura` (percentiles de cada canal) | Adaptar el rango a tu guante y tu luz |
| 5 | **Erosión y dilatación** | Erosión: `(A ⊖ B) = {z : B_z ⊆ A}`<br>Dilatación: `(A ⊕ B) = {z : B_z ∩ A ≠ ∅}`<br>Apertura: `A ∘ B = (A ⊖ B) ⊕ B`<br>Cierre: `A • B = (A ⊕ B) ⊖ B` | Quitar ruido y rellenar huecos |
| 6 | **Momentos de imagen** | `M_pq = Σ_x Σ_y x^p · y^q · I(x,y)` | M00 = área |
| 7 | **Centroide** | `cx = M10 / M00`, `cy = M01 / M00` | Posición del guante |
| 8 | **Casco convexo y solidez** | `solidez = área(contorno) / área(casco convexo)`<br>El área se calcula con la fórmula del polígono (Shoelace): `A = ½ · |Σ (xᵢ·yᵢ₊₁ − xᵢ₊₁·yᵢ)|` | Distinguir la mano abierta del puño |
| 9 | **Transformada de distancia** | `D(p) = min ‖p − q‖` para todo `q` del fondo (distancia euclidiana)<br>Centro de la palma = `argmax D`, radio `r = max D` | Encontrar la palma y cortar el brazo |
| 10 | **Normalización de la mira** | `aim = clamp((cx − centro) / alcance, −1, 1)`<br>`alcance = w/2 − margen·w` | Posición → valor en [−1, 1] |
| 11 | **Suavizado exponencial** | `aimₜ = α · medidaₜ + (1 − α) · aimₜ₋₁`, con α = 0.4 | Quitar el temblor |
| 12 | **Detección de flanco** | `disparo = puñoₜ ∧ ¬puñoₜ₋₁` | Un disparo por cada cierre |
| 13 | **Giro por posición** | `Δθ = (aimₜ − aimₜ₋₁) · π/3`<br>En el margen: `+ signo(aim) · ω · Δt`, con ω ≈ 2 rad/s | La vista sigue a la mano |

## Conexión con el juego — [bridge.py](bridge.py)

- `start()` abre la cámara y ejecuta el pipeline en un **hilo aparte**, así la cámara (~30 fps)
  no limita los fps del juego.
- En cada frame, el juego llama a `get_controls()` desde `Player.update()` y recibe
  `{'aim', 'shoot'}`. `aim` vale `None` si no hay mano.
- `shoot` se retiene hasta que el juego lo lee, para no perder un disparo si el juego y la cámara
  van a distinta velocidad.
- `draw_preview()` dibuja la vista previa en la esquina superior derecha del juego.

En el juego solo cambian dos archivos:
- [main.py](../main.py): iniciar y cerrar la cámara, y dibujar la vista previa.
- [player.py](../player.py): `aim_control` y `fire` reemplazan al mouse. El movimiento con
  W A S D es el original.

**Giro por posición, como un mouse** (`aim_control`):
- En cada frame, el giro es el cambio de posición de la mano multiplicado por la sensibilidad:
  `Δángulo = (aim − aim_anterior) · HAND_SENSITIVITY`. Con `HAND_SENSITIVITY = π/3`, cruzar la
  zona de −1 a +1 gira 120°.
- **Margen:** si `|aim| > 0.95` (`HAND_EDGE`), la vista además gira de forma continua hacia ese
  lado (≈ 115°/s). Así se puede dar la vuelta completa sin salir de la zona.
- Si no hay mano (`aim = None`), la vista no gira, y al reaparecer la mano no hay salto.

Las dos constantes están en [settings.py](../settings.py).

## Cómo usarlo

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python main.py                          # jugar
python -m vision.main                   # ver la vista previa y la máscara, y calibrar el color
python -m vision.tests.test_pipeline    # pruebas automáticas (no necesitan cámara)
```

1. **Calibra una vez:** en `python -m vision.main`, pon la palma del guante sobre el recuadro
   amarillo y pulsa **`c`**. Copia los dos valores que se imprimen (`HSV_LOWER`, `HSV_UPPER`) en
   [config.py](config.py).
2. Revisa en la máscara que el guante salga completo en blanco y que no aparezcan otras cosas.
3. En el juego, usa el guante a la derecha de la línea verde, con los dedos separados.

## Limitaciones

- Otros objetos azules en la zona (jeans, camisas, afiches, el cielo por una ventana) pueden
  aparecer en la máscara. Conviene calibrar y no usar ropa azul.
- Con luz muy tenue, la saturación del guante baja y puede perderse. En ese caso, vuelve a calibrar.
- La mano abierta debe tener los dedos separados. Con los dedos juntos, la solidez sube y puede
  confundirse con un puño.
