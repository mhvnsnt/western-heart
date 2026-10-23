# Virtua Fighter 5 — Definitive Status (2026-10-23)

**Lane:** teardown-completion sweep, tail item (documentation only — no conversion work was started by this lane).
**Game:** Virtua Fighter 5 (PS3, BLES00029, Ver.C) — Western Heart universe name: `virtual-soul` (`RENAME-MAP.md`).
**One-line state:** Extraction is 100% and API-verified; Western Heart model conversion is **BLOCKED on Windows + Autodesk 3ds Max** (see §3).

All release facts in §1 were verified by this lane against the live GitHub API
(`gh api repos/mhvnsnt/western-heart/releases/...`) on 2026-10-23. All in-repo
facts were read from `main` the same day.

---

## 1. What exists

### 1.1 Source

| Item | Value |
|---|---|
| Game | Virtua Fighter 5 (PS3, 2007), BLES00029, Ver.C revision |
| Source dump | Archive.org `games_20250220` → `Virtua Fighter V PS3/GAMES.rar` (per `teardown/virtua-fighter-5/TEARDOWN.md`) |
| Source RAR size | 3,686,456,692 bytes, verified on disk 2026-10-13 (per `TEARDOWN.md` / `VF5-VERIFICATION.md`) |
| Edition note | This is base VF5 Ver.C, **not** Final Showdown. Jean Kujo and Taka-Arashi are Final Showdown-only and are **not** in this dump. |

### 1.2 Release `vf5-ps3-v1` — the raw extraction (API-verified)

- Repo: `mhvnsnt/western-heart` · Tag: `vf5-ps3-v1` · Name: "Virtua Fighter 5 PS3 (BLES00029) v1"
- Published: 2026-10-13T15:56:20Z · Draft: no · Prerelease: no
- URL: https://github.com/mhvnsnt/western-heart/releases/tag/vf5-ps3-v1
- **89 assets, 4,987,414,284 bytes total**, broken down as:

| Category | Count | Notes |
|---|---|---|
| Source RAR chunks | 8 | `vf5-500m.part_00`–`part_07` — 7 × 524,288,000 B + 16,440,692 B = 3,686,456,692 B. Reassemble: `cat vf5-500m.part_* > vf5-ps3-games.rar` |
| Fighter body archives | 19 | 18 fighters + `akixx.farc` (Akira alt body, 2,672,983 B). The 18 base body `.farc` files are tiny stubs (758–762 B each) — the model data lives in the item archives below. |
| Fighter item archives | 18 | `*itm.farc`, 25,510,344 B (Dural) to 71,985,799 B (Lau) each — these hold the `*_obj.bin` model + `*_tex.bin` texture pairs |
| Stage archives | 38 | `stg*.farc` — 18 arenas + 20 training/test/special (see §1.4) |
| Common / databases | 7 | `dbg.farc`, `effcmn.farc`, `itmcmn.farc`, `test.farc`, `obj_db.bin` (504,864 B), `tex_db.bin` (591,152 B) |

Every asset carries a `sha256:` digest in the API (per-asset digests were
spot-verified by this lane; the full list is reproducible with
`gh api repos/mhvnsnt/western-heart/releases/tags/vf5-ps3-v1`).

### 1.3 Release `vf5-model-library-v1` — the organized model library (API-verified)

This is the release the conversion lane will consume. **The figures below are
the API-verified truth and correct the older brief/manifest numbers where they
differ.**

- Repo: `mhvnsnt/western-heart` · Tag: `vf5-model-library-v1` · Name: "VF5 Model Library v1"
- Published: 2026-10-15T01:30:57Z · Draft: no · Prerelease: no
- URL: https://github.com/mhvnsnt/western-heart/releases/tag/vf5-model-library-v1
- Release body: "Virtua Fighter 5 model library: 19 fighters + 38 stages (1.3GB). Recovery upload 2026-10-14."
- **3 assets, 1,301,084,160 bytes total:**

| Asset | Size (bytes) | SHA-256 (API `digest`) | Downloads at check |
|---|---|---|---|
| `vf5-models-a.tar` | **412,958,720** | `243fcdbe05aec6f1e0dfd09523b6b666946319ff61e7d97f5ffe82ef9ac50ddb` | 5 |
| `vf5-models-b.tar` | **404,111,360** | `a5e9f0992619d46b922f0c0301d725cefd10bbb03df1c29383339e7ed89dd379` | 2 |
| `vf5-stages.tar` | **484,014,080** | `58edef73f35f382de7d7dbc8555fef37dac95499a921f99d3ea807d5b90c3fc9` | 0 |

