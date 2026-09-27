"""Prueba con la cámara, sin el juego.

Uso (desde la raíz del proyecto):  python -m vision.main
Teclas: c = recalibrar la posición neutra de la cabeza   q / Esc = salir.
La ventana "Ajustes" cambia los umbrales en vivo.
"""
import cv2

from vision import config as cfg
from vision.pipeline import START, process
from vision.utils.drawing import draw
from vision.utils.trackbars import create_trackbars, read_trackbars


def main():
    cap = cv2.VideoCapture(cfg.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit('No se pudo abrir la cámara')
    create_trackbars()
    r = START

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        read_trackbars()
        r = process(frame, r)
        cv2.imshow('Control con la mano  |  imagen  |  mascara', cv2.resize(draw(r), None, fx=2, fy=2))

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        if key == ord('c'):
            r['face_ref'] = None      # la posición actual de la cara pasa a ser la neutra

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
