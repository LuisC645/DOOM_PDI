"""Pruebas del pipeline con imágenes sintéticas (no necesitan cámara).

Uso (desde la raíz del proyecto):  python -m vision.tests.test_pipeline
También funcionan con pytest si está instalado.
"""
from vision import config as cfg
from vision.pipeline import START, process
from vision.processing.controls import aim_from_x
from vision.processing.segmentation import preprocess, segment
from vision.tests.synthetic import blank, frame

CENTER_X = 640 - 2 * (cfg.HAND_ZONE[0] + cfg.HAND_ZONE[2] // 2)  # x de cámara que cae en el centro de la zona


def test_background_is_not_skin():
    assert segment(preprocess(blank())).max() == 0


def test_hand_is_segmented():
    assert process(frame(CENTER_X))['hand'] is not None


def test_open_hand_has_low_solidity():
    r = process(frame(CENTER_X, open_=True))
    assert r['solidity'] < 0.7 and not r['fist']


def test_fist_has_high_solidity():
    r = process(frame(CENTER_X, open_=False))
    assert r['solidity'] >= 0.8 and r['fist']


def test_shoots_once_per_fist():
    sequence = [True] * 3 + [False] * 3 + [True] * 3 + [False] * 3   # abrir, cerrar, abrir, cerrar
    r, shots = START, 0
    for open_ in sequence:
        r = process(frame(CENTER_X, open_=open_), r)
        shots += r['shoot']
    assert shots == 2


def test_aim_deadzone_and_limits():
    x, _, w, _ = cfg.HAND_ZONE
    margin = cfg.AIM_MARGIN * w
    assert aim_from_x(x + w / 2) == 0.0                 # centro -> quieto
    assert aim_from_x(x + margin) == -1.0               # margen izquierdo -> máximo a la izquierda
    assert aim_from_x(x + w - margin) == 1.0            # margen derecho -> máximo a la derecha
    assert aim_from_x(x) == -1.0 and aim_from_x(x + w) == 1.0   # más allá del margen se mantiene en ±1


def test_aim_follows_hand():
    left = process(frame(CENTER_X + 120, face=False))   # cámara x mayor = izquierda en la imagen espejada
    right = process(frame(CENTER_X - 120, face=False))
    assert left['aim'] < 0 < right['aim']


def test_hand_in_face_zone_is_ignored():
    assert process(frame(600, face=False))['hand'] is None   # x=600 de cámara -> zona de la cabeza


def test_face_is_detected_without_neck():
    r = process(frame())
    x, y, w, h = r['face_box']
    assert r['face'] is not None and h <= cfg.FACE_RATIO * w + 1


def test_straight_face_has_no_roll():
    r = process(frame())
    assert abs(r['roll_deg']) < 3 and r['roll'] == 0.0


def test_roll_follows_tilt():
    # en la cámara, horario = la parte de arriba va a la derecha; tras el espejo va a la izquierda (-)
    left = process(frame(tilt=25))['roll_deg']
    right = process(frame(tilt=-25))['roll_deg']
    assert left < -15 and right > 15


def test_pitch_follows_vertical_movement():
    ref = process(frame())                                    # primer frame: fija la posición neutra
    forward, back = ref, ref
    for _ in range(10):
        forward = process(frame(face_dy=35), forward)          # cara más abajo -> adelante (+)
        back = process(frame(face_dy=-35), back)               # cara más arriba -> atrás (-)
    assert forward['pitch'] > 0.3 and back['pitch'] < -0.3


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