**Corrections to earlier numbers (read this before quoting sizes):**

- A pre-sweep brief gave `vf5-models-a.tar` as "394,460,160-ish bytes". That is
  **wrong as bytes**. The API size is **412,958,720 bytes**. The "394" figure is
  the size in MiB (412,958,720 B = 393.8 MiB), which is what the in-repo
  manifest (`VF5-MODELS-MANIFEST.md`) lists as "394MB".
- Same reconciliation for the other two: manifest "386MB" = 385.4 MiB =
  404,111,360 B; manifest "462MB" = 461.6 MiB = 484,014,080 B. The manifest is
  not wrong — it is in MiB labelled MB. This doc quotes bytes.
- The three SHA-256 prefixes circulated in the brief (`243fcdbe…`,
  `a5e9f099…`, `58edef73…`) are **confirmed correct** — they match the leading
  bytes of the full API digests above.

**Contents** (per in-repo manifest `teardown/virtua-fighter-5/VF5-MODELS-MANIFEST.md`,
108 files total; this lane did not re-extract the tars):

| Tar | Contents |
|---|---|
| `vf5-models-a.tar` | 8 fighters: `lau, wol, jef, jak, aoi, lio, bra, shu` |
| `vf5-models-b.tar` | 11 fighters + common: `lei, msk, kag, goh, van, sar, mon, pai, aki, dur, akixx` + common + README |
| `vf5-stages.tar` | All 38 stages |

### 1.4 Counts — roster and stages (reconciled)

The docs use "17 / 18 / 19 fighters" in different places. The reconciled truth:

- **18 distinct fighters** are in this dump: Akira Yuki (`aki`), Pai Chan
  (`pai`), Lau Chan (`lau`), Wolf Hawkfield (`wol`), Jeffry McWild (`jef`),
  Kage-Maru (`kag`), Sarah Bryant (`sar`), Jacky Bryant (`jak`), Shun Di
  (`shu`), Lion Rafale (`lio`), Aoi Umenokouji (`aoi`), Lei-Fei (`lei`),
  Vanessa Lewis (`van`), Brad Burns (`bra`), Goh Hinogami (`goh`), Eileen
  (`mon` = monkey), El Blaze (`msk` = mask), and Dural (`dur`, boss).
  (`VF5-VERIFICATION.md`: base PS3 VF5 has 18 playable fighters.)
- **19 fighter directories** in the model library = the 18 above + `akixx`
  (Akira Yuki alt body variant). This is the "19 fighters" figure used by the
  release body and manifest.
- `TEARDOWN.md`'s roster table lists 17 because it predates Dural being
  counted in the roster (Dural is item 19 in `models/README.md`).
- **38 stage archives** = 18 arenas (`are aur ban bar cas djo dur hai jin nyc
  riv sin slk tak tan ter umi yuk`) + 20 training/test/special (`tr2`–`tr9`,
  `trm`, `trn`, `trs`, `ts2`, `ts3`, `tst`, `du1`–`du4`, `cid`, `wht`), per
  `stages/README.md`. Each stage `.farc` parses to exactly 1 `*_obj.bin` + 1
  `*_tex.bin` (verified with `farc_extract.py` on every archive).

### 1.5 Third VF5 release (for completeness)

- `vf5-local-models-v1` — "VF5 local models — 334 files (141,977,600B)",
  published 2026-10-16T22:52:08Z. One asset: `vf5-local-334files.tar`,
  141,977,600 B, SHA-256
  `21f5295fdba53029dd2dcd223d14d9b597b443512df4cf8a662b98e84ace87cb`.
  A tar of the full local `virtua-fighter-5/models/` tree, stored during disk
  cleanup. It is a backup of the same library, not a separate extraction.

### 1.6 What is in the repo on `main` (API-verified 2026-10-23)

VF5 teardown home: **`teardown/virtua-fighter-5/`** in `mhvnsnt/western-heart`.

