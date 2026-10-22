# WWF NO MERCY — Teardown for Western Heart

**Role in Chimera Build:** Wrestling systems + character customization + grappling animations.
**Engine:** AKI Corporation (same family: WCW/nWo Revenge, WrestleMania 2000, Virtual Pro Wrestling 2)
**Platform:** Nintendo 64
**Last updated:** 2026-10-13 (full asset extraction sweep)

---

## What's Extracted and Documented

### ROM — Verified
- `WWF No Mercy (USA) (Rev-A).z64` — 32,554,432 bytes, CRC32 `BACEEA13` (byte-verified)
- Source: Internet Archive `n64patchedwrestlingroms` (`WWF No Mercy (Unlocked).zip`, also in TeraBox `/western-heart/teardown-source-binaries/`)
- **FileTable @ `0x16C31D8`, FirstFile @ `0x1BD150`** (= VPWStudio `NoMercy_NTSC_U_11`). Verified correct 2026-10-13: LZSS-encoded files decode to exact header-claimed sizes and face textures render as faces. (An earlier pass used the NTSC_U_10 offsets `0x16C3238`/`0x1BD1B0`, which decode plausible-looking but misaligned data — corrected.)

### Animation Keyframe Bank — FULLY EXTRACTED (2026-10-13)
- **5,787 clips** in `animations/clips/anim_XXXX.npy` (int16, shape `(nframes, 26, 3)`), ~152k frames total, 36 MB.
- Clip list = every file labeled `AkiAnimation` in VPWStudio's `FileTableDB/NoMercy.txt` (MIT; copied as `tools/NoMercy-FileTableDB.txt`).
- `animations/manifest.json`: per-clip `file_id`, `toki2`, `nframes`, `kind` (`system` 1,353 / `move` 4,434), `anim_id` (move clips: `file_id − 0x3322`, the key joining move-table entries to clips), and **`label`** — the DB's human-readable move name (e.g. `"[Weak Arm Striking] Chop 01"`).
- `animations/FORMAT.md`: full NPY layout doc (26-joint order, PR/OM/MV channel semantics).
- Tools: `tools/extract_all_anims.py`, `tools/anim_extract.py` (decode matches VPWStudio `AkiAnimation.cs` field-for-field), `tools/lzss.py` (Asmik LZSS decoder, ported from VPWStudio).
- 2 DB entries don't parse as animations (`0x4473` encoded/478 B, `0x4C05` empty) — skipped with warnings, documented as DB mislabels.

### Wrestler Models — EXTRACTED (2026-10-13)
- **3,570 meshes** as Wavefront OBJ (+ `.vc` vertex-color sidecars) in `models/`, 29 MB. Format: AKI `AkiModel` (Scale, 8-byte vertices: s8 XYZ + u8 UV + RGB, 3-byte triangle faces) per VPWStudio `AkiModel.cs`; 16 DB-labeled files don't parse (kept in manifest as unparseable).
- Breakdown: `body_parts/` 220 (CAW body-type meshes: Skinny/Medium/Thick/Fat × parts), `arena/` 263, `backstage/` 402, `stage/` 92, `lobby/` 79, `face/` 48 (face + hair meshes), `weapon/` 34, `attire_parts/` 1, `unlabeled/` 2,431 (wrestler-specific attire/costume meshes, DB has no labels).
- `models/manifest.json`: per-model file_id, DB label, vertex/face counts.
- Community rips (pre-existing): 13 character GLBs + 2 environment GLBs in `re-docs/assets/3d Assets/` (9 wrestlers: Rock ×3, Austin, HHH, Nash, Hall, HBK ×2, Angle, RVD, Rhino, Stephanie).

