# DOA4 Movesets — research report (worker 59, 2026-10-22)

## What this is
Full moveset extraction for the 17 Dead or Alive 4 fighters not already covered by the
existing `doa` bank on main (which covers bass, kasumi, hayabusa, ayane, tina, jannlee).
No duplication with that bank: roster cross-checked against the fandom DOA4 roster lists.

## Sources
- **Primary:** deadoralive.fandom.com per-character DOA4 command lists
  (real move names; command icon alt text gives exact DOA commands).
  - Tengu's page lives under his real name: `Bankotsubo/Dead_or_Alive_4_command_list`
    (`Tengu/...` and `Tengu_(Dead_or_Alive)/...` both 404).
  - La Mariposa's page lives under `Lisa_Hamilton/Dead_or_Alive_4_command_list`
    (`La_Mariposa/...` 404s).
  - Alpha-152's page is a plain-text command list ripped from the 2005.09.30 prototype
    (no icon images; duplicate/tentative names as listed).
- **Not published on fandom:** damage and frame data. Estimated from archetype
  (jab s.167/d4; string ender d12–16; launcher d16–18 heavy knock 5.0–5.2;
  throw d20–28 heavy knock 5.0–6.0; counter hold d14–18 knock 3.8).
  Every entry flags estimates in `source_page`/`notes`; the ingest script must carry
  `name_status: "estimated"`-style honesty flags into the library (same as the VF5 lane).

## DOA → Tekken notation conversion (documented in each file's `conversion_rule`)
- P → 1/2 (armR/armL alternating), K → 3/4 (legL/legR alternating) on multi-hit strings
- numpad 8/2/4/6/9/7/3/1 → u/d/b/f/u/f/u/b/d/f/d/b; 66 → f,f; 236 → qcf; 214 → qcb;
  63214 → hcb; 41236 → hcf; 360 → 360
- F+P (throw) → 1+3; F+G (counter hold) → 1+2; F+P+K attacks → 1+2
- Counter holds → `counter` class + `counter-hit` property
- Colliding inputs (same Tekken input, different DOA moves) get a `~variant` suffix
  on the dictionary key only; `entry.input` keeps the true Tekken input.
- Limb convention: 1=armR, 2=armL, 3=legL, 4=legR.

## Files (staging: `~/workspace/w59/staging/game/assets/movesets/`)
| File | Fighter | Moves | Style |
|---|---|---|---|
| doa4-alpha152.json | Alpha-152 | 94 | Kasumi-style clone set (prototype rip) |
| doa4-bayman.json | Bayman | 91 | Commando sambo |
| doa4-bradwong.json | Brad Wong | 55 | Drunken boxing |
| doa4-christie.json | Christie | 87 | Poison Serpent stance system |
| doa4-ein.json | Ein | 71 | Karate |
| doa4-eliot.json | Eliot | 68 | Xing Yi Quan |
| doa4-genfu.json | Gen Fu | 47 | — |
| doa4-hayate.json | Hayate | 47 | Mugen Tenshin ninjutsu |
| doa4-helena.json | Helena | 104 | Bokuho stance + back-facing set |
| doa4-hitomi.json | Hitomi | 100 | Karate |
| doa4-kokoro.json | Kokoro | 93 | Ba Ji Quan + back-facing set |
| doa4-lamariposa.json | La Mariposa | 78 | Lucha libre |
| doa4-leifang.json | Lei Fang | 41 | — |
| doa4-leon.json | Leon | 61 | Commando sambo |
| doa4-spartan458.json | SPARTAN-458 | 57 | Mugen Tenshin Karate (armored guest) |
| doa4-tengu.json | Tengu | 71 | Tengu-Dō (demon martial arts) |
| doa4-zack.json | Zack | 41 | — |
| **Total** | 17 fighters | **1206** | |

## Schema note
5 files written pre-compaction (hayate, zack, leifang, genfu, bradwong) use an older
federation schema (`fighter`/`display`/`tekken_base` keys; moves with `move_class`,
`startup` in seconds, `knock`, `soulGain`). The 12 post-compaction files use the new
format (`fighter_id`/`fighter_name`, `class`, integer `limb`). The ingest script
`tools/moveset-library-w59/ingest-doa4-kof.mjs` normalizes both at ingest time.

## Corrections during extraction
- Leon: one fabricated entry (`f,f+1+3` Neck Hang dash) removed; two JSON corruptions
  introduced by the edit repaired. Leon validates at 61 moves.
- SPARTAN-458: page lists duplicate move names with different commands (Slipspace
  Straight Combo ×2) — both kept as variants, both are real listed moves.

## Linkage to worker 47's lane
Read-only reuse: `tools/moveset-library/ingest.mjs`, `game/data/moveset-library/`
(banks + schema.json) were read, never edited. My lane adds a NEW bank
(`doa4`, `kof3d`) via my own ingest script + registration supplement for index.json
(worker 47's index.json itself is not edited). Documented in
`docs/decisions/2026-10-22-doa4-kof-ingest.md`.