| Path | Contents |
|---|---|
| `teardown/virtua-fighter-5/TEARDOWN.md` | Extraction methodology, formats, pipeline, sources |
| `teardown/virtua-fighter-5/VF5-MODELS-MANIFEST.md` | Model-library manifest (contents of the three tars) |
| `teardown/virtua-fighter-5/VF5-VERIFICATION.md` | 2026-10-14 100% verification of `vf5-ps3-v1` |
| `teardown/virtua-fighter-5/docs/VF5-MECHANICS.md` | Mechanics federation doc (VF mechanics → WH) |
| `teardown/virtua-fighter-5/docs/FarcPack.7z` (111,469 B) | FarcPack tool archive (MikuMikuLibrary) |
| `teardown/virtua-fighter-5/docs/MikuMikuModel.7z` (7,468,771 B) | MikuMikuModel tool archive |
| `teardown/virtua-fighter-5/tools/farc_extract.py` | In-house FArC extractor (pure Python) |
| `teardown/virtua-fighter-5/models/README.md` | Full roster table with inner-file counts |
| `teardown/virtua-fighter-5/models/aki/` | `aki.farc` (759 B) + `akiitm.farc` (36,336,557 B) + README |
| `teardown/virtua-fighter-5/models/akixx/` | `akixx.farc` (2,672,983 B) + README |
| `teardown/virtua-fighter-5/models/dur/` | `dur.farc` (760 B stub) + README only |
| `teardown/virtua-fighter-5/stages/README.md` | Stage catalogue — **no stage binaries in git** |

Important: **most model binaries are NOT in git.** On `main`, `models/` holds
only the `aki`, `akixx`, and `dur` directories (and `dur` is only the stub);
the other 16 fighter directories and all 38 stages exist **only** inside the
`vf5-model-library-v1` tars (and as `.farc` assets on `vf5-ps3-v1`).

Related docs elsewhere in the repo:

- `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md` — 2026-10-22 integration
  round: Linux geometry parser, T-pose clay renders of all 18 fighters, the
  four owner-locked VF5→WH source mappings (Jeffry→Bannon, Wolf→El Toro de
  Oro, El Blaze→Pablo, Lei-Fei→NPC Finxsse), moveset conversions.
- `docs/research/VF5-MOTION-GAP-2026-10-22.md` — motion-data gap (see §2.4).
- `docs/decisions/2026-10-22-vf5-integration.md` — decision log for that round.
- `game/assets/movesets/` — 7 VF5 moveset JSONs already wired at data level:
  `vf-akira.json`, `vf-elblaze.json`, `vf-jeffry.json`, `vf-kage.json`,
  `vf-leifei.json`, `vf-sarah.json`, `vf-wolf.json`. **No VF5 fighter model
  GLB is in the game** — movesets exist, models do not (that is the §3 block).
- `teardown/vf5/ACQUISITION-PLAN.md` — a **different game**: Virtua Fighter 5
  R.E.V.O. World Stage (PC/Steam). Mirrored in
  `mhvnsnt/game-reverse-engineering` (`vf5-revo/ACQUISITION-PLAN.md`). It is
  not part of this PS3 extraction and is out of scope for this status.

Local tooling (workspace, not repo): `tools/vf5-extract/` in the agent
workspace holds `FarcPack.7z`, `MikuMikuModel.7z`, `farc_extract.py`, and
`quickbms.zip` (same tool archives as in `docs/` above).

### 1.7 Visibility — owner instruction on record (NOT executed by this lane)

API-verified today: repo `mhvnsnt/western-heart` is **public**
(`private=false`, `visibility=public`), and all three VF5 releases above are
published (not draft). 

**Owner instruction on record: the VF5 model library release stays PUBLIC
until Western Heart integration + rename are done, and goes private only
after that.** This lane changed no visibility, and no future lane should
change it early — the sequencing is: convert (§4) → integrate → rename →
*then* privatize.

---

## 2. The model format and what conversion actually has to do

### 2.1 Format chain (each step cited to in-repo docs/tools)

1. **`.farc` container** — Sega archive. Format per
   `teardown/virtua-fighter-5/tools/farc_extract.py`: magic `FArC` + header,
   then per entry `[name\0][offset BE u32][comp_size BE u32][uncomp_size BE u32]`,
   payloads gzip-compressed. The in-house extractor is validated on all 79
   objset `.farc` files (`models/README.md`).