### Textures — EXTRACTED (2026-10-13)
- **5,029 PNGs** in `textures/rom/`, 23 MB, via DB-guided decode (Asmik LZSS → TEX/CI8/CI4/I4 parsers → RGBA5551 palettes → PNG).
- **CAW faces: all 118 (98 male + 20 female)** in `textures/rom/face/` — 32×64 CI8, verified by rendering (The Rock's face confirmed visually).
- **Creation-suite parts:** `front_hair/` 62, facial hair 30, `tattoo/` 99, `mask/` 45, `hair/` 49, full attire library (`ring_attire_-_short/long/pants/wrestling/full_body`, `upper_body_-_no_sleeves/sleeve_s/sleeve_l/others`, `boots/`, `body/`, gloves, wrist bands, elbow/knee pads), `character_portrait/` 101, `character_icon/` 102.
- **Arena/stage:** `arena/` 127, `stage/` 90, `arena_menu/` 70, `titantron/` 313, `lounge/`, `locker_room/`, `lobby/`.
- Also: `textures/characters/` + `textures/environments/` — 350 PNGs extracted from the community GLBs' embedded textures (`tools/extract_glb_textures.py`).
- Key format finding: in DB texture/palette pairs the two files are systematically type-swapped (the "Palette" entry holds the texture and vice versa) — the extractor classifies by content (dimension header), not by DB type label. Some attire textures had no reachable palette and were rendered grayscale (marked in manifest).
- `textures/rom/manifest.json`: per-texture file_id, kind, DB label.

### Character Data Tables (ROM-verified, static RE)
- **Wrestler display-name / internal-ID table @ `0x168D930`:** 42 entries (`docs/wrestler-id-table.json`).
- Move tables, move-data index (40 runs @ `0xF5BF8`), overlay DMA table (@ `0x539A0`), camera/spawn float table (@ `0x13E2BC`). Documented: `docs/CHARACTER-DATA.md`, `docs/NOMERCY-TEARDOWN.md`, `docs/ANIMATION-ISOLATION.md`.
- Tool: `tools/analyze_nomercy.py`.

### Text Engine + CAW Docs (2026-10-13)
- `TEXT-CODE-DICTIONARY.md` — 2-class text-code model. `TOKI2-SEMANTICS.md`. `CAW-SAVE-RECORD-STATUS.md`.
- CAW part-string tables: `docs/` in source repo (`caw-categories.json`, `caw-name-table.json` — id→name for every creation-suite part).

### AKI → Tekken 3 Retarget — v1 (2026-10-13)
- `aki_to_tekken3.py` + `aki_to_tekken3_v1.json`, documented in `AKI-TEKKEN3-RETARGET.md`.
- **NOTE:** v1 was built from the earlier misaligned animation export — regenerate from `animations/` (corrected bank) before use.

### Community RE Resources (cloned locally)
- `re-docs/` — chaotix610/wwfnomercy-docs (systems, move DB, creation suite docs; 15 community GLBs)
- `recomp/` — Gadge64/WWFNoMercyRecomp (N64Recomp static recompilation)
- VPWStudio (AKI-Club, MIT) pulled 2026-10-13 for: `DefaultGameData.cs` file IDs, `AsmikLzss.cs` decoder, `AkiModel`/`AkiTexture`/`Ci*Texture` formats, `FileTableDB/NoMercy.txt` (19,462 labeled files — the map for this entire extraction).

### Creation Suite Architecture
- 4 attire slots per character; modular appearance (14M+9F body types × 8 skin tones, 7M/3F head shapes, 98M/20F face textures, 22 hair styles, 31 facial hair, ~150 ring-attire + ~150 upper-body pieces, 28 tattoos, per-limb gear) — the reference model for Western Heart's character customization.

---

## What's Blocked and Why

- **CAW save-record byte layout** — needs a real emulator save file to diff against the id tables (ROM side complete).
- **Per-code text-engine dictionary** — Class B expansion tokens partially mapped; full table needs the AKI text renderer (does not block motion/model work).
- **16 AkiModel files don't parse** (mostly 32-byte DB mislabels; `0x26` belt model is a different structure) — listed in `models/manifest.json` → `unparseable`.
- **2 AkiAnimation DB entries don't parse** (`0x4473`, `0x4C05`) — DB mislabels.
- **~1,750 attire textures rendered grayscale** — no palette found within ±64 files; CAW attire colors are user-selected at runtime, so grayscale is representative, but exact in-game colors need the palette links.
- **Unlabeled models (2,431)** — DB has no names; they are wrestler-specific costume meshes keyed by file ID only.
- **Move→clip linkage beyond AnimID** — `anim_id` + DB labels give the mapping; per-wrestler move-slot assignments still live in the move tables (documented, not yet joined).

## Chimera Build Value

- **5,787 named animation clips** (grapples, strikes, taunts, stances) with human-readable labels — the wrestling move library for Western Heart's Wrestling Mode, retargetable via the proven AKI→Tekken pipeline.
- **Full CAW part library as data**: 220 body-part meshes + 118 face textures + complete attire/gear texture set — the customization system's asset foundation.
- **Arena geometry** (263 meshes) + backstage/lobby/stage sets for the wrestling environment.
- **42-wrestler ID table** + move tables + creation-suite id mappings = the systems data.

## Next Steps

1. Regenerate `aki_to_tekken3` retarget from the corrected animation bank.
2. Join move-table entries → `anim_id` → clips into the chimera move database schema.
3. CAW save-record layout (needs emulator save).
