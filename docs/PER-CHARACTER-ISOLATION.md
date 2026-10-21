# PER-CHARACTER ISOLATION — the pose/animation gate

**Owner law, 2026-10-20 (verbatim core):** "The extra arms for Dxmmii, the
jiggle bones, the wings, extra wrists/hands — those are PER CHARACTER, added
onto that character's own already-working Tekken skeleton and animations…
A two-armed character should never start acting like the four-armed
character. Their stuff is separated, per character."

**Refinement (owner, 2026-10-20):** per-character work must be GATED so an
edit for one character cannot leak into another — *unless it actually
parallels*. Characters built on the same Tekken source share what truly
parallels, **through the shared source data, deliberately**. An edit made
for one character must never bleed into another character's files or state
as a side effect. Structure per-character data the way Tekken's own
developers do (per-character files in the teardown data), not by
hand-tooling shared state.

This document is the gate. Every lane that touches models, rigs, or
animation reads it first.

---

## 1. The golden architecture (2026-10-14/15 — restore target)

When Pantera was first modded in, he moved **exactly like King**: King's
real decoded Tekken 3 motion, baked onto Pantera's own skeleton
(`lab/tools/t3_motion_bake.py`, commits `124c03c` + `9bab504`, bank dir
`king_on_pantera_leoman/`). That is the pattern for every character:

- **Motion comes from the character's Tekken source**, decoded from the
  teardown — never hand-authored pose values, never another character's
  clips.
- Each fighter's animation bank lives in **its own directory**
  (`game/assets/anim/t3/<source>/`), mirroring Tekken's own per-character
  file layout in the teardown data.
- The fighter's **own model file** carries its own skeleton, skin, and
  embedded clips. Additions (extra arms, wings, jiggle, extra hands) are
  built **on that character's own skeleton**, in that character's own
  files.

## 2. The gate — where data is allowed to live

| Data | Lives in | Shared? |
|---|---|---|
| Skinned model + skeleton + skin weights | The character's own GLB (`roster/<char>/…` or `game/assets/models/<char>.glb`) | **Never.** Editing it affects that character only. |
| Tekken motion bank (stance/attacks/walk) | `game/assets/anim/t3/<moveset-source>/` | **By design, through the source.** Fighters whose moveset source is the same Tekken character share the bank *because they parallel* (e.g. every King-source fighter reads the `king` bank). |
| Moveset data (inputs, damage, frame data) | `game/assets/movesets/<char>.json`, `game/assets/<source>_moves.json` | Per character / per source. |
| Per-character additions (Dxmmii's arms, wings, jiggle, transforms) | That character's own directory + that character's own model file | **Never.** A two-armed character must never gain four-armed behavior. |
| Engine code (`fighter.js`, `assets.js`, `t3anims.js`, `main.js`) | `game/js/` | Shared **plumbing only**. A shared-code change must be *data-neutral*: it may wire/discover/route per-character data, it must never inject one character's data, pose values, or rig assumptions into another character. |

### Hard rules

1. **No mass in-place model rewrites.** A commit that rewrites many
   characters' GLBs at once (e.g. PR #264's 41-file "re-rig wave") is
   forbidden. Rig/repair work lands **one character at a time**, as a
   **new file in that character's own directory**, with the model's entry
   in `assets.js` `MODEL_URLS` repointed at it. The original file stays.
2. **Restore-from-source only.** If a stance/pose is wrong, the fix is to
   re-derive it from the character's Tekken source data (teardown banks,
   the model's own embedded clips). Hand-tweaked pose numbers are not a
   fix — if a character seems to need them, stop and report instead.
3. **Banks bind by moveset source, always.** `bankIdFor(charId, movesetId)`
   in `fighter.js` is the only routing. There is no default bank: a
   fighter whose source has no decoded bank gets **no** bank — never
   another character's (this was the pre-#369 bug: every fighter played
   the King bank).
4. **Clip/bone names are canonical.** Banks use the canonical 22-bone
   Mixamo names. Name canonicalization (e.g. the bake's `Chest` →
   `Spine2`) happens in `t3anims.js` clip construction — once, for every
   bank equally — never by editing a character's skeleton to match a clip.
5. **Statues don't ship as fighters.** A model with no skin/skeleton
   cannot idle, stance, or fight. Unrigged Tripo/figurine exports must go
   through the auto-rig pipeline (`tools/auto_rig/`, heat backend) into
   the character's own directory **before** they are wired as a playable
   attire. Gate check: `tools/auto_rig/pose_gate.py`.
6. **Additions are additive.** Per-character systems (limb system,
   transforms, wings) attach to the character's own already-working
   skeleton and animations. They must be removable without touching any
   other character's files or behavior.

## 3. What broke (audit 2026-10-20, summary)

Full audit: `docs/POSE-AUDIT-2026-10-20.md`. Root causes, in order:

1. **The banks' stance clips were never played.** `fighter.js` `_animate`
   had no `idle` case — idle fell through to `_stopT3()`, so in-fight idle
   was the generic Mixamo mocap layer (or a raw T-pose / frozen statue),
   not the fighter's own Tekken stance. The select screen had the same
   gap (embedded `Idle` or rest pose only).
2. **Pre-#369, every fighter played the King bank** (`getT3Clips()`
   default). PR #369 (2026-10-20) fixed the routing per source — the
   isolation-correct direction — but idle still never called the stance.
3. **19 wired models were unrigged statues** (0 skins, 0 animations —
   raw Tripo/figurine exports), including Demonio's default Attire 1 and
   SAM-UR-A1. In game they stand frozen in their authored pose forever.
4. **Dead chest track on every bank clip:** the T3 bake named the chest
   bone `Chest`; every shipped skeleton names it `Spine2`. The track
   bound to nothing roster-wide, so all T3 motion lost its chest segment.
5. **Native idles ignored:** KOF-source models (Iori/Deathfang rig) carry
   their idle as `Battle_Idle`; the loader only registered exact `Idle`,
   so their base layer found nothing.
6. **Shared-code hazards** (kept fixed): the gyro-arms IK scratch-aliasing
   bug (#369, shared scratch vectors in the shared `Fighter` class) is the
   template for what rule 2/6 above forbids — per-fighter state must be
   per-fighter instances, never shared scratch.
7. **Non-defects verified:** Dxmmii's shipped model has **no** extra-arm
   bones (its skeleton is the standard 49-bone rig — the limb system was
   never wired into the shipped GLB, so it also never leaked); there is
   **no** jiggle code anywhere in the shipped game; Mariposa's wings are
   inside her own model files. Pantera's floating `belt2`/`buckles`
   meshes are a per-file skin defect present since the golden Oct-14 file
   (byte-identical blobs) — a Pantera-file repair item, not a regression
   and not shared.

## 4. The fix (this PR)

- `fighter.js`: `idle` state plays the fighter's **own bank stance**
  (loop); `walk` uses the bank's `walkFwd`/`walkBack` when the model has
  no embedded `Walk` of its own. Fighters without a bank are untouched.
- `main.js`: the select preview poses in the fighter's own bank stance
  when available; the procedural "breathing" fallback no longer applies
  on top of a posed fighter.
- `assets.js`: a model's own `Battle_Idle`/`Stage_Idle` clip registers as
  its `Idle` (per-model data only).
- `t3anims.js`: `Chest` → `Spine2` track canonicalization at clip build.
- Statues rigged one at a time via `tools/auto_rig` into each character's
  own `roster/<char>/…` directory as **new files**; `MODEL_URLS` repointed
  per character. Originals untouched.
- `tools/auto_rig/pose_gate.py`: the pre-flight gate — run it on any
  model before wiring it as playable.
