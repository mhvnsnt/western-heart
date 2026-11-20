# Def Jam: Fight for NY (PS2) — Teardown

**Owner directive 2026-10-13 · Worker: defjam-teardown**
**Game:** Def Jam: Fight for NY (EA Chicago, 2004) · **Platform:** PlayStation 2 (USA, SLUS_210.04)
**Source:** Internet Archive `slus-210.04.-def-jam-fight-for-ny` — `SLUS_210.04.Def Jam - Fight for NY.iso` (4,694,573,056 bytes)
**Extraction method:** surgical HTTP Range extraction (ISO9660 parsed remotely; only needed files fetched — ~450MB, no 4.7GB download)
**Status:** 2026-10-13 — models, motion data, XML data model extracted. Mesh decode (SHPS) = open RE work.

## Why this game matters (owner thesis)

FFNY is the proof that **wrestling/grappling animations work inside a Tekken-style 3D fighter engine**.
EA Chicago built it on the AKI wrestling-engine lineage from Def Jam Vendetta (2003):
`ASSETS/AKI_CFG.XML` ships on-disc (facial/hands/directional animation toggles, `pause_use_aki` flag),
and the motion bank is literally named `WRES_ALL.VIV` with `wresNNN` animation sets. Five fighting styles
(streetfighting, kickboxing, martial arts, wrestling, submission) share one grappling core — strikes and
grapples blend in a single engine. The animation/grappling SYSTEM findings live in
`western-heart/teardown/def-jam-fight-for-ny/ANIMATION-FINDINGS.md` (mechanics federate; models stay here).

## Disc layout (ISO9660 root)

| Path | Size | Contents |
|------|------|----------|
| `FIGHTER.XML` | 45,931 | **142 fighter entries**: name → model (`V2IP_xxx`), style (STF/MAR/WRE/SUB/KIC), bodysize, speechID |
| `CHARS.XML` | 7,807 | Character select metadata |
| `VENUE.XML` | 19,378 | **48 venues**: name → model (`V2BG_xxx`), display name, crowd/ambient/speech config |
| `GAMEDATA.XML` / `GCONFIG.XML` / `GAMECORE.XML` | — | Game/mode configuration |
| `ASSETS/` | — | `AKI_CFG.XML`, `COMBS.XML` (combo/skill chains), `TAUNT.XML`, `ENTITY.XML`, `*.VIV` model packs, `TINT.SSH` |
| `MOTION/` | — | **The animation system** (see below) |
| `AUDIO/` | — | `ANIMTAGS.DAT` (anim tag index), `MUSIC0-4.VIV`, `SFX0-3.VIV`, `SPEECH1-3.VIV` |
| `MOVIES/` | — | `*.MPC` FMVs, `MOVIES.VIV` (not extracted — FMV out of scope) |
| `SCREENS/` `FONTS/` `IOP/` | — | Frontend, fonts, IOP modules |

## Container formats

### BIGF-variant archive (`.VIV` files are NOT VIV — they are BIGF)

Every `.VIV` on this disc is an EA BIG archive with a **mixed-endian header quirk**:

| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Magic `BIGF` (`42 49 47 46`) |
| 4 | 4 | Total archive size, **LE32** |
| 8 | 4 | File count, **BE32** |
| 12 | … | Entries: **BE32 offset, BE32 size, NUL-terminated name**, back to back |

Quirks: size is little-endian while count/offsets/sizes are big-endian (standard EA BIGF is
all big-endian). Entry #0 has 4 anomalous bytes before its name (parser must tolerate).
Extractor: `tools/bigf_extract.py` (in `defjam-work/tools/`, carried with this teardown).

### `10 fb` record wrapper

Nearly every game file (models, motion, objects) starts with a `10 fb` record header:
`10 fb <type:1> <sub:1> ...`. Observed types: `06 10` (fighter models), `04 05` (boss/alt models),
`04 27`/`00 0a`/`00 26` (EAGL objects), `06 48` (motion .ord). Followed by either `SHPS`
(mesh), `\x7fELF` (EAGL object — see below), or binary track data.

### EAGL objects (`.o`, `.ord`, `.orl`, `_F.o`)

EA Graphics Library toolchain objects. They borrow the ELF magic (`\x7fELF`) but the header
fields are **not standard ELF** (e_type=0xE100, e_machine=0xC730, section headers unreadable
by readelf/pyelftools) — proprietary EAGL object format, full decode = open RE work.
Section names visible: `.data`, `.shstrtab`, `.rel`, `__EAGL_TOOLLIB_VERSION`.
`_F.o` files reference `__PosePaletteBank` — the **bone pose palette used for skinning**.

## Models — fighters (`V2IP.VIV`, 28.3MB, 234 entries)

78 fighter model sets. Each fighter = 3 files:

| File | Size | Contents |
|------|------|----------|
| `V2IP_xxx.ssh` | ~200–255KB | **SHPS mesh container** (`10 fb` + `SHPS` magic, model name e.g. `G359A001`); vertex/index data (encoding TBD — no plaintext past header) |
| `V2IP_xxx.o` | ~5KB | EAGL object — skeleton/rig definition |
| `V2IP_xxx_F.o` | ~1.4KB | EAGL object — face; references `__PosePaletteBank` (skinning bone palette) |

Variants: standard fighters use `10 fb 06 10` SHPS; `V2IP_4xx`/`5xx`/`126B` (bosses/alts)
use `10 fb 04 05` SHPS — same family. All 78 `.ssh` verified to carry SHPS magic.
FIGHTER.XML maps 142 fighter entries (incl. CAW/story variants) → these 78 base models.

