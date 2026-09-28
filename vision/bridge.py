"""Puente entre la cámara y el juego.

La cámara se procesa en un hilo aparte para no frenar el juego. El juego solo usa:
    start()          abrir la cámara
    get_controls()   {'aim', 'shoot'} del último frame
    draw_preview()   dibujar la vista de la cámara en la pantalla de Pygame
    stop()           cerrar la cámara
"""
import threading

import cv2
import pygame as pg

from vision import config as cfg
from vision.pipeline import START, process
from vision.utils.drawing import annotate

_state = {'result': START, 'shoot': False, 'preview': None, 'running': False}
_lock = threading.Lock()
_cap = None


def _loop():
    r = START
    while _state['running']:
        ok, frame = _cap.read()
        if not ok:
            continue
        r = process(frame, r)
        preview = cv2.cvtColor(annotate(r), cv2.COLOR_BGR2RGB)
        with _lock:
            _state['result'] = r
            _state['shoot'] = _state['shoot'] or r['shoot']   # se guarda hasta que el juego lo lea
            _state['preview'] = preview


def start():
    global _cap
    _cap = cv2.VideoCapture(cfg.CAMERA_INDEX)
    if not _cap.isOpened():
        raise SystemExit('No se pudo abrir la cámara')
    _state['running'] = True
    threading.Thread(target=_loop, daemon=True).start()


def stop():
    _state['running'] = False
    if _cap is not None:
        _cap.release()


def get_controls():
    """Controles para el juego; `shoot` es True una vez por cada puño."""
    with _lock:
        r = _state['result']
        shoot, _state['shoot'] = _state['shoot'], False
    return {
        'aim': r['aim'] if r['hand'] is not None else None,   # posición de la mano en [-1, 1]; None = sin mano
        'shoot': shoot,                                       # mano: puño
    }


def draw_preview(screen, pos=None):
    """Dibuja la vista de la cámara (320x240) en la esquina superior derecha."""
    with _lock:
        preview = _state['preview']
    if preview is None:
        return
    h, w = preview.shape[:2]
    surface = pg.image.frombuffer(preview.tobytes(), (w, h), 'RGB')
    screen.blit(surface, pos or (screen.get_width() - w - 10, 10))
