# POSE AUDIT — 2026-10-20

Owner complaint (2026-10-20 ~08:10 CDT): characters "posed in a weird
pose… bent over, back bent backwards, legs bent weird… not how the Tekken
games would have them," and per-character additions (Dxmmii's extra arms,
jiggle, wings, extra hands) leaking across characters.

Method: every wired model's skeleton/clips/rest-pose measured from the
files on `main`; front renders in Blender (Cycles) of every distinct
default model, viewed by the auditor; in-engine idle screenshots via the
game's own `Fighter`/`assets`/`t3anims` modules (headless Chromium) before
and after the fix. Pantera (Oct 14–15 golden state: moving exactly like
King, commits `124c03c`/`9bab504`) is the standard of correct.

## What the player actually sees (root causes)

There is no single "bent pose" file. The wrongness is composed at
runtime from five independent defects:

1. **Idle never plays the Tekken stance.** `fighter.js` `_animate` had
   no `idle` state case — idle fell to `_stopT3()`, leaving the generic
   Mixamo mocap layer (or nothing). The banks' `stance` clips — the
   fighters' real Tekken 3 stances — were loaded but never used for
   idle, in-fight or on the select screen.
2. **19 wired models are unrigged statues** (0 skins, 0 animations):
   they render frozen in their authored pose forever — they cannot
   stance, walk, or fight. Includes **Demonio's default Attire 1**,
   SAM-UR-A1, both other Demonio forms, Kronos ×2, Koreshi, Dxmmii
   Attire 2, Zangief, Blanka, Armor King, and 7 Doc Frank forms.
3. **T-pose idles.** Six canonical-rig models ship no embedded clips
   (Baek Master White, Bloodline Ember, Mariposa ×2, Dxmmii ×2): with
   no bank stance played, they stand in raw T-pose (the select screen's
   procedural "breathing" then bends the spine of a T-posed model).
4. **Dead chest track on every T3 clip.** The T3 bake named the chest
   bone `Chest`; every shipped skeleton names it `Spine2`. The track
   bound to nothing — all T3 motion lost its chest segment roster-wide.
5. **Native idles ignored.** KOF-source fighters (Iori, Deathfang)
   carry 61 native clips including `Battle_Idle`, but the loader only
   registered the exact name `Idle`, so their base layer found no idle.
6. **Split-skin garment meshes.** In the Tekken-7 part-split exports,
   garment meshes that span body regions were bound to spine bones only:
   Steve Fox's shirt (incl. both sleeves) has ZERO arm-bound verts, so
   in motion the sleeves hold the T-pose while his arms animate away —
   the "detached/extra arms" the owner saw, on the placeholder model
   ~17 roster entries share. Pantera's belt/buckles are the same class
   of defect in his own file.

