# JOB 3 — COM B4 continuation: glyph map (PROVEN core) + compression probes (negative)

## (a) FONT GLYPH → INPUT MAP

The moveset input notation lives in per-move name records as
game-font PUA codepoints U+E000–U+E023 (round 13). Two independent
evidence lines fix the core map:

**Font-layout evidence.** The EBOOT font charmap (the `owfont`
subsystem: RTTI `owfont_fnt_t` / `owfont_ntx_t` / `tcb_owfont_t`)
contains a Unicode→glyph table at file offset 0x3ab818
(VA 0x08bae818) in which the PUA block runs **consecutively,
E000–E07E in codepoint order** — the font assigns the notation
glyphs a contiguous ordered block, and within it the two
sub-blocks below are internally ordered exactly as the proven
semantics require: the 8 directions in ring order
(d/b, d, d/f, b, f, u/b, u, u/f — consecutive codepoints
E000–E007) and the button block in combo order
(1, 2, 1+2, 3, 1+3, ·, 1+2+3, 4, ·, ·, 2+4, ·, 3+4 at
E015–E020). The font *texture atlas* itself ships inside NTPP
packages and is behind the same evidence wall as Job 1 (see
JOB1 verdict) — the atlas grid was not readable this round; the
charmap table + codepoint-block ordering is the font evidence
obtained, stated exactly.

**Known-move decodes (the proof gate, exceeded).** Each mapping
below is fixed by at least one exact record decode against cited
community notation for the same named move in Tekken 6:

| glyph | input | proof decode |
|---|---|---|
| U+E000 | d/b | Giant Swing motion (below); Tombstone Piledriver |
| U+E001 | d | Giant Swing motion; Corpse Thrust d+1 (Wavu) |
| U+E002 | d/f | Giant Swing motion; Dragon Uppercut d,df+1 |
| U+E003 | b | Giant Swing motion |
| U+E004 | f | Giant Swing motion; Stonehead f,f+1+2 |
| U+E005 | u/b | Avenger u/b+1+2 (Jin) |
| U+E007 | u/f | Hunting Hawk u/f+3,4,3 (Baek) |
| U+E015 | 1 | Left Right Combo 1,2 (all chars) |
| U+E016 | 2 | Left Right Combo; Giant Swing chain 2,1,4,3 |
| U+E017 | 1+2 | Median Line Destruction 1+2 (Wavu); Stonehead |
| U+E018 | 3 | Kazama Style 5 Hit Combo 1,3,2,1,4 |
| U+E019 | 1+3 | Knee Bash 1+3 (King movelist) |
| U+E01B | 1+2+3 | Chicken Wing Face Lock chain 2,1,1+2+3 |
| U+E01C | 4 | Kazama 5 Hit; Hunting Hawk |
| U+E01E | 2+4 | Tombstone Piledriver d/b,f+2+4 (all 3 chars) |
| U+E020 | 3+4 | Double Lift Kick d+3+4; Raijin Stance d+3+4 |

Showcase decodes (verbatim from the records):
- King "Giant Swing" motion record `E004 E003 E000 E001 E002 E004
  E015` → **f,b,d/b,d,d/f,f+1** = f,HCF+1 (FAQ) — glyph-for-glyph.
- King chain record `E016 E015 E01C E018` → **2,1,4,3** = the
  FAQ's "2,1,4,3 Giant Swing" chain input, glyph-for-glyph.
- Baek "Hunting Hawk" `E007 E018 E01C E018` → **u/f+3,4,3** (FAQ).
- Jin "Median Line Destruction" `E017` → **1+2** (Wavu Wiki).

**Special mark U+E00C** — appears as the second element of f,f
inputs (Demon's Paw f,f+2 = `E004 E00C E016`; Stonehead f,f+1+2 =
`E004 E00C E017`) and as a trailing mark after strings (Baek
1,2,3~f). Decoded contextually in the v2 files: "f" after U+E004,
"~f" elsewhere. Precise semantics (hold vs repeat) not provable
from records alone — labelled, not guessed.

**Unproven codepoints** (present in records, deliberately NOT
named): U+E006 (u by elimination — candidate only), U+E008,
U+E009, U+E00A, U+E00B, U+E00E, U+E00F, U+E01A, U+E01D, U+E01F,
U+E021, U+E022, U+E023 — stance/state/chain icons and two
button-combo candidates (E01A, E01D) whose contexts are recorded
in the working notes; v2 output keeps them as `U+Exxx` tokens and
flags the move `command_complete: false`.

**Citations (accessed 2026-10-22):** Wavu Wiki, Jin counterplay
(wavu.wiki/t/Jin_counterplay) — Median Line Destruction 1+2,
Switchblade 2,4, Corpse Thrust d+1 · GameRevolution, "Tekken 6
FAQ/Move List" v1.06 by Catlord — Tombstone Piledriver d/b,f+2+4,
Stonehead f,f+1+2, Giant Swing f,HCF+1 and its 2,1,4,3 chain,
Hunting Hawk u/f+3,4,3, Chicken Wing Face Lock 2,1,1+2+3, and the
button convention 1=LP 2=RP 3=LK 4=RK (PSP □△✕○) · Tekken Wiki,
King/Tekken Movelist — Knee Bash 1+3.

**Deliverable:** the 18 moveset JSONs regenerated as additive v2
files (`movesets/t6psp-*-moveset-v2.json`): every move gains
`command_glyphs` (codepoint list), `command_decoded`,
`command_complete`. 6,814 moves carry notation; **6,209 decode
completely** with the proven map; 605 are partial (contain an
unproven codepoint, kept as a token). All original fields —
including the verbatim `record_hex` — are byte-identical to the
round-7 files (verified field-by-field over 7,341 moves, 0 diffs).

## (b) COMPRESSION PROBES — slots 25/26/30 × 18 files: NEGATIVE

Probe battery per slot (54 slot instances): magic scan (zlib
78 9c/da/01, gzip, bzip2, xz, zstd, LZ4 frame, LZO); raw-deflate
trials (zlib wbits −15/15/31) at offsets 0–64 and at every magic
hit; per-1024 container-cipher trial with entropy comparison.

- **0/54 slots decode as any probed format.** No deflate trial
  produced ≥64 B of output anywhere; the cipher trial moved no
  slot's entropy toward structure.
- Three stray magic hits (gzip @977 in idx62 slot 26, zlib-da @464
  in idx68 slot 30, zlib-01 @770 in idx74 slot 25) are chance byte
  pairs in high-entropy data — deflate trials at those exact
  offsets produced nothing.
- Entropies stand as round 13 measured: slot 25 5.46–6.12,
  slot 26 7.14–7.40 (with its structured 16-byte head), slot 30
  6.90–7.10 at fixed 644 B.

Verdict: slots 25/26/30 are **not** zlib/gzip/raw-deflate/LZ4/
bzip2/xz/zstd/LZO data and not container-cipher data. The standing
interpretation (round 13) is unchanged: packed binary structures
(bitfield/AI tables), with slot 26's repeating head suggesting a
typed record stream — structure recovery is a fresh hop, not a
compression hop.

## Residuals named exactly

- Glyph map: 12 unproven codepoints (E006 candidate "u"; E008,
  E009, E00A, E00B, E00E, E00F, E01A, E01D, E01F, E021, E022,
  E023) — closing them needs the font atlas (Job 1 wall) or
  per-move community cross-checks beyond this round's bound.
- Slots 25/26/30: unidentified packed structures; not compression
  under the standard PSP candidate set (probe list above).
