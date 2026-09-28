"""Etapa 7: posición de la mano -> mira."""
from vision import config as cfg


def aim_from_x(cx):
    """Posición horizontal de la mano -> mira en [-1, 1] (0 = centro de la zona).

    La mira llega a ±1 a una distancia AIM_MARGIN del borde, porque el centroide
    de la mano nunca toca el borde de la zona. Más allá del margen se queda en ±1.
    """
    x, _, w, _ = cfg.HAND_ZONE
    reach = w / 2 - cfg.AIM_MARGIN * w                 # distancia del centro al punto de ±1
    return max(-1.0, min(1.0, (cx - (x + w / 2)) / reach))


def smooth(new, previous):
    """Media móvil exponencial: evita que la mira tiemble."""
    return cfg.SMOOTHING * new + (1 - cfg.SMOOTHING) * previous
