# Tekken 6 PSP — ROUND 7 JOB 3: COM moveset decode (18/18)

Date: 2026-10-21, round 7 attempt 3. Decoder:
`round7-evidence/r7_com_decode.py`. Outputs:
`teardown/tekken6/movesets/t6psp-<fighter>-moveset.json` ×18 +
`INDEX.json`. Inputs: adler-exact COM plaintexts in the retained
workdir `decoded76/` (sha256 re-verified per file against the
round-6 inventory before decode — 18/18 match).

## Per-character isolation + assignment evidence

One JSON per fighter; no cross-file mixing. Assignment is the
round-6 HIGH-confidence evidence: each file's OWN character string
at offset 624 (`[NAME]1` + author + `Sun Nov 01 21:5x JST 2009`
build timestamp minutes apart across the set).

Set (exactly the 18 fighters named @624): LAW, KING, NINA,
Lin_Xiaoyu, JIN, Kuma, HEIHACHI, LEE, MARDUK, ROGER, Wang, Asuka,
BAEK_DOO_SAN, RAVEN, ARMOR_KING, Dragunov, EDDY, ZAFINA.

## What each JSON carries (verbatim from file bytes)

- Header: BE version 1, `COM\0`, word @8, count word @12 (7–16;
  referent still UNPROVEN — recorded, never used as a census).
- The full 32-slot pointer table @368: both words per slot +
  computed section length (next distinct offset − offset).
  31 live slots per file; slot 31 is the (0,0) terminator.
- Move-name records: every byte-carried name string in the name
  region (624 → first structured section) with its offset, plus
  the **verbatim record hex** spanning name offset → next name
  offset (name string + the binary record that follows it).
  The region holds English move names first, then localized
  name/description variants — all byte-carried, nothing invented.
  Totals: **7,341 name records across 18 fighters** (210–943 per
  fighter; KING highest — grapple-chain variants).
- Every ASCII string ≥4 in the whole file with offset, and every
  UTF-8 Japanese run with offset (nothing filtered away).
- MOTA: all 6 offsets, chunk headers (hex + LE words), and the
  four 20-byte tail records verbatim (they end exactly at EOF).

## Tekken-input conversion — logged, name-derived only

Each move carries `input_from_name` produced ONLY by token
substitution on its English name (Left→`1`, Right→`2`,
Left Right→`1,2` — Tekken LP/RP notation). The rule table is
embedded in every JSON under `tekken_input_conversion`. This is a
conversion OF THE NAME STRING, not a decode of the binary command
records; the verbatim record hex is the byte truth and the binary
command encoding remains a named open item (see JOB 4 blockers).

## Format precedent

Per-fighter JSON in the sweep moveset-library style (SCII PR #32 /
Urban Reign PR #442): verbatim records first, conversions logged
and labeled, move names only where file bytes carry them.
