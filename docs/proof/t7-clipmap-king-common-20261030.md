# King 0x8000 join test against GRE common.arc (2026-10-30)

Programme step (c/g): the King clipmap gap from PR #1228 — 71 attacks on the
0x8000 bank — tested against the shared common bank. This record closes the
"common bank not held" question the #1259 inventory corrected: `common.arc`
IS held, and the join works.

## Sources (all read from the GRE repo, main state at run time)

- Private repo `mhvnsnt/game-reverse-engineering`, tree
  `teardown/tekken7-steam/tkdata/mothead/`:
  - `mask/common.arc` — 5,049,396 bytes, blob `80453212f9a2a2d526a36991e40841dd01959c3f`
  - `json/kinmot.json` — 7,633,965 bytes, blob `c71d1de7a7be2285dd013267afa6662bb063ebe8`
  - `mask/kinrotsm.arc` — 7,794,048 bytes, blob `be4c97c3a5553d92f6a59f36e5849c564e5a9270`
- Tool under test: `tools/anim/t7_clipmap.py` as extended in this chunk
  (optional 4th argument `common.arc`; `_decode_row` shared by the rotsm
  and common banks; exit non-zero on any rotsm/common decode failure).

## Method

Same bank rule as the rotsm join: first `MOTA` block, clip index
`anim_id & 0x3FFF`, type byte at the clip offset (`0x64` = full
`Anim64` decode, `0xC8` = frame count from the header). `common.arc`
holds exactly one `MOTA` block with 1,711 clips, starting at offset 0.
Two levels of proof were run: (1) the extended clipmap over the full
2,787-move `kinmot.json` (header decode per row, exit 0); (2) a full
frame decode (`Anim64.frames()`) of every 0x8000 attack clip, so the
claim is not header-only.

## Result — King coverage in the PR #1228 format

| Bank | Moves | Attacks | Decoded |
|---|---|---|---|
| 0x4000 rotsm (`kinrotsm.arc`, 1,138 clips) | 1,037 | 467 | 467, 0 errors (baseline reproduced exactly) |
| 0x8000 common (`common.arc`, 1,711 clips) | 1,628 | 71 | 71, 0 errors |
| 0x0000 inline (per-character story bank) | 122 | 14 | 0 — still a gap |
| **Total** | **2,787** | **552** | **538 / 552 = 97.5%** |

0x8000 attack detail: clip indices 2–1647, all in range of the 1,711
common clips; 64 distinct clips for the 71 attacks; all type `0x64`;
full-frame decode 71/71 with 0 errors, 5,528 frames total, per-clip
frames 3–232. Sample: `Co_runchop` clip 49 (87 frames),
`Va_Dwn_rk00` clip 270 (60 frames), `Co_Aokilk00` clip 276 (66 frames).
Backward compatibility: running the extended clipmap without the 4th
argument reproduces the old behaviour (common rows listed with bank and
clip index only, exit 0, same summary counts).

## What this does NOT claim

- The 0x64 joint-frame fix is still open: these clips decode, but 0x64
  attack clips decode crumpled including frame 1 (BUILD-LOG 2026-10-29
  18:00 finding). Join resolution is clip identity, not pose quality —
  baking still waits on the joint-frame fix. No clip is claimed
  bake-ready by this record.
- The 14 inline attacks remain unresolved (per-character inline/story
  bank, not in any GRE arc tested here): `Co_sjprk01F/02F/03F` (clips
  100–102), `Kg_lp00F` (103), `Kg_turas_n` (104), `Kg_t_slpF` (106),
  `Kg_rp00B` (107), `Kg_4rplp` (108), `Kg_AmericaRK` (110),
  `Kg_hizilp` (112), `Kg_shoryu_B2/B/EX` (114/115/117), `Kg_dki11` (118).
  They are the whole remaining King gap, not a partial count.
- No T7 clip is wired into the game by this chunk: no
  `game/assets/anim/t7/` bank, no `anim_t7` refs, no `_attackClipPlan`
  change. Wiring is programme step (f) and still needs the bake (step
  (e)), which still needs the joint-frame fix (step (a)).

## Next steps named by this record

1. Run the same extended clipmap for the other five T7 core-8 bases
   (Jin, Akuma, Alisa, Bob, Miguel — all FULL source per #1259) in this
   format, so each fighter's 0x8000 split is measured, not assumed.
2. The 0x64 joint-frame fix (step (a)) — still gated on paired
   0xC8/0x64 GRE data or a named community source; no guessed rotation.
3. The 14 inline attacks: community-extracted source first, then
   T3/VF5 fill documented per move (programme step (g)).
