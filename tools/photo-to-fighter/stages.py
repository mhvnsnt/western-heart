"""
Photo-to-fighter stage I/O contracts.

Pipeline: IntakeSpec -> SplatAvatar (AdaHuman 3DGS) -> GameMesh
(3DGS->mesh) -> RiggedFighter (UniRig) -> TexturedFighter
-> PhotoFighter (assembly + optional GAIA head pass).

Each stage validates its own inputs/outputs so a backend can be swapped
(real GPU service <-> stub) without changing the orchestration.
CPU-only, std-lib + numpy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


class StageError(ValueError):
    """Raised when stage data violates its contract."""


# ---------------------------------------------------------------------------
# Stage 0: intake
# ---------------------------------------------------------------------------

@dataclass
class IntakeSpec:
    """Validated photo intake for one avatar."""

    photo_path: str
    width_px: int
    height_px: int
    subject_is_adult: bool
    consent_record_id: str  # likeness_policy.log_likeness_record() id
    face_source: str = "own"  # "own" | "ai-generated"

    def validate(self) -> "IntakeSpec":
        if not self.photo_path:
            raise StageError("photo_path required")
        if self.width_px < 1024 or self.height_px < 1024:
            raise StageError(
                f"photo {self.width_px}x{self.height_px} below 1024px minimum"
            )
        if not self.subject_is_adult:
            raise StageError("adult gate: subject must be an adult (ALL CHARACTERS ARE ADULTS)")
        if not self.consent_record_id:
            raise StageError("consent gate: no likeness consent record")
        if self.face_source not in ("own", "ai-generated"):
            raise StageError(f"face_source {self.face_source!r} not allowed")
        return self


# ---------------------------------------------------------------------------
# Stage 1: AdaHuman -> A-pose 3D Gaussian splats
# ---------------------------------------------------------------------------

@dataclass
class SplatAvatar:
    """AdaHuman output: A-pose 3DGS avatar."""

    splat_count: int
    a_pose: bool
    bounds_m: tuple  # (min_xyz, max_xyz) in meters
    preview_views: List[str] = field(default_factory=list)

    def validate(self) -> "SplatAvatar":
        if self.splat_count < 10_000:
            raise StageError(f"splat_count {self.splat_count} implausibly low")
        if not self.a_pose:
            raise StageError("AdaHuman output must be standardized A-pose for rigging")
        (lo, hi) = self.bounds_m
        height = hi[1] - lo[1]
        if not (1.2 <= height <= 2.4):
            raise StageError(f"avatar height {height:.2f}m outside human range")
        return self


# ---------------------------------------------------------------------------
# Stage 2: 3DGS -> mesh
# ---------------------------------------------------------------------------

MESH_METHODS = ("sugar", "2dgs", "gof", "mvs-fallback")


@dataclass
class GameMesh:
    """Watertight mesh extracted from splats, scaled to WH proportions."""

    vertex_count: int
    triangle_count: int
    watertight: bool
    method: str
    height_m: float

    def validate(self) -> "GameMesh":
        if self.method not in MESH_METHODS:
            raise StageError(f"unknown mesh method {self.method!r}")
        if not self.watertight:
            raise StageError("mesh must be watertight before rigging")
        if self.vertex_count < 1_000:
            raise StageError(f"vertex_count {self.vertex_count} implausibly low")
        if not (1.2 <= self.height_m <= 2.4):
            raise StageError(f"mesh height {self.height_m:.2f}m outside human range")
        return self


# ---------------------------------------------------------------------------
# Stage 3: auto-rig (UniRig) -> WH skeleton
# ---------------------------------------------------------------------------

# Minimal WH humanoid skeleton contract the rigger must satisfy.
REQUIRED_BONES = [
    "pelvis", "spine1", "spine2", "neck", "head",
    "l_collar", "r_collar", "l_shoulder", "r_shoulder",
    "l_elbow", "r_elbow", "l_wrist", "r_wrist",
    "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle",
]


@dataclass
class RiggedFighter:
    """Mesh + skeleton + skinning weights, playable-gate validated."""

    bones: List[str]
    skinning_weights: np.ndarray  # (n_verts, n_bones), rows sum to 1
    rigger: str = "unirig"

    def validate(self) -> "RiggedFighter":
        missing = [b for b in REQUIRED_BONES if b not in self.bones]
        if missing:
            raise StageError(f"rig missing required bones: {missing}")
        w = np.asarray(self.skinning_weights, dtype=np.float64)
        if w.ndim != 2 or w.shape[1] != len(self.bones):
            raise StageError(f"skinning weights shape {w.shape} != (n_verts, {len(self.bones)})")
        if not np.all(np.isfinite(w)) or np.any(w < -1e-6):
            raise StageError("skinning weights contain NaN/inf/negative")
        row_sums = w.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=1e-3):
            raise StageError("skinning weight rows must sum to 1")
        return self


# ---------------------------------------------------------------------------
# Stage 4: texture bake (WWE-style photo projection + PBR)
# ---------------------------------------------------------------------------

REQUIRED_MAPS = ("albedo", "normal", "roughness")


@dataclass
class TexturedFighter:
    """PBR texture set for the fighter."""

    maps: Dict[str, str]  # map name -> file path
    uv_regions: List[str] = field(default_factory=list)

    def validate(self) -> "TexturedFighter":
        missing = [m for m in REQUIRED_MAPS if m not in self.maps]
        if missing:
            raise StageError(f"texture set incomplete, missing: {missing}")
        return self


# ---------------------------------------------------------------------------
# Stage 5/6: assembly (+ optional GAIA head pass)
# ---------------------------------------------------------------------------

@dataclass
class GaiaHeadPass:
    """Identity-locked expression library from the GAIA head stage."""

    identity_latent_id: str
    expressions: List[str]  # e.g. ["neutral", "intro-smirk", "win-grin", "damage-grimace"]
    blendshape_params: Dict[str, List[float]] = field(default_factory=dict)

    def validate(self) -> "GaiaHeadPass":
        if not self.identity_latent_id:
            raise StageError("GAIA head pass requires an identity latent id")
        if "neutral" not in self.expressions:
            raise StageError("expression library must include neutral")
        return self


@dataclass
class PhotoFighter:
    """Final assembled fighter ready for an attire slot."""

    fighter_id: str
    rig: RiggedFighter
    textures: TexturedFighter
    head_pass: Optional[GaiaHeadPass]
    likeness_record_id: str
    attire_slot: str = "user-1"  # photo avatars are USER attires, never defaults

    def validate(self) -> "PhotoFighter":
        if not self.fighter_id:
            raise StageError("fighter_id required")
        self.rig.validate()
        self.textures.validate()
        if self.head_pass is not None:
            self.head_pass.validate()
        if not self.likeness_record_id:
            raise StageError("likeness record required on final fighter")
        if not self.attire_slot.startswith("user-"):
            raise StageError(
                "photo fighters ship as user attires only "
                "(DISPLAY ORDER LAW: Tripo models first)"
            )
        return self
