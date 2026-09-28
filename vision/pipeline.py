"""Une todas las etapas: frame de la cámara -> mira, puño y disparo."""
from vision import config as cfg
from vision.processing.controls import aim_from_x, smooth
from vision.processing.features import centroid_x, find_hand, remove_arm, solidity
from vision.processing.segmentation import preprocess, segment

START = {'hand': None, 'aim': 0.0, 'fist': False}   # estado inicial (antes del primer frame)


def process(frame, previous=START):
    """Procesa un frame. `previous` es el resultado del frame anterior (para suavizar y disparar)."""
    img = preprocess(frame)
    mask = segment(img)
    hand = find_hand(mask)
    r = {'img': img, 'mask': mask, 'hand': hand, 'solidity': 0.0, 'aim': 0.0, 'fist': False, 'shoot': False}
    if hand is None:
        return r

    hand = r['hand'] = remove_arm(hand)
    r['solidity'] = solidity(hand)
    aim = aim_from_x(centroid_x(hand))
    r['aim'] = smooth(aim, previous['aim']) if previous['hand'] is not None else aim  # al reaparecer, sin arrastre
    r['fist'] = r['solidity'] >= cfg.FIST_SOLIDITY
    r['shoot'] = r['fist'] and not previous['fist']   # dispara solo al cerrar la mano
    return r
