# T7 frame data (data-only reference)

Directory: `game/data/t7-frame-data/`

Two source families live here, both Tekken 7 only, both in the same
LP1/RP2/LK3/RK4 JSON schema (`source`, `metadata_original`,
`move_count`, `dups_removed`, `moves`):

- **DLC 9** (`t7-fahkumram`, `ganryu`, `geese`, `kunimitsu`, `leroy`,
  `lidia`, `negan`, `noctis`, `zafina`): converted from the TekkenDocs
  T7 JSON API (`https://tekkendocs.com/api/t7/{slug}/framedata`),
  backed by the TekkenDocs / rbnorway shared Google Sheet. SHA-256
  verified against `conversion_manifest.json` at import time.
  Loader: `game/js/t7-frame-data-loader.js` (consumer import held
  until the batch-stack freeze lifts — the data lands, the hook does
  not).
- **Base 35** (`t7-akuma` … `t7-yoshimitsu`, 5,648 moves total):
  converted from `TheBigTuna/Tekken-7-Frame-Data`, `frames-json/`.
  No overlap with the DLC 9 (disjoint character sets).

## Hard limits (do not soften)

- Frame data is NOT a playable moveset. No animation IDs exist in
  either source; the loader's stubs carry `anim_ref: null` /
  `anim_status: 'UNMAPPED'` by design. Never coerce annotated values
  (`"20 cs6"`, `"-16"`, `"--"`, `"16~18?"`) into fake numbers, and
  never present a frame-data row as animation-wired.
- `null` damage values are gaps, kept as gaps.
- Repeated notations with DIFFERENT values (e.g. King `f, F+LP1` at
  damage `29?` vs `33`) are distinct source rows (patch variants),
  preserved as-is — they are not duplicates to delete.

## Dedup note — King jab

The raw TheBigTuna King source carried the jab `1` twice as
identical rows. The converter already removed it: King
`dups_removed: 34`, and the mirrored file holds exactly ONE jab row
(`notation_original: "1"` → `LP1`, damage 9, speed 10, on_block +1,
on_hit +8). No further King row was deleted at mirror time.
The King jab damage 9 vs the WH Pantera T7-block damage 7 (matching
10f / +1 / +8) is a patch-version question — patch version is
unstated in the source, so WH values are NOT overwritten from this
data until a patch version is pinned.

## Kuma

Kuma is ABSENT, deliberately. The upstream Kuma file is a 141-byte
empty placeholder; no Kuma file was mirrored and none was
synthesised. (Akuma IS present — Akuma is not Kuma.)

## Licence flags (recorded, never cleared by this lane)

- TheBigTuna repo has NO licence file (verified 2026-10-24).
  Treat as unlicensed community data: internal reference OK; check
  with the author before shipping it verbatim commercially.
- TekkenDocs data lives in a Google Sheet that is the source of
  truth for TekkenDocs and rbnorway.org, with no redistribution
  licence stated in the workspace files. Same author-check rule
  before verbatim commercial redistribution.
- Bandai CC BY-NC 4.0, MB-Lab GPL-3.0 (asset licence unstated),
  and the other wave licence flags live in
  `docs/research/OPEN-SOURCE-WAVE2-2026-10-24.md` and the wave-2
  build-check note — they are not resolved by this file.

## Coverage gap (queued, not hidden)

The base 35 + DLC 9 do not cover the whole T7 roster (Anna, Armor
King, Julia, Marduk and other season 2–4 fighters are still
missing). Per-slug TekkenDocs attempts are a separate queue item;
no missing slug is claimed here.
