# Byou → Wang Jinrei base rebuild — proof (2026-11-06)

Owner ruling (2026-11-06): "He can have wang if no one else does."
Verified before wiring: no fighter holds Wang Jinrei anywhere (full
taken set from `game/data/roster_map.json` + every moveset header on
main, checked 2026-11-06). Lei Wulong is Rave's alone (owner
2026-10-21, recorded in `game/js/roster-full.js` and
`docs/movesets/SOURCE-MERGE-2026-10-21.json`).

## Source revision used

`teardown/tekken6/movesets/t6psp-wang-moveset-v3.json` — v1/v2/v3 are
one decode of the same source container (idx68_entry724.bin, sha256
eb6224a929c39d1844540226282e01f1bb76084a2c3781ee1225c3efcedd3fd2, 254
name records). v2 added the round-14 notation pass, v3 the round-15
notation pass (command_decoded glyph decode: 233 of 254 records carry a
decoded command, collapsing to 70 unique commands; the 254 records are
multi-language name strings, not 254 distinct moves). v3 is the most
complete revision and is the one wired.

## Probe (file-level, run against the rebuilt byou.json)

```
== parse + header ==
fighter: byou | tekken_base: Wang Jinrei | t3_source: jin | t6_base: wang | t7_base present: False | schema: 2
== playable entries ==
moves: 157 (before 728)
entries missing playable fields: 0 []
strings: 29 | specials: 4 | hit_words: 153 | stance_after: {}
== Wang resolution ==
wang records wired: 254 (decoded 233, undecoded 21)
unique commands: 70; with playable entry: 16; kit-only: 54
playable entries carrying a t6_wang ref: 17
lei anim_refs remaining in moves: 0
lei mentions in header fields: []
== signatures (byte-level compare of the move objects) ==
  D+K: identical to pre-rebuild = True
  S: identical to pre-rebuild = True
  d+4: identical to pre-rebuild = True
  1+2: identical to pre-rebuild = True
  canon_moves identical = True
  Wrong Foot name: Wrong Foot [WH SIGNATURE] | Sickness Pattern name: Sickness Pattern [WH SIGNATURE]
== entry delta ==
entries removed: 571 (all T7 Lei layer; the same kit lives in rave.json: 1,086 moves)
entries added: []
```

Node checks: `roster-full.js` parses as ESM; `byou.json` and
`roster_map.json` parse; roster_map byou = Wang Jinrei with
moveset_sources {"t6":["wang"],"t3":["jin"]}, moves_match_slot true;
slots Lei Wulong = ["rave"], Wang Jinrei = ["byou"]; the Lei
double-claim issue string is gone.

## What the numbers mean (honest limits)

- The 571 removed entries were the T7 Lei Wulong import layer inside
  Byou's file (anim_refs t7:lei). Lei's full kit, including the same
  Five Animals stance map, lives in `game/assets/movesets/rave.json`
  (1,086 moves). Nothing was lost from the repo.
- Wang's sources in our holdings contain names and commands only: no
  frame data, no damage, no animation bank (Wang is not in Tekken 7/8;
  his TTT2 motbin was never decoded). The 54 kit-only commands are
  wired as kit data in `wang_kit` with `playable_entry: false`, not
  given invented numbers. Playable frame/damage/anim rows remain the
  T3 jin bank this file has always run (the same proxy-bank pattern as
  Dio on heihachi and Slice on bryan), now documented in the file's
  `wang_rebuild.gaps`.
- No gameplay harness run is claimed: this proof is file-level
  (parse, completeness, resolution, signature integrity). Byou's
  vessel loads `demonio` in `game/js/roster-full.js` (wh_moveset),
  which this PR deliberately does not change.
