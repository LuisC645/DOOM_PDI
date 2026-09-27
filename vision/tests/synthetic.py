"""Genera frames de prueba (640x480, como una webcam) con formas color piel."""
import cv2
import numpy as np

SKIN = (130, 160, 215)        # BGR con Cr y Cb dentro del rango de piel
BACKGROUND = (60, 90, 40)     # verdoso, fuera del rango de piel


def blank():
    return np.full((480, 640, 3), BACKGROUND, np.uint8)


FACE_X, FACE_Y = 520, 180    # cámara x=520 -> zona de la cabeza (izquierda de la imagen espejada)


def draw_face(img, x=FACE_X, y=FACE_Y, tilt=0):
    """Cara (elipse) + cuello. `tilt` en grados: positivo = gira en sentido horario en la cámara."""
    cv2.rectangle(img, (x - 30, y + 40), (x + 30, y + 300), SKIN, -1)
    cv2.ellipse(img, (x, y), (55, 75), tilt, 0, 360, SKIN, -1)


def draw_hand(img, x, y=360, open_=True):
    """Palma + antebrazo; con `open_` se agregan cinco dedos separados.

    Ojo: `x` está en coordenadas de la cámara (antes del espejo): x pequeño = derecha de la imagen final.
    """
    cv2.circle(img, (x, y), 45, SKIN, -1)
    cv2.rectangle(img, (x - 25, y + 30), (x + 25, y + 260), SKIN, -1)
    if open_:
        for angle in (-60, -30, 0, 30, 60):
            a = np.radians(angle - 90)
            tip = (int(x + 110 * np.cos(a)), int(y + 110 * np.sin(a)))
            cv2.line(img, (x, y), tip, SKIN, 18)


def frame(hand_x=None, open_=True, face=True, tilt=0, face_dy=0):
    img = blank()
    if face:
        draw_face(img, y=FACE_Y + face_dy, tilt=tilt)
    if hand_x is not None:
        draw_hand(img, hand_x, open_=open_)
    return img
