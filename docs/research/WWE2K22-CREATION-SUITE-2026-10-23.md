# WWE 2K22 — Creation Suite / Animation / Rig / Community Creations: Format Research

**Date:** 2026-10-23
**Author:** DoggByte (research subagent)
**Owner instruction:** "Perfect for animations and rigs and customization and creation suite/community creations"
**Repo:** `mhvnsnt/western-heart` (PUBLIC)

---

## 0. Method & provenance

- This VM has **no Steam credentials**, so no game files were pulled and none were examined locally. **No pull was faked.**
- All format claims below come from **publicly documented modding knowledge**: modding-community tutorials, tool READMEs/docs, and SteamDB. Each claim is cited; URLs are in the Sources section.
- A separate **DepotDownloader pull of WWE 2K22 is already in progress on another machine — do not duplicate it.** This document is the *format map + extraction plan* for the crew that has the files.
- **"Researched" vs "awaits file pull"** is separated throughout. Where no public knowledge exists (animation clips, skeleton/rig formats), that is stated as a gap rather than guessed.

---

## 1. Game identity & depot layout (verified on SteamDB, 2026-10-23)

| Fact | Value | Source |
|---|---|---|
| Steam App ID | 1255630 | SteamDB |
| Content depot | **1255631** "Windows 64-bit Bailey Content" | SteamDB depots page |
| Size | **51.92 GiB on disk / 52.11 GiB download** | SteamDB |
| Current public build | 11167313 (built 2023-05-05) | SteamDB branches |
| Redist depot | 228988 (VC 2019 runtime — not needed for assets) | SteamDB |
| Developer | Visual Concepts | SteamDB |
| Store status | **Retired at publisher request** (no longer on the Steam store) | SteamDB — still downloadable by owners; the in-progress pull uses an owned license |
| Detected SDKs | **Bink Video SDK** (cutscenes/titantrons = `.bk2`), **Oodle SDK** (chunk compression) | SteamDB "Detected Technologies" |

Extraction-plan implication: the crew's DepotDownloader pull targets **app 1255630 / depot 1255631 only**. There is exactly one content depot — no DLC depots to chase. Expect ~52 GB download, ~52 GB on disk.

---

## 2. Creation suite structure (researched — publicly documented)

