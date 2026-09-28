"""Parámetros del sistema. Todo lo ajustable está aquí."""

CAMERA_INDEX = 0
WIDTH, HEIGHT = 320, 240          # resolución de procesamiento

# Imagen ya espejada:  | cara (1/4) | mano (3/4) |
HAND_X = WIDTH // 4               # línea que separa la pantalla
HAND_ZONE = (HAND_X, 0, WIDTH - HAND_X, HEIGHT)   # x, y, ancho, alto

# Segmentación del guante azul en HSV (en OpenCV: H 0-179, S 0-255, V 0-255)
# Rango inicial para azul; `python -m vision.main` + tecla c calcula el de tu guante.
HSV_LOWER = (100, 80, 40)         # H mínimo (azul), saturación y brillo mínimos (descarta grises y sombras)
HSV_UPPER = (130, 255, 255)
CALIB_PAD = (8, 50, 50)           # holgura que se suma al rango medido al calibrar (H, S, V)
MIN_AREA = 1500                   # área mínima (píxeles) de un contorno para ser mano

# Mano
PALM_SEARCH = 0.75                # el centro de la palma se busca en esta fracción superior del blob
WRIST_CUT = 1.1                   # se corta el brazo a esta distancia (en radios de palma) bajo el centro
FIST_SOLIDITY = 0.84              # solidez >= este valor -> puño (abierta ≈ 0.72, puño ≈ 0.96)
AIM_MARGIN = 0.15                 # la mira llega a ±1 a esta distancia del borde (fracción del ancho)
SMOOTHING = 0.4                   # suavizado (1 = sin suavizar, cerca de 0 = muy suave)
