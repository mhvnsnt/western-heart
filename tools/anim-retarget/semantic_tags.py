"""Semantic joint description protocol for topology-agnostic retargeting.

Implements the *semantic joint alignment* core of SATA
("Semantic-Aware Motion Encoding for Topology-Agnostic Character Animation",
Zhang et al., arXiv:2605.27055, May 2026, ICML 2026; code Apache-2.0 at
https://github.com/zzysteve/SATA), paper Section 3.2 and Table 11.

Paper method: for each joint, an MLLM (Gemini 2.5 Pro) generates a
taxonomic-neutral functional description ("the pelvis and hip root anchor");
a frozen T5 encoder embeds it into X_t; Semantic-Spatial Modulation (FiLM
gamma/beta + gate, eq. 1-3) aligns functional correspondences across species,
decoupling motion from bone hierarchy -- no canonical joint set, no
source-target pairs, no hand-crafted joint correspondences.

This module provides the WH-native, dependency-free equivalent:
  1. ROLE INFERENCE -- joint names are normalized and mapped to canonical
     functional roles (root, pelvis, thigh, shin, ...). Unknown joints fall
     back to structural descriptions derived from graph position (the paper's
     "structural generalization"), so novel creature rigs still get grounded.
  2. DESCRIPTION PROTOCOL -- taxonomic-neutral functional descriptions in the
     paper's Table-11 style ("the left upper arm bone").
  3. EMBEDDING -- deterministic TF embedding over the protocol vocabulary
     (offline stand-in for the paper's frozen T5 encoder; cosine similarity
     on shared functional words drives alignment). An optional
     HuggingFace sentence-transformer backend can be selected with
     SEMRET_EMBED=hf when closer parity with the paper is wanted.

The embedding choice is a documented deviation from the paper (no trained
weights ship with this tool); the alignment *mechanism* -- functional
correspondence from semantic tags + spatial structure, never joint names or
manual maps -- is the paper's core technique.
"""

import math
import os
import re
from collections import Counter

# ---------------------------------------------------------------------------
# 1. Role inference
# ---------------------------------------------------------------------------

# (role, keyword alternatives). Order matters: first match wins.
_ROLE_KEYWORDS = [
    ("root", ["root", "hipsroot", "pelvisroot", "reference", "world"]),
    ("pelvis", ["pelvis", "hips", "hip", "crotch"]),
    ("spine", ["spine", "lowerback", "back", "waist", "abdomen", "belly"]),
    ("chest", ["chest", "thorax", "upperback", "ribcage", "torso"]),
    ("neck", ["neck", "throat"]),
    ("head", ["head", "skull", "face", "jaw", "crown"]),
    ("clavicle", ["clavicle", "collarbone", "shoulder"]),
    # NOTE: order matters -- "forearm" is checked before bare "arm" so that
    # Tekken-style "LeftArm" (upper arm) vs "LeftForeArm" resolve correctly.
    ("forearm", ["forearm", "lowerarm", "lower_arm", "elbow"]),
    ("upper_arm", ["upperarm", "upper_arm", "armupper", "bicep", "arm"]),
    ("hand", ["hand", "wrist", "palm", "fist", "finger", "claw", "paw"]),
    # NOTE: "upleg" (thigh) checked before bare "leg" (shin) so Tekken-style
    # "LeftUpLeg" vs "LeftLeg" resolve correctly.
    ("thigh", ["thigh", "upperleg", "upper_leg", "legupper", "upleg"]),
    ("shin", ["shin", "lowerleg", "lower_leg", "calf", "knee", "leglower", "leg"]),
    ("foot", ["foot", "ankle", "heel", "pawfoot"]),
    ("toe", ["toe", "toebase", "ball"]),
    ("tail", ["tail"]),
    ("wing", ["wing"]),
    ("ear", ["ear"]),
    ("horn", ["horn", "antler"]),
]

_SIDE_PREFIX = re.compile(r"^(left|right|l|r)[_\-\.\s:]+", re.IGNORECASE)
_SIDE_SUFFIX = re.compile(r"[_\-\.\s:]+(left|right|l|r)$", re.IGNORECASE)
_SIDE_INFIX = re.compile(r"(left|right)", re.IGNORECASE)


def _normalize(name):
    n = name.strip()
    n = re.sub(r"[\s\-_\.]+", "", n)
    return n.lower()


def detect_side(name):
    """Return 'left', 'right', or None for a joint name."""
    m = _SIDE_PREFIX.match(name) or _SIDE_SUFFIX.search(name)
    if m:
        s = m.group(1).lower()
        return "left" if s in ("left", "l") else "right"
    m = _SIDE_INFIX.search(name)
    if m:
        return m.group(1).lower()
    return None


