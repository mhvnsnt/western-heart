# T7 Clip Mapping — the 781 UNMAPPED anim_refs, resolved from real Tekken 7 code (2026-10-30)

Owner order (2026-10-30): pull from the real code in the games in his Steam
library to fill the gaps. Source of record: the owner's own Steam TEKKEN 7
(app 389730), previously pulled via DepotDownloader into the PRIVATE
game-reverse-engineering repo (`teardown/tekken7-steam/`). No fighter
moveset file was edited by this lane; the per-fighter JSONs in
`game/assets/anim/t7/clip-maps/` are the supply layer for the provenance
lane to wire, per-character, at its own pace.

## What was blocking

The 781 moves (`anim_ref: UNMAPPED:t7-clip-pending`, audit 2026-10-29) needed
two things: (1) which real T7 move each WH move is, and (2) that move's actual
animation clip bytes. The clip bytes lived in `tkdata/mothead/mask/*.rotsm.arc`
— MOTA banks no lane had ever decoded (the "0x8000-bank clip bytes").

## What landed

**MOTA format cracked + validated** (full spec in GRE
`teardown/tekken7-steam/tkdata/mothead/mask/MOTA-FORMAT.md`): a `.rotsm.arc`
is a little-endian outer header wrapping big-endian MOTA sections (offset
table at +0x14 after a 0x14-byte header). Signature validation: 11,690/11,690
table entries across 10 arcs land on clip-start words 100/200. Bank map:
anim_id ≥ 0x8000 → `common.arc` (bare MOTA, 1,711 entries, key = id − 0x8000);
0x4000 ≤ id < 0x8000 → the character's own arc, section 0 (key = id − 0x4000);
id < 0x4000 → a bank whose file is NOT in the pulled tkdata tree (bounded,
see remainder). Clip format: header word 100/200 + track count; the 200-family
body is fully decoded (dense float32 BE, frames × tracks × vec3, size equation
exact on every clip); the 100-family body is sliced and indexed but its
quantised encoding is not yet decoded.

**The join** (WH move → real T7 motbin move): MVL display-name+notation exact
matches, the motbin cancel graph (incl. group cancels decoded from raw bytes),
and damage/startup fingerprint corroboration. The t7_id ordinal → MVLT row
shortcut was TESTED AND REJECTED with counterexamples (king_87 "Atlas Hammer"
is MVLT row 37, motbin move 2556 `Kg_WHummer`). Every mapping carries its
evidence and a confidence; no closest-match substitutes anywhere.

## Counts (of the 781)

| Outcome | Count |
|---|---|
| Mapped to a real T7 move AND clip byte-range resolved | **450** |
| Mapped to a real T7 move, clip in the un-located bank-0x0000 file | 31 |
| Honestly unmapped, with per-move reasons + candidate pools | 300 |

Per fighter (clip-resolved / bank-0 / unmapped): pantera 68/4/37,
phantom 67/1/59, skull 63/6/45, burger 80/3/28, kinpo 49/7/47,
demonio 48/0/32, diablo 39/8/33, scimitar 36/2/19. Confidence over the 481
mapped: 208 high, 273 medium. Scimitar's base Shaheen is T7 code `arb`
(`arbmot.json`, "[SHAHEEN]") — he is not T7-missing.

Clip blobs are on GRE release `t7-rotsm-clips-v1` (59.2 MB, sha256 manifest
included); per-entry locators (section, offset, size, format word, sha256)
are in GRE `.../mothead/mask/indexes/` and repeated inside each clip-map JSON.

## Remainder (explicit, not deferred silently)

- 300 unmapped: 81 strong T8-only candidates (moves T7 simply does not have —
  the T8 pass's exact workload), 91 in ambiguous candidate pools (a
  TheBigTuna startup/damage fingerprint pass would resolve many), 39
  MVL-confirmed but requirement-gated in the graph (chain throws etc. — needs
  the motbin requirements-table decode), the rest no-evidence.
- 31 bank-0x0000 moves: move identity proven; their clip file was not in the
  pulled `tkdata/mothead/` tree (names are facial/`vlc_` cutscene-flavoured).
  Needs a wider game-data pull or a runtime trace to locate.
- Format-100 clip bodies: sliced + indexed, encoding not yet decoded
  (format-200 bodies are fully decoded). Most clips are format 100, so this
  is the gate on converting clips into WH-playable animation data; the
  mapping layer above is complete regardless.
- T8 pass not started: no T8 moveset data exists in any of our stores
  (models/UI only). It needs the same DepotDownloader route on the owner's
  Steam TEKKEN 8 — the T7 lane's Steam credentials were session-supplied and
  never committed — or community TKMovesets2 outputs.
