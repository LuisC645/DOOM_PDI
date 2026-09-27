"""Etapa 7: descriptores -> comandos (mira, puño, roll y pitch)."""
from vision import config as cfg


def scale(value, deadzone, max_value):
    """Lleva un valor a [-1, 1]: 0 dentro de la zona muerta, ±1 desde max_value en adelante."""
    magnitude = min(1.0, max(0.0, (abs(value) - deadzone) / (max_value - deadzone)))
    return magnitude if value >= 0 else -magnitude


def aim_from_x(cx):
    """Posición horizontal de la mano -> mira en [-1, 1].

    La mira llega a ±1 a una distancia AIM_MARGIN del borde, porque el centroide
    de la mano nunca toca el borde de la zona.
    """
    x, _, w, _ = cfg.HAND_ZONE
    reach = w / 2 - cfg.AIM_MARGIN * w                 # distancia del centro al punto de ±1
    offset = (cx - (x + w / 2)) / reach
    return scale(offset, cfg.DEADZONE, 1.0)


def smooth(new, previous):
    """Media móvil exponencial: evita que el valor tiemble."""
    return cfg.SMOOTHING * new + (1 - cfg.SMOOTHING) * previous


def is_fist(solidity):
    return solidity >= cfg.thresholds['Solidez %'] / 100


def roll_from_angle(degrees):
    """Inclinación lateral de la cabeza -> [-1, 1]  (+ = hacia el hombro derecho)."""
    return scale(degrees, cfg.ROLL_DEADZONE, cfg.ROLL_MAX)


def pitch_from_y(cy, ref_y, face_h):
    """Desplazamiento vertical de la cara respecto a la posición neutra -> [-1, 1].

    Al inclinar la cabeza hacia adelante la cara baja (+); hacia atrás, sube (−).
    """
    return scale((cy - ref_y) / face_h, cfg.PITCH_DEADZONE, cfg.PITCH_MAX)
