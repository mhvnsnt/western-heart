# T7 Steam prep — research report (2026-10-23)

Prep work for the authorized Tekken 7 Steam pull (user bought T7 on Steam;
game-ownership rule = authorization). Everything below was verified from
public sources — no Steam login used, no EXE inspected, no paid-game depot
touched.

## 1. Depot verification (steamdb.info, public)

| Claim | Result |
|---|---|
| Steam AppID | **389730** — confirmed via store page, SteamDB, third-party trackers |
| Windows content depot | **389731** — "389730 Windows 64-bit TEKKEN 7 Content" |
| Cross-package check | Depot 389731 appears in FOUR independent SteamDB package pages: base game (Sub 74007), Originals Edition (Sub 643882), Ultimate Edition (Sub 302917), Definitive Edition (Sub 643883). Single content depot for all of T7. |
| Last depot update | 7 March 2023 (per SteamDB package pages) |
| Pak path | `TekkenGame/Content/Paks/` — confirmed by the CDDTreborn modding wiki (author's own Paks path) and multiple mod-install guides |

## 2. AES key status — the big finding: NO KEY NEEDED

CDDTreborn/Tekken7_PC-Modding-Guides wiki (Umodel quick-start, public):
**"Tekken 7 has no game encryption."** T7's paks open with `repak unpack`
and no `--aes-key`. The only encrypted T7 content is Geese (MRY) and Noctis
(MRZ) DLC files (per-file encryption, "need additional tools") — neither is
in our pull scope. Documented in `tools/depot-pull/FMODEL.md` with the
rotation-check order (wiki → TekkenMods → Modding Zaibatsu Discord) in case a
future patch ever encrypts the paks.

This is BETTER than the T8 situation (T8 needs a community AES key + .usmap):
the T7 pipeline has one fewer secret to manage and no key-rotation risk today.

## 3. Pak layout — shared chunks, NOT per-character files

T7's depot ships numbered chunk paks under `TekkenGame/Content/Paks/`
(UE4 `_P.pak` convention). DLC characters (Eliza, Geese, Noctis, Anna, Lei,
Marduk, Armor King, Julia, Negan, Ganryu, Leroy, Fahkumram, Kunimitsu, Lidia)
arrived through the SAME depot 389731 — there are no per-character depots or
per-character paks. Consequence: **DepotDownloader filelists cannot isolate
Law/Lars at the depot level** — the `-filelist` regex matches depot file
paths, and no depot file is "Law's pak".

Design decision (documented in GAME-TARGETS.md + extraction doc):
- `t7-law-lars.txt` / `t7-full-roster.txt` pull the paks (`regex:.*\.pak$`,
  same pattern as the existing `paks-only.txt`).
- Fighter isolation happens POST-UNPACK via in-game paths
  (`Game/Character/Items/Mesh/<CODE>/`, codes LAW/LAR/MAR…), or USER-SIDE via
  the new `t7-find-character-paks.bat` (repak list + code grep → upload only
  matching paks). This keeps the user's upload to a few GB instead of ~47 GB.

## 4. Asset identification (community-verified paths)

From the CDDTreborn wiki (two pages: Umodel quick-start + Basic Modding
Information):

- In-game root `Game/Content` (pak prefix `TekkenGame/Content/`); UE4 root `Content/`.
- Character meshes: `Game/Character/Items/Mesh/<3-LETTER-CODE>/` with
  per-part subfolders (Upper, Lower, Full_body, Head, Face…).
- Prefixes: `SK_` skeletal mesh, `SKT_` skeleton, `SM_` static mesh,
  `PA_` physics asset; textures `T_*` with `_D/_N/_M/_R/_S/_E` suffixes.
- Character items (CI/CCI/CS/aura/effect): `Game/Character/Items/...` —
  umodel "save package", not plain export.
- UI art: `Game/Content/UI_common/Texture2D/ReplaceImages`, `CS_*` folders =
  character-select panels/portraits (directly feeds the user's select-screen
  rebuild directive).
- Stages: `Game/Content/Maps` (`stgXX_geom.umap`), meshes
  `Game/Content/Stage/stgXX`; full stage code table on the wiki.
- Audio: `Game/Content/WwiseAudio/Windows/`.
- Animation asset paths were NOT pinned down on the wiki pages read —
  flagged as "confirm in umodel at pull time" in the extraction doc.
- The wiki's character-code list is missing Julia/Zafina codes — flagged likewise.

## 5. Tool verification (headless pipeline)

| Tool | Role | Verified |
|---|---|---|
| repak (trumank) | unpack + `repak list` (no AES for T7) | CLI confirmed from project README (`repak list mod.pak`, `repak unpack --aes-key …`) |
| umodel (Gildor) | mesh/animation export, Tekken 7 profile | GUI path community-documented (UE4 → Tekken 7 override); CLI batch `-path -game -export -out` per UEViewer docs; no official Linux build → Windows or Wine |
| FModel | interactive fallback (Windows) | no `.usmap` needed for T7 (unlike T8) |
| CUE4Parse (FabianFG) | scripted cross-platform asset reads | .NET library; crew has built it before |
| UEFormat (h4lfheart) | Blender import of `.psk/.uemodel/.ueanim` | per existing FMODEL.md |

## 6. Moveset caveat (kept honest)

T7's native moveset binary format is NOT publicly documented (unlike T3's).
The Steam pull unblocks models/skeletons/animations/textures/UI/stages/audio;
per-move frame data continues from `docs/t7t8-reference/frame-data-t7/`
(`law.json`/`lars.json` already banked) + the TTT2/T3 moveset lanes. Native
T7 moveset-binary reverse-engineering is logged as an open research item, not
a blocker for the Law/Lars lane.

## 7. Disk reality

Full T7 depot ≈ 47 GB (per TEKKEN7-ROSTER-COVERAGE.md). VM has ~20 GB free —
the pull CANNOT run here, which is why the pipeline is user-side
(T7-USER-STEPS.md) with DISK-RULES applying to whatever comes back
(extract → convert → delete paks).

## 8. Open items (need the user)

1. Run Path A or B of `tools/depot-pull/T7-USER-STEPS.md` and upload the paks
   (Law/Lars first).
2. Confirm the upload destination (GitHub release link or shared location).
3. Nothing else — no credentials, no installs, no manual ripping on their end
   beyond the 5 steps.
