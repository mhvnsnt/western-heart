# Community Animation Pulls — Research Report — 2026-10-24

Button names used everywhere in this report: LP1 = Left Punch = Tekken 1,
RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Scope and rules applied

- Searched TekkenMods (tekkenmods.com), community forums and GitHub by
  public web search and text fetch only. No live-browser visit, sign-in,
  purchase or download-button click is claimed anywhere in this report.
  Anything that requires a download button is listed under "Parent
  browser delegation" with its exact URL, and was NOT fetched.
- No pirated full-game copies or repacks. Community MODS, TOOLS, GUIDES
  and KNOWLEDGE only. Nothing in the search set below is a full-game
  repack; one mirror link (Project Angel's Mega folder) is a mod-file
  mirror, not a game repack, and is still delegation-only, not fetched.
- No Tekken 8 data is used for any Tekken 7 character. Tekken 8 moveset
  mods found in the search are recorded as EXCLUDED for this purpose.
- No large files were downloaded to this VM. URLs and file lists are
  recorded; bulk download was not done.
- Usability rule (from the task brief, applied strictly): a community
  file is usable as WIRING only if it contains actual move→animation
  references (animation names/addresses, row indices, or equivalent).
  A pack of raw clips with no mapping is recorded as "clips only, no
  mapping" and no mapping was invented for it. A tool that extracts
  mappings from a running game is recorded as a tool, not as a bank.

## Headline finding

No text-fetchable, pre-made Tekken 7 animation bank for King, Raven,
Lucky Chloe, Jun (TTT2), Shaheen, Katarina, or any other WH-fighter
Tekken base was found in this pass. What exists publicly in the searched
sources is:

1. TOOLS that extract move→animation mappings from a running owned copy
   of Tekken 7 / TTT2 (the real path to T7 banks), and
2. TEKKENMODS MOVESET MODS in extractor format (move→animation references
   inside the mod files) that sit behind TekkenMods download buttons and
   were therefore NOT fetched from this VM.

That is a sourcing result, not a failure to search: the same pattern
recurs across every query (tool pages, mod pages, GitHub repos). Any
claim of a "downloaded T7 King bank" from these sources would require
either running the extractor against the owned game or a browser
download — both listed as delegation, neither claimed here.

## Part 1 — Tools (contain move→animation mapping logic; NOT banks)

### 1. Kiloutre / TekkenMovesetExtractor — THE extraction path for T7 banks

- URL: https://github.com/Kiloutre/TekkenMovesetExtractor
- TekkenMods page: https://tekkenmods.com/mod/2365/tekkenmovesetextractor-for-tekken-7
- License: GPL-3.0. Stars: 79 (checked 2026-10-24 via API). Last update
  2026-10-04. Root files include `motbinExport.py`, `motbinImport.py`,
  `GUI_TekkenMovesetExtractor.py`, `GUI_TekkenMovesetEditor.py`,
  `GUI_TekkenAnimationEditor.py`, `GUI_TekkenCameraAnimator.py`, plus
  per-game alias files (`Tag2Aliases.py`, `T6Aliases.py`, `T5Aliases.py`,
  `T4Aliases.py`).
- What it contains: extracts MOVESETS (not models, not standalone
  visuals) from a running game into memory, and re-imports them. A
  moveset export carries the move list with each move's animation
  reference — that IS a move→animation mapping, in the tool's own format.
  The MovesetEditor lets animations and moves be copied between
  movesets. It also includes a rudimentary animation-from-scratch tool
  and a camera animator.
- Games it extracts from (per its TekkenMods page): Tekken 7 (all
  versions since Season 2), Tekken Tag Tournament 2 (the page says TTT2
  is "the only one with Tekken 7 that truly works well"), Tekken
  Revolution, Tekken 6, Tekken 5, Tekken 3DS. Exports are prefixed `7_`
  for T7, `2_` for TTT2, and land in `extracted_chars/`.
- Caveat from its own issue tracker (issue text found in search):
  Tekken 6 movesets extracted this way are reported glitchy/broken as
  playable movesets, and a maintainer reply states T5/T6 extraction
  exists "so that you can use the animations and eventually see how
  some specific moves are constructed" — not as playable sets. For this
  project that distinction matters: T6/T5 exports are animation
  reference material, not drop-in banks.
- Verdict: TOOL, not a bank. This is the correct way to produce T7 banks
  for King, Raven, Chloe, Shaheen, Katarina and every other T7 base from
  the owned game — run the extractor with the game loaded, export each
  character, then convert the export's move→animation references to the
  WH bank format. That run needs a game-capable machine and is listed
  under delegation (§4), because this VM cannot run the game or the
  extractor's memory import.
- What it does NOT give from this VM: no pre-made character export was
  found in the repo itself (the repo is code + aliases, no
  `extracted_chars/` banks).

### 2. Kiloutre / TKMovesets (TKMovesets2) — successor tool

- URL (repo): https://github.com/Kiloutre/TKMovesets (found via API
  search; GPL-3.0, 36 stars, updated 2026-10-12). Root includes
  `TKMovesets2/`, `CMakeLists.txt`, `Sig/`.
