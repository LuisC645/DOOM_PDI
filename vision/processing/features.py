"""Etapas 5-6: contornos y descriptores geométricos (mano y cara)."""
import math

import cv2
import numpy as np

from vision import config as cfg


def largest_contour(mask, zone):
    """5. Contorno más grande dentro de una zona (x, y, w, h), o None si es muy pequeño."""
    x, y, w, h = zone
    contours, _ = cv2.findContours(mask[y:y + h, x:x + w], cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE, offset=(x, y))  # offset: coords. de la imagen
    biggest = max(contours, key=cv2.contourArea, default=None)
    if biggest is None or cv2.contourArea(biggest) < cfg.MIN_AREA:
        return None
    return biggest


def centroid(contour):
    """Centroide por momentos de imagen: (M10/M00, M01/M00)."""
    m = cv2.moments(contour)
    return m['m10'] / m['m00'], m['m01'] / m['m00']


def solidity(contour):
    """Área del contorno / área del casco convexo. Mano abierta ≈ 0.6, puño ≈ 0.87."""
    hull = cv2.convexHull(contour)
    return cv2.contourArea(contour) / cv2.contourArea(hull), hull


def face_region(contour):
    """Máscara solo de la cara: se rellena el contorno y se corta el cuello.

    La piel de la cara y el cuello forman un solo blob; la cara es la parte de arriba
    con alto ≈ FACE_RATIO × ancho. Devuelve (máscara de la cara, caja (x, y, w, h)).
    """
    x, y, w, h = cv2.boundingRect(contour)
    face_h = min(h, int(cfg.FACE_RATIO * w))
    mask = np.zeros((cfg.HEIGHT, cfg.WIDTH), np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mask[y + face_h:] = 0
    return mask, (x, y, w, face_h)


def orientation(binary):
    """Centroide y ángulo del eje mayor respecto a la vertical, con momentos centrales.

    θ = ½·atan2(2·μ11, μ02 − μ20). Devuelve (cx, cy, grados); positivo = parte de arriba
    inclinada hacia la derecha de la imagen.
    """
    m = cv2.moments(binary, binaryImage=True)
    cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
    theta = 0.5 * math.atan2(2 * m['mu11'], m['mu02'] - m['mu20'])
    return cx, cy, -math.degrees(theta)
