"""Vista previa: la línea que separa la pantalla y el estado de la mano."""
import cv2

from vision import config as cfg

GREEN, RED, GRAY = (0, 255, 0), (0, 0, 255), (160, 160, 160)


def annotate(r):
    img = r['img'].copy()
    x = cfg.HAND_X
    cv2.line(img, (x, 0), (x, cfg.HEIGHT), GREEN, 2)

    if r['hand'] is None:
        text, color = 'SIN MANO', GRAY
    elif r['fist']:
        text, color = 'CERRADA', RED
    else:
        text, color = 'ABIERTA', GREEN
    cv2.putText(img, text, (x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return img
