# Teardown Manifest — 2026-10-24

Audit of EVERY game teardown file group: deciphered / extracted / decrypted /
usable / wired-into-repo status, with file evidence. No guesses: every status
below cites a path, a count, or a doc measured in this audit.

Status key: DONE = verified in repo/game. PARTIAL = some done, remainder named.
NO = not done, blocker/next named. LANE = another agent lane owns it; this
manifest does not duplicate that lane's work.

## 1. Tekken 7 — mot.bin (move data) — DECODED, GRE PR IN FLIGHT (sibling lane)

- Source bins: 57 files in `teardown/tekken7-steam/tkdata/mothead/bin/`
  (private repo `mhvnsnt/game-reverse-engineering`).
- Decoder: `t7_motbin_to_json.py` replica, validated by reproducing
  `leemot.json` from `leemot.bin` with ZERO differences. Schema
  `wh-t7-motbin-json/1`. Move stride 176, cancel stride 40; anim_ref banks
  0x0000 (mot.bin slot-0 MOTA) / 0x4000 (rotsm.arc section-0 MOTA) /
  0x8000 (main character MOTA).
- Local decoded set: 51/51 bins in `~/workspace/batch-motbin/batch-bin/` have
  matching `json/` outputs (verified: no missing JSON, no extra JSON).
  `json/` files carry the WH fighter name in `meta.fighter` (e.g. kinmot →
  pantera, 2787 moves); `json_id/` files are the identification decodes
  (meta.fighter = T7 code). Blob-SHA verified for kinmot/jinmot against the
  prior PR log (exact match).
- Already on GRE main: `teardown/tekken7-steam/tkdata/mothead/json/` holds
  asamot.json, bobmot.json, leemot.json (committed 2026-10-23) plus frv.json
  (Raven/Pond, 2338 moves) and dnc.json (Chloe/Ryusan, 2183 moves) via
  PR #61, MERGED 2026-10-24T21:41Z (state closed, merged true).
