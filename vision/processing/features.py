"""Etapas 5-6: contorno de la mano (sin el brazo), centroide y solidez."""
import cv2
import numpy as np

from vision import config as cfg


def find_hand(mask):
    """5. Contorno más grande dentro de la zona de la mano, o None si no hay mano."""
    x, y, w, h = cfg.HAND_ZONE
    contours, _ = cv2.findContours(mask[y:y + h, x:x + w], cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE, offset=(x, y))  # offset: coords. de la imagen
    hand = max(contours, key=cv2.contourArea, default=None)
    if hand is None or cv2.contourArea(hand) < cfg.MIN_AREA:
        return None
    return hand


def remove_arm(contour):
    """5b. Deja solo la mano: corta el brazo por debajo de la muñeca.

    La transformada de distancia da, para cada píxel, su distancia al borde. El máximo es el
    centro de la palma (la parte más ancha) y su valor es el radio de la palma. Se busca solo
    en la parte de arriba del blob porque el brazo entra desde abajo.
    """
    blob = np.zeros((cfg.HEIGHT, cfg.WIDTH), np.uint8)
    cv2.drawContours(blob, [contour], -1, 255, -1)
    x, y, w, h = cv2.boundingRect(contour)
    dist = cv2.distanceTransform(blob, cv2.DIST_L2, 5)
    _, radius, _, (_, palm_y) = cv2.minMaxLoc(dist[y:y + int(cfg.PALM_SEARCH * h)])
    blob[int(y + palm_y + cfg.WRIST_CUT * radius):] = 0         # todo lo de abajo es brazo
    contours, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea)


def centroid_x(contour):
    """6a. Coordenada x del centroide por momentos de imagen: M10 / M00."""
    m = cv2.moments(contour)
    return m['m10'] / m['m00']


def solidity(contour):
    """6b. Área del contorno / área del casco convexo. Mano abierta ≈ 0.6, puño ≈ 0.87."""
    return cv2.contourArea(contour) / cv2.contourArea(cv2.convexHull(contour))
