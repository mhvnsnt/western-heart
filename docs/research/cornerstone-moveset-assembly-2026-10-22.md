# CORNERSTONE moveset assembly (worker 68, 2026-10-22)

## Owner directive (verbatim, 2026-10-22 ~18:07 CDT)
"Name is CORNERSTONE (capital C, capital S). 'Ryuji Rock' was the working name.
Internal ID stays `ryuji-rock` for plumbing. Update canon refs to CORNERSTONE."
Full spec: (1) Ryuji Yamazaki base (3D KOF): stance, taunts (tongue out),
Serpent Slash, Sand Kick, Knife Slash, Bai Gaeshi, Bakudan Pachiki, Todome,
Guillotine, Pit Viper, Drill — from 3D KOF games, coordinate with worker 59's
KOF lane, don't duplicate acquisition. (2) The Rock: Rock Bottom (King's Tekken
version + WWE All Stars + WWE teardown animations), People's Elbow (King's
jumping diving elbow from Tekken), Sharpshooter, Brahma Bull Lariat.
(3) Younger Toguro (Yu Yu Hakusho): the thumb flick blast — repeatable air
pressure blast, SPAMMABLE like in the anime — plus whatever the YYH teardown
gives. Everything stacked on the Tekken base + input-to-move fidelity
(Tekken notation, press 1 = left punch). Build through the moveset library per
worker 47's format. Canon: Cornerstone's full name in docs/owner-directives.md
+ CANON.md (surgical edits only).

## Coordination
- Worker 59's KOF3D lane covered Iori/Kyo/Leona/Terry/King/Mai — NOT Ryuji
  Yamazaki. No acquisition duplicated: I decoded Yamazaki's XV command list from
  published sources (altarofgaming icon-alt text) and recorded XIV/MI deltas in
  notes, following w59's federation format and conversion rule exactly.
- Worker 47's library (PR #678/#699, unmerged at build time): banks and manifest
  below follow `game/data/moveset-library/schema.json` (v1) field-for-field;
  federation files follow w59's `kof3d-*.json` shape. Nothing of w47's or w59's
  was edited — only new files added, plus the ryuji-rock.json rewrite and two
  surgical registry/doc edits that are this lane's own.

## KOF3D Ryuji bank — what was decoded
- Source: KOF XV Yamazaki command list (altarofgaming, 17 moves, icon alt text
  decodes every command); XIV deltas from snk.fandom (Climax list, Drill page);
  classic kit from the KOF Neowave move list (SNK wiki).
- 26 entries: stance, Eviscerator (f+1), Slam (f+3), Serpent Slash x3
  (qcb+1/+3/+2), Keep/Cancel, Spray Sand (dp+4 — XV standalone AND Serpent
  follow-up), Bombshell Badda-Bing x2 (hcb,f+1/+2), Double Return x2 (qcf+1/+2,
  reflects projectiles), Sadomaso x2 (hcf+3/+4 — THE tongue taunt counter),
  Fight of Tempering (dp+3), Todome XV x2 (hcb,f+3/+4), Guillotine x2
  (qcf,qcf+1/+2), Pit Viper x2 (qcb,hcf+1/+2), Drill Climax 4 levels
  (hcb,hcb+1), Kachikomi / Whackdown Wallop (1+3), Knife Slash legacy (hcf+1).
- Notable findings: XV FLIPPED Serpent Slash from qcf to qcb (recorded);
  classic 2D Knife Slash is absent from XV (kept as legacy per owner spec);
  XV Todome (hcb,f+K) is a different move from the classic downed-finisher
  Todome — both kept, versioned.
- **Pit Viper correction:** the pre-existing `ryuji.json` had Pit Viper as
  `qcb,qcf+1` — XV-verified command is **qcb,hcf+P** (altarofgaming icon alts).
  Corrected in the assembled file with a note; bank carries the verified input.

