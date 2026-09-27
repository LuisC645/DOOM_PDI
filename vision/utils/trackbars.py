"""Barras de OpenCV para ajustar los umbrales en vivo."""
import cv2

from vision import config as cfg

WINDOW = 'Ajustes'


def create_trackbars():
    cv2.namedWindow(WINDOW)
    for name, value in cfg.thresholds.items():
        cv2.createTrackbar(name, WINDOW, value, 100 if name == 'Solidez %' else 255, lambda v: None)


def read_trackbars():
    """Copia la posición de cada barra en config.thresholds."""
    for name in cfg.thresholds:
        cfg.thresholds[name] = cv2.getTrackbarPos(name, WINDOW)
