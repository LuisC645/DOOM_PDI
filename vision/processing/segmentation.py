"""Etapas 1-4: frame de la cámara -> máscara binaria del guante."""
import cv2
import numpy as np

from vision import config as cfg

KERNEL_OPEN = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
KERNEL_CLOSE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))


def preprocess(frame):
    """1. Redimensionar, espejar y suavizar con un filtro Gaussiano (reduce ruido)."""
    frame = cv2.resize(frame, (cfg.WIDTH, cfg.HEIGHT))
    frame = cv2.flip(frame, 1)
    return cv2.GaussianBlur(frame, (5, 5), 0)


def segment(img):
    """2. BGR -> HSV   3. Umbral en H, S y V (color del guante)   4. Apertura y cierre."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(cfg.HSV_LOWER, np.uint8), np.array(cfg.HSV_UPPER, np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL_OPEN)                   # quita puntos sueltos
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL_CLOSE, iterations=2)  # rellena huecos


def calibrate(img, box):
    """Mide el color del guante dentro de `box` (x, y, w, h) y ajusta HSV_LOWER / HSV_UPPER.

    Se usan los percentiles 5 y 95 de cada canal (ignoran reflejos y píxeles de borde)
    más una holgura. S y V no tienen techo: un guante más saturado o iluminado sigue siendo el guante.
    """
    x, y, w, h = box
    hsv = cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_BGR2HSV).reshape(-1, 3)
    low = np.percentile(hsv, 5, axis=0) - cfg.CALIB_PAD
    high = np.percentile(hsv, 95, axis=0) + cfg.CALIB_PAD
    cfg.HSV_LOWER = tuple(int(v) for v in np.clip(low, 0, 255))
    cfg.HSV_UPPER = (int(min(high[0], 179)), 255, 255)
