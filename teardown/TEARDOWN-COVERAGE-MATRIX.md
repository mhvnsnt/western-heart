# TEARDOWN COVERAGE MATRIX

**Generated:** 2026-10-22 (teardown-tooling lane); Tekken 5 row updated 2026-10-23 (T5 extraction lane)
**Grounding:** `teardown/TEARDOWN-STATUS.md` (updated 2026-10-13 — flagged STALE where
newer lane work exists), per-game `teardown/<game>/` dirs, `docs/MOVESET-COVERAGE.md`
(regenerated 2026-10-21: 85 fighter files, 7,294 base moves), `tools/re/QUEUE.md`.
**Owner directive:** 100% teardown of every game. No gaps. No deferral.

Asset columns: **Models** (fighters rigged/extracted) · **Anims** (animation banks decoded) ·
**Movesets** (per-fighter move data) · **Stages** (arenas) · **Audio** · **UI/Textures**.
Scores are teardown completeness (extraction + decode + wiring), not game-ship quality.

## Tekken family (priority order per owner: T3 → T7 → T6 PSP → Tag → others)

| Game | Models | Anims | Movesets | Stages | Audio | UI/Tex | Overall | Blocker |
|---|---|---|---|---|---|---|---|---|
| Tekken 3 (PS1) | 100% — 7 fighters, KMD bodies via `tools/anim/t3_extract_bodies.py` | 100% — banks decoded, `t3_row_bake.py`/`t3anims.js` retarget | 100% — 3,247 moves, `moveset_*.json` per fighter | 100% — 15 stages | 100% | 100% — 8,556 textures, TIM decoded | **100%** ✅ | none — RE only for gaps |
| Tekken 7 (PS4/PC) | ~35% — 5 King variants only (T8 base 50,950p, T8 S2 43,462p, T3 legacy 66,052t, T7 1P 54,612t, Armor King 48,870p); rest via rigmodels/DeviantArt pulls | ~30% — T7 anims via TKMovesets path only where extracted | ~40% — frame data 47 chars/11,137 rows (`fetch_t7chicken_framedata.py`); TKM2 decode lane ready (`tools/moveset-decode/`) | ~10% — Mishima Dojo map only | 0% | ~20% | **~40%** | full 51GB game never acquired (landing-zone problem) |
| Tekken 6 (PSP) | ~10% — NDPP bounding volumes only; DATA401 models encrypted | ~10% — videos (46 endings) done, motion data locked in DATA401 | ~20% — 40-fighter roster mapped, no per-fighter moves | ~10% — structure mapped | ~30% — videos extracted | ~20% | **~30%** | DATA401.IDX + 384MB region encrypted (see `teardown/tekken6/T6-KEYHUNT-REPORT-2026-10-22.md`) |
| Tekken Tag 2 (X360) | ~5% — 26/26 chunks on release, STFS not extracted | 0% | 0% (TKMovesets supports TTT2 gameId 2 — extractor ready, needs data) | 0% — 29 stages documented, none extracted | 0% | 0% | **~15%** | STFS extraction; **NEW unblock:** TTT2-PC static-recomp port (`TTT2-PC-PORT-ASSESSMENT.md`) |
| Tekken 8 (PC) | ~15% — King T8 base/S2 variants pulled as reference only | 0% | ~10% — wavu frame data 41 chars/6,284 moves (reference, not extraction) | 0% | 0% | 0% | **~10%** | binary not acquired |
| Tekken 5 / REV | 0% | 0% (498 motion files mapped, romD format queued) | 0% (roster mapped; TKMovesets gameIds 3/5 structs ready) | 0% (16 versus + 5 DW stages documented) | 0% (inventoried) | 0% (inventoried) | **~15%** | ISO acquired+surveyed 2026-10-23; DW anim files located; model/anim/moveset decode → RE bench |

## Other games (owner vision: folded in the same way after Tekken)

| Game | Models | Anims | Movesets | Stages | Audio | UI/Tex | Overall | Blocker |
|---|---|---|---|---|---|---|---|---|
| WWF No Mercy (N64) | 100% — 3,570 models | 100% — 5,787 anims | 100% | 100% — 17 arenas | 100% | 100% — 5,029 textures | **100%** ✅ | none |
| Virtua Fighter 5 (PS3) | 100% — 19 fighters | 100% | 100% | 100% — 38 stages | 100% | 100% | **100%** ✅ | none (customization/moveset RE queued) |
| Urban Reign (PS2) | ~95% — VGS cracked, 509 files; DCM semantics + inner PPK geometry open | ~95% — 46 motion packs | ~90% | ~95% — 72 UI screens | 100% — 1,033 audio files extracted | ~95% | **~95%** ✅ | bind matrices in Ghidra now (`tools/re/QUEUE.md` #1) |
| WWE WrestleMania XIX (GC) | ~90% — 126 wrestler OBJs, 2,690 CAW parts | ~85% — 170 YANM anims | ~70% | ~90% | ~85% | ~85% | **~80%** | format semantics (watchdog lane, 28 attempts) |
| Soulcalibur II (Xbox/PS2) | ~70% — Xbox extracted; PS2 FS not cracked | ~60% | ~50% | ~60% | ~60% | ~60% | **~60%** | owner decision: Xbox vs PS2 as primary |
| Dead or Alive 4 (X360) | 0% — 30/30 chunks on release, not reassembled | 0% | 0% | 0% | 0% | 0% | **~15%** | reassemble ISO + extract (sequenced after TTT2; disk) |
| Soulcalibur VI (PC) | 0% — mechanics doc only | 0% | ~10% (doc) | 0% | 0% | 0% | **~10%** | 32GB binary not acquired |
| Dead or Alive 6 (PC) | 0% — mechanics doc only | 0% | ~10% (doc) | 0% | 0% | 0% | **~10%** | 50GB+ binary not acquired |
| Eastern Mind (PC-98) | 0% — 549MB safe on release, not extracted | 0% | 0% | 0% | 0% | 0% | **~20%** | extraction not started |
| Def Jam: FFNY | — | — | — | — | — | — | **—** | assess `teardown/def-jam-fight-for-ny/` |
| Street Fighter EX / 3D SF | — | — | — | — | — | — | **—** | assess `teardown/street-fighter-*/` |
| WWE 2K18 / 2K19 | 0% | 0% | 0% | 0% | 0% | 0% | **0%** | acquisition not started (issue #253 merged plan) |

## How to move a number

1. Pick the top blocker in the Tekken table, in owner priority order.
2. Run it through the RE bench (`tools/re/README.md`): `analyze.sh` → scripts → GhidraMCP →
   extractor → verify (extract + render vs real game).
3. Land the extractor as a permanent stage under `tools/` or `lab/tools/` with docs
   (NO-HAND-TOOLING law: no one-off scripts, only pipeline stages).
4. Update this matrix + `teardown/TEARDOWN-STATUS.md` + `tools/re/QUEUE.md` in the same PR.

## Freshness

`TEARDOWN-STATUS.md` was last updated 2026-10-13. This matrix re-grounds every number
on 2026-10-22. If a lane changes a number, it updates both files — a stale scoreboard
is how gaps hide.