- TekkenMods page: https://tekkenmods.com/mod/2429/ — "TKMovesets2 0.6
  — Moveset export / import / edit", described as aimed at replacing
  and surpassing the old extractor. At version 0.6, only Tekken 7 is
  supported; the tool is tailored to the latest T7 version.
- Features (per that page): extractor (from memory, T7, with options to
  carry camera / face / hand animations); importer to any character in
  memory; movesets compressed on disk; online play via Steam networking
  (max 50 MB per moveset).
- Verdict: TOOL, same class as #1, newer codebase. No pre-made banks in
  the repo. Same delegation requirement: run against the owned game.

### 3. Kiloutre / BlenderTekkenDirect + BlenderTekkenAnimationImporter

- BlenderTekkenDirect: https://github.com/Kiloutre/BlenderTekkenDirect
  (8 stars, updated 2026-08-14) — "Preview animations in Tekken 7 live
  from blender". Files: `TekkenDirect.py`, `TekkenAnimHelper.py`,
  `game_addresses.txt`.
- BlenderTekkenAnimationImporter:
  https://github.com/Kiloutre/BlenderTekkenAnimationImporter (5 stars,
  updated 2026-10-21) — animation import/export code
  (`AnimationImporter.py`, `AnimationExporter.py`, `Animation0xC8.py`,
  `AnimationFrame0x17.py`, `AnimationHeader0xC8.py`).
- Verdict: TOOLS for inspecting and converting live T7 animation data
  in Blender. No pre-made banks, no move→animation mapping file for a
  character. Useful for the conversion step AFTER an extractor export,
  not a source of banks by themselves. License: none stated on either
  repo (checked via API) — confirm before redistributing code from them.

### 4. Umodel + CDDTreborn Tekken 7 PC Modding Guides — guide, mesh only

- Guide page (text-fetched via search):
  https://github-wiki-see.page/m/CDDTreborn/Tekken7_PC-Modding-Guides/wiki/Umodel-UE-Viewer-Quick-Start-Guide-or-Reference---Tekken-7
- What the guide documents: exporting meshes/textures as `.psk` /
  `.gltf`, and extracting assets as `.uasset` packages (commonly used
  for CI, CCI, CS, images, umaps). It documents SK_ skeletal meshes and
  SKT_ base skeletons as asset types.
- Verdict: GUIDE + mesh tool. The guide text found does NOT document a
  T7 animation-sequence export with move→animation mapping, and no
  `.psa` animation bank for any character was located through it.
  Recorded as "clips/mesh only, no mapping proven" — do not cite umodel
  as an animation-bank source without a further, specific animation
  export procedure. T7 is a UE4 game; its animation assets are
  `.uasset` sequences, not the PSK/PSA pipeline the older UE guides
  describe, and that mismatch is itself a blocker to quote, not to
  paper over.