## The Rock bank — 6 entries
Rock Bottom (1+3, uranage — multi-source per owner: King's Tekken version,
WWE All Stars, WWE teardown animations), People's Elbow diving (u/f+2 —
King's jumping diving elbow, owner-specified), Sharpshooter (d/b+1+3 hold),
Brahma Bull Lariat (f,F+2), Layin' the Smackdown (1,1,2 string),
Rock's DDT (d/b+1+2, kept from ryuji.json).

## Toguro bank — 18 entries
Full YYH: Dark Tournament kit — see
`docs/research/yyh-dark-tournament-younger-toguro-2026-10-22.md`. Universal
normals, 4 spirit moves, 3 combos. Thumb Flick Blast: `qcf+1`, hold-repeat,
12f recovery.

## Assembly
- Manifest: `game/data/movesets/cornerstone.json` (w47 format, assembly v2) —
  50 library refs (26 kof3d + 6 wwe-rock + 18 yyh), 4 documented layers.
  Tekken-base normals carry over from `ryuji.json`'s KOF normal mappings
  (already Tekken-ized 1:1) — documented in the manifest, not duplicated.
- Game file: `game/assets/movesets/ryuji-rock.json` — 116 moves (103 carried
  from `ryuji.json` + 13 new: Sharpshooter, Brahma Bull Lariat, Thumb Flick
  Blast, Earth Slash, Ki Blast, Increase Strength, Repel, Toguro Finisher,
  Long Way to Hell, Spray Sand, Fight of Tempering, Todome XV x2).
  `display: "CORNERSTONE"`, `variant: 2`, proxy fields removed.
- Wiring: `game/js/movesets.js` loads `assets/movesets/{fighter_id}.json`;
  `game/assets/movesets/index.json` `ryuji-rock` entry updated (display,
  counts, bytes, `library_manifest` pointer). No other registry needed.

## Source-law check (claimed-map.json, worker 47)
- King is claimed by Pantera — the old `ryuji-rock.json` T3-King proxy
  (24 moves) has been REMOVED and replaced by the real Yamazaki kit.
  Cornerstone now pulls from KOF / WWE / YYH namespaces only: all unclaimed.
- The `ryuji` (pure Yamazaki) slot is untouched.

## Index registration (for whoever merges second)
This branch adds `game/data/moveset-library/banks/{kof3d,yyh,wwe-rock}.json`
but does NOT touch `game/data/moveset-library/index.json` (worker 47's PR owns
it). When #678/#699 merges, add to `banks[]`:
```json
{"id":"kof3d","game":"kof_xiv_xv_mi","file":"banks/kof3d.json","moves":26,"source_banks":1},
{"id":"yyh","game":"yyh_dark_tournament_ps2","file":"banks/yyh.json","moves":18,"source_banks":1},
{"id":"wwe-rock","game":"wwe_multi","file":"banks/wwe-rock.json","moves":6,"source_banks":1}
```
Namespaces `kof3d:` / `yyh:` / `wwe:` extend the schema's id vocabulary
(`game/data/movesets/cornerstone.json` carries the same snippet in
`index_registration`).

## Validation
- `node gen-cornerstone.mjs` — all 8 files written; 116 moves / 114 inputs.
- Schema check: all 50 bank entries carry every v1 required field; frames are
  numbers; `provenance.estimated` is an array on every entry.
- Manifest cross-check: all 50 `library_id` refs resolve to bank ids.
- Federation files parse; assembled file parses; `display === "CORNERSTONE"`.
- Estimated fields flagged per-entry (frames.active/recovery/total, damage,
  hit_advantage; damage_raw where the source published no number). Toguro
  combo `damage_raw` carries the FAQ's real numbers (981 / 1223).

## Generator
`~/workspace/w68/gen-cornerstone.mjs` — single source of truth
(federation-first, projected to library v1 + manifest + assembled file).
Re-run: `node gen-cornerstone.mjs <repo-root>`.
