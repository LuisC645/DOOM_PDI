"""Une todas las etapas: frame de la cámara -> comandos de la mano y de la cabeza."""
from vision import config as cfg
from vision.processing.controls import aim_from_x, is_fist, pitch_from_y, roll_from_angle, smooth
from vision.processing.features import centroid, face_region, largest_contour, orientation, solidity
from vision.processing.segmentation import preprocess, segment

# Estado inicial. face_ref = altura neutra de la cara (None = se toma en el próximo frame con cara).
START = {'aim': 0.0, 'fist': False, 'roll': 0.0, 'pitch': 0.0, 'face_ref': None}


def process_hand(mask, previous, r):
    hand = largest_contour(mask, cfg.HAND_ZONE)
    r.update(hand=hand, hull=None, center=None, solidity=0.0, aim=0.0, fist=False, shoot=False)
    if hand is None:
        return
    cx, cy = centroid(hand)
    r['solidity'], r['hull'] = solidity(hand)
    r['center'] = (int(cx), int(cy))
    r['aim'] = smooth(aim_from_x(cx), previous['aim'])
    r['fist'] = is_fist(r['solidity'])
    r['shoot'] = r['fist'] and not previous['fist']   # dispara solo al cerrar la mano


def process_face(mask, previous, r):
    face = largest_contour(mask, cfg.FACE_ZONE)
    r.update(face=face, face_box=None, face_center=None, roll_deg=0.0, roll=0.0, pitch=0.0,
             face_ref=previous['face_ref'])
    if face is None:
        return
    face_mask, r['face_box'] = face_region(face)       # sin el cuello
    cx, cy, r['roll_deg'] = orientation(face_mask)
    r['face_center'] = (int(cx), int(cy))
    if r['face_ref'] is None:                          # primera vez: esta es la posición neutra
        r['face_ref'] = cy
    face_h = r['face_box'][3]
    r['roll'] = smooth(roll_from_angle(r['roll_deg']), previous['roll'])
    r['pitch'] = smooth(pitch_from_y(cy, r['face_ref'], face_h), previous['pitch'])


def process(frame, previous=START):
    """Procesa un frame. `previous` es el resultado del frame anterior (suavizado, disparo, referencia)."""
    img = preprocess(frame)
    mask = segment(img)
    r = {'img': img, 'mask': mask}
    process_hand(mask, previous, r)
    process_face(mask, previous, r)
    return r