### 5. Wavu / tekkendocs — frame data only, NOT animation

- Wavu King movelist (example): https://wavu.wiki/t/King_movelist
- tekkendocs repo (pbruvoll/tekkendocs): character movelist CSVs under
  `data/wavuConvertedCsv/{character}/{character}-special.csv` and JSON
  under `utils/wavu-importer/src/json_movelist/{character}.json`.
- Verdict: MOVE PROPERTIES ONLY (command, damage, startup, level, notes).
  No clips, no animation references, no wiring. Useful as Tekken 7
  truth for VERIFYING a T3 or extractor clip (the T3 verification report
  uses wavu T7 pages exactly this way), but it cannot supply an animation
  bank. Recorded here so it is not mistaken for one.

## Part 2 — Community moveset mods (extractor format = mapping inside the file)

Every mod below is a TekkenMovesetExtractor-format moveset: the file, once
obtained, contains move entries with animation references — i.e. it
qualifies as mapping-bearing material under the usability rule. But
none of the mod FILES was fetched from this VM: TekkenMods serves them
behind download buttons, and the text fetch of each mod page returns the
description only, not the file list. They are therefore listed with exact
URLs under delegation (§4), with what the page text proves about each.

### 6. King — "King Of Beasts, Over-Tuned King (Updated!)"

- URL: https://tekkenmods.com/mod/3731/king-of-beasts-over-tuned-king-updated
- Author: Bloom (showcase on Odysee, per page text). Page text fetched
  2026-10-24.
- What the page proves: a King moveset mod (extractor format implied by
  the genre; the page itself does not name the extractor in the fetched
  text, so the format is INFERRED from the mod class, not proven from
  this page — the file must be inspected after download to confirm).
  Contents per page: Beast Mode state, more grabs and chain grabs
  (including spliced moves from other movesets), 2 new grabs, KO Item
  Grab from Tag 2, new parry, old grabs/moves from T6 and older games,
  animation and grab bug fixes, reworked grab inputs.
- WH relevance: King is Pantera's Tekken base. A T7 King moveset would
  give T7 move→animation references for Pantera's T7-era moves — but it
  is a MODIFIED moveset (over-tuned, spliced, Beast Mode), not a clean
  T7 King export. Even after download, every move→animation reference
  in it must be checked against clean T7 King truth (wavu) before use;
  spliced moves are not King truth.
- Verdict: MAPPING-BEARING (pending file inspection), DELEGATION ONLY
  (download button; file list not visible in text fetch). Do NOT use
  until inspected.

### 7. Jun (TTT2) — LukzB / tk7-junmoveset — UNAVAILABLE

- URL: https://github.com/LukzB/tk7-junmoveset
- License: none stated. Stars: 4. Last update 2022-07-29. Repo root
  contains ONLY `README.md` (checked via API 2026-10-24).
- What the page proves: Jun Kazama's TTT2 moveset re-worked for Tekken 7,
  made with TekkenMovesetExtractor, intended for `extracted_chars/` as
  `7_JUN_KAZAMA_Vx.y.rar`. The README states, verbatim in substance:
  "Moveset files are no longer available to download. I will re-work
  the mod in order to avoid legal issues with unauthorized file
  distribution, so stay tuned." Download links section reads "Moveset:
  Coming soon."
- WH relevance: Jun is Megami's Tekken base (TTT2 Jun). This was the
  closest community Jun source found — and it is currently empty.
- Verdict: NOT USABLE (no files). Recorded so the search is not repeated
  blindly. The README's own move descriptions (Rage Art d/f+3+4, Rage
  Drive u/f+3+4, screw/bound/homing lists, sample combos) are INPUT
  documentation only — they name inputs, not animation references, and
  must not be treated as wiring. The correct Jun path remains a TTT2
  extraction via tool #1 (CEMU + TTT2) or a clean T7-era Jun source, not
  this repo.

### 8. Angel (TTT2) — "Project Angel v1.2"

