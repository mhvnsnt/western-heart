# KOF 3D Movesets — research report (worker 59, 2026-10-22)

## What this is
Moveset extraction for the 3D King of Fighters games feeding the moveset library:
KOF XIV (primary source — most complete public data), KOF XV (deltas recorded),
KOF: Maximum Impact 1 & 2 (classic kit, shared with the base movelist).

## Priority: Iori Yagami (Deathfang's moveset source)
User-approved exception: Iori is Deathfang's moveset source. Keep the claimed-map
consistent — recorded in `kof3d-iori.json` (`wh_claimed_map` field) and in
`docs/decisions/2026-10-22-doa4-kof-ingest.md`.

Iori's 3D kit:
- **KOF XIV:** Sakahagi / Kanyarai (throws); Ge-Shiki Yumebiki (+follow-up),
  Gofu In "Shinigami", Yuriori (command); 108 Shiki Yami Barai, 100 Shiki Oniyaki,
  127 Shiki Aoi Hana (3-hit rekka), 212 Shiki Kototsuki In, Kuzukaze, 311 Shiki
  Tsumakushi (specials); Kin 1211 Shiki Ya Otome = **Maiden Masher** (super),
  Ura 316 Shiki Saika (Ya Otome follow-up), Ura 1018 Shiki Yashiori,
  Kin 1218 Shiki Yatagarasu (Climax).
- **KOF XV deltas:** **Ura 108 Shiki Ya Sakazuki** (qcb,hcf+P, chargeable) takes the
  qcb,hcf+P slot (replaces Yashiori); Yami Barai REMOVED from Iori in XV.
  Both recorded in the federation file (`~xv` entry + note on Yami Barai).
- **Maximum Impact 1 & 2:** share the classic Yasakani kit (same move names);
  no separate file needed — noted in the source field.

## Sources
- **Primary:** snk.fandom.com — "The King of Fighters XIV/Move List"
  (full roster, one page; move names + command icon alt text decode every command).
- **XV deltas:** SNK wiki KOF XV move list (move-name level).
- Frame/damage not published per-move → estimated from archetype, flagged as
  estimated (same honesty rule as the DOA4/VF5 lanes).

## SNK → Tekken notation conversion (in each file's `conversion_rule`)
- A (LP)=1, C (HP)=2, B (LK)=3, D (HK)=4; directions map directly
- qcf/qcb/dp/hcb/hcf/qcf+hcb/qcb+hcf/2qcf/2qcb/reverse-dp preserved
- Close-only throws → 1+3-family; charge motions noted, input keeps end direction+button
- Rekka follow-ups recorded as input chains / sequenced entries
- `~variant` key suffixes for colliding inputs; `entry.input` keeps the true input

## Files (staging: `~/workspace/w59/staging/game/assets/movesets/`)
| File | Fighter | Moves | Style |
|---|---|---|---|
| kof3d-iori.json | Iori Yagami | 20 | Yasakani claw/flame (Deathfang's source) |
| kof3d-kyo.json | Kyo Kusanagi | 26 | Kusanagi kenpo/flame (full rekka tree) |
| kof3d-leona.json | Leona Heidern | 12 | Heidern assassination arts (charges) |
| kof3d-terry.json | Terry Bogard | 11 | Hakkyokuseiken |
| kof3d-king.json | King | 9 | Muay Thai |
| kof3d-mai.json | Mai Shiranui | 15 | Shiranui-ryuu ninjutsu |
| **Total** | 6 fighters | **93** | |

## Scope notes
- Ryo Sakazaki, Robert Garcia, Yuri Sakazaki have stub-only sections on the XIV page
  (no move data) — excluded rather than fabricated.
- Broader roster expansion (Benimaru, Daimon, K', Kula, Geese, etc.) is future work;
  the page structure is mapped (all 58 character section line numbers recorded this
  session) so a follow-up worker can pull them cheaply.
- VF5 motion stays with worker 57 — not touched.

## Linkage to worker 47's lane
Same as the DOA4 lane: read-only reuse of `tools/moveset-library/ingest.mjs` +
`game/data/moveset-library/`; new `kof3d` bank via my own ingest script.
