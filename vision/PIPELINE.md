# Control de Doom con la mano y la cabeza: pipeline de procesamiento de imágenes

El juego se controla frente a la webcam usando solo técnicas básicas de procesamiento digital de
imágenes: umbralización, morfología, contornos y momentos de imagen. No se usa IA.

| Parte | Gesto | Valor que se obtiene | Acción en el juego |
|---|---|---|---|
| Mano | Moverla a la izquierda o a la derecha | `aim` ∈ [−1, 1] | Girar |
| Mano | Cerrarla (puño) | `shoot` | Disparar |
| Cabeza | Inclinarla hacia adelante o atrás (pitch) | `pitch` ∈ [−1, 1] (+ = adelante) | Avanzar / retroceder |
| Cabeza | Inclinarla hacia un hombro (roll) | `roll` ∈ [−1, 1] (+ = hombro derecho) | Moverse de lado |

## Zonas de la pantalla

```
+----------------+---------------------------------+
|                |      (cara: queda fuera)        |
|    CABEZA      +---------------------------------+
|    (1.5/4)     |      MANO (2.5/4)               |
|                |   |←margen            margen→|  |
+----------------+---------------------------------+
```

- **Zona de la mano:** los 2.5/4 derechos, solo en la mitad inferior (altura del pecho).
  - La mitad superior queda fuera para que la cara no se una con la mano.
  - Las líneas grises interiores marcan el **margen**. La mira llega a ±1 en esas líneas, no en el
    borde, porque el centroide de la mano nunca toca el borde del recuadro.
- **Zona de la cabeza:** los 1.5/4 izquierdos, con todo el alto. La cara va ahí.

Las proporciones se cambian en [config.py](config.py) con `HAND_X`, `HAND_Y` y `AIM_MARGIN`.

## Estructura de archivos

```
vision/
├── bridge.py              ← puente con el juego: hilo de la cámara + get_controls()
├── config.py              ← parámetros: zonas, umbrales, zonas muertas
├── pipeline.py            ← une las etapas: process_hand() y process_face()
├── main.py                ← prueba con la cámara real
├── processing/            ← las etapas de procesamiento de imágenes
│   ├── segmentation.py    ← 1-4. redimensionar, espejo, Gaussiano, YCrCb, umbral, morfología
│   ├── features.py        ← 5-6. contornos, centroide, solidez, recorte de la cara, orientación
│   └── controls.py        ← 7. valores → [−1, 1] (zona muerta, margen, suavizado)
├── utils/                 ← herramientas de apoyo, no son parte del procesamiento
│   ├── drawing.py         ← dibuja zonas, contornos, ejes y barras
│   └── trackbars.py       ← barras para ajustar umbrales en vivo
└── tests/                 ← pruebas sin cámara
    ├── synthetic.py       ← genera imágenes de prueba (cara con cuello, mano abierta, puño)
    └── test_pipeline.py   ← 12 pruebas de cada etapa
```

## Pipeline

```
Cámara → [1] Preprocesamiento → [2] YCrCb → [3] Umbralización → [4] Morfología
       ├→ zona de la mano:  [5] contorno → [6] centroide, solidez      → [7] mira, disparo
       └→ zona de la cabeza: [5] contorno → [6] recorte, orientación    → [7] roll, pitch
```

### Etapas comunes — [processing/segmentation.py](processing/segmentation.py)

**1. Preprocesamiento**
- La imagen se reduce a 320x240 y se voltea horizontalmente para que funcione como un espejo.
- Se suaviza con un **filtro Gaussiano 5x5**, que reduce el ruido del sensor.

**2. Espacio de color YCrCb**
- YCrCb separa la luminancia (**Y**) de la crominancia (**Cr, Cb**).
- La piel ocupa un rango compacto de Cr y Cb aunque cambie la luz, por eso se umbraliza en esos canales.

**3. Umbralización**
- `cv2.inRange` deja en blanco los píxeles con Cr ∈ [133, 173] y Cb ∈ [77, 127], y en negro el resto.
- El resultado es una imagen binaria. Los umbrales se ajustan en vivo con las barras.

**4. Morfología**
- **Apertura** con un elemento de 3x3: quita puntos blancos sueltos.
- **Cierre** con un elemento de 9x9: rellena huecos, como ojos y boca en la cara o sombras en la mano.

### Mano — [processing/features.py](processing/features.py), [processing/controls.py](processing/controls.py)

**5. Contorno:** se toma el contorno de mayor área dentro de la zona de la mano. Si mide menos
de 1500 píxeles, se considera que no hay mano.