- URL: https://tekkenmods.com/mod/852/project-angel-v1-2
- What the page proves: a moveset mod designed for TekkenMovesetExtractor
  import. Requirements stated on the page: Angel's animations from TTT2
  PLUS some Tekken 7 animations for reworked moves/mechanics; a
  `required_animations.txt` inside the project lists the required
  animation `.bin` files; the page instructs the user to extract those
  `.bin` files themselves via the extractor's GitHub instructions, then
  place them in `anim/` and move the `PROJECT_ANGEL_KAT/NIN` folder to
  `extracted chars`. Works properly on Nina or Katarina (intro/outro
  differences); playable on any character with odd intro/outro camera.
- Mirror link printed on the page (NOT fetched, delegation only):
  https://mega.nz/folder/B1VnXIKA#Zdzq6_Yu-Ko_HnqdYxMxNg — described on
  the page as an alternate source for users who cannot grab the animation
  files manually.
- Verdict: MAPPING-BEARING STRUCTURE (moveset + explicit
  `required_animations.txt` animation list is exactly the kind of
  move→animation reference this project needs), but the animation
  `.bin` files themselves are NOT in the text fetch and the Mega mirror
  was not fetched. Delegation only. WH relevance is indirect: Angel is
  not a WH base, but the project's STRUCTURE (moveset + required-anim
  list + TTT2/T7 hybrid) is the template for how a TTT2-derived Jun or
  any TTT2 bank should be packaged.

### 9. Other TekkenMods moveset mods found (delegation only, not inspected)