def infer_role(name):
    """Infer (role, side) for a joint name. role may be None if unknown."""
    norm = _normalize(name)
    side = detect_side(name)
    for role, keywords in _ROLE_KEYWORDS:
        for kw in keywords:
            if kw in norm:
                return role, side
    return None, side


# ---------------------------------------------------------------------------
# 2. Description protocol (paper Table 11 style, taxonomic-neutral)
# ---------------------------------------------------------------------------

_ROLE_DESCRIPTIONS = {
    "root": "the body root anchor, overall position and facing reference",
    "pelvis": "the pelvis and hip root anchor",
    "spine": "a lower spine bone segment",
    "chest": "the chest and thorax segment",
    "neck": "the neck segment connecting torso to head",
    "head": "the head segment",
    "clavicle": "the {side} shoulder clavicle bone",
    "upper_arm": "the {side} upper arm bone",
    "forearm": "the {side} forearm bone",
    "hand": "the {side} hand segment",
    "thigh": "the {side} upper leg thigh bone",
    "shin": "the {side} lower leg calf bone",
    "foot": "the {side} foot segment",
    "toe": "the {side} toes tip",
    "tail": "a tail segment",
    "wing": "a wing segment",
    "ear": "an ear segment",
    "horn": "a horn segment",
}

_SIDE_WORD = {"left": "left", "right": "right", None: ""}


def describe_joint(name, depth=0, is_leaf=False, n_children=0, chain_len=1):
    """Functional description for a joint.

    Known roles get the protocol description (paper Table 11 pattern).
    Unknown joints get a structural description from graph position -- the
    paper's structural-generalization fallback, keeping novel creature
    joints (extra arms, tails, wings) semantically grounded instead of
    unmapped.
    """
    role, side = infer_role(name)
    if role is not None:
        template = _ROLE_DESCRIPTIONS[role]
        side_word = _SIDE_WORD[side]
        desc = template.format(side=side_word).replace("  ", " ").strip()
        return desc
    # Structural fallback: taxonomic-neutral, position-based.
    pos = "terminal" if is_leaf else ("branching" if n_children > 1 else "intermediate")
    side_word = _SIDE_WORD[side]
    where = f"on the {side_word} side " if side_word else ""
    return (
        f"an unnamed {pos} skeletal segment {where}at hierarchy depth {depth} "
        f"of an articulated chain of length {chain_len}"
    )


# ---------------------------------------------------------------------------
# 3. Embeddings
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z]+")


def _tokenize(text):
    return _TOKEN_RE.findall(text.lower())


class ProtocolEmbedder:
    """Deterministic TF-IDF embedding over the description-protocol vocabulary.

    Offline stand-in for the paper's frozen T5 encoder. IDF down-weights
    glue words ("the", "bone", "segment") so functional words ("clavicle",
    "thigh", "anchor") dominate -- descriptions that share functional
    words get high cosine similarity, which is exactly what drives
    cross-topology alignment.
    """

    def __init__(self, descriptions):
        self.n_docs = len(descriptions)
        df = Counter()
        for d in descriptions:
            df.update(set(_tokenize(d)))
        self.vocab = sorted(df)
        self.index = {w: i for i, w in enumerate(self.vocab)}
        self.idf = {
            w: math.log(self.n_docs / max(c, 1)) for w, c in df.items()
        }

    def embed(self, description):
        vec = [0.0] * len(self.vocab)
        counts = Counter(_tokenize(description))
        for w, c in counts.items():
            if w in self.index:
                vec[self.index[w]] = (1.0 + math.log(c)) * self.idf[w]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def _try_hf_embedder(descriptions):
    """Optional HuggingFace backend (closer to the paper's T5 embeddings)."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    class _HF:
        def embed(self, description):
            v = model.encode(description, normalize_embeddings=True)
            return [float(x) for x in v]

    # Warm the model once so failures surface here, not mid-retarget.
    _HF().embed(descriptions[0])
    return _HF()


def make_embedder(descriptions):
    """Pick the embedding backend.

    SEMRET_EMBED=hf selects the HuggingFace sentence-transformer backend
    (needs `sentence-transformers` installed + model download). Default is
    the offline deterministic protocol embedder.
    """
    if os.environ.get("SEMRET_EMBED", "").lower() == "hf":
        emb = _try_hf_embedder(descriptions)
        if emb is not None:
            return emb, "hf/all-MiniLM-L6-v2"
    return ProtocolEmbedder(descriptions), "protocol-tf/offline"