- Remaining 50 JSONs (31 WH-fighter files — kin, jin, hei, yos, arb, bry, fen,
  mar, hwo, lar, xia, edd, ltn, law, pau, ann, jul, nin, lil, mut, dra, gan,
  zaf, ste, lei, aki, knm, mry, mrz, nsa, nsd; 71,933 WH moves per prior PR
  body — plus 19 non-WH decoded files): WIRED TO GRE VIA PR #63, verified
  this audit. Sibling run completed EXIT:0 — commit
  bcaaa78eb3958bce095101523264efc1207d86d9 on branch
  `batch-motbin-all-t7`, PR #63
  (https://github.com/mhvnsnt/game-reverse-engineering/pull/63), state
  OPEN, mergeable TRUE, 50 files, 0 deletions. The 31-file PR body is
  `~/workspace/batch-motbin/pr_body.md`; the 50-file body is
  `pr_body_all.md`. Merge of #63 is still owed (it is open, not merged)
  — after merge, re-list `teardown/tekken7-steam/tkdata/mothead/json/`
  to confirm all 50 land. NOTE: the converter script
  `t7_motbin_to_json.py` was NOT in the 50 files — commit it alongside
  (it is the decoder of record; without it the JSONs are unverifiable).
- Known gaps inside this group (nothing invented for them): NO mot.bin for
  Christie→Star, True Ogre→Chatur, Roger Jr.→Menajerii, Mokujin→DXMMII,
  Akuma→Dio, Bosconovitch→Doc Frank, Gun Jack→SAM-UR-A1, Fahkumram, Leroy.
  `jacmot`/`ja4mot` are both header [Jack], NOT Gun Jack — never substituted.
  Heihachi variant `yhemot` (2487 moves) decoded locally, NOT shipped (one
  fighter, one file rule). DLC WH names unassigned for Kunimitsu/Geese/
  Noctis/Negan/Lidia — their meta.fighter uses the T7 name, flagged.
- Clip bytes: BLOCKER. Bank 0x8000 clip bytes need main-character MOTA from
  pakchunk data or live-game memory. GRE `teardown/pakchunk0/` holds
  manifest.json (74,872 bytes) + `models/` + `textures/` dirs — animation /
  MOTA contents are NOT confirmed in that listing, so the blocker stands
  until animation data is confirmed in pakchunk0 (next: enumerate
  pakchunk0/models/ + read manifest.json for animation entries).
  Move→clip keys (bank + clip_key) are exact; byte offsets are UNRESOLVED
  and never asserted. Bank 0x0000/0x4000 clips resolve from tkdata/rotsm
  data.
- Game wiring: PARTIAL, owned by the mega-batch lane (open WH PR #1039:
  T8 purge + MOD damage sync + unified index; rewrites 8 movesets incl.
  pantera/demonio/diablo/phantom/scimitar/skull). A prior batch wired 24
  movesets locally (`~/workspace/batch-motbin/wired/`, 2.7–3.9 MB each) but
  those are NOT on WH main (main pantera.json is still the old 803,774-byte
  blob, SHA-matched to the pre-wire blob). DO NOT PR the wired set
  separately — it would collide with #1039. Reconciliation with the
  mega-batch lane is the named next step, not a second moveset PR.

## 2. Tekken 7 — .mvl (display movelists) — DECODED, HONEST PARTIAL

- 53 `.mvl` files local in `~/workspace/mega-batch-t7/mvl/` (aki, ann, arb,
  asa, ask, bob, bry, crz, dmy, dnc, dra, dvj, edd, elz, fen, frv, gan, hei,
  hwo, ita, ...). Titles + demo inputs decoded to LP1/RP2/LK3/RK4 where
  possible (frv 175 titles, dnc 138 titles).
- Display→move join is HONEST PARTIAL: cancel-graph walk from neutral
  resolves only 30 frv + 11 dnc displayables deterministically; the rest are
  DEAD_END / AMBIGUOUS / NO_PLAYABLE (string continuations live in
  requirement/group-cancel semantics). `playable_id` is NOT a move index.
  Titles are labelled WALK-MAPPED / SUSPECT / UNMAPPED — never wired as
  true move names. No bulk .mvl parser exists anywhere; .mvl is
  display-only (Kiloutre: stored to show the custom movelist in training).
- Wired: NO (display data only; game uses mot.bin JSONs + TheBigTuna
  frame data for movesets). Next: title→move verification before any
  display-title wiring.

## 3. Tekken 7 — frame data (TheBigTuna) — EXTRACTED, WIRED (MOD damage)

- `~/workspace/mvlt-community-pull/t7-all/` — all 35 TheBigTuna characters
  converted to LP1/RP2/LK3/RK4 format, 5,648 moves, MOD damage (parser PR
  #999). King deduplicated 191→157. Kuma skipped (141-byte empty file).
- Missing DLC (no TheBigTuna rows): Anna (covered from T7 DLC/T6 via PR
  #1011), Armor King, Fahkumram, Ganryu, Geese, Julia, Kunimitsu, Leroy,
  Lidia, Negan, Noctis, Zafina, Marduk — frame data for these must come from
  wavu.wiki / geppopotamus / fandom joins (separate lane: DLC frame data).
- Wired: YES — MOD damage wiring PRs #1000 + #1002 (31 files, 1,720 +
  4,000 entries). Never T8 data for T7 characters (tekkenDocs king.json is
  T8 — banned for T7 Pantera).

## 4. Tekken 7 — models / pakchunk / UI — PARTIAL, LANES OPEN

- GRE `tekken7/` dirs: arenas, customization, king, models, stages,
  tekkenmods-docs, tools. GRE `teardown/pakchunk0/` exists (contents
  pending enumeration in this audit).
- Open WH PR #863 (another lane): "T7 Steam extraction #1: pakchunk0 meshes
  (Alisa/Lee/Bob + 35 more), textures, UI" — model extraction lives there;
  this manifest does not duplicate it.
- WH `teardown/tekken7-steam-ui/` + `teardown/tekken7/ui/` + `tekkenmods-docs/`:
  UI teardown used by the menu lanes (submenu work, T7 select rebuild PR
  #826 open). Status: docs-level, UI assets wired per menu PRs.
- 0x8000 clip bytes: see §1 blocker (pakchunk animation data).

## 5. Tekken 3 — animations (divmot) — DECIPHERED, EXTRACTED, WIRED

- Source: 21 `divmot*.bin` files in WH `teardown/tekken3/animations/`:
  divmot00 Paul, 01 Law, 02 Lei, 03 King, 04 Yoshimitsu, 05 Nina, 06
  Hwoarang, 07 Xiaoyu, 08 Eddy, 09 Jin, 10 Julia, 11 Kuma, 12 Bryan, 13
  Heihachi, 14 Ogre, 16 Gunjack, 17 Anna, 18 Bosconovitch, 19 Gon,
  20 Forest Law, 99 common. NOTE: divmot15 is MISSING from the listing —
  identify which character slot 15 is before claiming full coverage.
- Wired into game: YES — `game/assets/anim/t3/` holds 22 bank dirs (anna,
  armorking, bosconovitch, bryan, eddy, forestlaw_on_law, gon, gunjack,
  heihachi, heihachi_on_jin, hwoarang, jin, julia, king_on_pantera_leoman,
  kuma, law, lei, nina, ogre, paul, xiaoyu, yoshimitsu) + `reactions.json`
  (1,912,315 bytes). These are the live fight banks (fighter.js
  bankIdFor). Reaction/throw clips: 7,368 decoded; hit-reaction wiring is
  open WH PR #1034 (sibling lane); throw-pair wiring is open WH PR #1031
  (sibling lane).
- T3 movesets: `teardown/tekken3/movesets/` exists; `WIRING-INVENTORY.md`
  (3,426,201 bytes) + `model-inventory.json` (8,346,757 bytes) +
  `tim-inventory.json` (10,022,608 bytes) are the inventories. T3 moveset
  wiring status per moveset file is tracked in that inventory, not
  re-audited here. T3 = FALLBACK ONLY per standing law (no new T3 models).
- T3 models: `teardown/tekken3/models/` + `model-inventory.csv` — models
  NOT wired as new fighters (fallback law); animations only.

## 6. Tekken 5 — cataloged, NOT decoded to game animations

- WH `teardown/tekken5/`: DEVIL-WITHIN-DATA.md, INVENTORY.md, ROSTER.md,
  STAGES.md, TEARDOWN.md, `t5_char_codes.txt`, `t5_motion_manifest.txt`
  (lists `gym_*.dat` motion files by name — e.g. gym_Bbr_bbblow.dat,
  gym_Gan_mekin.dat, gym_Mco_y_Bpon.dat).
- GRE `tekken5/`: Devil Within deep docs, TK5DATA1-FILE-TABLE.csv,
  cipher-hunt + obfuscation analysis docs, `data/` holding ONLY
  name_tables.json + roster.json. The `gym_*.dat` motion FILES are NOT in
  either repo (names cataloged, bytes absent).
- Status: DECIPHERED = NO (motion format not decoded to clips).
  EXTRACTED = NO. WIRED = NO. Next: locate the T5 motion .dat bytes
  (PS2 disc / archive) then decode; Devil Within stage-flow docs are the
  design reference, not game data.

## 7. Tekken 6 — DINF decrypted, IDX contested, motion NOT extracted

- WH `teardown/tekken6/`: TEARDOWN.md, DATA401-RE-NOTES.md,
  DINF-400-DECRYPTED.md (restored 2026-10-23), T6-KEYHUNT-REPORT,
  MOTION-UNBLOCK-2026-10-23.md, PPSSPP-LIVE-RUN-GUIDE.md, `decrypted/`
  holding EBOOT.DECRYPTED.ELF (4,158,144 bytes) + README.md.
- Facts from MOTION-UNBLOCK: sector cipher 0x8AA2CA8 fully reversed
  (bit-exact Python model, unicorn-validated 768/768 words); per-sector
  K1/K2 extraction solved (CRC32-gated table indirection); DINF_400.BIN
  decrypts with keyset B (K1=0xebcf9603, K2=0xb3bef6a4) → manifest 2169
  entries, 384,051,200 bytes, build 2009-11-09. Oct 15–16 bulk-decrypt work
  was wiped from main Oct 17 (DXMMII commit); `tools/dinf_decrypt.py` was
  restored Oct 23 and DINF decrypt re-verified (magic DINF, 2169 ✓).
- IDX: DATA401.IDX (26,028 bytes, entropy 7.993) — keyset A gives 89/2169
  "plausible" (FAILS rigorous tiling/sortedness test); keyset B result was
  still open in the doc excerpt. Motion-file mapping via IDX is therefore
  UNRESOLVED.
- Local: `~/workspace/t6work/tekken6-psp.iso` + `t6work/tekken6/` (PSP ISO
  on disk; T6 PSP IDX encrypted, no voice attribution per prior audit).
- Status: DECRYPTED = PARTIAL (DINF yes, IDX contested, EBOOT yes).
  EXTRACTED = NO motion clips. WIRED = NO. Next: resolve IDX mapping
  (keyset B result + tiling test), then extract motion; T6 voice (King)
  stays blocked on the same IDX attribution problem — never present stage
  sounds as voice.

## 8. Tekken Tag Tournament 2 — extracted-small, NOT identified, NOT wired

- WH `teardown/tekken-tag-tournament-2/`: EXTRACTION-RUNBOOK.md,
  HEADER-LISTING.txt, INVENTORY.md, ROSTER.md, STAGES.md, TEARDOWN.md,
  TTT2-PC-PORT-ASSESSMENT.md, XDVDFS-LISTING.md, `extracted-small/` with
  13 hash-named files (98,304–450,560 bytes, e.g.
  000005440E4582E3C2F571D64E4D0859, 392CFF5C9DB17CCAEBC3).
- Status: files extracted from XDVDFS, but hash-named and NOT identified
  to characters — Jun (Megami's base) is NOT identified among them.
  DECIPHERED = NO (no per-file character/move mapping). WIRED = NO.
  Next: identify the 13 files by header/content match (Jun search first),
  then decode; TTT2 team-battle PRs #668/#660 are a separate game-mode
  lane, not extraction.
- GRE `tekken-tag-tournament-2/` exists (contents not enumerated here).

## 9. WWE — No Mercy wired, WMXIX decoded/partial, 2K22 gap

- No Mercy: `game/data/moveset-library/` holds index.json (2,029 bytes,
  pointer) + `banks/` + claimed-map.json + schema.json. Library content:
  4,409 moves, 4,153 with input populated (first entry 'Chop 01').
  Status: EXTRACTED + WIRED (creation-suite moveset library; editor
  adapter pattern). Source teardown: WH `teardown/wwf-no-mercy/` —
  TEARDOWN.md, CANON-CONVERSION.md, CAW-SAVE-RECORD-STATUS.md,
  TEXT-CODE-DICTIONARY.md, TOKI2-SEMANTICS.md, WIRING-INVENTORY.md
  (2,610,726 bytes), aki_to_tekken3 converters + JSONs, animations/
  arenas/ models/ textures/ tools/ dirs.
- WMXIX: WH `teardown/wmxix/` — TEARDOWN.md, CANON-CONVERSION.md,
  ARENA-UNIVERSE-MAP.md, WMXIX-GHIDRA-MOVESET-XREF, WMXIX-MOVE-NAME-SURVEY,
  WMXIX-MPC-ASSIGNMENT-DECODE, WMXIX-MPC-INDEX.json (254,274 bytes),
  WMXIX-WPRM-DECODE.json (430,220 bytes), atr_all_events.json (242,384
  bytes), YANM-ITEM cycle docs, caw-parts/, wrestlers/, textures/,
  extract_*.py + catalog_caw.py + decode_tpl.py tools. Library content:
  169 moves, 0 with input — registry labels ONLY, explicitly flagged
  "provisional registry label — per-clip move identity not yet decoded;
  NOT a canon move name." WMXIX clip labels must NEVER be presented as
  real move names. Status: DECODED (structure), PARTIALLY wired (registry
  only). Next: per-clip move identity decode, then input wiring.
- WWE 2K19/2K20/2K22: WH teardown dirs `wwe2k19/`, `wwe2k20/`, `wwe-2k/`
  exist; `wwe2k22/` holds ONLY README.md (1,824 bytes). 2K22 Create-A-
  Moveset structure is NOT extracted (gap; matches the unanswered #866
  request). GRE `teardown/wwe2k19/` + `wrestling-games/` exist (contents
  pending enumeration). Next: 2K22 CAW structure extraction (creation
  suite lane owns the editor side; extraction is the gap).
- WWE 2K templates for creation suite: the creation-suite-fix lane owns
  template wiring; teardown coverage for templates is the No Mercy +
  WMXIX material above.

## 10. Virtua Fighter 5 — plan only, NOTHING extracted

- WH `teardown/vf5/` + GRE `vf5-revo/` hold ONLY ACQUISITION-PLAN.md
  (4,932 bytes) each. No VF5 motion, model, or moveset files in either
  repo. Dural (Zen's base) motion is therefore NOT extracted; Zen's
  stance/moves from VF5 are blocked on extraction (model-only status from
  prior audits stands).
- Open WH PR #713 (another lane): "VF5 motion pipeline: Dural stance for
  Zen" — motion work lives there; this manifest does not duplicate it.
  Next: VF5 motion extraction (tool chain unverified in public search —
  targeted modding-wiki/format research first, per studio-workflow audit).

## 11. Dead or Alive / Soulcalibur / other fighters — docs-level

- WH teardown dirs: dead-or-alive-4, dead-or-alive-6, soulcalibur-2,
  soulcalibur-6, street-fighter-3d-games, street-fighter-5,
  street-fighter-ex-plus-alpha, street-fighter-ex2-plus, street-fighter-ex3,
  urban-reign, def-jam-fight-for-ny, yakuza-kiwami, firepro, gang-beasts,
  nioh, wrestling-empire. Docs present (e.g. DOA6 mechanics, SCVI
  mechanics, Urban Reign UI system, Def Jam animation findings, SF 3D
  catalog). GRE `dead-or-alive/` holds a `doa4/` dir (contents pending
  enumeration); GRE `soulcalibur/`, `street-fighter-3d-games/`,
  `urban-reign/`, `yu-yu-hakusho-dark-tournament/` exist.
- Status for all of these: DECIPHERED/EXTRACTED = NO binary game data
  confirmed in this audit (docs + mechanics research only), WIRED = NO
  (except Bass Armstrong, already used per prior records, and Ashlane→DOA
  claimed-map work in PR #706, another lane). EXCEPTION, verified:
  GRE `dead-or-alive/doa4/` holds ONLY .gitignore (29 bytes) +
  download_chunks.sh (3,980 bytes) — NO game files at all. DOA4 is
  download-script-only; nothing extracted. Next: enumerate each dir's
  binaries before claiming anything further. DO NOT present doc-level
  research as extracted game data.
- SCVI note: user does not own SCVI per Steam list (absence ≠ proof of
  non-ownership per standing rule — never make the user prove ownership;
  SCVI work stays docs-level unless ownership is stated).

## 12. Eastern Mind stage sounds / Pantera voice — files exist, wiring lane open

- WH `teardown/eastern-mind/` holds CANON-CONVERSION.md, TEARDOWN.md,
  WIRING-INVENTORY.md (2,338,665 bytes), incarnation-system/, palettes/,
  prologue-ending/, soundtrack/, stage-1-plains-of-chi-u/ through
  stage-6-octagonal-shrine-par-fang/, transcript-promo/. The
  stage-1-plains-of-chi-u/ dir previously yielded the 9 `F_KING_s*.wav`
  stage-sound clips — PROVENANCE WARNING (standing): those 9 clips are
  stage sounds/music/SFX, NOT King's voice — never present them as
  dialogue. Character voice comes from character voice banks only.
- Pantera voice proper: `~/workspace/king-mods/` — T7 "King Classic
  Sounds" mod 681 (26 clips) + T7 "King Grunts from Tekken 2" mod 1242
  (26 clips, owner-preferred) + T8 death scream mod 3111 (1 clip),
  decoded with vgmstream, samplers + manifest in king-mods/. Wiring is
  open WH PR #1035 (sibling lane: Pantera voice bank into audio engine +
  fight grunt triggers) and PR #1028 (re-wire). Samplers are concatenated
  MP3s, NOT split clips — splitting (or cue-offset computation from the
  manifest) is still owed before the audio JSON is usable. Full T7 bank
  still needs game-file pull (0x8000-style blocker class: needs pakchunk
  or live memory, not available from this VM).

## 13. Other teardown dirs — existence noted, depth TBD (honest scope line)

- GRE `teardown/firepro/`: PULL.md + `decompiled/` + manifest_564231_*.txt
  (22,715 bytes). Fire Pro decompiled material EXISTS; decoded-to-WH-
  systems status = NO (no moveset/animation wiring confirmed).
- GRE `teardown/gang-beasts/`: DEPOT-FILES.tsv, FILES-SHA256.txt, PULL.md,
  SOURCE-SHA256.txt, `decompiled-signatures/`, dump.cs (27,071,272 bytes),
  il2cpp.h (43,195,264 bytes), script.json (81,530,163 bytes),
  stringliteral.json (1,794,706 bytes). Gang Beasts IL2CPP dump EXISTS
  (matches GRE PR #62 "Gang Beasts IL2CPP dump + signatures").
  Deciphered to WH systems (ragdoll/physics) = NO — dump is function
  signatures + strings, not wired ragdoll data. Next: mine dump.cs /
  script.json for ragdoll/physics parameters (Euphoria + Gang Beasts +
  Human Fall Flat mix is the standing ragdoll vision; activation is
  contextual-only per law).
- GRE `teardown/wrestling-empire/`: PULL.md + `decompiled/` + `docs/`.
  Decompiled material EXISTS; wired into WH mobile/audio reference = NO
  (the Wrestling Empire mobile-UX lane is separate work; decompiled
  content is not yet mined for it).
- GRE `teardown/wwe2k19/`: FILES-SHA256.txt, PULL.md, SOURCE-SHA256.txt,
  batch1.txt, `extracted/` (contents not enumerated). 2K19 extracted
  material EXISTS at top level; CAW-structure wiring status = same gap
  as §9 (2K CAW structure not extracted to the editor).
- GRE `teardown/yakuza-kiwami/`: FILES-SHA256.txt, HACT-FILES-SHA256.txt,
  PULL.md, SOURCE-SHA256.txt, `extracted/`, manifest_834531_*.txt
  (675,350 bytes), `raw-small/`. Yakuza extracted material EXISTS;
  decoded-to-WH-systems status = NO.
- GRE `teardown/tekken7-steam/tkdata/`: dictionary/, list/, mothead/
  dirs (mothead/bin + mothead/json covered in §1).
- GRE top dirs NOT deeply enumerated here: docs, models, naming,
  soulcalibur, street-fighter-3d-games, tooling, toolkit, tools,
  urban-reign, western-heart, wrestling-games, wwe-wrestlemania-xix,
  wwf-no-mercy, yu-yu-hakusho-dark-tournament.
- WH teardown dirs NOT deeply enumerated here: community, models, nioh,
  western-heart-design, wrestling-empire, wwe-2k, tekken7/arenas|king|
  models|rigging-reference|tekkenmods-docs|tools|ui,
  tekken3/disc|docs|models|movesets|renders|rigging-reference|stages|
  tim-output|tools|ui, tekken5/6 rigging-reference|tools|ui|docs|models|
  ref_frames|videos, TTT2 rigging-reference|tools|ui.
- Nothing in the "not deeply enumerated" lines is claimed
  deciphered/extracted/wired. Next audit pass: enumerate each such dir's
  file list + sizes, then promote each to a §1–§12 style entry. Nothing
  in this section may be cited as game data.

## 14. Workspace teardown work files (not repo, but part of the pipeline)

- `~/workspace/t7-motbin-analysis/`: frv.json, dnc.json, move_clip_map
  CSVs, displayables CSVs, parse_motbin.py, parse_mvl.py,
  t7_motbin_to_json.py, T7-MOTBIN-*.md reports. frv/dnc now on GRE main
  via PR #61 (see §1). The converter script itself was never committed
  to GRE originally — commit it alongside the JSONs (it is the decoder
  of record; without it the JSONs are unverifiable).
- `~/workspace/mvlt-community-pull/`: t7-all/ (35 chars) + King file +
  README. Conversion output, not source teardown; source is TheBigTuna
  (see §3).
- `~/workspace/batch-motbin/`: batch-bin/ (51 bins), json/ (51 finals),
  json_id/ (identification decodes), wired/ (24 wired movesets, NOT on
  main — see §1 reconciliation note), maps/, finals*.json, wire.py,
  make_pr.py, gh.py, pr_body.md, pr_body_all.md, pr_pairs.txt (50 pairs),
  private_pr.log (sibling run in flight).
- `~/workspace/mega-batch-t7/`: mvl/ (53 .mvl), asamot/bobmot/leemot
  JSONs, unified_index.json, mvl_display.json, mvl_listing.json,
  live-movesets/, patched/ — the mega-batch lane's working area (PR
  #1039). Do not edit from this lane without coordinating with it.
- `~/workspace/king-mods/`: see §12. `~/workspace/t6work/`: T6 PSP ISO +
  extracted dir (see §7). `~/workspace/tekken5-extract/`: T5 coverage
  matrices + status docs (see §6). `~/workspace/t7-worker/`: T7 roster
  mapping/coverage/model catalog docs (see §4).
- `~/workspace/teardown-audit/raw/`: 16 doc files (PLAYBOOK, README,
  TEARDOWN-COVERAGE-MATRIX, TEARDOWN-STATUS, TEARDOWN.md + per-game
  teardown docs for DOA6, Def Jam, Eastern Mind, SCVI, SF 3D, Urban
  Reign, WMXIX) — doc-level research, not binary data.

## 15. What "done" means for the next pass (acceptance criteria)

1. GRE batch-motbin PR (sibling run) lands: 31 WH + 19 non-WH JSONs on GRE
   main under `teardown/tekken7-steam/tkdata/mothead/json/`, plus the
   converter script committed. Verify by listing that dir after merge.
2. WH moveset reconciliation: mega-batch lane (#1039) + batch-motbin
   wired/ output resolved into ONE moveset per fighter on main — no
   competing rewrites, no clobber.
3. 0x8000 clip bytes: pakchunk0 enumerated; MOTA offset-list parsing done
   for at least the 8 T7-mapped fighters; clip_start_bytes no longer
   UNRESOLVED for those banks.
4. T5 motion bytes located + decoded (or a precise missing-source note).
5. T6 IDX mapping resolved (keyset B result + tiling test) → motion
   extraction unblocked.
6. TTT2 13 files identified (Jun first) → Jun decode for Megami.
7. VF5 motion extraction started (tool chain verified, not just planned).
8. WMXIX per-clip identities decoded → inputs wired (registry-only
   status retired).
9. 2K22 CAW structure extracted → creation-suite template lane unblocked.
10. Every §13 dir enumerated and promoted to a full entry.
11. GPU jobs run (parent browser task): job 01 Gang Beasts mining +
    job 02 all-bank anim classification; outputs committed to repo;
    king row 38 classification checked against the LP1 jumping-punch
    user report.
12. UI citation gap closed: GRE tekken7/ui/flash paths in ui_sources.json
    either restored (assets located in pakchunk0/UI_common/flash per
    T7-UI-LAYOUT.md) or re-pointed; the 7 legacy-unsourced screens
    sourced from teardown UI data or explicitly re-scoped.
13. Steam sweep (§18): every GAP title either pulled (teardown started)
    or explicitly deferred with a reason — none left as "looked at,
    skipped" without a note.
14. T8 model archives (83 MB + 30 MB in teardown/tekken8/models/)
    decoded to WH rigs or explicitly deferred — they are the largest
    single teardown binaries in the public repo and currently unwired.

## 16. UI / MENU / FRONTEND EXTRACTION — first-class, not an afterthought

UI teardown is uneven: T7/T8 menu data is genuinely measured and wired,
T3 UI art is extracted but unwired, and seven game screens are still
hand-made with no teardown source. The gap-fill coordinator wires from
this section.

### 16a. Tekken 7 UI — MEASURED, EXTRACTED, WIRED (with one citation gap)

- WH `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (1,830 bytes, READ this
  audit): measured layout rules from the T7 Steam extraction (PR #863,
  branch feat/t7-steam-extraction), source
  `teardown/tekken7-steam/pakchunk0/textures/UI_common/flash/` +
  `teardown/tekken7-steam/tkdata/list/SW_UI_*.bin`. Rules recorded (no
  Namco pixels in the public repo): roster card 96x148, P1 cursor
  208x336 red #e0182a double frame gradient-up, P2 cursor 208x336 blue
  #1a8cff, side panels 108x292, stage info 420x656 navy->black gradient
  red 1px rim notched corner, stage panel 1180x696, result lightning
  400x580 vertical blue-white bolt behind italic WIN, main menu column
  572x1080 dark glass vertical list soft blue core, panel gradient
  #1b2740 -> #0d1322 (55%) -> #04060a. Reproduced in CSS
  (game/t7-skin.css, game/menu-t7.css, game/js/menu-t7-layout.js).
- WH `teardown/tekken7/ui/`: GAME-OPTION-VS-MENU.md (1,815 bytes) +
  UI-EXTRACTION-STATUS.md (2,461 bytes). Docs only.
- GRE `teardown/tekken7-steam/tkdata/list/` dir EXISTS (dictionary/,
  list/, mothead/ confirmed) — SW_UI_MainMenu.bin / SW_UI_Option.bin
  files inside are NOT individually confirmed. Next: list list/ contents.
- CITATION GAP (verified 404 this audit): `game/ui_sources.json`
  cites `gre:tekken7/ui/flash/SW_UI_*.png` (MainMenu Base_OnlineMenu,
  CharacterSelect SlotRed/SlotBlue/Rep_CS_CH_PANEL_00, PauseMenu Replay
  Cursor_Sub/NavigationBar_Waku, ControllerSetup PanelBase1, StoryMode
  Win_3line, Result Lightning_02) — but GRE `tekken7/ui/` DOES NOT
  EXIST (404; GRE tekken7/ holds only arenas, customization, king,
  models, stages, tools, TEKKEN7-ROSTER-MAPPING.md, tekkenmods-docs).
  The ui_sources check (tools/ui-sources/check.py) should flag these.
  The assets' true home per T7-UI-LAYOUT.md is pakchunk0/textures/
  UI_common/flash/ (PR #863 branch) — next step: confirm
  UI_common/flash entries in GRE teardown/pakchunk0/manifest.json and
  re-point ui_sources.json, or restore the flash dir. Until then, the
  screen-menu/select/result "sourced" status rests on the WH-side
  measured doc (real) plus broken GRE citations (not real).
- Wired screens (ui_sources.json, verified this audit): screen-menu
  SOURCED, screen-select SOURCED, screen-result SOURCED.
- UNSOURCED screens (ui_sources.json status legacy-unsourced, i.e.
  pre-law hand-made, grandfathered only while untouched): screen-
  collection, screen-daily, screen-howto, screen-modewin, screen-
  movelist, screen-online, screen-reincarnate. THESE are the UI gaps:
  each needs a teardown source (T7 UI bins, T8 UI docs, or T3/T6 UI
  art) or an explicit re-scope decision. The movelist screen gap is
  doubly important: the Create-A-Move List editor (PR #998) is the
  user's correction tool, and its screen has no teardown source yet.

### 16b. Tekken 8 UI — select doc + refs, wired as reference

- WH `teardown/tekken8/ui/`: CHARACTER-SELECT.md (1,831 bytes) +
  refs/ (t8-select-ref-1/2/3.png per ui_sources.json). Cited as a
  screen-select source. Status: docs + reference images, not extracted
  UI binaries. T8 UI is reference-only for WH (T7 is the select source
  per standing law); do not wire T8 UI geometry as if it were T7's.

### 16c. Tekken 3 UI — EXTRACTED art, NOT wired into game UI

- WH `teardown/tekken3/ui/`: README.md + character-art/ (1 TIM+PNG pair:
  tim_8550) + fonts-text/ + menus/ (6 TIM+PNG pairs: tim_0947, tim_1031,
  tim_5894, tim_7524, tim_7576, tim_8552) + title-screens/. TIM = PSX
  texture format; PNG previews accompany each TIM. Status: EXTRACTED
  (real UI art bytes in repo) + DECODED (TIM->PNG previews exist) +
  NOT WIRED (no game UI screen uses T3 UI art). Experimental use
  (PROPOSED, not done): T3 retro UI theme / title-screen homage /
  font reference for a classic-mode menu skin. Never present T3 UI art
  as T7 UI data.

### 16d. Tekken 6 / 5 / TTT2 UI — art fragments + status docs only

- T6 UI: README.md + UI-EXTRACTION-STATUS.md + psp_ICON0.png
  (17,590 bytes) + psp_PIC1.png (251,946 bytes, PSP key art). PSP
  store art only — no menu layouts, no HUD definitions.
- T5 UI: UI-EXTRACTION-STATUS.md (1,528 bytes) only.
- TTT2 UI: UI-EXTRACTION-STATUS.md (4,775 bytes) only.
- Status for all three: docs-level. No extracted menu structures, HUD
  definitions, or select-screen geometry. Gap-fill: T6/T5/TTT2 menu
  structure extraction is unstarted work, not a completed pull.

### 16e. Other games' UI — docs-level only (except where noted)

- Urban Reign: UI-SYSTEM.md (in WH teardown/urban-reign/) — system
  doc, not extracted UI data.
- WWE 2K CAW flows: creation-suite spec PRs #770/#773/#775/#776/#777/
  #778 (menus from teardown research) — the creation-suite-fix lane
  owns wiring these into sub-menus/categories; the underlying 2K22
  CAW structure extraction gap (§9) still blocks full fidelity.
- No other game's UI binaries (HUD definitions, frontend flows,
  loading screens) were found in this audit. Loading screens
  specifically: no extracted loading-screen data from any game was
  found — WH loading UX (load-progress.js, 6% creep cap) is hand-made.
  Tekken loading-flow extraction (what T7 shows while loading, and
  when) is an open gap for the loading-speed lane (PR #1041).

## 17. GPU JOBS — per-file mapping (scripts in tools/kaggle-teardown-jobs/)

Full index + parent browser run instructions: tools/kaggle-teardown-
jobs/README.md (working copies in ~/workspace/kaggle-teardown-jobs/).
Summary (honest split — GPU where it helps, CPU where it does not,
BLOCKED where no bytes exist):

- GPU job 01 — Gang Beasts dump mining (01-gang-beasts-dump-mine.py):
  CPU-parallel keyword mining over dump.cs (27 MB) + il2cpp.h (43 MB) +
  script.json (81 MB) + stringliteral.json; OPTIONAL GPU semantic
  search (--embed, sentence-transformers). Verified on synthetic
  inputs (8 hits, correct counts). Parent runs on Kaggle with the four
  dump files as an input dataset; outputs = physics/ragdoll index for
  the WH ragdoll system. The script's verification file states GPU
  acceleration NONE for the mining step — regex does not run on GPU.
- GPU job 02 — T3 anim batch classification
  (02-anim-batch-analysis.py): vectorized root-trajectory
  classification over all 22 bank packs. Scale authority VERIFIED from
  tools/anim/t3_row_bake.py lines 173-175: rx/ry/rz are base64 int16
  root translation in MILLIMETRES (metres = value/1000); q is base64
  int16 quats x32767. Classification: jumping = rise >= 0.15 m and
  fall >= 0.10 m; crouching = drop >= 0.15 m ending down; else
  standing. Verified on synthetic inputs (flat -> standing, 0.4 m arc
  -> jumping, 0.3 m drop -> crouching). First real-run check owed:
  king bank row 38 (Pantera LP1) must classify jumping if the user's
  jumping-punch report is right. Torch CUDA when present, else honest
  CPU report — never a silent CPU pass as GPU.
- CPU sufficient (no GPU job, and none should be invented): T7 mot.bin
  decode (51/51 done, seconds/file), T7 .mvl parse, T7 frame-data
  conversion, T3 reaction bake, No Mercy/WMXIX decode, UI measurement
  (measurement + CSS, not batch math), gltfpack model optimization
  (CPU-parallel, studio lane, proven -54% to -65%).
- Real GPU jobs owned by sibling lanes (do not duplicate): Real-ESRGAN
  texture upscale (studio lane), UniRig rig/retarget (studio lane),
  Nosferatu track cutting (music lane, CUDA-proven script with loud
  failure without CUDA).
- BLOCKED (no job can run without bytes first): T5 motion, T6 IDX
  semantics (26 KB, 2 keysets — NOT a brute-force problem; GPU
  brute-force here would be theater), TTT2 identification, WWE 2K
  structure, VF5, DOA, Steam titles with no teardown (§18).

## 18. ANYTHING-ELSE SWEEP — every Steam title + every Tekken game

Source: ~/workspace/user/steam-library.md (85 Steam titles, PARTIAL
snapshot — user owns way more beyond Steam; absence from the list does
NOT mean not owned; never make the user prove ownership). Status key:
COVERED = teardown files exist (see manifest section). GAP = no
teardown files found this audit. PROPOSED = experimental WH use, NOT
pulled, NOT extracted — a direction for a future pull, never presented
as game data. Tekken games are listed first (the base), then other
games.

### 18a. Tekken games — the base (all covered or partial, none skipped)

- Tekken 3 — COVERED (banks wired, §5; UI art extracted, §16c).
- Tekken 5 — PARTIAL (catalog only, §6). GAP: motion bytes.
- Tekken 6 — PARTIAL (DINF decrypted, IDX contested, §7; UI art
  fragments, §16d). GAP: motion + voice attribution.
- Tekken Tag Tournament 2 — PARTIAL (13 hash files, §8; UI status
  doc, §16d). GAP: Jun identification.
- Tekken 7 — COVERED deep (mot/mvl/frame/UI/models, §1-§4, §16a).
- Tekken 8 — PARTIAL (select doc + refs, 2 SFM model archives:
  PHANTOM-t8-yoshimitsu-s1.7z 83,173,144 bytes + asuka-kazama-t8_SFM.rar
  30,027,257 bytes, §16b + §15 item 14). GAP: decoded movesets,
  animations, UI binaries. T8 mod stuff authorized (user owns T8 on
  disk; disk not accessible phone-only; access via mods/community).

### 18b. Steam titles WITH teardown coverage (6)

- Fire Pro Wrestling World (133.5h) — COVERED (GRE decompiled +
  manifest, §13). WH use: simulation/booking systems (already in
  scope as extra on top of Tekken base).
- Wrestling Empire (71.4h) — COVERED (GRE decompiled + docs, §13).
  WH use: mobile audio/UX reference (standing directive) + wrestling
  systems.
- Gang Beasts (11.2h) — COVERED (IL2CPP dump, §13 + job 01). WH use:
  ragdoll physics (standing vision).
- Yakuza Kiwami (26.7h) — COVERED (GRE extracted + manifest, §13).
  WH use: beat-em-up adventure structure (Heart and Mind Within
  reference) + city/stage design.
- WWE 2K19 (113 min) — COVERED in GRE only (extracted dir, §13);
  WH side = README stub. WH use: CAW parts + moveset library.
- TEKKEN 7 — COVERED (see §18a).

### 18c. Steam titles with NO teardown — GAP, each with a PROPOSED use

Nothing below is pulled. Each line is: title — PROPOSED experimental
use (one phrase). Pull order follows WH priorities (combat, creation,
story, UI, performance), not playtime.

- WWE 2K20 (57.3h) — PROPOSED: CAW structure + moveset library (same
  lane as 2K19; WH dir is a README stub, so this is a real gap, not a
  duplicate of 2K19 coverage).
- WWE 2K22 (49.2h) — PROPOSED: Create-A-Moveset structure (the
  unanswered #866 request) + CAW templates for the creation suite.
  WH dir is a README stub — highest-priority WWE gap.
- WWE 2K26 + every WWE 2K game (owned per user, absent from Steam
  list) — PROPOSED: latest CAW + moveset structures once 2K22's gap
  is closed; do not start 2K26 before 2K22's structure is understood.
- Yakuza 0 — PROPOSED: beat-em-up adventure structure + city design
  (same lane as Kiwami).
- Yakuza Kiwami 2 (19 min) — PROPOSED: same as Kiwami (engine
  iteration; compare Kiwami vs Kiwami 2 systems).
- Nioh: Complete Edition (3.1h) — PROPOSED: stance/ki-pulse combat
  rhythm ideas for WH stance systems. WH dir is a README stub.
- Nioh 2 (23 min) — PROPOSED: same as Nioh (burst-counter / yokai
  shift as transformation-system reference for WH transformations).
- Overgrowth (32 min) — PROPOSED: procedural animation / parkour
  movement reference for WH locomotion.
- Spore (6.2h) + Spore: Galactic Adventures + Spore: Creepy & Cute —
  PROPOSED: creature-creator parametric ideas for the creation suite
  (creature parts + sliders, same family as MPFB/MB-Lab wiring).
- Borderlands 3 (85.3h) — PROPOSED: loot/variant generation systems
  (attire/part variants) + cel-shaded rendering reference.
- The Elder Scrolls V: Skyrim Special Edition (77.4h) — PROPOSED:
  open-world quest structure for Heart and Mind Within adventure mode
  + modding/creation-kit patterns for WH's creation suite.
- Yu-Gi-Oh! Duel Links (69.2h) + Yu-Gi-Oh! Master Duel (3.8h) —
  PROPOSED: card/duel side-mode mechanics as a cousin to Go Qombat
  (grid/card strategy side mode family).
- Dragon's Dogma: Dark Arisen (39.1h) — PROPOSED: pawn/companion AI
  + climbing-grapple combat (grapple-system cousin).
- L.A. Noire (36.8h) — PROPOSED: investigation/dialogue structure
  for WH story mode (evidence/interrogation as non-fight gameplay).
- METAL GEAR SOLID V: THE PHANTOM PAIN (24h) + GROUND ZEROES —
  PROPOSED: stealth/infiltration mission structure + open-base
  systems for WH side modes.
- 3on3 FreeStyle: Rebound (18.1h) — PROPOSED: team sports side-mode
  structure (3v3 arena cousin to tag systems).
- War Robots (10.6h) — PROPOSED: mech/attire rigging reference
  (heavy-frame fighters) + team battle structure.
- The Witcher 3: Wild Hunt (9.9h) — PROPOSED: quest/choice story
  structure + sign/combat-stance variety for WH story mode.
- Drunken Wrestlers 2 (7.5h) — PROPOSED: physics-wrestling cousin
  to Gang Beasts ragdoll (same ragdoll lane, different flavor).
- Middle-earth: Shadow of War (6.9h) — PROPOSED: nemesis/rival
  system for WH arcade ladders (rival fighters that remember bouts).
- Crossout (5.7h) — PROPOSED: vehicle/part-builder cousin to the
  creation suite (modular part assembly).
- Max Payne 3 (4.9h) + Max Payne 2 (2.4h) — PROPOSED: bullet-time /
  slow-motion presentation for WH KO/finisher cameras (KESSHOU
  presentation, not a combat mechanic).
- Path of Exile (3.6h) — PROPOSED: skill-tree/progression systems
  for WH rank ladder + fighter progression.
- Muck (3.5h) — PROPOSED: survival/co-op side-mode structure.
- Just Cause 2 (3h) — PROPOSED: grapple/parachute traversal ideas
  for WH realm travel (roads-not-portals traversal flavor).
- RuneScape (2.9h) + Old School RuneScape — PROPOSED: skill/progress
  systems + economy for WH meta-progression.
- Red Faction: Guerrilla Steam Edition (2.4h) + Red Faction +
  Red Faction Guerrilla Re-Mars-tered + Red Faction: Armageddon —
  PROPOSED: destruction physics for WH stage interaction (wall/floor
  break presentation cousin).
- Red Dead Online (2.2h) — PROPOSED: open-frontier world structure
  for WH's Western Heart overworld flavor.
- STAR WARS: The Old Republic (57 min) — PROPOSED: MMO class/role
  structure for WH team modes.
- Pro Wrestling X (55 min) — PROPOSED: wrestling-system cousin
  (same lane as Fire Pro/Wrestling Empire).
- Walking Simulator 2020 (55 min) — PROPOSED: none seriously;
  noted only for completeness (walking-sim structure is the null
  case — no WH system needs it; recorded so it is not re-asked).
- Digimon Masters Online (27 min) — PROPOSED: monster-partner
  progression cousin to WH spirit/stand companions.
- Drug Dealer Simulator: Free Sample (23 min) — PROPOSED: none
  seriously; noted for completeness (economy-sim flavor only, no WH
  system needs it; recorded so it is not re-asked).
- Tap Ninja (16 min) — PROPOSED: none; idle-game loop is not a WH
  system (recorded for completeness).
- Creativerse (14 min) — PROPOSED: voxel building cousin to WH
  stage/creation tools (block building for custom arenas).
- Alien Swarm: Reactive Drop (13 min) — PROPOSED: top-down co-op
  shooter structure for a WH side mode.
- Crab Game (13 min) — PROPOSED: party-minigame structure for WH
  side games / for-fun section.
- Destiny 2 (13 min) — PROPOSED: live-service season/ladder
  structure for WH daily challenges + ranked seasons.
- Aimlabs (9 min) — PROPOSED: aim/timing trainer structure for WH
  training mode (input-timing drills).
- Fallout 3: Game of the Year Edition (8 min) + Fallout Shelter —
  PROPOSED: open-world quest structure (Fallout 3) + base-management
  side mode (Shelter) for WH meta-progression.
- eFootball (7 min) — PROPOSED: sports side-mode structure.
- UNDEFEATED (6 min) — PROPOSED: superhero-flight movement
  reference for WH flying/transformation states.
- Counter-Strike 2 (5 min) — PROPOSED: round/economy structure
  cousin to WH round flow (buy-phase ideas do NOT map to Tekken
  rounds; noted as structure-only reference).
- Tales of the Neon Sea (4 min) — PROPOSED: detective-puzzle story
  structure (same lane as L.A. Noire).
- Master Spy (2 min) — PROPOSED: stealth-puzzle side mode.
- Game Migrated to Another Steam Page (2 min) — PROPOSED: none;
  unidentifiable title, recorded for completeness only.
- Angel Wings — PROPOSED: flight/visual-novel structure (needs
  identification before any pull; recorded, not skipped silently).
- Century: Age of Ashes — PROPOSED: dragon-flight combat as
  transformation-state movement reference.
- Conqueror's Blade — PROPOSED: large-battle / siege structure
  for WH multi-fighter modes.
- DC Universe Online — PROPOSED: superhero MMO power/role systems
  for WH power customization.
- DCS World Steam Edition — PROPOSED: flight-sim fidelity
  reference only (no WH flight system planned; recorded, not skipped).
- ENDLESS Space – Definitive Edition — PROPOSED: 4X strategy
  structure as a distant cousin to Go Qombat (strategy side mode).
- Gorilla Tag — PROPOSED: VR locomotion reference (arm-swing
  movement; WH is phone-first, so VR-only mechanics do not transfer
  — recorded with that limitation).
- H1Z1: Test Server — PROPOSED: battle-royale structure for a WH
  multi-fighter side mode.
- Halo Infinite — PROPOSED: arena shooter structure + grapple-shot
  traversal cousin.
- Heavy Burger — PROPOSED: party-brawler structure (same family
  as Gang Beasts / Crab Game side modes).
- Knightfall: Rivals — PROPOSED: card-battler structure (same
  family as Yu-Gi-Oh side-mode notes).
- MechWarrior Online — PROPOSED: mech customization (same lane
  as War Robots heavy-frame reference).
- Paladins (+ Public Test) — PROPOSED: hero-shooter role structure
  for WH team modes.
- Phantasy Star Online 2 New Genesis — PROPOSED: action-MMO combat
  rhythm for WH adventure mode.
- Portal Reloaded — PROPOSED: portal/traversal puzzle ideas for
  WH realm travel (roads-not-portals flavor — portals as contrast,
  not as the mechanic).
- Quantum Replica — PROPOSED: time-manipulation presentation
  cousin to WH time-break systems (presentation only).
- Re-Legion — PROPOSED: cult/convert strategy structure (distant
  cousin to WH soul systems — thematic only, not mechanical).
- Rogue Company — PROPOSED: hero-shooter role structure (same
  lane as Paladins).
- SMITE (+ Public Test) — PROPOSED: god-archetype roster design
  (divine-being fighters are already WH canon; SMITE's god roster
  is a design-comparison reference, not a pull source).
- Splitgate — PROPOSED: portal-arena shooter structure (same
  traversal note as Portal Reloaded).
- Z1 Battle Royale — PROPOSED: battle-royale structure (same
  lane as H1Z1).
- TEKKEN 8 (owned on disk, absent from Steam list) — see §18a.

### 18d. Non-Steam games already in teardown scope (not in the 85)

- WWF No Mercy, WWE WrestleMania XIX, WWE 2K19/20/22 (see §9) —
  wrestling base for creation suite + movesets.
- Virtua Fighter 5, Dead or Alive 4/6, Soulcalibur 2/6, Street
  Fighter 3D games / EX series / 5, Def Jam Fight for NY, Urban
  Reign, Yakuza Kiwami, Nioh, Fire Pro, Gang Beasts, Wrestling
  Empire (see §10-§13) — docs-level or better, each with a named
  next step in its section.
- TempleOS (public domain, user-approved 2026-10-24 evening as
  Shrine体系): pull all of TempleOS + wire three ways (Heart and
  Mind Within mode, Eastern Mind canon sacred computer-system realm,
  own playable mode in side games / for-fun section: retro terminal,
  16-color look, playable mini-game from TempleOS's games). Canon
  100%, grounded in CANON.md. TempleOS attribution stays in
  technical docs only — never "TempleOS" in-game. This is a NEW
  sweep item from the evening's standing directives, not a Steam
  title, and it belongs in the anything-else list because the user
  explicitly approved it the same evening as this audit.
