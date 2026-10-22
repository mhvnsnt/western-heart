# DOC FRANK — Attire Slots (owner 2026-10-19; ladder reorder 2026-10-21; owner override 2026-10-21 ~23:14 CDT; Tripo-forefront + full rigging 2026-10-21 late)

## Ladder rule (owner override 2026-10-21 ~23:14 CDT, verbatim)

> "his 1, 2, 3, 4, 5 should be his Tripo models; the Tekken reskins go toward
> the back, not 1 or 2. Stop showing me the Tekken versions first — show the
> Tripo 3D models I made for him."

Doc Frank's **Tripo models lead picker slots 1–5+**; the **Tekken-based
models go toward the back** — never slot 1 or 2, never the default. This
supersedes the 2026-10-21 ~19:08 CDT ladder rule, which had put Attire 1's
pre-form old man (`doc-frank-a1`) at the forefront: its file lineage is the
PR #263 machine-shop texture reskin of the Bosconovitch base (a Tekken
reskin, not a Tripo model), so the owner moved it back with the other
Tekken-based models. The Dr. Bosconovitch base model and all
retextures/reskins ladder **BACK** behind every Tripo model.

Every Tripo form is **rigged** (owner standing rule 2026-10-21 ~23:01 CDT: a Tripo model gets rigged to its character's rig on intake, automatically — no unrigged statues).

## Presentation order (the picker ladder, `ATTIRE_VARIANTS['docfrank']`)

| Picker # | Key | Provenance | Rig |
|----------|-----|------------|-----|
| 1 (DEFAULT) | `doc-frank-big` — Attire 1 · Transformed | **Tripo** 2c6cff79 (597c67b3 pull) | ✅ rigged 2026-10-21 (this PR) |
| 2 | `doc-frank-wowomomo` — Attire 2 · Wowomomo | **Tripo** 84b128d2 | ✅ rigged (Lane 4 batch 3, PR #478; binds normalized this PR) |
| 3 | `doc-frank-wowomomo-big` — Attire 2 · Wowomomo XL | **Tripo** | ✅ rigged 2026-10-21 (this PR) |
| 4 | `doc-frank-hood` — Attire 3 · Hood Scientist | **Tripo** f40c7cde | ✅ rigged (73 joints; binds normalized in PR #465) |
| 5 | `doc-frank-hood-big` — Attire 3 · Hood XL | **Tripo** | ✅ rigged 2026-10-21 (this PR) |
| 6 | `doc-frank-frankenstein` — Attire 4 · Frankenstein's Cyborg | **Tripo** 2bea6cac | ✅ rigged (Lane 4 batch 3, PR #478; binds normalized this PR) |
| 7 | `doc-frank-frankenstein-big` — Attire 4 · Frankenstein XL | **Tripo** 690d28a2 | ✅ rigged 2026-10-21 (this PR) |
| 8 | `doc-frank-a1` — Attire 1 · Old Man (pre-form) | Reskin-lineage GLB (see provenance notes) | ✅ rigged (178 joints; binds normalized in PR #465) |
| 9 | `doc-frank` — Bosconovitch Base | **Tekken base** | ✅ rigged (178 joints) |
| 10 | `doc-frank-machine-shop` — Machine Shop | **Reskin / retexture** of the base | ✅ rigged (178 joints) |

The main `docfrank` roster entry's model is `doc-frank-big`, and
`selectedAttireModel()` resolves the picker default to ladder entry 1 —
both surfaces default to the Tripo transformed form.

## Attires (two-form, transform pairs)

| Attire | Forms | Transform |
|--------|-------|-----------|
| 1 — Old Man / Transformed | pre-form `attire1/pre-transform/model.glb` (key `doc-frank-a1`) ↔ transformed `attire1/post-transform/model-rigged.glb` (key `doc-frank-big`, **Tripo**) | Main-entry forms map: pre-form transforms UP to `doc-frank-big` (+40% power, −12% speed, +15% defense, bodyScale 1.18); the Tripo form transforms DOWN back to the pre-form. TRANSFORM touch button (down = tap while crouching). |
| 2 — Wowomomo / Transformed | base `attire2/base/model-rigged.glb` (key `doc-frank-wowomomo`, Tripo villain, glass dome helmet, W emblem) ↔ transformed `attire2/transformed/model-rigged.glb` (key `doc-frank-wowomomo-big`, Tripo, bigger brain-dome) | Own roster entry transform → `doc-frank-wowomomo-big`. Canon: Dr gero meets mojo Jojo meets bosconovitch meets Dr wierd. |
| 3 — Hood Scientist / Transformed | base `attire3/base/model.glb` (key `doc-frank-hood`, Tripo f40c7cde — elderly scientist in suit, club-night look) ↔ transformed `attire3/transformed/model-rigged.glb` (key `doc-frank-hood-big`, Tripo — massive muscular form, jacket burst off Roshi-style) | Own roster entry transform → `doc-frank-hood-big`. |
| 4 — Frankenstein's Cyborg / Transformed | base `attire4/base/model-rigged.glb` (key `doc-frank-frankenstein`, Tripo 2bea6cac) ↔ transformed `attire4/transformed/model-rigged.glb` (key `doc-frank-frankenstein-big`, Tripo 690d28a2) | Own roster entry transform → `doc-frank-frankenstein-big`. |
| — Bosconovitch Base (ladder-back) | `game/assets/models/doc-frank.glb` (key `doc-frank`) | The Dr. Bosconovitch base attire. NOT a default; a ladder-back alternate, same as every other character's Tekken base. |
| — Machine Shop (ladder-back) | `attires/machine-shop/doc-frank-machine-shop-rigged.glb` (key `doc-frank-machine-shop`) | Texture reskin of the base model — 5 embedded PNGs swapped, no rig or geometry changes (PR #263). NOT a Tripo model and NOT a default. Also has its own roster entry. |

Original Tripo `model.glb` files are never modified: each rigged build
lands beside its original as `model-rigged.glb`, and MODEL_URLS points at
the rigged file.

## Provenance notes (read before naming any model's origin)

- Attire 1's pre-form GLB (`attire1/pre-transform/model.glb`) is
  byte-identical to `attires/machine-shop/doc-frank-machine-shop.glb`
  (sha256 55e1f8578a78…): the PR #263 reskin file was adopted as Attire
  1's old-man form. Its file lineage is the reskin — do not call it a
  Tripo model, and do not present it (or the base, or Machine Shop) as
  Doc Frank's forefront.
- **No genuine Tripo old-man pre-form exists.** Registry/release audit
  2026-10-21 (this PR): Doc Frank's Tripo pulls on record are the
  transformed form (597c67b3), Wowomomo (84b128d2), Hood Scientist
  (f40c7cde) and Frankenstein pair (2bea6cac / 690d28a2) — no Tripo
  old-man pre-transform pull was ever recorded. If the owner makes one,
  it wires in as Attire 1's pre-form in place of the reskin-lineage file.
- Rig state (verified 2026-10-22 by GLB skin scan): ALL forms rigged.
  Pre-form 178 joints, Hood base 73 joints, Wowomomo + Frankenstein
  bases 49 joints (Lane 4 batch 3). The four transformed forms are
  rigged onto **Doc Frank's own Bosconovitch skeleton (178 joints —
  the skeleton of the pre-form/base and of the animation bank
  itself)**, via the repo's k-NN transfer path
  (`tools/auto_rig/backends/knn_transfer.py` + `apply_skin.py` — the
  PR #264 dense-static path; the GameRig/Blender intake OOM-killed on
  these ~1M-vert meshes on the current VM). `apply_skin.py` was
  generalized in this PR to accept any donor rig (it previously
  copied only the donor's first 50 nodes, a Pantera-layout
  assumption; regression-verified byte-identical output on the
  canonical path). Why the Bosconovitch rig: an earlier build of the
  four forms on the 49-joint GameRig-template skeleton deformed
  correctly at rest but folded under the game's bank retarget —
  control-proven in the game's own render path (the Lane 4 base on
  the same template folds identically; the 178-joint pre-form renders
  the same stance clean). On the Bosconovitch skeleton the four
  forms pose-measure identically to the shipped pre-form
  (headAboveHips 0.48, toes +Z) with zero outlier vertex displacement
  in the audit (see `docs/proof/docfrank-rig-forefront-20261021/`).
  All shipped Doc Frank GLBs carry all-identity bind locals (the
  PR #465 standard): the batch-3 base rigs arrived with 7
  pose-encoded binds each (Hips 180°, shoulders, up-legs, feet) and
  were normalized in this PR with the bind-fix tools (bind-pose
  skinning invariance verified to 4.5e-08).
  KNOWN FOLLOW-UP (not this PR's files): the Lane 4 Wowomomo and
  Frankenstein BASE rigs ride the same 49-joint template and fold
  under bank retarget the same way; they should be re-rigged onto
  the Bosconovitch skeleton with this same path.

## Slot-ordering law

- The forefront is Tripo-only: picker entries 1–7 are his Tripo models,
  entry 1 (the default) is Attire 1's Tripo transformed form.
- The reskin-lineage pre-form, the Tekken base attire and reskins
  ladder behind the Tripo forms (owner rule 2026-10-21 ~22:55 CDT).

## History

- 2026-10-19: Owner shared the bigger-form Tripo link in chat ("he can
  transform mid match... like master roshi from dbz"). Both forms wired as
  Attire 1 + generic transform mechanic implemented in `game/js/`.
- 2026-10-19: Attire 2 "Wowomomo" wired (base + transformed, both Tripo). Attire 3 "Hood scientist" wired (base + transformed, both Tripo). All attires transform mid-match.
- 2026-10-21: Ladder reorder (owner correction ~19:08 CDT, PR #483). Before: picker
  slot 1 was the Bosconovitch base GLB ("BASE"), the main roster entry's
  model was the machine-shop reskin, and Attire 1's own pre-form GLB had
  no MODEL_URLS key at all. After: `doc-frank-a1` key added, Tripo pairs
  forefront, base + reskin ladder back.
- 2026-10-21 (~23:14 CDT): Owner override (verbatim): "his 1, 2, 3, 4, 5
  should be his Tripo models; the Tekken reskins go toward the back, not 1
  or 2. Stop showing me the Tekken versions first." The ~19:08 rule had put
  the old-man pre-form (a Tekken reskin by file lineage) at the forefront,
  so the user was still seeing a Tekken version first. Fix: all seven Tripo
  models lead the picker (slots 1–7), `doc-frank-a1` old man moves to the
  back with the Tekken base + Machine Shop reskin (slots 8–10); main
  `docfrank` entry model → `doc-frank-big` (matches the picker default).
  Reorder only — every model stays reachable.
- 2026-10-21 (late): Owner restated the forefront rule hard (~22:55 CDT:
  attires 1–5 = his Tripo models, reskins to the back, stop showing the
  reskin models) + the auto-rig-on-intake standing rule (~23:01 CDT).
  This PR: picker leads with the Tripo transformed form as the resolved
  default, pre-form/base/reskin move to picker slots 8–10, the
  unrigged Tripo transformed forms rigged (Attires 1–3 onto the
  178-joint Bosconovitch skeleton; Attire 4 XL onto the 49-joint
  template after its Bosconovitch weight field failed the pose
  gate on the forearms/cables — follow-up, see PROOF.md), batch-3
  base rigs bind-normalized.
