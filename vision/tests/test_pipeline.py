"""Pruebas del pipeline con imágenes sintéticas (no necesitan cámara).

Uso (desde la raíz del proyecto):  python -m vision.tests.test_pipeline
También funcionan con pytest si está instalado.
"""
from vision import config as cfg
from vision.pipeline import START, process
from vision.processing.controls import aim_from_x
from vision.processing.segmentation import calibrate, preprocess, segment
from vision.tests.synthetic import SKIN, blank, frame

CENTER_X = 640 - 2 * (cfg.HAND_ZONE[0] + cfg.HAND_ZONE[2] // 2)  # x de cámara que cae en el centro de la zona


def test_background_is_not_glove():
    assert segment(preprocess(blank())).max() == 0


def test_glove_is_segmented():
    assert process(frame(CENTER_X))['hand'] is not None


def test_bare_hand_is_ignored():
    assert process(frame(CENTER_X, color=SKIN))['hand'] is None   # solo cuenta el color del guante


def test_calibration_adapts_to_glove():
    dark_glove = (35, 15, 8)                                       # azul muy oscuro (V ≈ 35 < V mínimo)
    original = cfg.HSV_LOWER, cfg.HSV_UPPER
    try:
        assert process(frame(CENTER_X, open_=False, color=dark_glove))['hand'] is None
        img = preprocess(frame(CENTER_X, open_=False, color=dark_glove))
        x, y = 640 - CENTER_X, 360                                 # centro de la palma, espejado
        calibrate(img, (x // 2 - 10, y // 2 - 10, 20, 20))
        assert process(frame(CENTER_X, open_=False, color=dark_glove))['fist']
    finally:
        cfg.HSV_LOWER, cfg.HSV_UPPER = original


def test_open_hand_has_low_solidity():
    r = process(frame(CENTER_X, open_=True))
    assert r['solidity'] < cfg.FIST_SOLIDITY - 0.05 and not r['fist']


def test_fist_has_high_solidity():
    r = process(frame(CENTER_X, open_=False))
    assert r['solidity'] > cfg.FIST_SOLIDITY + 0.05 and r['fist']


def test_bent_arm_does_not_change_hand_state():
    # con el brazo doblado, el contorno mano + brazo tiene una concavidad grande;
    # al cortar el brazo, la solidez vuelve a depender solo de la mano
    assert not process(frame(CENTER_X, open_=True, bent=True))['fist']
    assert process(frame(CENTER_X, open_=False, bent=True))['fist']


def test_shoots_once_per_fist():
    sequence = [True] * 3 + [False] * 3 + [True] * 3 + [False] * 3   # abrir, cerrar, abrir, cerrar
    r, shots = START, 0
    for open_ in sequence:
        r = process(frame(CENTER_X, open_=open_), r)
        shots += r['shoot']
    assert shots == 2


def test_aim_is_linear_with_limits():
    x, _, w, _ = cfg.HAND_ZONE
    margin = cfg.AIM_MARGIN * w
    center = x + w / 2
    assert aim_from_x(center) == 0.0                                    # centro -> 0
    assert abs(aim_from_x((center + x + w - margin) / 2) - 0.5) < 1e-9  # a mitad de camino -> 0.5 (sin zona muerta)
    assert aim_from_x(x + margin) == -1.0                               # margen izquierdo -> -1
    assert aim_from_x(x + w - margin) == 1.0                            # margen derecho -> +1
    assert aim_from_x(x) == -1.0 and aim_from_x(x + w) == 1.0           # más allá del margen se queda en ±1


def test_no_smoothing_drag_when_hand_reappears():
    r = process(frame(CENTER_X - 120, face=False))                     # mano a la derecha
    r = process(frame(face=False), r)                                   # la mano desaparece
    back = process(frame(CENTER_X - 120, face=False), r)                # vuelve al mismo lugar
    assert abs(back['aim'] - process(frame(CENTER_X - 120, face=False))['aim']) < 1e-9


def test_aim_follows_hand():
    left = process(frame(CENTER_X + 120, face=False))   # cámara x mayor = izquierda en la imagen espejada
    right = process(frame(CENTER_X - 120, face=False))
    assert left['aim'] < 0 < right['aim']


def test_hand_outside_zone_is_ignored():
    assert process(frame(600, face=False))['hand'] is None   # x=600 de cámara -> izquierda de la imagen


def test_face_is_not_detected_as_hand():
    assert process(frame())['hand'] is None                   # solo la cara (piel), sin guante


if __name__ == '__main__':
    tests = [(name, fn) for name, fn in globals().items() if name.startswith('test_')]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f'OK     {name}')
        except AssertionError:
            failed += 1
            print(f'FALLO  {name}')
    print(f'\n{len(tests) - failed}/{len(tests)} pruebas correctas')
    raise SystemExit(1 if failed else 0)