- "Legacy Heihachi Partially Restored":
  https://tekkenmods.com/mod/4756/legacy-heihachi-partially-restored —
  Heihachi moveset edits (legacy 1,1,2 / LP1,RP2,RP2 framing, old f+3
  and f+2,3 restored, old df+1 animation, Omen). Extractor format per
  page (references LukzB's extractor releases). WH relevance: Heihachi
  is Diablo's base; legacy restorations are T6/older animation
  references, useful as leads, not as clean T7 truth.
- "Over-Tuned Jaycee": https://tekkenmods.com/mod/3003/over-tuned-jaycee
  — Jaycee (Julia) moveset, Tag 2 moves ported and "T7fied", Tag 2
  stances, new grabs, built on MotorMike's Jaycee mod
  (https://tekkenmods.com/mod/1720/tekken-7-jaycee-moveset-mod, referenced
  on the page but not text-fetched here). WH relevance: Julia is
  Nightwolf's canon base; a Jaycee/Julia moveset is a lead for Julia
  T7-era references, subject to the same modified-moveset caveat as #6.
- "Screw Combos from Tekken 7 replacing Tornado":
  https://tekkenmods.com/mod/6006/screw-combos-from-tekken-7-replacing-tornado
  — system-level screw/tailspin moveset edits across 26 characters, not
  a character bank. Low value for per-character banks; recorded for
  completeness, not pursued.
- "Armor King Reimagined Moveset Mod":
  https://tekkenmods.com/mod/6994/armor-king-reimagined-moveset-mod —
  EXCLUDED for this purpose: it is a TEKKEN 8 moveset mod
  (`t8_ARMOR_KING_REIMAGINED`, Tekken 8 `Polaris/Content/Paks/~mods`
  install path on the page). Per the task rule (never T8 data for T7
  characters) it must NOT be used as a T7 Armor King source, even
  though Armor King is Yukihyo's base. Recorded as skipped-with-reason,
  not as usable.

### 10. Skipped with reason (not pursued, not fetched as banks)

- Full-game repacks: none encountered in this search set. No URL is
  recorded for any repack because none was found — if a future search
  surfaces one, skip it under the same rule and note it as skipped.
- Paid moveset editors (e.g. a Payhip "KILLER MOVESET EDITOR" listing
  surfaced in search): not a bank, not a mapping source, not pursued.
- MUGEN / sprite sources, TikTok/YouTube showcases, frame-data wikis:
  inputs or video only, no animation references. Not wiring.
- Tekken 8 documentation pages (TekkenMods T8 moveset-structure docs):
  useful for FORMAT understanding (requirements, extra move properties,
  camera extra data), but T8 structures must not be back-ported as T7
  character data.

## Part 3 — Coverage vs WH-fighter Tekken bases

| WH need (Tekken base) | Community source found? | What it actually gives |
|---|---|---|
| King → Pantera | Mod #6 (delegation) + tool #1 (clean export path) | Modified T7 King moveset (inspect after download); clean path is extractor export from owned T7 |
| Raven → Pond | NOTHING character-specific found | No T7 Raven moveset mod surfaced; tool #1 export is the only path found |
| Lucky Chloe → Ryusan | NOTHING character-specific found | Same: tool #1 export only |
| Jun (TTT2) → Megami | Repo #7, files REMOVED | No usable files; TTT2 extraction via tool #1 (CEMU) is the path found |
| Shaheen → Scimitar | NOTHING character-specific found | Tool #1 export only |
| Katarina → Michiko | NOTHING character-specific found (Project Angel notes Katarina only as a host body for Angel, not as a Katarina bank) | Tool #1 export only |
| Heihachi → Diablo | Mod #9 Legacy Heihachi (delegation) | Legacy/older animation references, not clean T7 |
| Julia → Nightwolf | Mod #9 Jaycee (delegation) | Modified Julia/Jaycee moveset, inspect after download |
| Armor King → Yukihyo | T8 mod found, EXCLUDED | No T7 Armor King bank found; tool #1 export only (Armor King is not in T7's base roster as a standalone — TTT2/legacy path via tool #1) |
| All other T7 bases (Asuka, Lars, Lee, Steve, Dragunov, Lili, Miguel, Zafina, Josie, Negan, etc.) | NOTHING character-specific found in this pass | Tool #1 export only |

The pattern is consistent: the community does NOT publish clean,
per-character T7 animation banks as downloadable files. It publishes
the extractor (which makes them from a running game) and modified
movesets (which remix them). Any future "bank pull" claim should be
checked against that pattern before it is believed.

## Part 4 — Parent browser delegation list (exact URLs, NOT fetched)

These need a browser download-button click or a game-capable run. They
were NOT fetched, NOT downloaded, and are NOT claimed as obtained:

1. TekkenMovesetExtractor (tool download):
   https://tekkenmods.com/mod/2365/tekkenmovesetextractor-for-tekken-7
   and https://github.com/Kiloutre/TekkenMovesetExtractor/releases
   — Blocker: executable release download; text fetch gives code/docs
   only.
2. TKMovesets2 (tool download):
   https://tekkenmods.com/mod/2429/ — Blocker: TekkenMods download button.
3. King Of Beasts (King moveset):
   https://tekkenmods.com/mod/3731/king-of-beasts-over-tuned-king-updated
   — Blocker: TekkenMods download button; file list not visible in text
   fetch.
4. Project Angel (Angel moveset + required animations list):
   https://tekkenmods.com/mod/852/project-angel-v1-2 — Blocker:
   TekkenMods download button for the mod; Mega mirror
   https://mega.nz/folder/B1VnXIKA#Zdzq6_Yu-Ko_HnqdYxMxNg — Blocker:
   third-party file-host folder, not text-fetchable.
5. Legacy Heihachi:
   https://tekkenmods.com/mod/4756/legacy-heihachi-partially-restored —
   Blocker: TekkenMods download button.
6. Over-Tuned Jaycee:
   https://tekkenmods.com/mod/3003/over-tuned-jaycee — Blocker:
   TekkenMods download button.
7. Clean T7 exports (King, Raven, Chloe, Shaheen, Katarina, all other T7
   bases) via TekkenMovesetExtractor / TKMovesets2 — Blocker: requires
   running the owned Tekken 7 game with the extractor attached (memory
   import/export). This VM cannot run the game. This is the highest-value
   delegation item: one extractor session per character produces the
   clean move→animation mapping that no download replaces.

## Part 5 — What to do with a downloaded mod file (inspection protocol)

When a delegated download lands, do NOT wire it directly. Inspect first:

1. Confirm format: TekkenMovesetExtractor `extracted_chars/` layout
   (moveset JSON + `anim/` `.bin` files) vs a `.pak` or other package.
2. Confirm the move list's inputs are file inputs (the mod's own
   notation fields), converted to LP1/RP2/LK3/RK4 by the parser — never
   re-guessed.
