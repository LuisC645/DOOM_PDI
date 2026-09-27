"""Etapas 1-4: frame de la cámara -> máscara binaria de piel."""
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
    """2. BGR -> YCrCb   3. Umbral en Cr y Cb   4. Apertura (quita ruido) y cierre (rellena huecos)."""
    t = cfg.thresholds
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    mask = cv2.inRange(ycrcb, np.array([0, t['Cr min'], t['Cb min']], np.uint8),
                              np.array([255, t['Cr max'], t['Cb max']], np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL_OPEN)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL_CLOSE, iterations=2)
