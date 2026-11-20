# Tekken 7 Customization Parts — Holdings Survey (2026-10-21)

**Owner order (2026-10-21 ~08:09 CDT):** pull ALL Tekken 7 customization parts —
generic AND per-character — from our sources, convert them, and wire them into
the Creation Suite for building proprietary characters. Proof piece #1: Slice's
skull mask, which the owner identifies as Tekken 7's **generic** skull mask.

**Verdict: the part meshes are NOT in any holding we have.** Survey counts are
**0 meshes in every one of the 16 T7 slot classes**. This document is the
evidence, the exact acquisition route, and the import spec that runs the day
the parts land. Nothing in this lane was fabricated, AI-generated, or
hand-painted to fill the gap.

---

## 1. What was surveyed, and what was actually in it

| Holding | How it was checked | What it contains | T7 customization part meshes |
|---|---|---|---|
| **tekken7-full-v1** release (mhvnsnt/western-heart, 7 parts, ~3.3 GB tar) | Full 1,266-entry tar index (`~/workspace/_heihachi-lane/tar_full_index.txt`) grepped for custom/item/mask/skull/head/accessory terms and read by top-level tree | Character model dirs (King variants 498 entries, Eddy, Steve, Xiaoyu, Asuka…), the tekkenmods-docs tree, `tekken7/tools/umodel_linux`. The only "custom" hit is a docs PNG. "Mask" hits are **King's own costume textures** (`King_MaskFur1_D/N/S`, `King_Mask1Head_*`, `King_TigerMask_*`) — his jaguar mask is part of his full character costume, not a generic equippable part | **0** |
| **tekken-models-batch-2** release (14 assets) | Asset list read via GitHub API | Full character rigs / costume blends only: Dragunov T7 rig (Slice's source), Feng Wei, Hwoarang, Kunimitsu, Tekken Force Soldier, Zafina alt **costumes**, plus T8 packs | **0** |
| **tekken-models-batch-3** release (23 assets) | Asset list read via GitHub API | SFMLab / rigmodels **full-character** packs (Akuma, Alisa, Anna, Jin, Lee, Miguel, Shaheen, Yoshimitsu…) and full alternate costumes (Josie diva / summer school, Julia classic). No separated item/part packs | **0** |
| **game-reverse-engineering/tekken7** | `~/workspace/tekken-customization-extraction/REPORT.md` (2026-10-16) + the tar mirror above | The complete customization **DB schema** (tekkenmods-docs/TKDataPatcher) + 29 character model dirs. REPORT.md states it directly: "We do NOT have the actual game .uasset files" | **0** |
| **Local disk** (all of ~/workspace) | `find` for `*.pak` / `*.uasset`; workspace-wide filename search for `*skull*`; directory search for Customize trees | No Tekken 7 paks or uassets anywhere (the only .uasset tree is the unrelated SMOKE-MIRROR Lyra sample project). Skull hits: KayKit CC0 prop skulls (cape-jones-build), the fighter "Skull"'s moveset JSONs, facepaint PNGs — **none are T7 parts** and none were used as stand-ins | **0** |
| **western-heart repo, `customization/parts/`** | Tree listing via GitHub API | `parts/tekken/` = the T7 **slot schema** (`tekken7-slot-catalog.json`) + Tekken 6 item **data** (PR #416); `parts/masks/` = one WH-original (bannon-mask). The schema dir's own `MANIFEST.json` → `needs_pulling` already records: the .uasset item models were never pulled | **0** |
| **Tekken 7 PC game itself** | agent-ops checkpoints `tekken7-pull.json`, `tekken7-download.json` (both status: done) | The ~47 GB full-game download was **blocked and never landed** (no verified source; disk could not hold it). The lane pivoted to pulling the King model only. **We have never held the game's paks** — the umodel route has had nothing to run on | **0** |

### Counts per T7 slot class (meshes found in holdings)

| Slot | Count | Slot | Count |
|---|---|---|---|
| HEAD | 0 | FULL_BODY | 0 |
| HAIR | 0 | LOWER | 0 |
| FULL_HEAD | 0 | UPPER_ACC | 0 |
| HAIR_ACC | 0 | LOWER_ACC | 0 |
| GLA (glasses) | 0 | EXTRA | 0 |
| FACE | 0 | Effects | 0 |
| FACE_HAIR | 0 | Aura | 0 |
| MAKE_UP (texture class) | 0 | UPPER | 0 |

**Total T7 customization part meshes in holdings: 0.** Adjacent material that
does exist and must not be miscounted as parts: full character models and full
costumes (above), the complete DB **schema**
(`customization/parts/tekken/tekken7-slot-catalog.json`), and Tekken 6 item
name data (PR #416 — a different game's data, no meshes).

---

## 2. Proof piece #1 — Slice's skull mask: verdict

**Not in holdings. No part exists to convert, attach, or render.** The generic
skull mask the owner means lives only inside the Tekken 7 game paks (below).
No proof render was made: rendering a stand-in would mean fabricating the part,
which this lane does not do.

Status of the mask as of this survey:

- It is registered as a **named gap** in
  `customization/parts/tekken7/CATALOG.json` → `named_gaps`
  (id `tekken7:cmn:full_head:skull-mask`, slot FULL_HEAD / slotId 3, scope
  generic / PlayerCus 0, suite slot `full_head`, socket Head).
- Through the real runtime (`packages/creation-suite/src/catalogs.js`), a
  profile that assigns that part_id resolves today as **`unresolved`** —
  reported, never silently dropped (proven by
  `customization/parts/tekken7/catalog.test.mjs`). The day the real part lands
  in `parts[]`, the same id resolves with its GLB, with no consumer change.
- The owner's own Slice Tripo Attire 1 (cf9cf660, his default since
  2026-10-21 ~08:42 CDT) already carries a skull mask modeled on — his default
  look is covered. This gap is the **suite-placeable T7 part** for the
  PR #433 Dragunov attire and for any other character, per the owner's order.
- Slice's Attire 1 GLB (`roster/slice/attires/attire1/model.glb`) was **not**
  modified by this lane.

---

## 3. Acquisition route (exact)

### Primary — Tekken 7 PC game paks + umodel (yields the WHOLE set in one pass)

1. **Get the game files.** Tekken 7 (PC, Steam) installs to
   `…/steamapps/common/TEKKEN 7/TekkenGame/Content/Paks/` (~47–70 GB with
   DLC). Every customization item — generic and per-character — is inside
   those paks. **Disk gate:** local disk has ~11 GB free; stage the paks
   store-first (GitHub release / TeraBox) and stream-extract, or run the
   extraction on a machine that holds the owner's Steam install. Do not land
   47 GB on this disk.
2. **Export with umodel.** We already hold the tool:
   `tekken7/tools/umodel_linux` (inside the tekken7-full-v1 release tar).
   In-pak layout (documented by the community modding guide,
   CDDTreborn/Tekken7_PC-Modding-Guides wiki, "Umodel UE Viewer Quick Start
   Guide — Tekken 7",
   https://github-wiki-see.page/m/CDDTreborn/Tekken7_PC-Modding-Guides/wiki/Umodel-UE-Viewer-Quick-Start-Guide-or-Reference---Tekken-7):
   - **Meshes:** `Game/Character/Items/Mesh/<CHAR-ABBR>/` per character, and
     **`Game/Character/Items/Mesh/cmn/` for meshes not specific to one
     character — the generic set, skull mask included.** Each mesh folder is
     split by category (Upper, Lower, Full_body, Head, Face, …); each item
     folder holds the mesh, its textures, and its materials together.
   - **Item records (extractable, not viewable in umodel):** CI at
     `Game/Character/Items/CharacterItem`, CCI at
     `Game/Character/Items/Customization`, CS presets at
     `Game/Character/Items/Sets`, ACI at `Game/Character/Items/AuraItem`,
     ECI at `Game/Character/Items/EffectItem`.
3. **Classify from the folders + records**, per
   `customization/parts/tekken/tekken7-slot-catalog.json`: folder `cmn` →
   scope generic (PlayerCus 0); a character-abbreviation folder → that
   character (charId from the schema's 57-ID table); category folder → slotId;
   color-slot count (0–5) and names from the CCI/CI records (the 21-field CSV
   spec in the schema). The exact skull-mask item record is read from the
   CCI/CI data at this step — it is not guessed in advance.
4. **Convert:** umodel PSK mesh + TGA textures → Blender PSK import → GLB with
   textures bound (no clay parts ship). Placement = the bone-socket paradigm
   the schema documents (PartPoser-compatible); socket per slot class, numeric
   offsets measured from the real part.
5. **Catalog + wire:** append entries to
   `customization/parts/tekken7/CATALOG.json` → `parts[]` in the entry shape
   templated in that file's `_meta.entry_template`; GLBs land at
   `customization/parts/tekken7/<slot>/<item>/<item>.glb`. Re-run
   `catalog.test.mjs` (it asserts the skull-mask id flips from `unresolved`
   to resolved once its entry exists — the test is written to be updated to
   the resolved expectation at that point, recording the flip).
6. **Proof:** build a profile for Slice's Dragunov attire assigning
   `tekken7:cmn:full_head:skull-mask` at suite slot `full_head`, bake via the
   suite's `apply_customization.py`, front-render, and view the frame with
   the lane's own eyes before reporting (ONE Blender job at a time; the box
   is shared).

### Secondary — community channels (piecemeal; supplements, never replaces #1)

- **TekkenMods (tekkenmods.com)** hosts per-item Tekken 7 customization mods.
  Useful for an individual item ahead of the full extraction; it is not the
  game's full generic set, and each mod carries its own author/license terms
  to record (license-honesty rule).
- **The DeviantArt / Open3DLab ripper channel** that already supplied our King
  packs (Sticklove, WhiteMageSunny, 1Vote4Sake — see
  `tekken7/models/king-variants/`) occasionally posts separated head/item
  packs. Watch-and-pull only; nothing there was a generic item set at survey
  time.

---

## 4. Handoff — for the fighter-completeness / consumer lane

The catalog side is ready today; no consumer change is needed beyond loading
one more catalog:

```js
import { loadCatalog, mergeCatalogs } from './catalogs.js'; // packages/creation-suite/src/catalogs.js

const registry = await loadCatalog('customization/PARTS-REGISTRY.json', fetcher);
const tekken7  = await loadCatalog('customization/parts/tekken7/CATALOG.json', fetcher);
const entries  = mergeCatalogs(registry, /* …other catalogs… */, tekken7);
```

- `loadCatalog` validates `parts[]` is an array — the T7 catalog loads cleanly
  today with 0 parts and merges without disturbing registry entries (proven
  by `catalog.test.mjs` against the real registry).
- T7 entries, when they land, carry: `slot` = T7 slot name, `suite_slot` per
  the mapping in the catalog `_meta`, `scope` (`generic` | `character`),
  `char_id`, `player_cus_id`, `color_slots`, `glb`, and `placement` with the
  bone `socket` — everything `resolveProfileParts` and the bake consume.
- The skull-mask profile id is `tekken7:cmn:full_head:skull-mask` at suite
  slot `full_head`. Until extraction, it resolves `unresolved` — by design.
- This lane did **not** touch `game/js/custom-fighter.js` or
  `packages/creation-suite/src/catalogs.js` (consumer lane's files).

---

## 5. Lane log

- 2026-10-21 ~08:16 CDT — checkpoint opened; schema read
  (`~/workspace/tekken-customization-extraction/REPORT.md`); suite checkpoints
  of the other chat confirmed `done` (AshLanev2-scoped; not redone);
  gap-fill PRs #400/#401/#411/#415/#416/#420 confirmed merged.
- 2026-10-21 ~08:20–08:31 CDT — holdings survey (table in §1); verdict: 0
  meshes; skull mask = named gap (§2); acquisition route documented (§3).
- Catalog + this survey + test shipped as one additions-only PR; Slice's
  Attire 1 GLB untouched (byte-identical); no Blender work was needed or
  faked — there is no part to render yet.
