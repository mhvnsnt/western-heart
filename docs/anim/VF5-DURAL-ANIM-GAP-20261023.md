# Dural (VF5) motion — precise gap for Zen's permanent base (2026-10-23)

**Owner directive (2026-10-22, standing): Zen's PERMANENT BASE MIX is
Dural (Virtua Fighter 5) — the chrome humanoid base layer; Dural's stance
is Zen's stance. Stacked on top: Twelve's moves (N.D.L., A.X.E., D.R.A.,
X.FLAT) + X.COPY as ONE super, NOT his identity, plus Zen's canon stand
attacks, Tentacle Mode, Oversoul, transformation, and spirit-form stand.**

**The two sources are NEVER mixed in one moveset.** Heihachi-derived
moves (T3/T7/T8 pulls, all tagged as such in `game/assets/movesets/zen.json`)
are the interim kit. The Dural base is filed here as PENDING — a separate
extraction lane. When Dural motion lands, it becomes the base layer and
the Heihachi kit is re-evaluated against it; nothing is silently blended.

## The gap

**VF5 motion data was never converted.** The VF5 teardown has model data
only — no motion/animation extraction exists on disk. Dural's stance,
idle, strikes, and movement are therefore entirely absent. This is the
single biggest blocker on Zen's permanent base.

## What the extraction lane must produce

1. **VF5 motion format RE** — Sega's VF5 animation format reverse-engineered
   (no plaintext docs on disk; the VF5 model extraction is the starting
   reference).
2. **Dural motion set** — stance/idle (THE base stance per the directive),
   strikes, blocks, hits, KO, locomotion, Twelve-move conversions
   (N.D.L., A.X.E., D.R.A., X.FLAT as 3D conversions from 2D sprite data —
   separate hard problem, tracked here as a dependency).
3. **Conversion to wh-anim/1** — baked through the same pipeline as the T3
   banks (`tools/anim/`), landing at `game/assets/anim/vf5/dural/` with
   `skeleton.json` + `rows.pack.json`.
4. **Wiring** — registered in the anim bank table; `bankIdFor('zen')`
   binds `dural` when the base layer activates.

## FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

- **FIGHT** — Dural base stance/idle, strikes, Twelve-move conversions →
  Zen's combat bank and moveset (as the base layer).
- **SHOW** — Dural's intro/win presentation, transformation sequences →
  intro/win slots and cutscenes ONLY. SHOW clips must NEVER enter Zen's
  moveset without the user's explicit approval.

## Interim status (this pull, 2026-10-23)

- `game/assets/movesets/zen.json`: 639 moves. Heihachi kit verified
  COMPLETE: T8 Heihachi 145/145 by `t8_id`
  (`docs/t7t8-reference/frame-data-t8-full/heihachi.json`), plus 307 T3
  Heihachi and 183 T7 rows. **0 Heihachi gaps — nothing added by this
  lane.**
- `anim_set_lock` stamped at file level, explicitly noting the Dural
  base is pending and the sources are not mixed.
- T3 Heihachi bank (`game/assets/anim/t3/heihachi_on_jin/`) remains
  Zen's bound motion bank until the Dural lane lands.

## Dependencies (other lanes)

- Twelve 2D sprite → 3D conversion (blocked; needs its own RE lane).
- Eleven from SFV pull (blocked pending SFV download).
- VF5 model extraction exists; motion is the missing half.