2. **`*_obj.bin` — the model.** Per `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md`
   (2026-10-22 lane's own reverse engineering): magic `0x05062500` (LE),
   14 mesh chunks; chunk headers carry bounding sphere + submesh count; vertex
   positions are LE f32 triplets; indices are u16 triangle strips;
   **`SKIN` blocks are present per chunk (bone weights — parsed, not yet
   converted)**.
3. **`*_tex.bin` — the textures.** A TXP container; the documented extraction
   is `TXP.bms` under QuickBMS (`TEARDOWN.md`, every per-fighter README).

So "conversion" means: `.farc` → decompress → parse `*_obj.bin` **with its
skeleton, skin weights, and facial data** + decode `*_tex.bin` → export a
skinned, textured model → GLB for Western Heart. Step 1 is solved on Linux.
The skeleton-complete version of step 2 is the blocked part (§3).

### 2.2 The known full-fidelity route — chrrox 3ds Max script

Per `TEARDOWN.md` ("Extraction Pipeline", "Sources") and every per-fighter
README in the library:

> "Decompressed `*_obj.bin` → chrrox 3ds Max script; `*_tex.bin` → TXP.bms (QuickBMS)."
> "Import `.bin` models via chrrox 3ds Max script (**includes facial expressions + skeleton**)"
> Sources: Xentax thread "(PS3) Virtua Fighter 5 / Project Diva Dream Theater" (chrrox scripts).

- The chrrox script runs **inside Autodesk 3ds Max** (it is a MaxScript
  importer). That is the only documented route that imports the PS3
  `*_obj.bin` **with skeleton + facial expressions**.
- `TEARDOWN.md` also records what was **not yet pulled**: "chrrox 3ds Max
  import script (from Xentax thread)", "TXP.bms QuickBMS script (from Xentax
  thread)", "QuickBMS itself" — listed under *Also needed (not yet pulled)*.
  A future lane must source these first (Xentax thread per `TEARDOWN.md`).
- **GLB path from Max (planned, not yet executed):** run the chrrox importer
  in 3ds Max on each decompressed `*_obj.bin` (with its `*_tex.bin` decoded
  via QuickBMS/TXP.bms alongside) → export FBX from Max → import the FBX in
  Blender → export GLB → per-character WH wiring (§4). FBX is the interchange
  step because it carries skeleton + skin weights + facial/morph data out of
  Max intact; GLB is Western Heart's runtime format.

### 2.3 Alternatives — honestly assessed

| Route | What it does | Evidence | Verdict |
|---|---|---|---|
| **MikuMikuModel / MikuMikuLibrary** (blueskythlikesclouds) | Opens same-engine model `.bin`/`.farc`, exports **FBX** + textures as DDS/PNG. Its wiki states verbatim: "Games that use the same game engine such as **Virtua Fighter 5** and Miracle Girls Festival are also supported." Needs a configuration built from `obj_db.bin` + `tex_db.bin` — **both are present** on `vf5-ps3-v1` (§1.2), and the tool archives are already in-repo (`docs/MikuMikuModel.7z`, `docs/FarcPack.7z`). | Wiki: https://github-wiki-see.page/m/blueskythlikesclouds/MikuMikuLibrary/wiki/Miku-Miku-Model | **Community-proven** for VF5-family models, **unverified** on our PS3 Ver.C bins (nobody has run it on them in this project). **Does not remove the Windows requirement for the GUI**: the same wiki's requirements are Windows 7/8/8.1/10 + .NET Framework 4.7.2, with Linux only via Wine + `winetricks dotnet48`. Its CLI tools (FarcPack, TxpConverter) are .NET and are the only plausibly Linux-native piece — untested here. Also note the wiki itself says: for production rips it recommends chrrox's/minmode's Noesis scripts instead of its own ripper. |
| **Noesis scripts (chrrox / minmode)** | Noesis model viewer/converter scripts for the same formats; recommended by the MikuMikuLibrary author for production-quality rips (quote above). | Same wiki, "Ripping models" note | **Community-claim.** Not pulled, not tested in this project. Noesis is a Windows application, so this route also lands on a Windows seat. Worth evaluating on the same Windows seat as 3ds Max — it may prove faster than Max for batch export — but it is not a Linux escape hatch. |
| **In-house Linux parser** (`farc_extract.py` + the 2026-10-22 `vf5extract.py`) | FArC extraction + `*_obj.bin` geometry parsing (positions + indices) on pure Linux; produced T-pose **clay renders of all 18 fighters** in Blender (2026-10-22 round). | `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md` | **Proven — for static geometry only.** Explicit limits from that doc: SKIN blocks "parsed, not yet converted"; textures "not yet extracted (renders are untextured clay)". No skeleton, no weights, no textures, no GLB of a skinned VF5 fighter has come out of this route. It proves the models are intact; it does not unblock game-ready conversion. Extending it to full SKIN/texture conversion is a new RE project, not a known path. |
| **QuickBMS + TXP.bms** (textures only) | Decodes `*_tex.bin` TXP texture containers. | Documented in `TEARDOWN.md` pipeline; listed there as "not yet pulled" | **Unverified** in this project. Needed on whichever seat does the conversion; QuickBMS itself is also Windows-first tooling. |

### 2.4 Separate gap — motion/animation data (not a model-conversion issue)

Per `docs/research/VF5-MOTION-GAP-2026-10-22.md`: **motion data is not in
`vf5-ps3-v1` at all** — every `.farc` entry is an obj/tex pair. The motion
format is publicly undocumented; neither the chrrox scripts nor
MikuMikuLibrary cover PS3 VF5 motion (MikuMikuLibrary's motion support is for
its Project DIVA / VF5FS-PC family, per that doc's 2026-10-22 web research).
Motion likely lives in the full ROM filesystem outside the objset archives
(possibly inside the 3.7 GB RAR's unpulled areas). This is a separate
multi-day RE lane (an open motion-pipeline PR, #713, already exists — this
doc does not duplicate it). **Even a perfect 3ds Max model conversion does
not deliver VF5 animation clips.** Movesets (inputs/frame data) are a
different thing and are already partially wired (§1.6).

---

## 3. The blocker — exact statement

> **BLOCKER: Full-fidelity VF5 → Western Heart model conversion (skeleton +
> skin weights + facial + textures, exported as GLB) is blocked on a Windows
> machine or VM running Autodesk 3ds Max with the chrrox import script —
> the only documented importer for the PS3 `*_obj.bin` format with skeleton
> and facial data. 3ds Max is Windows-only (Autodesk's SDK requirements list
> target operating systems Windows 10 x64 / Windows 11 for current 3ds Max;
> the 2026.2 release is "compatible with Windows 10+", rental-only), and
> this project's VM is Linux. There is no Linux build of 3ds Max and no
> proven Linux-native importer for the skinned format.**

Sources for the Windows-only claim (searched 2026-10-23):

- Autodesk 3ds Max SDK requirements table — every listed 3ds Max version's
  target OS is Windows (2025: "Windows 10 x64 / Windows 11"):
  https://help.autodesk.com/cloudhelp/2025/ENU/MAXDEV-Developer/files/about_the_3ds_max_sdk/sdk_requirements.html
- CG Channel, "Autodesk releases 3ds Max 2026.2" — "3ds Max 2026.2 is
  compatible with Windows 10+. It is rental-only.":
  https://www.cgchannel.com/2025/08/autodesk-releases-3ds-max-2026-2/

**Owner's standing decision on this blocker: "Get the software"** (owner,
pre-sweep, recorded in checkpoint `teardown-sweep-vf5.json`: extraction is
100%; WH conversion blocked on Windows 3ds Max per owner "Get the software").
That decision stands: the unblock is procuring/installing 3ds Max on a
Windows seat — not re-scoping the conversion to a lesser route.

Related in-flight work (checked 2026-10-23, do not duplicate): PR #713
"VF5 motion pipeline: Dural stance for Zen" (OPEN) and PR #704 "VF5 full
integration — van/wol renders + Wolf head fix" (OPEN) are other lanes'
work; neither removes the §3 blocker for skinned model conversion.

---

## 4. Integration plan (documented, NOT executed)

A future conversion lane starts here. Prerequisites: **a Windows seat with
3ds Max installed (owner: "Get the software") + this doc.** Nothing below was
done by this documentation lane.

1. **Set up the Windows seat.** Install Autodesk 3ds Max on Windows 10/11.
   On the same seat, also install QuickBMS and evaluate MikuMikuModel and
   Noesis (§2.3) — one seat serves every route.
2. **Pull the chrrox tooling.** Source the chrrox 3ds Max import script and
   `TXP.bms` from the Xentax thread cited in `TEARDOWN.md` (both listed
   there as not yet pulled). Log what was pulled, from where, and its
   license status in the lane's PR (research-to-repo rule).
3. **Stage the library on the seat.** Download the three tars from
   `vf5-model-library-v1` and **verify SHA-256 against §1.3 of this doc**
   before extracting. Also pull `obj_db.bin` + `tex_db.bin` from
   `vf5-ps3-v1` (needed for MikuMikuModel configuration and texture naming).
4. **Convert per character — isolated, one at a time.** Per the standing
   per-character isolation law (owner 2026-10-20): every character's
   skeleton, animations, and add-ons stay separate; no shared mutable rig
   state. For each fighter: `.farc` → `farc_extract.py` → chrrox import in
   Max (skeleton + facial) → textures via TXP.bms → export FBX → Blender →
   GLB. One character directory, one proof, one commit-sized unit at a time.
5. **Prove each character with your own eyes before wiring.** T-pose /
   bind-pose render of the *skinned, textured* GLB, viewed and confirmed
   (skeleton present, weights sane, textures applied) — a script exiting
   clean is not proof.
6. **Wire into Western Heart** to the acceptance standard already on record
   for this sweep: content **live in the playable build** (`game/`) —
   fighters usable in a real fight or the creation suite — following the
   PR #397 wiring standard and the precedents in PRs #379/#382/#385.
   Namespaced per character under the `virtual-soul` universe.
7. **Rename / canon.** All 18 VF5 fighter names and all 38 stage names are
   `NEEDED` in `RENAME-MAP.md` — WH proprietary names are owner-created; a
   lane never invents them. Apply owner-supplied names, log every
   old→new mapping in `RENAME-MAP.md`, and update the moveset JSONs and
   model paths to the canon names.
8. **Only then: privatize.** After steps 6–7 are complete and verified,
   the `vf5-model-library-v1` release (public today, §1.7) goes private
   per the owner instruction on record. Not before, and not as part of
   the conversion PR itself.
9. **Motion stays a separate lane** (§2.4). Model integration must not be
   reported as "VF5 done" while motion clips are absent; moveset JSONs
   carry `anim_ref` hooks for the retarget pipeline when motion lands.

---

## 5. Gate table

Gates as used for this game in this doc. Extraction-side gates (G1–G3) are
about getting the game's data out and understood; G4 is the blocked
conversion gate; G5–G6 are Western Heart-side.

| Gate | Meaning | State | Evidence |
|---|---|---|---|
| **G1 — Source secured** | Game dump acquired and verified | ✅ **PASS** | RAR verified 3,686,456,692 B; 8 chunks on `vf5-ps3-v1` (§1.2) |
| **G2 — Extraction** | Containers opened; full roster + stages extracted and stored | ✅ **PASS** | 19 fighter dirs + 38 stages + common on `vf5-ps3-v1` (89 assets) and organized in `vf5-model-library-v1` (API-verified §1.3); `VF5-VERIFICATION.md` |
| **G3 — Format decode** | Model/texture/motion formats understood | ⚠️ **PARTIAL** | `.farc` fully decoded (`farc_extract.py`, 79/79). `*_obj.bin` geometry decoded on Linux; **SKIN parsed, not converted**; TXP textures not decoded in-project; **motion format not decoded and motion data not in the release** (§2.4) |
| **G4 — Conversion to usable assets** | Skinned, textured GLBs for WH | ❌ **BLOCKED** | No skinned VF5 GLB exists. Known full route needs Windows + 3ds Max + chrrox script (§3). Static-geometry clay renders are not G4 output. |
| **G5 — WH integration** | Content live in the playable build | ⚠️ **PARTIAL (data only)** | 7 moveset JSONs + mechanics federation doc on `main`; **no VF5 fighter model live in `game/`**. Model side of G5 cannot start until G4 clears. |
| **G6 — Rename/canon + privatization** | WH names applied; release made private after integration | ❌ **NOT DONE (by design, sequenced last)** | All 18 fighter + 38 stage WH names `NEEDED` in `RENAME-MAP.md`; releases still public per owner sequencing (§1.7) |

**Bottom line:** VF5 extraction is done and proven (G1–G2, G3 partial).
Everything downstream of the model files waits on one thing: a Windows seat
with 3ds Max — owner's instruction: "Get the software."
