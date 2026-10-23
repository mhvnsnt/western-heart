# Urban Reign Phase 5 — Job 2: the type-14 root decode (CRACKED)

Phase 4 left 7 of P1's 8 unproven records blamed on a "type-14
root-decode gap": pmot001 candidate motions whose bone-0 track is
type 14 decoded to off-scale roots under the Phase-2 `ur_gyu.py`
(type-13-style little-endian pair assembly + single cumulative sum).

## The crack

Type-14 track payload (per 8-key block, block offsets s16 @+36 as in
type 12; range-coded with the ELF set-2 tables, as before):

1. Each key consumes 6 symbols = 3 components × 2 symbols.
2. Each component's symbol pair is a **big-endian** s16: the FIRST
   symbol is the HIGH byte, the second is the low byte
   (`v = s16(((hi & 0xff) << 8) | (lo & 0xff))`). Phase-2 code read
   the pair little-endian.
3. The s16 values are **second differences**: the sampler is a
   double integrator, reset per block — `pos[0] = v[0]`,
   `vel[0] = 0`; for k ≥ 1: `vel[k] = s16(vel[k-1] + v[k])`,
   `pos[k] = s16(pos[k-1] + vel[k])`.
4. Output is the type-12 mapping: `out_c = base_c + pos_c * step_c`
   (float pairs @+12/+24).

How it was found: from motdatP1 record 6's payload, the implied
integer accumulators under (base, step) were computed and compared
against the raw symbol stream; the first key of pmot001 m024 matched
`5058 = (19 << 8) | (−62 & 0xff)` exactly, and the double-integrator
recurrence then reproduced every implied accumulator of the first
blocks to <1 unit (including a natural saturation at 16383 in
m011 block 1). A variant grid (byte order × integration order ×
block-reset policy, 12 combinations × 4 records) confirms
BE + double + per-block reset is the only family that comes close;
all others are ≥364 mm on m011 (vs 76 mm residual for the winner —
see the residual note below).

**Proof of exactness:** with this decode, motdatP1 record 7
(`cbco_wp2h_kokyu01`, 80 frames) matches **general_weapon motion 33**
(type-14 root, 23-bone bank) at **max dev 0.0014 mm over all frames**
— float-rounding identity, the Phase-4 proven standard. The fixed
decoder is landed at `tools/ur_gyu.py` (type-14 branch rewritten;
type-13 left as-is, still unvalidated) and is regression-tested in
this phase's work log at exactly that pair.

## What this does to P1 (char001): 27 → 30 of 35 records sourced

| record | name | verdict |
|---|---|---|
| 7 | `cbco_wp2h_kokyu01` | **PROVEN** → general_weapon m033, maxDev 0.0014 mm (type-14). A weapon-bank move (`wp2h`), never a pmot001 clip — recorded in `name-bridge-char001-proven.json` as a cross-bank hit; NOT annotated on ur-char001's pmot clips. |
| 13 | `moco_dchopelbow` | **PROVEN** → the same motion in three banks at identical maxDev 0.0501 mm: pmot005 m011, pmot021 m014, tmot009 m020. Not a pmot001 clip; cross-bank record only. |
| 29 | `moco_huntingh3` | **PROVEN** → pmot042 m045, maxDev 0.0264 mm. Cross-bank record only. |
| 6 | `cbco_screw_r` | unproven — see below |
| 10 | `moco_d_jumpk_f` | unproven — see below |
| 11 | `moco_d_jumpk_y1` | unproven — see below |
| 12 | `moco_d_jumpk_y2` | unproven — see below |
| 14 | `moco_doubleairk_f` | unproven — no 88-frame motion exists in pmot001; best candidate in any of 46 banks searched is ≥1079 mm away. |

## The 4 remaining type-14 records: NOT a decode gap anymore

Records 6/10/11/12's frame-matching pmot001 candidates (m011, m024,
m025, m026 — all type-14 roots) come much closer under the fixed
decode (maxDev 2400→76, 5288→693, 9966→635, 8835→235 mm) and match
their payloads **exactly (≤0.06 mm) over long stretches**: e.g.
record 10 vs m024 — Y exact over all 90 frames, X exact frames 0–19,
Z exact frames 0–33; record 12 vs m026 — all components exact
frames 0–22. But no candidate meets the ≤0.10 mm full-track gate,
so **no pair is assigned** (never-force rule).

The residual pattern identifies what these candidates are:
**directional sibling variants of the records' true motions.** The
jumpk set is the clear case: records 10/11/12 are the `_f` / `_y1` /
`_y2` directional variants of one jump kick; they share the vertical
(jump) profile — record 10's Y is *identical* to m024's Y for all
90 frames — while their horizontal travel differs. Records 13 and
29 prove the same pattern from the type-8 side: their pmot001
frame candidates are siblings, and their exact sources live in
other banks. For records 6/10/11/12/14, the exact source bank is
**not among the 46 banks searched** (31 pmot + 10 tmot + 3 general
+ main.ppk's two embedded general-class banks; main_in.ppk holds
copies of general_normal/general_30frame). The named missing step
is therefore no longer a decode step: it is a **bank outside the
shipped set** (the motdat test tool's working banks, or a variant
bank not present in the DVD000 AFS; DVD001's entries are unnamed
`file_NNNNN.bin` and were not content-searched). If such a bank is
ever captured (e.g. PCSX2 RAM dump of the test scene), the fixed
decoder + gate in `tools/ur_name_bridge.py` will match these five
records mechanically.

## Cross-fighter impact (feeds Job 1)

The type-14 gap was never P1-specific: root tracks across the pmot
banks are type 8 or type 14, and every fighter's bridge in Job 1
was run with the fixed decode. Type-14-rooted proven pairs are
marked `rootType: 14` in each `name-bridge-<char>-proven.json`
(e.g. char057 rec32's candidate m031 is a type-14 near-miss at
0.102 mm, left unproven under the gate — see the summary's
borderline note). Without the fix, all type-14 candidates would
have failed at thousands of mm, exactly as in Phase 4.
