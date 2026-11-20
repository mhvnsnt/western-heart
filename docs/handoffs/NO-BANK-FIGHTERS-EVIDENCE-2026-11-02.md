# No-bank fighters — evidence close-out (2026-11-02)

Lane A / A2 (banks + NO-ENTRY lane). Question closed here: for every fighter
with no clip bank, what is the base, what data proves it, what exists today,
what is missing, and what exactly unblocks it. All claims below were read
from the fighter's own data files on `main` (HEAD `1a6c77a7`) or from the
teardown records cited inline. Bases were resolved from the characters' own
data (owner method 2026-11-01: "the characters data will say 10 times
over"), never guessed.

## Engine facts that frame all six cases

- `game/assets/anim/t3/` holds 22 clip banks only (see
  `game/assets/anim/t3/STANCE-STATUS.json`). No Raven, Lucky Chloe, Jun,
  Dural, Bass, or Yamazaki/Rock bank exists in that set.
- `game/assets/anim/t7/INDEX.json` states it in its own headline: **zero T7
  clip banks exist in `game/assets/anim/`**. The T7 bank `0x8000`
  (frv 1,593 + dnc 1,527 moves) is CLIP-UNRESOLVED; `pakchunk0` was ruled
  out (meshes/textures only). GRE `teardown/tekken7-steam/tkdata/mothead`
  is move *tables* (JSON), not clip bytes.
- There is no T7 clip loader in `game/js` (only
  `game/js/t7-frame-data-loader.js`). Even with resolved keys, no playable
  T7 clip path exists in the engine today.
- The T7 INDEX names the primary unblock itself: **live-memory extraction
  with TKMovesets2 on a Windows machine running the owned T7** (load the
  base character in practice mode, export P1, confirm the ~1,702-entry
  MOTA). That is a live-game/browser-lane job on the owner's Windows/T7
  setup; it cannot be done from this VM.

## vainabel — base Bass Armstrong (DOA4). No Tekken bank exists.

- **Base, from its own data:** `game/assets/movesets/index.json` →
  `vainabel.tekken_base = "Bass Armstrong"`; the moveset's `doa_source` is
  `teardown/dead-or-alive-4/movesets/bass-armstrong/BASS-MOVELIST.md`
  (triangulated DOA2/DOA5/DOA6); curated rows live in
  `game/assets/movesets/doa-bass.json` and the bank table in
  `game/data/moveset-library/banks/doa.json`. The 60 fight moves already
  carry `doa:` anim_refs.
- **What exists:** full move table + documented movelist. No clip bytes.
- **What is missing:** the FIGHT clip bank. Designated source is DOA4 ISO
  motion extraction — `docs/anim/VAINABEL-ANIM-GAP-20261023.md` (FIGHT =
  DOA4 ISO motion extraction; SHOW = win/intro/taunts, no documented clips
  on disk).
- **DOA4 ISO path — concrete status (evaluated 2026-11-02):** the ISO
  itself is secured and verified: assembled 7,834,892,288 B from GitHub
  release `doa4-iso-v1` (30 parts, sequential append, size-verified;
  XGD/XEX2 format confirmed) — `teardown/dead-or-alive-4/DOA4-ISO-STATUS.md`.
  Extraction has since passed the XGD blocker and carved the AFS archives:
  219 XPR2 textures and 105 vertex buffers decoded (20-byte big-endian
  verts), index-buffer (IBUF) format still undecoded —
  `teardown/dead-or-alive-4/MODELS-ANIMATIONS.md`. The motion archives
  themselves, `mot.afs` (71 MB) and `anm.afs` (2.9 MB), are recorded as
  **ENCRYPTED** in the extraction report (`~/workspace/doa4-bass/
  EXTRACTION-REPORT.md`, file table) and have never been decoded; no DOA4
  motion-format parser exists in the teardown tooling (the Ghidra phase-17
  work targeted the XEX executable, not motion data).
- **Exact unblock:** a DOA4 motion-format decode (decrypt/parse `mot.afs` /
  `anm.afs` from the secured ISO, then convert Bass's clips to the game's
  bank format). That is an extraction-lane research project, not a wiring
  job. Until then vainabel's stance prefixes already read 0 NO-ENTRY
  (15/15 engine-resolved) — the gap is clips, not inputs.

## ryuji — hybrid base, no bank BY DESIGN

- **Base, from its own data:** `game/assets/movesets/index.json` →
  `ryuji.tekken_base = "Ryuji Yamazaki (KOF XV) / The Rock hybrid"`. There
  is no single Tekken base; only some moves name a `tekken_source`
  (King T7, e.g. the Rock Bottom rows). `proxy = false`.
- **What exists:** the hybrid move table (103 moves in index).
- **What is missing:** nothing that a bank assignment could supply — no
  single source character exists whose bank would be correct. Assigning
  any Tekken bank would be a wrong-character bank.
- **Exact unblock:** none applicable by design. Clips arrive per-move from
  their named sources (KOF XV Yamazaki / Rock-via-King rows) if/when those
  source extractions happen; there is no bank-level action.

## ryusan — base Lucky Chloe (Tekken 7). Table exists, no clip bytes.

- **Base, from its own data:** `index.json` →
  `ryusan.tekken_base = "Lucky Chloe (Tekken 7)"`; decisions doc
  `docs/decisions/2026-10-23-smutbase6-parts-system.md` (Ryusan (Mina
  Ashido) → Lucky Chloe).
- **What exists:** the T7 motbin move *table*
  `game/assets/anim/t7/dnc-ryusan-motbin-bank.json` (446,447 B,
  `wh-t7-motbin-bank/1`, GRE PR #61) — move rows only, **no clip bytes**.
  The moveset records `t7_motbin_clips.playable_wiring = "NONE"` (the join
  is not play-verified; dnc walks land on `Dc_sWALKF`).
- **What is missing:** Lucky Chloe's clip bytes + a T7 clip loader
  (see Engine facts).
- **Exact unblock:** live-memory TKMovesets2 extraction of Lucky Chloe
  from the owned T7 (per the T7 INDEX), then a T7 clip-bank format + loader
  in `game/js`. Not wireable from data already on disk.

## pond — base Raven (Tekken 7). Table exists, no clip bytes.

- **Base, from its own data:** `index.json` →
  `pond.tekken_base = "Raven (Tekken 7)"`; decisions doc 2026-10-23
  (Pond (Tsuyu) → Raven).
- **What exists:** the T7 motbin move *table*
  `game/assets/anim/t7/frv-pond-motbin-bank.json` (478,249 B) — move rows
  only, **no clip bytes**; `playable_wiring = "NONE"` as above.
- **What is missing:** Raven's clip bytes + a T7 clip loader.
- **Exact unblock:** live-memory TKMovesets2 extraction of Raven from the
  owned T7 (per the T7 INDEX: load Raven in practice, export P1, confirm
  the ~1,702-entry MOTA), then the T7 bank/loader work. Not wireable from
  data already on disk. (Pond's 80 NO-ENTRY stance inputs — LAB/SZN/HAZ/
  DEEP/MIST/STRIDE — are Raven T7 stance rows; they inherit this same
  clip-bank block and are itemised in the stance close-out.)

## zen — OWNER DECISION: no public bank, intentionally

- **Owner decision (binding):** `docs/decisions/2026-10-24-zen-base-decision.md`
  — Zen's base chain is Eleven/Twelve → Dural (VF5); Zen is **neither
  Heihachi nor Julia**. `game/js/fighter.js` `FIGHTER_BANK` carries
  `zen: null` *intentionally* (`hasOwnProperty('zen')` is true, so
  `bankIdFor` returns null before any fallback): "zen: null = UNMAPPED
  (owner decision 2026-10-24)".
- **The stale entry:** `game/assets/movesets/index.json` still lists
  `zen.anim_bank = "heihachi"` (and `tekken_base = "Heihachi"`). Per the
  code comment at that map, that is INTERIM frame-data provenance for his
  639 interim rows only; it is overridden by `FIGHTER_BANK` before use and
  is **not** a bank assignment. It is left as-is: changing it is a
  provenance-record edit, not a wiring fix, and this lane does not
  re-decide it.
- **What exists:** a private Dural bank exists only in the private GRE
  build (`game/assets/private/anim/vf5/dural/`, behind
  `__WH_PRIVATE_ASSETS`; `game/js/t3anims.js` `T3_BANKS.dural` is
  conditional on it).
- **Exact unblock:** none requested and none permitted from this lane —
  **do not wire a public bank for zen.** His 20 NO-ENTRY stance inputs
  (RAI/WAR/TACKLE/REV — VF5/VF-style rows from the interim set) stay
  itemised as owner-decision remainders, not defects to route around.

## megami — base Jun Kazama (TTT2). Move table exists, no clips anywhere.

- **Base, from its own data:** `index.json` →
  `megami.tekken_base = "Jun Kazama (Tekken Tag Tournament 2)"`,
  `t3_source = "tekken-wiki TTT2 Jun Kazama movelist (documented, no
  teardown bank)"`; decisions doc 2026-10-23 (Megami (Parvati) → Jun
  Kazama). Moves carry `anim_ref ttt2:jun:row:N` into the move table
  `game/assets/ttt2/movesets/jun.json` (40,154 B, PR #1235).
- **What exists:** Jun's full move table. **No clips:** Jun has no T3 bank
  (not in Tekken 3's 22 banks), no T7 appearance (T8 only; the `t8` folder
  holds clip-maps, no clips).
- **TTT2 motion evaluation (the one untested clip source, closed
  2026-11-02):** TTT2's motion container **was** reached. `data004.bin`
  (4,075,114 B compressed, XDVDFS sector 2116880, sha256
  `d8c73be42717153855815f505dc3f8dd384748e4d5458d412646b719fb003f51` —
  `teardown/tekken-tag-tournament-2/pulls/pull-manifest.json`) was
  LZX-decoded by the 2026-10-25 teardown lane to 6,522,032 B and is
  identified in `teardown/tekken-tag-tournament-2/DATANNN-MAP-20261025.md`
  as the **MOTA motion/animation table** (`MOTA` magic ×21). The decoded
  stream is reproducible from GitHub release `ttt2-7z-v1` (27 assets,
  13,529,225,673 B) with the in-repo tools
  (`teardown/tekken-tag-tournament-2/tools/lzx-decode/` +
  `tools/ttt2-section-decode/`); Jun's presence in the file set is
  confirmed (data052 customization table #42 is `jun`). **It stops there —
  this is a research-scale parse project, not a lane-scope decode:**
  1. No TTT2 MOTA parser exists anywhere in the repo's tooling
     (`tools/anim/` is T3 `t3_*` and T7 `t7_*` only). The MOTA record
     structure for the TTT2 build has never been parsed.
  2. Whether `data004.bin` holds Jun's actual keyframes, or a table whose
     entries point into the 33-of-42 `dataNNN.bin` files that were never
     pulled (inner set 8.4 GB; status doc
     `teardown/tekken-tag-tournament-2/TEARDOWN-STATUS-20261025.md`), is
     unverified — no dataNNN file has been mapped to a character's motion
     data.
  3. The engine has no TTT2 clip loader or bank path (banks are T3-format
     via `game/js/t3anims.js`), so even a parsed MOTA would need a new
     converter + loader before a single clip could play.
- **Exact unblock:** a dedicated TTT2 motion lane: (i) re-decode data004
  from `ttt2-7z-v1`; (ii) reverse the TTT2 MOTA record layout (Ghidra on
  the XEX / format RE — the NO-HAND-TOOLING route); (iii) prove Jun's
  clips are in data004 or pull the dataNNN file that holds them;
  (iv) build the MOTA→WH-bank converter + loader. Steps (ii)–(iv) are each
  open-ended; nothing in reasonable lane scope produces a wireable clip.

## Summary table

| fighter | base (per its own data) | table exists | clip bytes | unblock |
|---|---|---|---|---|
| vainabel | Bass Armstrong (DOA4) | yes (doa-bass.json, doa.json bank table) | none | DOA4 `mot.afs`/`anm.afs` motion decode (encrypted, unparsed) |
| ryuji | Yamazaki (KOF XV) / The Rock hybrid | yes (hybrid table) | none | none — no single base exists, by design |
| ryusan | Lucky Chloe (T7) | yes (dnc motbin table, 446,447 B) | none | TKMovesets2 live-memory extraction + T7 loader |
| pond | Raven (T7) | yes (frv motbin table, 478,249 B) | none | TKMovesets2 live-memory extraction + T7 loader |
| zen | Eleven/Twelve → Dural (VF5), owner decision 2026-10-24 | interim rows only | private GRE build only | none permitted — do not wire a public bank |
| megami | Jun Kazama (TTT2) | yes (ttt2 jun.json, 40,154 B) | none | dedicated TTT2 MOTA parse project (see above) |

No wiring change is landed with this document: every candidate assignment
was either a wrong-character bank, an owner-decision override (zen), or a
table without clip bytes. The stance-prefix consequences of these six are
itemised in the Step-2 stance close-out (Lane A, 2026-11-02).