**6. Descriptores**
- **Centroide** a partir de los momentos: `cx = M10 / M00`.
- **Solidez** = área del contorno / área del casco convexo. La mano abierta da ≈ 0.6 por el
  espacio entre los dedos y el puño da ≈ 0.87.

**7. Comandos**
- **Mira:** `(cx − centro) / alcance`, donde el alcance es la distancia del centro al margen.
  - Zona muerta de ±0.15 en el centro.
  - Suavizado exponencial: `0.4·nuevo + 0.6·anterior`.
- **Disparo:** la solidez es ≥ 0.80 en este frame y en el anterior no lo era, es decir, la mano
  se acaba de cerrar.

### Cabeza — [processing/features.py](processing/features.py), [processing/controls.py](processing/controls.py)

**5. Contorno:** se toma el contorno de mayor área dentro de la zona de la cabeza.

**6a. Recorte del cuello** (`face_region`)
- La cara y el cuello son piel continua, así que forman un solo blob.
- Se usa la proporción de una cara humana: la cara es la parte superior del blob, con un alto de
  **1.3 × ancho**. Lo que queda debajo es cuello y se descarta.

**6b. Orientación por momentos centrales** (`orientation`)
- Con los momentos centrales de segundo orden (μ20, μ02, μ11) de la región de la cara se calcula
  el ángulo de su **eje mayor** respecto a la vertical:

  `θ = ½ · atan2(2·μ11, μ02 − μ20)`

- Una cara derecha tiene el eje mayor vertical (θ ≈ 0°). Al inclinarla hacia un hombro, el eje
  rota y ese ángulo es el **roll**.

**7. Comandos**
- **Roll:** zona muerta de ±8° y valor máximo a partir de 30°. Resultado en [−1, 1].
- **Pitch** (adelante o atrás):
  - Al inclinar la cabeza hacia adelante, la cara baja en la imagen; hacia atrás, sube.
  - Se mide el desplazamiento vertical del centroide respecto a una **altura neutra** y se divide
    por el alto de la cara, para que no dependa de la distancia a la cámara.
  - Zona muerta de 0.08 y valor máximo a partir de 0.35.
- **Altura neutra:** se toma automáticamente en el primer frame en que aparece la cara. La tecla
  **`c`** la vuelve a tomar.

## Conexión con el juego — [bridge.py](bridge.py)

- `start()` abre la cámara y ejecuta el pipeline en un **hilo aparte**, así la cámara (~30 fps)
  no limita los fps del juego.
- En cada frame, el juego llama a `get_controls()` desde `Player.update()` y recibe
  `{'aim', 'forward', 'strafe', 'shoot'}`.
- `shoot` se retiene hasta que el juego lo lee, para no perder un disparo si el juego y la cámara
  van a distinta velocidad.
- `draw_preview()` dibuja la imagen anotada en la esquina del juego y `recalibrate()` se activa
  con la tecla **C**.

En el juego solo cambian dos archivos:
- [main.py](../main.py): iniciar la cámara, mostrar la vista previa y la tecla C.
- [player.py](../player.py): `movement`, `aim_control` y `fire` leen los controles de la cámara
  en lugar del teclado y el mouse.

## Cómo usarlo

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python -m vision.main                   # prueba con la cámara
python -m vision.tests.test_pipeline    # pruebas automáticas (no necesitan cámara)
```

1. Buena luz frontal y un fondo sin colores parecidos a la piel.
2. Colócate de modo que tu **cara quede en el recuadro morado** (izquierda) y pon la mano derecha
   en el **recuadro verde**, a la altura del pecho y con los dedos separados.
3. Con la cabeza derecha y en reposo, pulsa **`c`** para fijar la posición neutra.
4. Si la mano o la cara no aparecen completas en blanco en la máscara, ajusta las barras de Cr y Cb.
5. `q` o `Esc` para salir.

## Limitaciones

- Los objetos del fondo con color piel (madera, paredes beige) pueden aparecer en la máscara.
- El **pitch** se estima por el desplazamiento vertical de la cara. Si te mueves entero hacia
  arriba o hacia abajo, por ejemplo al acomodarte en la silla, también cuenta como pitch. En ese
  caso, recalibra con `c`.
- El **roll** medido es algo menor que el ángulo real, porque el recorte conserva un poco de cuello,
  que es vertical. La dirección siempre es correcta.
- La mano abierta debe tener los dedos separados. Con los dedos juntos, la solidez sube y puede
  confundirse con un puño.
