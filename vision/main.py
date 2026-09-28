"""Prueba con la cámara, sin el juego: vista previa + máscara del guante.

Uso (desde la raíz del proyecto):  python -m vision.main
Teclas: c = calibrar (guante dentro del recuadro amarillo)   q / Esc = salir.
Al calibrar se imprime el rango HSV para copiarlo en config.py.
"""
import cv2
import numpy as np

from vision import config as cfg
from vision.pipeline import START, process
from vision.processing.segmentation import calibrate
from vision.utils.drawing import annotate

# recuadro de calibración: en el centro de la zona de la mano
CALIB_BOX = (cfg.HAND_X + (cfg.WIDTH - cfg.HAND_X) // 2 - 20, cfg.HEIGHT // 2 - 20, 40, 40)


def main():
    cap = cv2.VideoCapture(cfg.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit('No se pudo abrir la cámara')
    r = START

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        r = process(frame, r)
        preview = annotate(r)
        x, y, w, h = CALIB_BOX
        cv2.rectangle(preview, (x, y), (x + w, y + h), (0, 255, 255), 1)
        view = np.hstack([preview, cv2.cvtColor(r['mask'], cv2.COLOR_GRAY2BGR)])
        cv2.imshow('Vista previa  |  mascara  (c = calibrar)', cv2.resize(view, None, fx=2, fy=2))

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        if key == ord('c'):
            calibrate(r['img'], CALIB_BOX)
            print(f'HSV_LOWER = {cfg.HSV_LOWER}\nHSV_UPPER = {cfg.HSV_UPPER}   <- copia estos valores en vision/config.py')

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