**Location in this repo:** `teardown/def-jam-fight-for-ny/models/fighters/` (78× `.ssh`+`.o`+`_F.o`)

## Models — CAW parts (`V2CP_0..3.VIV`, 218MB, ~1,900 entries)

Create-a-fighter customization parts: `V2CP_xxx_xxxx_A01_01.ssh` (clothing/body parts,
~47–55KB each) + `V2CP_D_A..F.ssh` (defaults). Directly relevant to the Western Heart
from-scratch character builder (CAW parts federate as a system; the part MESHES stay here).

**Location in this repo:** `teardown/def-jam-fight-for-ny/models/caw-parts/`

## Models — venues (`V2BG.VIV`, 50.6MB)

48 venues per VENUE.XML (`V2BG_01A` = Hunt's Point Scrapyard, `V2BG_02A` = The Foundation,
…). Same SHPS family as fighters (verify at commit).

**Location in this repo:** `teardown/def-jam-fight-for-ny/models/venues/`

## Motion / animation (`MOTION/`)

| File | Size | Contents |
|------|------|----------|
| `WRES_ALL.VIV` | 64.2MB | **423-entry BIGF**: `wresNNN.mnl` + `wresNNN.ord` + `wresNNN.orl` triplets (NNN = 001…141) |
| `BASE00.VIV` | 2.4MB | Base skeleton / shared animations |
| `BLAZIN.VIV` | 2.9MB | Blazin'-finisher animations |
| `MAIN_ALL.DAT` | 283KB | **WAZA move database** (see below) |
| `CAMERA.XML` | 143KB | Camera definitions |

Triplet roles (from sizes + binary analysis):
- **`.mnl`** (172–682B): per-move header/index. `10 fb` magic, then a TLV/opcode stream with
  embedded move IDs (e.g. `N04F4_A`). Hypothesis: AKI-style move script bytecode.
- **`.ord`** (300–755KB): the meat — `10 fb` 6-byte header + embedded EAGL object
  (code + data). Contains the move's animation data and logic.
- **`.orl`** (12–21KB): per-bone animation tracks. After `10 fb` header + section names
  (`.data`, `.shstrtab`, `.rel`, `__EAGL_TOOL`, `Animation`), a run of `11 07 VV` triplets
  where `VV` sweeps smoothly (signed 8-bit quantized keyframe values) — uniformly-sampled
  bone rotation tracks. Full track decode = open work.

**`MAIN_ALL.DAT` — the WAZA move database** (技 = "technique", the AKI lineage showing):
676 distinct named moves in plaintext, including the grappling vocabulary —
`POWERBOMB`, `POWERPLEX`, `PILEDRIVER`, `SIDESLAM`, `ARMBAR`, `CHOKE`, `CHOKEOUT`,
`HEADBUTT`, `DROPKICK`, plus style moves (`SOUTHPAW`, `BLITZ`, …). Full list:
`teardown/def-jam-fight-for-ny/motion/waza_names.txt`.

**`AUDIO/ANIMTAGS.DAT`** (`TAGS` magic, 475KB): animation tag index — `A100_EC`,
`A200_EC`, … (1,919 distinct tags). Maps animation IDs → tags used by the engine.

System-level findings (how grappling works in this engine) →
`western-heart/teardown/def-jam-fight-for-ny/ANIMATION-FINDINGS.md`.

## Audio (`AUDIO/`)

`MUSIC0-4.VIV` (729MB), `SFX0-3.VIV` (548MB), `SPEECH1-3.VIV` (377MB) — all BIGF-variant
containers (same format as above). Full audio = 1.65GB, out of disk scope for this pass;
format documented, sample extraction = open work. `TV.TXT` (2.7KB) extracted.

## Data model XMLs (all extracted, plaintext)

`FIGHTER.XML` (fighters+styles), `VENUE.XML` (venues), `COMBS.XML` (combo chains reference
`skill no` IDs resolved by the WAZA DB), `TAUNT.XML`, `ENTITY.XML`, `GAMECORE.XML`,
`AKI_CFG.XML`, `CAMERA.XML` — in `teardown/def-jam-fight-for-ny/data/`.

## Tools (carried with this teardown)

- `tools/bigf_extract.py` — BIGF-variant extractor (handles mixed-endian header + entry0 anomaly)
- `tools/iso_tree.py` — ISO9660 tree lister via pycdlib
- `tools/assemble.py` — segmented-download assembler (for the full ISO pull)

## Open work

1. **SHPS mesh decode** — vertex/index encoding past the header is undocumented; no plaintext.
   Needed for GLB conversion of the 78 fighters.
2. **EAGL object decode** — proprietary header layout; needed for skeleton + PosePaletteBank.
3. **`.orl` track decode** — triplet structure characterized; bone mapping + time base TBD.
4. **`.mnl` bytecode** — TLV/opcode stream hypothesis unconfirmed.
5. **Full audio extraction** — 1.65GB, needs disk headroom.
6. **Full ISO** — 4.7GB, staged for TeraBox when the background pull completes.

## Provenance

- ISO: `https://archive.org/download/slus-210.04.-def-jam-fight-for-ny/` (verified 4,694,573,056 bytes)
- Extracted 2026-10-13 via surgical range requests (no full ISO download needed)
- Commit: branch → PR → merge, zero open PRs
