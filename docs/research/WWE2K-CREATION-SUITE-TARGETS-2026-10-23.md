# WWE 2K Creation-Suite File Targets — 2K25/2K26 Selective Pull + New OSS Tools (2026-10-23)

Research-only. No extraction executed. Owner-authorized selective pull: creation-suite files ONLY.

## Owner authorization (verbatim)

> "I goddamn own every fucking WWE 2K game bro... you could even pull from 2K26 or 2K25 if you wanted to because I own them bitches but yeah any of them whichever one will be easiest or best."

> "let's continue to research and pull stuff in related to all those areas"

Standing context: the WWE 2K creation system goes into Western Heart (CAW exception, owner-confirmed 2026-10-18). This doc makes the target list concrete per the playbook in `customization/` (PR #773) and the 2K19 pull plan in `customization/wwe2k-caw/PULL-PLAN.md`.

## 1. Recommendation: which game to pull from

| Game | Install size (verified) | Data layout | Extraction tooling | DRM friction | Verdict |
|------|------------------------|-------------|-------------------|--------------|---------|
| **2K19** | 50.96 GB (CSF, Archive.org) | Loose `pac/edit/*.pac` — fully documented in-repo | Mature: PAC Editor, WrestleMinus, rePac, CCT, Data Editor, Genesis suite | None | **EASIEST** — playbook exists, pipeline-proven |
| **2K25** | **102.47 GiB** on disk (SteamDB depot 2878961, build 20915020) | **15× `.cak` archives = 82.04 GiB** + 93× `.pck` audio = 19.92 GiB. No loose `.pac` ships. | `.pac` injection tooling mature (CCT/Data Editor/CakeTools/CakeHook); **public `.cak` unpacker not confirmed in this pass** | None on data files | Best balance once `.cak` extraction is solved |
| **2K26** | 120 GB required; ~122.6–128.2 GB installed (v1.04) | Same `.cak` generation expected (not yet manifest-verified) | Immature; main installers (Tribute, CakeView) Patreon-paywalled; exe-level tools broken | **Denuvo** — file reads OK, process injection blocked | BEST assets, HARDEST pull |

**Recommended phasing (recommendation, not a decision):**
1. **Phase 1 — 2K19** (easiest): run the existing `customization/wwe2k-caw/PULL-PLAN.md` end to end. Proves the pipeline.
2. **Phase 2 — 2K25**: resolve `.cak` extraction (see §4), then pull the edit-parts subset. No Denuvo; one year of community tooling.
3. **Phase 3 — 2K26**: newest assets (doubled creation suite: 200 CAW slots, 2,000 community images, deeper body/face morphing, two-tone hair, face-scan importing). Revisit when `.cak` tooling is proven and 2K26-specific tools mature.

The user owns all three on Steam — the pull reads from the owner's local Steam install (`steamapps/common/WWE 2K25/` etc.). No re-download, no archival hunting needed for 2K25/2K26.

## 2. Concrete file targets

### 2.1 WWE 2K19 — verified targets (from in-repo playbook)

Base: `<steam>/steamapps/common/WWE 2K19/` (~50.96 GB). Copy ONLY these:

| Category | Path | Contents | Format |
|----------|------|----------|--------|
| Body templates | `pac/edit/bbtemplate.pac` | Male/female base bodies, morph targets | Yuke's `.pac` archive |
| Default parts | `pac/edit/default.pac` | Starter heads, bodies, attire | Yuke's `.pac` |
| Edit parts | `pac/edit/edit.pac` | Full customization part library (largest) | Yuke's `.pac` |
| Sample parts | `pac/edit/sample.pac` | Preset samples | Yuke's `.pac` |
| Head parts | `pac/edit/ch/` | Masks, face accessories, normals | `.pac` per part |
| Body parts | `pac/edit/body/` | Torso, limb meshes | `.pac` per part |
| CAW metadata | `pac/profile/profile_dat.pac` | Hometown, CAW IDs, slot data | Yuke's `.pac` |
| Reference bodies | slots 256 (male) / 257 (female) default CAW | Cutscene base bodies → full character templates | in `pac/ch/` |

Extraction: PAC Editor / WrestleMinus / rePac (community `.pac` tools); the 2KLive **Genesis** suite (2026, github.com/2KLive/Genesis) handles 2K19 `.pac` import with automatic chunk regeneration. Expected selective-pull size: single-digit GB (exact figure measured at extraction — see §4 method).

### 2.2 WWE 2K25 — SteamDB-verified layout (AppID 2878960)

- Depot **2878961**: 102.47 GiB on disk / 99.28 GiB download; public build 20915020 (2025-11-24).
- File-type breakdown (SteamDB manifest 4792023227088475130):
  - **`.cak`: 15 files, 82.04 GiB** ← ALL game data incl. creation-suite parts lives here
  - **`.pck`: 93 files, 19.92 GiB** ← Wwise audio banks — **EXCLUDE per §3**
  - exe: 4 files, 513.27 MiB — EXCLUDE; dll/com — EXCLUDE
- Engine tech: Oodle SDK compression, Bink Video (SteamDB detected).
- Save data (for CAW slot research, not assets): `C:\Program Files (x86)\Steam\userdata\<id>\2878960\remote`; config: `Documents\WWE2K25\config.ini`.
- Face-scan template pipeline (community): 512×512 "Face Photo" upload via wwe2k.com/upload → in-game Image Manager. (Reference for our suite's face-scan import design; GNM already covers parametric faces.)
- **Selective-pull target**: the creation-suite subtree *inside* the `.cak` archives — expected analogues of the 2K19 `pac/edit/*` set (body templates, default/edit/sample parts, head/body parts, CAW metadata). Exact inner paths are determined at extraction time once a `.cak` unpacker is confirmed (§4). The game still reads loose `.pac` overrides via the `_mods` folder (CakeTools/CakeHook injection path), which confirms the inner format remains `.pac`-family.

### 2.3 WWE 2K26 — verified facts (AppID 3717070)

- Released 2026-03-13. Steam storage requirement: **120 GB**; installed ~122.6–128.2 GB (v1.04).
- **Denuvo** on PC: blocks exe-level tampering (memory editors, Cheat Engine, exe hooks). File-based `.pac` mods via `_mods` folder remain possible — file reads are unaffected.
- Creation suite upgrades (the "best" argument): CAW slots **doubled to 200**, community image capacity **doubled to 2,000**, deeper body + face morphing tools, **two-tone hair color blending**, expanded MySUPERSTAR builder with **face-scan importing**.
- Tooling friction: primary mod installers (Tribute, CakeView) require Patreon subscriptions; 2K26-specific extraction tooling immature as of this writing.
- Selective-pull target: same class as 2K25 (creation-suite subtree inside data archives). Manifest/file-type breakdown not yet pulled from SteamDB — do at extraction phase.

### 2.4 Size-measurement method (extraction phase)

On the owner's PC (or any machine with the Steam install), before copying anything:
`Get-ChildItem -Recurse <game>\pac\edit | Measure-Object -Property Length -Sum` (2K19),
or list `.cak` members once unpacked (2K25/2K26). Copy ONLY the §2 file set to the store (TeraBox `/WesternHeart/teardowns/wwe2k/` per the PULL-STRAIGHT-TO-STORE law). Do not stage the full game on the VM (disk constraints per playbook).

## 3. What the pull must NOT touch

- **Full game binaries**: exes, DLLs (2K25: 513 MB exe set) — never copied, never committed.
- **Audio**: 2K25's 93× `.pck` Wwise banks (**19.92 GiB**) — excluded outright.
- **Video**: Bink cutscenes/movies.
- **Arenas, modes, The Island, DLC/Ringside Pass content** — creation suite ONLY.
- **No copyrighted/leaked game files in the public repo** (standing owner rule): extracted data lives on the private store (TeraBox), never committed to `mhvnsnt/western-heart`. Only our *derived* JSON catalogs/manifests (part names, slot maps, morph parameter schemas) go in `customization/`.

## 4. Extraction toolchain status + open items

| Game | Unpack | Inspect/edit `.pac` | Status |
|------|--------|--------------------|--------|
| 2K19 | PAC Editor / rePac / Genesis | WrestleMinus, CCT, Data Editor | Ready — documented in-repo |
| 2K25 | **`.cak` unpacker — UNCONFIRMED public tool** (open item #1) | CCT / Data Editor / CakeTools / CakeHook (`.pac` injection via `_mods`) | Blocked on open item #1 |
| 2K26 | Same as 2K25 | Same as 2K25, minus exe-level tools (Denuvo) | Blocked on open item #1 + tooling maturity |

**Open item #1**: confirm a public `.cak` unpacker (check smacktalks.org Tools & Resources; fallback: document the `.cak` header from the owner's install and write the unpacker as its own build task — do NOT hand-guess the format per the no-guessing law).
**Open item #2**: 2K26 SteamDB depot/file-type breakdown (same manifest method as §2.2).
**Open item #3**: per-file sizes of the 2K19 `pac/edit/` set measured from the owner's install (fills the size column the owner will want before approving the copy).

## 5. New open-source customization tools (2026 survey)

Checked against the repo's existing tool map (`customization/tools/`: GNM; `tools/open-source/`: TKMovesets, Wiggle 2/Wiggle Bones, Keemap, GameRig; plus in-repo Build-A-Bod, Fluid Painter, NaughTyRig, MPFB 2). Only genuinely-new items reported.

### 5.1 GarmentCode — procedural parametric garments (NEW, recommend)

- **What**: modular programming framework for designing *parametric sewing patterns* (Korosteleva & Sorkine-Hornung, ETH Zurich). Garments as code: hierarchical components, continuous/categorical/dependent parameters, retarget to different body shapes automatically. Ships `pygarment` + GUI configurator + 115k-garment synthetic dataset (GarmentCodeData).
- **Source**: https://github.com/maria-korosteleva/GarmentCode — **MIT License**, active (1,512 commits, not archived).
- **Suite menu**: **ATTIRE** (unified attire/garment system per the TOOL UNIFICATION LAW). Generates wrestling-gear sewing patterns (singlets, tights, jackets, trunks) parametrically fitted to the suite's body sliders — replaces hand-modeled attire variants. Pairs with the NvidiaWarp-GarmentCode cloth simulator, or bake → Blender cloth.
- **CPU/headless**: YES — pattern generation is pure Python, headless-safe. Drape simulation needs GPU (NVIDIA Warp) or a Blender cloth pass; pattern output alone is CPU-fine.
- **Watch**: Design2GarmentCode (2025, Style3D) — LLM turns design concepts into GarmentCode programs; research-grade, needs an LLM API key. Revisit, don't depend.

### 5.2 UniRig — automatic skeleton + skinning (NEW, recommend)

- **What**: SIGGRAPH 2025 (Tsinghua + Tripo/VAST AI Research) — one autoregressive model predicts a topologically valid skeleton *and* per-vertex skinning weights for arbitrary meshes (humans, creatures, objects). Directly attacks the repo's standing pain point (bad skin weights on Pantera/Yukihyo/Leopard King; "decrypted backwards" root-cause work).
- **Source**: https://github.com/VAST-AI-Research/UniRig — **MIT License**, 1,873 stars, active. Skeleton + skinning checkpoints released (Hugging Face `VAST-AI/UniRig`); successor SkinTokens announced. CLI: `generate_skeleton.sh` / `generate_skin.sh` / `merge.sh`; inputs `.obj/.fbx/.glb/.vrm`.
- **Suite menu**: **RIGGING** — unify with GameRig/NaughTyRig per the TOOL UNIFICATION LAW (three access layers: unified rigging system, each tool standalone, universal front-end).
- **CPU/headless**: CLI is headless-capable; **GPU strongly recommended** (PyTorch + spconv/torch_scatter/flash_attn stack). CPU inference works but is slow — fine for one-off Tripo-intake rigs, not batch.
- **Caveat**: weights download from Hugging Face on first use (same pattern as GNM's gated weights — document, don't commit).

### 5.3 Surveyed and NOT recommended

- **Fibric** (Houdini yarn-level cloth, Oct 2026) — commercial/paid. Skip.
- **HumGen3D** (Blender human generator) — free but proprietary, not open source. Note only.
- **Charakuru Kit** (illustration→VRM via AI agent) — commercial-use restrictions above ¥100M revenue/funding; depends on paid outside services (Tripo credits). Skip.
- **OpenVTO** (AI virtual try-on) — image-space try-on, not game-asset garment creation. Skip.
- **DressCode / ChatGarment** (text→garment research) — no stable release to wire in; watch.
- **Fay / SentiAvatar / LessUp meta-human** (digital-human frameworks) — dialogue-avatar stacks, not character-creation tooling. Skip.
- **Blender built-ins** (cloth sim, hair curves, Rigify) — already available to the suite via the Blender 4.0.2 toolchain; not new tools.

## 6. Next steps (build phase, not this PR)

1. Owner picks phase order (§1 recommendation: 2K19 → 2K25 → 2K26).
2. Resolve open items #1–#3 (§4) — `.cak` unpacker confirmation is the critical path for 2K25/2K26.
3. Execute the selective pull (copy §2 file set to TeraBox; never to the repo, never full game).
4. Pull GarmentCode + UniRig into `customization/tools/<name>/` per the tooling conventions (`UPSTREAM-COMMIT.txt`, `LICENSE.<name>`, `wh_<name>_wireup.py`, `WH-INTEGRATION.md`) and wire into the ATTIRE and RIGGING menus.

## Sources

- SteamDB WWE 2K25 app/depots: https://steamdb.info/app/2878960/depots/ (depot 2878961: 102.47 GiB; 15× .cak = 82.04 GiB; 93× .pck = 19.92 GiB; build 20915020)
- WWE 2K26 Steam: https://store.steampowered.com/app/3717070/WWE_2K26/ (120 GB; Denuvo; creation-suite doubling; face-scan importing)
- 2K26 Denuvo/modding impact: https://www.operationsports.com/how-wwe-2k26-denuvo-drm-will-affect-pc-mods/
- 2K25 face texture template: https://www.operationsports.com/wwe-2k25-face-texture-template-guide/
- Genesis 2K19 suite: https://github.com/2KLive/Genesis
- GarmentCode: https://github.com/maria-korosteleva/GarmentCode (MIT)
- UniRig: https://github.com/VAST-AI-Research/UniRig (MIT); paper https://arxiv.org/html/2504.12451v1
- In-repo: `customization/wwe2k-caw/PULL-PLAN.md`, `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`, `teardown/wwe-2k/WWE2K-TERABOX-SPEC.md`, `customization/tools/README.md`, `docs/research/OPEN-SOURCE-PULL-INS-2026-10-19.md`