3. Confirm each move's animation reference points at an animation
   actually present in the file set. A reference to a missing `.bin`
   (the Project Angel failure mode the page warns about: "game crashes
   might happen" without all `.bin` files) is UNMAPPED, not filled.
4. Check modified vs clean: spliced, over-tuned, Beast-Mode or
   "T7fied" moves are NOT clean T7 truth. Cross-check damage/startup/
   level against wavu T7 pages before accepting any reference as a T7
   bank row.
5. Convert, don't copy: a T7 moveset export's animation references are
   T7 animation indices/addresses, not WH bank rows. The conversion to
   WH's row/clip format must preserve the move→animation pairing from
   the file, and any move whose pairing cannot be preserved exactly is
   UNMAPPED in WH, even if the T7 file plays fine in T7.

## Sources consulted (search + text fetch, 2026-10-24)

- TekkenMods: TekkenMovesetExtractor (mod 2365), TKMovesets2 (mod 2429),
  Project Angel (mod 852), King Of Beasts (mod 3731, page text fetched),
  Armor King Reimagined (mod 6994), Legacy Heihachi (mod 4756),
  Over-Tuned Jaycee (mod 3003), Screw Combos (mod 6006), TTT2
  documentation page.
- GitHub (API, public): Kiloutre/TekkenMovesetExtractor (GPL-3.0),
  Kiloutre/TKMovesets (GPL-3.0), Kiloutre/BlenderTekkenDirect,
  Kiloutre/BlenderTekkenAnimationImporter, LukzB/tk7-junmoveset
  (README only, files removed).
- Guides/docs: CDDTreborn Tekken 7 PC Modding Guides (umodel page),
  TekkenMods T8 moveset-structure documentation (format reference only,
  excluded as data), wavu.wiki King movelist, tekkendocs movelist CSV/JSON
  structure.
- In-repo (for the T3 side of the comparison): `game/js/t3anims.js`,
  `game/js/fighter.js`, `docs/anim/BANK-TABLE-2026-10-20.md`,
  `docs/anim/T3-REMAINDER-BANKS-20261020.md`,
  `docs/anim/T3-REACTIONS.md`,
  `docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md`.

## GPU job specs (prepared, NOT run — Kaggle delegation)

CPU/GPU split, stated plainly: the searches, text fetches, API listings
and PR work in this report are CPU/I-O-bound and stay on the VM — a GPU
gives zero benefit there. The GPU-acceleratable steps that follow from
this report are in the companion document
`docs/anim/T3-GPU-JOB-SPECS-2026-10-24.md`, prepared for execution via
browser delegation on the user's Kaggle notebook (2x Tesla T4, 15 GB
each):
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
Relevant jobs: Job 4 (community-clip retargeting / format conversion,
4–12 GB on one T4 — ONLY after a delegated download passes the §5
inspection protocol, never on T8 files for T7 characters, never on
repacks) and Job 5 (render proofs for conversion candidates, 8–12 GB).
No Kaggle run is claimed in this report.

## Limitations of this pass

- Search is public-web search + text fetch only. TekkenMods file lists,
  Discord channels (Modding Zaibatsu `#movesets`, referenced on the
  extractor page), and file-host folders were not accessed.
- Character-specific T7 moveset mods for Raven, Chloe, Shaheen and
  Katarina may exist under titles this search did not surface; absence
  here means "not found in this pass", not "does not exist anywhere".
  The delegation list is the correct next step, not a second identical
  search.
- No community file was downloaded, so no mod file was inspected. Every
  "mapping-bearing" verdict for a TekkenMods mod is conditional on the
  file inspection in §5.
