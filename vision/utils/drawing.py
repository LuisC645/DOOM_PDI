"""Vista de depuración: imagen anotada + máscara binaria, lado a lado."""
import math

import cv2
import numpy as np

from vision import config as cfg

GREEN, GRAY, WHITE = (0, 255, 0), (90, 90, 90), (255, 255, 255)
BLUE, RED, YELLOW, MAGENTA = (255, 128, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_hand(img, r):
    # zona, centro (mira quieta) y margen interior (donde la mira llega a ±1)
    x, y, w, h = cfg.HAND_ZONE
    cv2.rectangle(img, (x, y), (x + w - 1, y + h - 1), GREEN, 1)
    cv2.line(img, (x + w // 2, y), (x + w // 2, y + h), GREEN, 1)
    margin = int(cfg.AIM_MARGIN * w)
    for mx in (x + margin, x + w - margin):
        cv2.line(img, (mx, y), (mx, y + h), GRAY, 1)

    # barra de la mira
    bar_y = y + h - 8
    cv2.line(img, (x + margin, bar_y), (x + w - margin, bar_y), GRAY, 2)
    cv2.circle(img, (int(x + w / 2 + r['aim'] * (w / 2 - margin)), bar_y), 5, YELLOW, -1)

    # mano: azul abierta, roja cerrada
    if r['hand'] is not None:
        color = RED if r['fist'] else BLUE
        cv2.drawContours(img, [r['hand']], -1, color, 2)
        cv2.drawContours(img, [r['hull']], -1, WHITE, 1)
        cv2.circle(img, r['center'], 4, color, -1)

    text = f"mira {r['aim']:+.2f}  solidez {r['solidity']:.2f}  {'PUNO' if r['fist'] else 'abierta'}"
    cv2.putText(img, text, (x + 5, 15), FONT, 0.35, GREEN, 1)
    if r['shoot']:
        cv2.putText(img, 'DISPARO', (x + 20, cfg.HEIGHT // 2 - 10), FONT, 0.9, RED, 2)


def draw_face(img, r):
    x, y, w, h = cfg.FACE_ZONE
    cv2.rectangle(img, (x, y), (x + w - 1, y + h - 1), MAGENTA, 1)
    if r['face'] is not None:
        fx, fy, fw, fh = r['face_box']
        cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), MAGENTA, 1)       # cara sin cuello
        cx, cy = r['face_center']
        a = math.radians(r['roll_deg'])                                     # eje de la cara
        dx, dy = int(fh / 2 * math.sin(a)), int(fh / 2 * math.cos(a))
        cv2.line(img, (cx - dx, cy + dy), (cx + dx, cy - dy), YELLOW, 2)
        cv2.circle(img, (cx, cy), 3, YELLOW, -1)
        ref = int(r['face_ref'])                                            # altura neutra
        cv2.line(img, (fx, ref), (fx + fw, ref), GRAY, 1)

    lines = [f"roll {r['roll_deg']:+.0f} gr -> {r['roll']:+.2f}",
             f"pitch {r['pitch']:+.2f}",
             "c = recalibrar"]
    for i, text in enumerate(lines):
        cv2.putText(img, text, (x + 4, h - 34 + 12 * i), FONT, 0.35, MAGENTA, 1)


def draw_annotated(r):
    """Imagen de la cámara con zonas, contornos y valores."""
    img = r['img'].copy()
    draw_face(img, r)
    draw_hand(img, r)
    return img


def draw(r):
    """Imagen anotada + máscara binaria, lado a lado."""
    return np.hstack([draw_annotated(r), cv2.cvtColor(r['mask'], cv2.COLOR_GRAY2BGR)])
