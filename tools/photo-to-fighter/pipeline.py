"""
PhotoToFighterPipeline: orchestrates the stage contracts end-to-end.

Backends are injected: the real GPU services (AdaHuman, splat-mesher,
UniRig, texture baker, GAIA head) implement the same small interfaces as
the stubs below, so swapping is mechanical. The orchestration, gates, and
validation never change.

Stages:
  intake (likeness_policy) -> AdaHumanBackend -> MeshBackend
    -> RigBackend (UniRig) -> TextureBackend -> [GaiaHeadBackend]
    -> assembly

Std-lib + numpy. Stubs synthesize plausible outputs (seeded) — they prove
the orchestration and contracts, not the AI.
"""

from __future__ import annotations

import numpy as np

from stages import (
    GaiaHeadPass,
    GameMesh,
    IntakeSpec,
    PhotoFighter,
    RiggedFighter,
    REQUIRED_BONES,
    SplatAvatar,
    StageError,
    TexturedFighter,
)
from likeness_policy import get_record


# ---------------------------------------------------------------------------
# Backend interfaces (real services implement these)
# ---------------------------------------------------------------------------

class AdaHumanBackend:
    """Photo -> A-pose 3DGS avatar. Real impl: GPU service (see README)."""

    def generate_avatar(self, spec: IntakeSpec) -> SplatAvatar:
        raise NotImplementedError


class MeshBackend:
    """SplatAvatar -> GameMesh. Real impl: SuGaR / 2DGS / GOF (see README)."""

    def extract_mesh(self, avatar: SplatAvatar) -> GameMesh:
        raise NotImplementedError


class RigBackend:
    """GameMesh -> RiggedFighter. Real impl: tools/auto_rig/ (UniRig, MIT)."""

    def rig(self, mesh: GameMesh) -> RiggedFighter:
        raise NotImplementedError


class TextureBackend:
    """(GameMesh, IntakeSpec) -> TexturedFighter. Real impl: tools/texture-pipe/."""

    def bake(self, mesh: GameMesh, spec: IntakeSpec) -> TexturedFighter:
        raise NotImplementedError


class GaiaHeadBackend:
    """Optional head pass: identity-locked expressions. Real impl: Phase 3."""

    def edit_head(self, fighter: PhotoFighter) -> GaiaHeadPass:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Stubs (plumbing only — synthetic, seeded outputs)
# ---------------------------------------------------------------------------

class StubAdaHuman(AdaHumanBackend):
    def generate_avatar(self, spec: IntakeSpec) -> SplatAvatar:
        return SplatAvatar(
            splat_count=120_000,
            a_pose=True,
            bounds_m=((0.0, 0.0, 0.0), (0.6, 1.8, 0.4)),
            preview_views=["front", "side", "back"],
        ).validate()


class StubMesher(MeshBackend):
    def extract_mesh(self, avatar: SplatAvatar) -> GameMesh:
        avatar.validate()
        return GameMesh(
            vertex_count=25_000,
            triangle_count=50_000,
            watertight=True,
            method="sugar",
            height_m=1.8,
        ).validate()


class StubRigger(RigBackend):
    def rig(self, mesh: GameMesh) -> RiggedFighter:
        mesh.validate()
        n_verts = 100  # synthetic skinning table shape for contract tests
        bones = list(REQUIRED_BONES)
        rng = np.random.default_rng(11)
        w = rng.random((n_verts, len(bones)))
        w = w / w.sum(axis=1, keepdims=True)
        return RiggedFighter(bones=bones, skinning_weights=w, rigger="unirig-stub").validate()


class StubTexturer(TextureBackend):
    def bake(self, mesh: GameMesh, spec: IntakeSpec) -> TexturedFighter:
        mesh.validate()
        return TexturedFighter(
            maps={
                "albedo": "avatar/albedo.png",
                "normal": "avatar/normal.png",
                "roughness": "avatar/roughness.png",
            },
            uv_regions=["face", "torso", "limbs"],
        ).validate()


class StubGaiaHead(GaiaHeadBackend):
    def edit_head(self, fighter: PhotoFighter) -> GaiaHeadPass:
        return GaiaHeadPass(
            identity_latent_id="stub-identity-001",
            expressions=["neutral", "intro-smirk", "win-grin", "damage-grimace"],
            blendshape_params={"jaw_open": [0.0, 0.2, 0.1, 0.4]},
        ).validate()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class PhotoToFighterPipeline:
    def __init__(
        self,
        adahuman: AdaHumanBackend,
        mesher: MeshBackend,
        rigger: RigBackend,
        texturer: TextureBackend,
        gaia_head: GaiaHeadBackend | None = None,
    ):
        self.adahuman = adahuman
        self.mesher = mesher
        self.rigger = rigger
        self.texturer = texturer
        self.gaia_head = gaia_head

    def run(self, spec: IntakeSpec, fighter_id: str) -> PhotoFighter:
        # Gate 0: intake contract + likeness record must exist
        spec.validate()
        get_record(spec.consent_record_id)

        avatar = self.adahuman.generate_avatar(spec)
        mesh = self.mesher.extract_mesh(avatar)
        rig = self.rigger.rig(mesh)
        textures = self.texturer.bake(mesh, spec)

        fighter = PhotoFighter(
            fighter_id=fighter_id,
            rig=rig,
            textures=textures,
            head_pass=None,
            likeness_record_id=spec.consent_record_id,
            attire_slot="user-1",
        ).validate()

        # Optional GAIA head pass (Phase 3). SHOW-set expressions only;
        # the show-animation lock still governs where they may play.
        if self.gaia_head is not None:
            head_pass = self.gaia_head.edit_head(fighter)
            fighter = PhotoFighter(
                fighter_id=fighter.fighter_id,
                rig=fighter.rig,
                textures=fighter.textures,
                head_pass=head_pass,
                likeness_record_id=fighter.likeness_record_id,
                attire_slot=fighter.attire_slot,
            ).validate()

        return fighter


def stub_pipeline(with_gaia_head: bool = False) -> PhotoToFighterPipeline:
    """Test/dev pipeline with all-stub backends."""
    return PhotoToFighterPipeline(
        adahuman=StubAdaHuman(),
        mesher=StubMesher(),
        rigger=StubRigger(),
        texturer=StubTexturer(),
        gaia_head=StubGaiaHead() if with_gaia_head else None,
    )
