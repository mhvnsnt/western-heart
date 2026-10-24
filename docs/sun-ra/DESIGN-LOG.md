# SUN RĀ — Design Log (LANE D, Round-2)

Worker: LANE D replacement (predecessor killed by daemon restart 2026-10-18; nothing had been pushed — verified no `r2/sun-ra` on origin, no PRs — started fresh).
Branch: `r2/sun-ra` from origin/main.
Work area: `game/assets/models/sun-ra*`, `docs/sun-ra/**` only. No roster wiring until the owner approves the look.

## Canon (CANON.md, owner-directed 2026-10-13)
- Sun Rā = final boss. "Not a fighter. A realm." The Soul-Eating Sun; Shao Kahn as a cute evil sun.
- Pac-Man base (owner: Pac-Man-style round base; he believed the model lived in a Tekken game).
- Runs 不死クォンバット ("Immortal Qombat" — only HE says the English version) death tournaments in his pocket realm; souls fight to the death for their souls; losers become part of him.
- Element: Fire — but a *wrong*, consuming fire. Body: "the round, cute, evil sun — the least threatening shape for the most threatening appetite."
- Mind: showman-tyrant (Shao Kahn arena logic × Malakor hunger, wearing a smile).
- Name: SUN + ラー (Rā, Egyptian sun god in Japanese).

## Owner's sculpt direction (this lane)
Start from a PAC-MAN-style round base, then build UP into "the round, cute, evil sun" — a FUSION (not a copy) of:
1. the sun guy + the moon from Soul Eater,
2. Bobobo-bo Bo-bobo energy (afro guy, nostril hairs, little son guy, water guy).
Cute + round + evil. Milestone renders (360° turntable, white-void) go to the owner for art direction BEFORE anything is finalized.

## Pac-Man verification — TEKKEN 7, not T6
- Searched `~/workspace/agent-ops/worktrees/wrestling-teardown/tekken7/models/` → found `pac-man/` containing `pac-man-t7-modelrip.zip` (4.8MB) — a T7 Pac-Man character rip (DAE + PKU.png + PKU_face.png, both 1024² RGBA). Pac-Man was a guest fighter in **Tekken 7**; he never appeared in Tekken 6 (no Pac-Man in any T6 material — T6 predates the guest).
- Rip structure: 24 skinned geometries (47.6k tris). The BODY is stored as 8 mouth-variant meshes (`Mouth_A`…`Mouth_H`, ~4.0–4.6k tris each) — Pac-Man's round body morphs per mouth shape. Bind-shape matrix is a uniform 80× scale; scaled body ≈ 6.4-unit sphere centered ~z=6.4.
- Blender 4.0.2 has NO Collada import (addon removed in 4.0), so the DAE is converted with the real `pycollada` library: bind-space verts ×80, UVs preserved, quads/ngons fan-triangulated → OBJ → Blender.
- License: Tekken 7 assets are Bandai Namco proprietary. Per house practice (steal-like-an-artist: study and reverse-engineer, never copy/redistribute/sell; proprietary renames logged), the rip is used ONLY as a sculpt base, heavily transformed into an original character. No T7 textures ship in the final model.

## Fusion design (Milestone 1 target)
- **Body:** Pac-Man T7 round body (neutral mouth variant) → re-skinned as a sun: warm gold-orange gradient, subtle surface noise so it reads as plasma, not plastic.
- **Soul Eater sun motif:** ring of sharp triangular rays around the sphere (stylized, evil-sharp — NOT a copy of the anime design).
- **Soul Eater moon motif:** pale crescent mark on the body's dark side (the moon's calm-creepy counterpoint); half-lidded eyes.
- **Face:** cute-but-evil — big glossy eyes + huge jagged grin (soul-eater's grin energy, original geometry).
- **Bobobo energy:** dark afro puff (the afro guy), exaggerated nostril-hair spikes (wacky), and a tiny orbiting "little son" mini-sun companion.
- Everything procedural in Blender 4.0.2 (headless, xvfb). No hand-drawn textures; vertex colors + procedural materials.

## Milestones
- M1: base body + rays + face + afro, white-void turntable MP4 + stills → OWNER REVIEW.
- M2 (after his notes): refine, companion mini-sun, final GLB.

## Checkpoint notes
- 2026-10-18: shared clone `~/workspace/western-heart` checkout is unusable (sibling lanes' `git checkout -b` processes hold it; full-tree checkout takes 40+ min). Working in sparse/partial lane clone `~/workspace/lanes/sun-ra` (depth-1, blob:none) on `r2/sun-ra`.
- /tmp is wiped on daemon restarts — all scratch lives in `~/workspace/_sunra-scratch/`.
