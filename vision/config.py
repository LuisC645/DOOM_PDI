"""Parámetros del sistema. Todo lo ajustable está aquí."""

CAMERA_INDEX = 0
WIDTH, HEIGHT = 320, 240          # resolución de procesamiento

# Zonas de la imagen (ya espejada):
# +----------------+---------------------------+
# |                |  (cara: queda fuera)      |
# |  cabeza        +---------------------------+
# |  1.5 / 4       |  mano: 2.5 / 4 (pecho)    |
# +----------------+---------------------------+
HAND_X = int(WIDTH * 1.5 / 4)     # la zona de la mano empieza aquí...
HAND_Y = HEIGHT // 2              # ...y solo en la mitad inferior
HAND_ZONE = (HAND_X, HAND_Y, WIDTH - HAND_X, HEIGHT - HAND_Y)   # x, y, ancho, alto
FACE_ZONE = (0, 0, HAND_X, HEIGHT)

MIN_AREA = 1500                   # área mínima (píxeles) de un contorno para ser mano o cara

# --- Mano: mira y disparo ---
AIM_MARGIN = 0.15                 # margen interior (fracción del ancho): la mira llega a ±1 antes del borde
DEADZONE = 0.15                   # zona muerta de la mira alrededor del centro
SMOOTHING = 0.4                   # suavizado (1 = sin suavizar, cerca de 0 = muy suave)

# --- Cabeza: inclinación ---
FACE_RATIO = 1.3                  # alto de la cara ≈ 1.3 × ancho; lo que sobra por debajo es cuello
ROLL_DEADZONE, ROLL_MAX = 8, 30   # grados: roll (inclinar la cabeza hacia un hombro)
PITCH_DEADZONE, PITCH_MAX = 0.08, 0.35   # desplazamiento vertical / alto de la cara (adelante-atrás)

# Umbrales iniciales; se ajustan en vivo con las barras (utils/trackbars.py)
thresholds = {
    'Cr min': 133, 'Cr max': 173,     # rango de piel en YCrCb
    'Cb min': 77, 'Cb max': 127,
    'Solidez %': 80,                  # solidez >= este valor -> puño
}
