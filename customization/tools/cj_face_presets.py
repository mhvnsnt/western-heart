#!/usr/bin/env python3
"""CJ parametric face — preset table + blend, GNM semantic-sampler style.

GNM maps 20 named expression classes -> 383-param vectors through a CVAE
decoder, and mixes them with blend_expressions({class: weight}). We do the same
thing for OUR cartoon face: named presets -> our ~20 semantic params, mixed
with blend_presets(). All values below are tuned against
characters/sheets/05-expression-eye-dart-matrix.jpg and
06-viseme-phoneme-mouth-matrix.jpg.

Canon: white eyes by default; pupil_toggle=1 only on emphasis beats.
"""

PARAMS = [
    # eyes (GNM: 100/eye)
    "blink_L", "blink_R", "wide", "squint_L", "squint_R", "look_x", "look_y",
    # brow (GNM has no brow basis; sheet 05 demands mask-brow movement)
    "brow_L", "brow_R", "brow_squeeze",
    # lower face (GNM: 150)
    "jaw_open", "smile", "frown", "grimace", "smirk_L", "smirk_R",
    "mouth_shift_x",
    # tongue (GNM: 32)
    "tongue_out", "tongue_side",
    # iris (GNM: 1)
    "pupil_toggle",
]

# preset -> (param overrides, mouth_index). Unlisted params default to 0.
# mouth_index follows the 17-mouth swap set in build_mouthkit.py.
PRESETS = {
    # --- sheet 05: the 8-expression matrix (the sign-off checklist) ---
    "determined_focused": (dict(brow_L=-0.45, brow_R=-0.45, brow_squeeze=0.35), 0),
    "angry_scowling":     (dict(brow_L=-1.0, brow_R=-1.0, brow_squeeze=0.7,
                                squint_L=0.35, squint_R=0.35,
                                frown=0.75, grimace=0.45), 15),
    "intrigued_questioning": (dict(brow_L=0.75, brow_R=-0.15, look_x=0.55,
                                   pupil_toggle=1.0, smirk_R=0.55), 0),
    "squinting_flight":   (dict(squint_L=1.0, squint_R=1.0, brow_squeeze=0.5,
                                brow_L=-0.3, brow_R=-0.3, frown=0.45), 10),
    "surprised_alarmed":  (dict(wide=1.0, brow_L=1.0, brow_R=1.0, jaw_open=0.85,
                                pupil_toggle=1.0), 16),
    "straining_grimacing": (dict(squint_L=0.8, squint_R=0.8, brow_squeeze=1.0,
                                 grimace=1.0, jaw_open=0.35, frown=0.5), 15),
    "concentrating":      (dict(squint_L=0.5, squint_R=0.5,
                                brow_L=-0.4, brow_R=-0.4, frown=0.3), 0),
    "unconscious_closed": (dict(blink_L=1.0, blink_R=1.0, jaw_open=0.15), 0),
    # --- sheet 05: isolated eye sheets (the eye-darts) ---
    "dart_up":            (dict(look_y=1.0, pupil_toggle=1.0), 0),
    "dart_left":          (dict(look_x=-1.0, pupil_toggle=1.0), 0),
    "dart_down":          (dict(look_y=-1.0, pupil_toggle=1.0), 0),
    "side_eye_suspicious": (dict(look_x=1.0, squint_L=0.3, squint_R=0.3,
                                 brow_L=-0.3, brow_R=-0.3, smirk_L=0.4,
                                 pupil_toggle=1.0), 0),
    # --- GNM-class-inspired extras (comedic range) ---
    "happy":              (dict(smile=1.0, squint_L=0.25, squint_R=0.25,
                                brow_L=0.3, brow_R=0.3), 7),
    "disgust":            (dict(frown=0.8, grimace=0.5, brow_L=-0.6, brow_R=-0.6,
                                brow_squeeze=0.6, mouth_shift_x=0.4), 11),
    "snarl":              (dict(grimace=0.9, brow_L=-0.8, brow_R=-0.8,
                                brow_squeeze=0.8, frown=0.4), 11),
    "pucker":             (dict(jaw_open=0.1), 13),
    "blow":               (dict(jaw_open=0.25, wide=0.2), 3),
    "tongue_center":      (dict(tongue_out=0.75, jaw_open=0.3), 1),
    "wink_left":          (dict(blink_L=1.0, smile=0.4, smirk_L=0.5,
                                pupil_toggle=1.0), 0),
    "wink_right":         (dict(blink_R=1.0, smile=0.4, smirk_R=0.5,
                                pupil_toggle=1.0), 0),
    "smug":               (dict(smirk_R=0.8, brow_R=0.5, brow_L=-0.2), 0),
}

# Sheet-05 checklist order for proof renders.
CHECKLIST = [
    "determined_focused", "angry_scowling", "intrigued_questioning",
    "squinting_flight", "surprised_alarmed", "straining_grimacing",
    "concentrating", "unconscious_closed",
]
DARTS = ["dart_up", "dart_left", "dart_down", "side_eye_suspicious"]


def preset_vector(name):
    """Full param vector for a preset (dict param -> value)."""
    overrides, _mouth = PRESETS[name]
    vec = {p: 0.0 for p in PARAMS}
    vec.update(overrides)
    return vec


def blend_presets(weights):
    """Weighted mix of presets -> param vector. Mirrors GNM's blend_expressions."""
    vec = {p: 0.0 for p in PARAMS}
    total = sum(weights.values()) or 1.0
    for name, w in weights.items():
        pv = preset_vector(name)
        for p in PARAMS:
            vec[p] += pv[p] * (w / total)
    return vec


def apply_to_props(params_obj, name):
    """Set a preset on a CJ_FaceParams object's custom props. Returns mouth_index."""
    vec = preset_vector(name)
    for p, v in vec.items():
        params_obj[p] = v
    return PRESETS[name][1]