Historical contamination (fixed before this audit, kept fixed): until
PR #369 (2026-10-20), **every fighter played the King bank** by default;
PR #264 (2026-10-18) rewrote 41 GLBs in place in one commit. The gyro-
arms bug was shared scratch vectors inside the shared `Fighter` class
(fixed in #369 with per-instance scratch). See
`docs/PER-CHARACTER-ISOLATION.md` for the gate that now forbids these
patterns.

**Verified non-leaks:** Dxmmii's shipped GLB contains no extra-arm bones
(standard 49-bone rig; the limb system was never wired into the shipped
model, so it never leaked — Dxmmii's problem is the opposite: its own
addition is missing and its base model idles in T-pose). No jiggle code
exists anywhere in the shipped game. Mariposa's wings are inside her own
model files.

## Per-model audit (default/wired models)

Families: **A** = 49-bone WH/Mixamo rig + embedded Idle/Walk/Run ·
**B** = same rig, no clips · **C** = 33-bone Lane-C rig, no clips ·
**D** = foreign rig · **E** = unrigged statue.

| Model | Used by | Family | Verdict |
|---|---|---|---|
| pantera.glb | Pantera + 8 entries (model field) | A | Pose OK (embedded idle). **Defect: `belt2`/`buckles` meshes float detached beside the shoulders — in Blender AND in-engine.** Present byte-identical since the golden Oct-14 file; per-file skin repair item, not a regression. |
| steve-fox.glb | ~16 entries (placeholder) | A | **Split-skin defect (proven in Blender + in-engine): the Shirt mesh — 2,246 verts including the full sleeves — is weighted 100% to Spine/Spine1, ZERO arm-bound verts. When the arm bones animate, the sleeves stay in T-pose and the real arms/gloves detach and hang beside the torso.** This is the visible "extra arms / detached hands" breakage on every fighter using this placeholder. Per-file repair: heat re-skin of the shirt mesh only (`tools/auto_rig/repair_stevefox_shirt.py`). |
| demonio.glb | Demonio Attire 2 | A | **Byte-identical duplicate of steve-fox.glb (md5 `fbb9496795a815f78d1d419a9fad8c0f`)** — Demonio has no model of his own here at all; same broken shirt. Demonio needs his own model (his attires are the statues below); reported to the Demonio lane. |
| demonio-a1.glb | **Demonio Attire 1 (default)** | E | **Frozen statue** (fierce authored standing pose). Cannot animate. → auto-rig. |
| demonio-winged.glb | Demonio attire | E | **Frozen statue** (wings are part of the statue). → auto-rig. |
| demonio-human.glb | Demonio attire | E | **Frozen statue.** → auto-rig. |
| demonio-bloodline-ember.glb | Jin / Bloodline | B | **T-pose idle.** → bank stance (jin) via fix. |
| baek-master-white.glb | Kevin A3 (parked) | B | **T-pose idle**; no bank for its source (heihachi→null) — stays rest-pose until its own source is decoded; reported, not substituted. |
| mariposa.glb / mariposa-monarch.glb | Mariposa | B | **T-pose idle**; wings inside own model ✓. Monarch has gray untextured wing/leg patches (texture defect, separate lane). No decoded bank for her source yet → reported. |
| dxmmii.glb / dxmmii-patchwork.glb | Dxmmii | B | **T-pose idle**; no extra-arm bones (limb system unwired — separate lane). No bank (mokujin undecoded) → reported. |
| dxmmii-a2.glb | Dxmmii Attire 2 | E | **Frozen statue** (one arm raised, authored). → auto-rig. |
| michiko.glb / star.glb / torch.glb | Michiko / Star / Torch | C | No clips → rest A-pose idle; Blender renders untextured white (textures are in the GLBs; in-engine they texture — verified in harness shots). Bank stance applies via fix (jin/xiaoyu/jin sources). |
| doc-frank.glb (+ machine-shop) | Doc Frank | D (178 bones, `Spine` name missing only) | T-pose rest; bank (gunjack) binds all but the `Spine` track. Stance via fix. |
| yukihyo.glb | Yukihyō | D (328 bones, canonical complete) | T-pose rest; king bank stance via fix. |
| bruno.glb | Bruno | D (missing `Spine2`+head names) | T-pose rest; bryan bank binds partially (no chest/head tracks). Reported partial. |
| dio.glb | Dio | D (174 bones, 16 canonical names missing incl. `Hips`) | **Cannot be animated by the engine at all** (no `Hips` → no T3 actions; no embedded clips). Needs its own rig repair/re-rig — reported. |
| vega.glb | (model library) | D (364 foreign-named bones) | Cannot bind canonical clips. Not a default fighter model. Reported. |
| iori.glb / deathfang.glb | Iori / Deathfang | D (79-bone KOF rig, 61 native clips) | Rest pose is Iori's authored slouch (correct for the character). `Battle_Idle` now registers as Idle via fix — proper hunched KOF stance in game. Werewolf attire file missing from repo (Deathfang lane owns the Tripo pull). |
| sam-ur-a1.glb | SAM-UR-A1 | E | **Frozen statue** (mech, authored standing pose). → auto-rig (proven: heat backend, validate PASS). |
| kronos.glb / kronos-attire2.glb | Kronos | E | **Frozen statues** (upright authored poses). → auto-rig. |
| koreshi.glb | Koreshi | E | **Frozen statue** (T-pose authored). → auto-rig. |
| zangief.glb | Zangief | E | **Frozen statue**, and the GLB includes a **figurine display pedestal** under his feet. → auto-rig (pedestal must be excluded by the rig lane — vertex-group cleanup in his own file). |
| blanka.glb | Blanka | E | **Broken file**: body parts scattered at disjoint offsets (Sketchfab conversion never assembled them) — renders as floating pieces. Needs model re-assembly from source parts before any rigging. Reported. |
| armor-king.glb | Armor King | E | **Frozen statue** (low-poly, 5.7k verts). → auto-rig candidate. |
| scimitar.glb | Scimitar (shelved) | E | **Mesh geometry mangled** (exploded cloth-like shards from every angle). Shelved per owner 2026-10-19 — reported only. |
| doc-frank wowomomo / hood / frankenstein (+ `*-big` forms) | Doc Frank attires/transforms | E | **Frozen statues** (authored poses; big forms hunched — authored Frankenstein slouch). → auto-rig. |

Missing files on `main`: `roster/ryuji-rock/attires/attire1/model.glb`
(documented model-pending), `roster/deathfang/attires/attire2/model.glb`
(Deathfang lane's werewolf Tripo, not yet landed).

## The fix

Code (data-neutral plumbing only — see the isolation doc):
- `game/js/fighter.js` — idle plays the fighter's **own** bank stance;
  walk uses the bank's walk cycles when the model has no embedded Walk.
- `game/js/main.js` — select preview poses in the fighter's own stance;
  breathing fallback suppressed once posed.
- `game/js/assets.js` — a model's own `Battle_Idle`/`Stage_Idle`
  registers as its `Idle`.
- `game/js/t3anims.js` — `Chest`→`Spine2` track canonicalization.
- `game/assets/models/steve-fox.glb` — shirt mesh re-skinned with
  automatic heat weights onto the model's own armature
  (`tools/auto_rig/repair_stevefox_shirt.py`, the PR #372 per-file
  repair pattern): sleeves now follow the arms (verified by front
  render at Idle frame 40 + the weight gate). Minor artifact: the
  skin arm tubes sit slightly proud of the shirt shoulder seam.
  `demonio.glb` is a byte-duplicate of the pre-repair file and was
  NOT touched (Demonio needs his own model decision — see below).

Models: statues auto-rigged one at a time (heat backend) into each
character's own roster directory as new files; `MODEL_URLS` repointed
per character; originals untouched.

## Post-fix verification

In-engine harness screenshots (idle, ~2.3 s in) before/after for the
representative set — Pantera, Rin (jin bank), Skull (bryan bank),
Michiko (Lane-C rig), Doc Frank (178-bone rig), Yukihyō (king bank),
Iori + Deathfang (native idle), Demonio A1 + SAM-UR-A1 (statue → rigged):
see the PR discussion for the shot set. Blender front renders of every
rigged statue were viewed before shipping each file.

## Reported, not fixed (need their own lanes/decisions)

- Pantera `belt2`/`buckles` skin repair (his own file; pipeline work —
  do NOT hand-tweak). Same defect class as the Steve shirt: garment
  meshes bound to spine bones only, geometry sitting off-body.
- Demonio has no model of his own in `game/assets/models/` — his
  Attire 2 file is a byte-duplicate of Steve Fox's. His real models are
  the Tripo statues (Attire 1 / winged / human), rigged by this lane.
- Blanka re-assembly; Scimitar mesh (shelved); Zangief pedestal removal.
- Dio re-rig (foreign skeleton, no canonical bind at all).
- Baek/Master White, Mariposa, Dxmmii: no decoded bank for their
  sources yet — they keep their rest pose rather than borrowing another
  character's stance (isolation law). Unblocks when their sources are
  decoded.
- Dxmmii limb system wiring (its own design exists in
  `tools/limb-system/dxmmii/` — never landed in the shipped model).
