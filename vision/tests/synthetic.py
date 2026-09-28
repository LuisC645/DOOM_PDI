"""Genera frames de prueba (640x480, como una webcam) con un guante azul y piel."""
import cv2
import numpy as np

GLOVE = (200, 80, 30)         # BGR azul -> HSV ≈ (111, 217, 200)
SKIN = (130, 160, 215)        # piel: no es azul, debe ignorarse
BACKGROUND = (60, 90, 40)     # verdoso


def blank():
    return np.full((480, 640, 3), BACKGROUND, np.uint8)


def draw_face(img, x=590, y=150):
    """Cara (elipse) + cuello, en el 1/4 izquierdo de la imagen espejada."""
    cv2.rectangle(img, (x - 30, y + 40), (x + 30, y + 110), SKIN, -1)
    cv2.ellipse(img, (x, y), (55, 75), 0, 0, 360, SKIN, -1)


def draw_hand(img, x, y=360, open_=True, color=GLOVE):
    """Guante (palma + puño del guante; con `open_`, cinco dedos separados) y antebrazo de piel.

    Ojo: `x` está en coordenadas de la cámara (antes del espejo): x pequeño = derecha de la imagen final.
    """
    cv2.rectangle(img, (x - 25, y + 30), (x + 25, y + 260), SKIN, -1)       # antebrazo
    cv2.rectangle(img, (x - 28, y + 20), (x + 28, y + 70), color, -1)       # puño del guante
    cv2.circle(img, (x, y), 45, color, -1)
    if open_:
        for angle in (-60, -30, 0, 30, 60):
            a = np.radians(angle - 90)
            tip = (int(x + 110 * np.cos(a)), int(y + 110 * np.sin(a)))
            cv2.line(img, (x, y), tip, color, 18)


def draw_bent_arm(img, x, y=360, color=GLOVE):
    """Brazo doblado del mismo color del guante (peor caso: un guante largo hasta el codo)."""
    cv2.line(img, (x, y + 30), (x + 150, y + 230), color, 55)
    cv2.line(img, (x + 150, y + 230), (x + 400, y + 260), color, 70)


def frame(hand_x=None, open_=True, face=True, bent=False, color=GLOVE):
    img = blank()
    if face:
        draw_face(img)
    if hand_x is not None:
        draw_hand(img, hand_x, y=200 if bent else 360, open_=open_, color=color)
        if bent:
            draw_bent_arm(img, hand_x, y=200, color=color)
    return img