### 2.1 Entry flow: Persona Creator
Creating a Superstar starts with a **Persona** (template) screen, then weight class + archetype (per the Smackdown Hotel official-details roundup and the Prima Games CAW guide):
- **Weight classes:** Cruiserweight, Light Heavyweight, Heavyweight, Super Heavyweight
- **Archetypes:** Striker, Technician, Powerhouse, High Flyer (the "Persona Creator" pre-built themes)
- Persona categories offered as templates: Wrestling, Streetwear, Battlewear, Cosplay, Formalwear, Future, Past, Sports, Entertainer, Occupations (FPS Index guide)
- Scale claim: **nearly 10,000 customizable components** in Create-A-Superstar (Smackdown Hotel, from 2K's pre-release details)

### 2.2 Face
Sub-menus (FPS Index guide):
- **Face Template** — base head sample from a large list
- **Facial Parts** — eyes, eyebrows, nose, cheek, mouth, jaw, ears, eyelids, lips, teeth: individually selectable + position/size adjustable
- **Face Deformation** — morph sliders per facial region
- **Face Photo Capture** — uploads a real photo onto the CAW face; aligns via mouth/lips first, then eyes/brows/nose; includes a color picker for skin-tone matching (Prima Games guide; Attack of the Fanboy guide)
- Extras: **moveable and immovable scars**, face paint, face tattoos (Revelleution guide); makeup/lipstick

### 2.3 Body
Sub-menus (FPS Index guide):
- **Body Type** — reported as Thin / Medium / Large / Heavy (guide text; distinct from the entry-flow weight classes, which drive height/weight/archetype stats)
- **Skin Color**, **Veins** (vein-visibility slider — the guide's author preferred the veiny look)
- **Body Hair**, **Body Tattoos / Scars** (upper + lower body, incl. back and hands)

### 2.4 Attire
Sub-menus (FPS Index + Revelleution guides):
- **Attire Type, Appearance, Clothing, Parts Color, Import Parts, Select Persona**
- Head: masks, hoods, hats, glasses, piercings
- Upper body: brassieres / tops 1 / tops 2 (layerable), jackets, outfits, elbow pads, upper/lower arms, hands, nails, fingers, chokers, necklaces, backpacks, wings — pieces mirrorable left↔right
- Lower body: trunks, wrestling tights, bottoms, belts, knee pads, socks, boots/shoes
- Each part carries **recolorable layers** (the CAW "formula" community documents parts as e.g. `Gloves 6 (43,0,0)` — part ID + color values), plus per-part **materials**
- Create-A-Championship documents the same layer model explicitly: parts get move/size/rotate/flip, materials, and colored layers with outline/drop-shadow options (Revelleution championship guide) — same engine, same paradigm

### 2.5 What this means for our creation suite
The in-game CAW is a **parts-list + per-part transform/color/material stack + morph-slider set**, not bespoke meshes per wrestler. Our suite's import target should therefore be:
1. The raw part meshes (from `.pac` chunks — §3),
2. The part catalog/IDs (the community's "formula" numbering),
3. The morph-slider definitions (face deformation regions, body regions),
4. The layering/material model (per-part color layers + materials).

---

## 3. Asset container formats (researched — public modding knowledge)

### 3.1 `.pac` / `.ch.pac` / `pach` — wrestler & arena containers
- WWE 2K-series assets ship as **`.pac` containers holding `pach` chunks**; wrestler models live under **`pac\ch`** and CAW/edit parts under **`pac\edit\ch`** (paths documented in the Smacktalks modding forums and the "WWE 2K18+" Data Editor docs — the tool's unlock manager checks exactly `\pac\edit\ch` and `\pac\ch` for wrestler pac files).
- Legacy X-PacKer documentation (PS3-era, but it describes the same family of containers): a "Main Pac" contains multiple PACH files; PACHs hold model files + texture archives; chunks were historically `bpe`-compressed and needed decompression before editing. **Caveat:** this is documented for the PS3 generation; for the PC/2K22 generation the exact chunk codec is **not publicly documented** — SteamDB's Oodle detection suggests Oodle-compressed chunks, but that awaits verification on the pulled files.
- Modern modding suite **Genesis** (2KLive, for WWE 2K19 — architecture reference, *not* 2K22-compatible) documents **`.ch.pac` variants including EMD and HSPC** and handles their "chunk regeneration" on import (Genesis README). Expect the same variant family in 2K22's `pac\ch`.
- Naming convention for attire chunks (documented in X-PacKer tutorials for the series): within a character pac, **in-ring attire chunks end in `...2`, entrance attires end in `...4`**; pattern `000 + model number + attire` (e.g. `00013602`, `00013612`, `00013622`; entrance: `00013604`, `00013624`).
- Render/portrait IDs live in **`ltag_typeb.pac`-family files** as 4-byte ID slots; the documented render-swap workflow is hex-editing those ID slots (Smacktalks "Replacing Renders Without X-Packer" tutorial).

### 3.2 Mod injection path (how the community loads modified assets)
- **CakeHook / CakeTools**: injects `.pac` files via a **`_mods` folder** — file-based modding without touching binaries (Operation Sports, on the 2K26/Denuvo article; applies to the 2K22-era pipeline).
- **WWE 2K18+ / Data Editor** (Smacktalks): installs downloaded `.pofo`/`.moveset` files and **rebuilds the def file**; has roster/slot management, string editor, unlock/gender/DLC managers.
- **CawModdingTool**: referenced in install guides as the tool for importing/applying modded CAW-related files.
- **Genesis** (2KLive): the modern reference implementation — roster management, drag-and-drop `.pac` import with automatic chunk regeneration, live Pofo editor, Moveset editor (18 move categories), entrance editor, string editor, GFX importer, JSON portability. **2K19 only**, but it is the best public documentation of the *data model* the 2K22 tools operate on.

### 3.3 Video
Titantrons/cutscenes are **Bink `.bk2`** (install guides list `.bk2` among mod-replaceable file types; Bink Video SDK detected on SteamDB).

---

## 4. Animations (researched — with explicit gaps)

### What is publicly documented
- **Movesets are data, not clips.** The modding community's documented layer is the **moveset/pofo system**: movesets are tables of move IDs across categories (Genesis documents **18 move categories** for the 2K19-era engine), and the Smacktalks "2K20 Data Breakdown" documents that a `.moveset` file bundles **moveset + entrance + victory data**, researched via in-game editors + Cheat Engine memory tables. The same data model is expected in 2K22.
- Individual **moves/animations are referenced by internal IDs** (the community's string-sheet/spreadsheet documents name↔ID mappings). Harvesting the *full move-ID list* from 2K22's data is the documented path to the "moveset library" the owner wants.

### What is NOT publicly documented (awaits file pull)
- **No public tool extracts 2K22 animation clips to an editable format.** Searches of the modding community (Smacktalks, tool READMEs, modding wikis) turned up no documented animation-clip extractor, no clip container spec, and no published bone-track format for the 2K22 generation.
- The extraction plan must therefore treat animation clips as **format-RE work on the pulled files**: locate the clip containers (candidates: inside `.ch.pac` chunks or a separate animation bank), identify the codec (Oodle-compressed per SteamDB detection), and document per-bone track layout empirically.
- Fallback deliverables that need no clip decoding: the complete move-ID inventory, the 18-category moveset schema, entrance/victory data layout, and per-wrestler moveset dumps — all achievable via the Data-Editor-style pofo/moveset path.

---

## 5. Rigs / skeletons (researched — with explicit gaps)

- **No public skeleton/rig format documentation exists for the 2K22 generation.** The community's documented model pipeline is: extract model chunks from `.pac` → convert for use in 3D tools → re-inject. No published bone-hierarchy spec, skin-weight layout, or rig interchange format was found.
- **Awaits file pull:** once the crew has the `.ch.pac` files, the work is: (a) identify the model-chunk format inside pach chunks, (b) recover the skeleton hierarchy and skin weights empirically, (c) document the bind pose and bone naming. This is the highest-value RE item for the owner's "animations and rigs" goal.
- Related public note: the CAW body-type system (§2.3) implies the base bodies are **morph/slider-driven variants of a shared rig** rather than per-wrestler skeletons — consistent with a single humanoid rig family. Verify on pull.

---

## 6. Community Creations format (researched — with explicit gaps)

### What is publicly documented
- Community Creations is **server-based** (2K's servers): uploads/downloads happen in-game via **Online → Community Creations**; the **day-one patch (~6 GB) enabled online features including Community Creations** (ExpertBeacon; TwistedVoxel).
- **Face Photo / image upload path** (Attack of the Fanboy guide): create a **2K Account** → upload selfie/CAW file on 2K's upload site → in-game **Online → Community Creations → Image Manager → Incoming** → image lands in the **Local** tab → applied via **Creations → Superstar → Face → Face Photo → Downloaded**. Uploaded custom images are also usable in Create-A-Championship front plates (Revelleution championship guide).
- Shared content types per the community: individual **attires, logos/images, entrance themes, movesets** — historically a **parts-bin model** (share elements, assemble locally) rather than whole-superstar downloads.

### What is NOT publicly documented (awaits file pull / live capture)
- The **wire/download package format** of Community Creations items is not publicly documented anywhere found. It is a server protocol + signed packages; reverse-engineering it is out of scope for a file pull and would require live traffic capture against 2K's (possibly sunset) servers.
- Practical recommendation: treat Community Creations as a **reference library, not an extraction source**. The harvestable equivalents are all local: CAW part meshes (`.pac`), the part catalog, moveset/pofo data, and the Image Manager's local image store (inspect the save-data layout on pull).

---

## 7. Public tool inventory (for the extraction crew)

| Tool | What it does | 2K22 status | Source |
|---|---|---|---|
| X-PacKer | Legacy `.pac`/pach extract/inject; documents the container/chunk/attire-naming model | **PS3-era** — container knowledge still relevant, codec details not current | sf4mods X-PacKer guide; Smacktalks tutorials |
| WWE 2K18+ / Data Editor | pofo/moveset install, def-file rebuild, roster/slot/string/gender managers | Series tool family; 2K22-era equivalents needed | Smacktalks tool thread |
| CawModdingTool | Imports/applies modded CAW files | Referenced in 2K22 install guides | mod install guide |
| CakeHook / CakeTools | `_mods`-folder `.pac` injection at load, no binary patching | 2K22-era standard | Operation Sports |
| Genesis (2KLive) | All-in-one suite: `.pac` import w/ chunk regen, Pofo/Moveset/Entrance/String/GFX editors, JSON portability | **2K19 only** — use as data-model reference, not as a 2K22 tool | GitHub 2KLive/Genesis README |
| Community "formulas" | Text recipes: part IDs + color values + morph numbers per CAW | Era-spanning community knowledge; gives us the part-catalog numbering | caws.ws / Smacktalks CAW threads |

---

## 8. Extraction plan for the crew (precise, file-level)

**Do not re-pull:** the DepotDownloader pull (app 1255630, depot 1255631, ~52 GB) is already running on another machine. This plan starts from the pulled tree.

### 8.1 Directory & file targets (in priority order)
1. **`pac\ch\*.ch.pac`** — every wrestler model: mesh chunks, texture archives, and (to be determined) animation/rig data. Highest priority: full inventory with per-file sizes and chunk listings.
2. **`pac\edit\ch\`** — CAW/edit parts: the creation-suite parts library. Catalog every part file; this is the raw material for our creation suite.
3. **`ltag_*.pac`** — render/portrait ID tables (4-byte ID slots); needed for the select-screen/portrait pipeline.
4. **Attire/chunk naming audit** — verify the `...2` = in-ring / `...4` = entrance convention holds for 2K22 chunks; record the actual pattern.
5. **`.bk2` files** — titantron/cutscene videos (Bink); low priority for the suite but trivially listable.
6. **pofo/moveset data stores** — locate where the game keeps profile + moveset tables (Data Editor docs describe the install/def-rebuild flow; find the backing files in the pulled tree).
7. **Save-data layout** — Steam userdata save files: CAW storage, Image Manager local images, downloaded Community Creations cache. Document offsets/structure empirically.
8. **Chunk codec identification** — first bytes of pach chunks vs. known Oodle/Kraken signatures (SteamDB detects Oodle SDK). If Oodle, the crew needs an Oodle decompressor to get at model/animation payloads.

### 8.2 Asset-type harvest list (what "done" looks like)
- [ ] Complete `.ch.pac` inventory (wrestler count, per-file chunk list, sizes)
- [ ] CAW parts catalog: part IDs ↔ files ↔ categories (face/body/attire), mapped to the §2 menu tree
- [ ] Texture formats per archive (DDS variants, e.g. BC7 per the render-swap tutorial's DXGI note)
- [ ] Move-ID inventory + 18-category moveset schema (via pofo/moveset dumps)
- [ ] Morph-slider inventory (face deformation regions, body regions) — from data files or UI-string tables
- [ ] Skeleton hierarchy + skin-weight layout (RE on model chunks) — **blocked until chunk decode works**
- [ ] Animation clip containers located; clip format documented — **blocked until chunk decode works**
- [ ] Save-file CAW/Image-Manager structure documented

### 8.3 Explicitly out of scope for the file pull
- Community Creations server package format (server-side, undocumented; see §6)
- Live 2K Account upload-site protocol

---

## 9. Researched vs. awaits-file-pull

| Item | Status |
|---|---|
| Depot layout (1255631, 51.92 GiB, build 11167313, Oodle+Bink SDKs) | ✅ Researched (SteamDB) |
| Creation-suite menu/part/layer/morph structure | ✅ Researched (guides) |
| `.pac`/pach container model + attire naming | ✅ Researched (legacy docs + Genesis README); chunk codec for 2K22 generation ⚠️ awaits pull |
| Mod injection path (`_mods` + CakeHook, Data Editor def rebuild) | ✅ Researched |
| Moveset/pofo data model (18 categories, move IDs) | ✅ Researched (data-model level) |
| Animation clip extraction | ❌ No public knowledge — awaits pull + RE |
| Skeleton/rig format | ❌ No public knowledge — awaits pull + RE |
| Community Creations package/download format | ❌ Server-side, undocumented — treat as reference library only |
| CAW save-file / Image Manager local layout | ⚠️ Partially documented path; structure awaits pull |

---

## 10. Sources

- SteamDB — WWE 2K22 Depots (app 1255630): https://steamdb.info/app/1255630/depots/ — depot 1255631, 51.92 GiB, build 11167313, Bink Video SDK + Oodle SDK detected
- Smackdown Hotel — "WWE 2K22 New Gameplay and Creation Suite Official Details": http://www.thesmackdownhotel.com/news/wwe2k22/wwe-2k22-new-gameplay-and-creation-suite-official-details — Persona Creator, ~10,000 components, Super Heavyweight body type
- Prima Games — "WWE 2K22: Create a Superstar guide — Face photos and CAWs": https://primagames.com/gaming/wwe-2k22-caw-create-a-superstar-guide — weight class/archetype flow, Face Photo alignment, attire part usage
- FPS Index — "WWE 2K22 - How to Create a Superstar Guide": https://fpsindex.com/wwe-2k22-how-to-create-a-superstar-guide-tutorial-for-beginners/ — Persona list, Face/Body/Attire sub-menus, body types, clothing categories
- Revelleution — "WWE 2K22: Beginner's Guide to Create a Superstar": http://www.revelleution.com/wwe-2k22-beginners-guide-to-create-a-superstar-wwe2k22/ — scars/tattoos/face paint, layered attire pieces, mirroring
- Revelleution — "Beginner's Guide to Create a Championship": https://www.revelleution.com/wwe-2k22-beginners-guide-to-create-a-championship-wwe2k22/ — part layer/material/color model
- Attack of the Fanboy — "WWE 2K22 - Create-A-Wrestler Face Photo Guide": https://attackofthefanboy.com/guides/wwe-2k22-create-a-wrestler-face-photo-guide/ — 2K Account upload → Image Manager → Incoming → Local tab flow
- Operation Sports — "How WWE 2K26 Denuvo DRM Will Affect PC Mods": https://www.operationsports.com/how-wwe-2k26-denuvo-drm-will-affect-pc-mods/ — CakeTools/CakeHook `_mods`-folder `.pac` injection
- Smacktalks — "Replacing Renders Without X-Packer": https://smacktalks.org/forums/topic/63174-replacing-renders-without-x-packer/ — `ltag_typeb.pac` 4-byte render ID slots, BC7/DXGI texture note
- Smacktalks — "X-Packer 9 Tutorial: Adding Mods Using the Misc Pac Editor": https://smacktalks.org/forums/topic/45665-x-packer-9-tutorial-adding-mods-using-the-misc-pac-editor/?tab=comments — pach attire naming (`...2` in-ring / `...4` entrance)
- Smacktalks — "WWE 2K20 Data Breakdown and Analysis": https://smacktalks.org/forums/topic/71971-wwe-2k20-data-breakdown-and-analysis/?do=findComment&comment=966687 — `.moveset` = moveset+entrance+victory data; pofo/moveset memory research method
- Smacktalks — "WWE 2K18+ Ver: 1.2.0": https://smacktalks.org/forums/topic/69369-wwe-2k18-ver-120-super-string-editor-added/ — Data Editor: pofo/moveset install, def rebuild, `\pac\edit\ch` + `\pac\ch` slot checks
- 2KLive/Genesis (GitHub): https://github.com/2KLive/Genesis — `.ch.pac` variants (EMD/HSPC), 18 move categories, Pofo/Moveset/Entrance editors (2K19-only; data-model reference)
- sf4mods — "How to work with Xbox 360 PAC files using X-PacKer": http://sf4mods.blogspot.com/2010/07/how-to-work-with-xbox-360-pac-files.html — Main Pac → PACH → model files + texture archives; bpe compression (legacy)
- ExpertBeacon — "How Much Storage Is WWE 2K22 PS5?": https://expertbeacon.com/how-much-storage-is-wwe-2k22-ps5/ — 47 GB base + ~6 GB day-one patch enabling online/Community Creations
- caws.ws / Smacktalks CAW threads (e.g. https://smacktalks.org/forums/topic/3813-lots-of-different-caws-inside/) — community CAW "formula" format: part IDs + color/morph values
