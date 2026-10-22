# Yu Yu Hakusho: Dark Tournament — Younger Toguro teardown (worker 68, 2026-10-22)

## Lane
YYH: Dark Tournament is worker 68's lane (parent dispatch 2026-10-22). No other
worker holds YYH material — checked worker 59 (DOA4/KOF3D: `doa4-iso/`, `kof-mi2/`,
no YYH) and worker 61's repo inventory (no toguro/yuyu/hakusho hits). No
duplication.

## Teardown status: RESEARCH TEARDOWN (no game files in holdings)
- The game is Yu Yu Hakusho: Dark Tournament (PS2, 2004, Digital Eclipse / Atari).
- No YYH game files exist in the teardown holdings — file-level motion
  extraction is future work (needs the disc + a PS2 animation pipeline; no crew
  pipeline exists for this title).
- This teardown documents Younger Toguro's COMPLETE kit from published sources:
  the GameFAQs walkthrough/FAQ (Team Toguro section), the US manual (PDF via
  Internet Archive), and the YYH fandom wiki. Move names, inputs, spirit-energy
  costs, combo damage, and mechanics below are all sourced, not invented.
- CANON.md's 2026-10-21 note said the Toguro blast "wires in when the source
  exists, never invented" — this research teardown IS the source. The blast is
  now wired (see `game/assets/movesets/ryuji-rock.json`).

## Sources
- GameFAQs: "Yu Yu Hakusho: Dark Tournament Walkthrough & Guide — Team Toguro"
  (https://gamefaqs.gamespot.com/ps2/920534-yu-yu-hakusho-dark-tournament/faqs/82147/team-toguro)
- US manual PDF: https://ia601507.us.archive.org/28/items/ps2_Yu_Yu_Hakusho-_Dark_Tournament_USA/Yu_Yu_Hakusho-_Dark_Tournament_USA_text.pdf
  (manual lists Younger Toguro spirit moves: Increase Strength, Earth Slash,
  Ki Blast, Finger Flip Bullets)
- YYH fandom wiki: Yu Yu Hakusho Dark Tournament (universal control list)
- Anime canon (thumb flick): en.mogimogy.com Younger Toguro strength writeup
  (Finger Flip Bullets — air bullets from a thumb flick, "very heavy" per Yusuke,
  fired in continuous series)

## Universal controls (all fighters, PS2)
| PS2 | WH Tekken input |
|---|---|
| Square (Jab) | 1 |
| Triangle (Punch) | 2 |
| Circle (Kick) | 4 |
| Left + Circle (Spin Kick) | b+4 |
| Down + X crouch, then Square (Low Punch) | d+1 |
| Down + X crouch, then Circle (Low Kick) | d+4 |
| Down + X crouch, then Triangle (Uppercut) | d+2 |
| Down + X crouch, then Left + Circle (Sweep) | d/b+4 |
| Triangle + Circle (Grab and Throw) | 1+3 |
| Hold X (Block) | b (hold back) |
| Square when fallen (Wake Up Kick) | 4 (grounded) |
| Up + X jump, then Square (Jumping Attack) | u+1 |
| R3 (Team Tag, tag mode only) | — |

## Younger Toguro — Spirit Moves (verbatim from the FAQ)
- **Increase Strength:** ↑ + R1 — 80%~ Spirit Energy. Toguro enters his 80% form
  for the REMAINDER OF THE ROUND. Increases the damage of Finger Flip Bullets
  and his normal attacks. The animation can be interrupted before he fully
  transforms. → WH: `u+1+2` (transition, armor while transforming)
- **Earth Slash:** ↓ + R2 — 50% Spirit Energy. Sends a red wave across the
  ground. Can go UNDER certain projectiles. → WH: `d+1+2`
- **Ki Blast:** ← + R2 — 25% Spirit Energy. Short-ranged, UNBLOCKABLE, negates
  projectiles, hits twice in the corner. → WH: `b+1+2`
- **Finger Flip Bullets:** → + R1 (CAN BE HELD) — 11% per shot. RAPIDLY fires
  small air bullets as long as the button is held. Huge damage at max spirit
  energy in 80% form. → WH: `qcf+1`, hold to repeat. **THE SPAMMABLE THUMB
  FLICK BLAST** — owner priority 2026-10-22 ("repeatable air pressure blast,
  SPAMMABLE like in the anime").

## Younger Toguro — Combos (verbatim from the FAQ)
- **Repel:** ←→ + O — 3-hit combo, hits further than it looks. → WH: `f+4,1,2`
- **Finisher:** ←→ + △, O, ↑ + △ — 981 damage while transformed. → WH: `f+2,4,u+2`
- **Long Way to Hell:** →← + △, ☐, O, ↑ + △ — 925 untransformed / **1,223
  transformed — one-shots anyone in a 2-player match**. Forward Back Triangle
  is 3 hits, Square is 4 hits, Circle is 3 hits, Up + Triangle is the last
  2 hits. → WH: `b,f+2,1,4,u+2`
- (Game's internal HP scale is unpublished — WH damage values are estimated and
  flagged in `provenance.estimated`; raw FAQ numbers kept in `damage_raw`.)

## Thumb Flick Blast deep-dive (why it is spammable)
- Anime: in 100% form Toguro launches air bullets by flicking his thumb
  (Shidan 指弾). Yusuke describes them as very heavy; Toguro fires them in a
  continuous series.
- Game: Finger Flip Bullets is explicitly hold-to-repeat (→ + R1 held),
  11% spirit energy per shot — the only rapid-fire projectile in his kit.
- WH wiring: `qcf+1`, low recovery (12f), hold-repeat. Increase Strength (80%)
  multiplies its damage, exactly like the source game.

## What this teardown feeds
- `game/assets/movesets/yyh-toguro.json` — federation file (w59 format), 18 entries
- `game/data/moveset-library/banks/yyh.json` — library v1 bank (w47 schema)
- `game/data/movesets/cornerstone.json` — manifest refs `yyh:toguro:*`
- `game/assets/movesets/ryuji-rock.json` — assembled CORNERSTONE game file
- Generator: `~/workspace/w68/gen-cornerstone.mjs` (federation-first, projected
  to library v1; method documented here)

## Open / future
- File-level motion extraction if/when the disc enters the holdings (new lane).
- Elder Toguro's kit (Hand Blade, Finger Spine, Regeneration) documented in the
  same FAQ — untouched, available for a future fighter or library bank.
