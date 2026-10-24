# Tekken 6 PSP — Wiring Inventory (round 3, 2026-10-20)

Per the owner acceptance target (2026-10-20 ~20:57 CDT) and the wiring
standard in PR #397 (gates G1–G4). This is the honest state of T6
content on its way into the playable western-heart build.

## What's decrypted / decoded

| Layer | State | Evidence |
|---|---|---|
| PSP ISO | Byte-exact on release `tekken6-psp-v1` | sha256 `b5e52660…` (round-2 scoreboard) |
| DATA401 sector cipher | SOLVED — 478 files in `bulk_decrypted.bin` | `tools/SECTOR-CIPHER-REVERSED.md`, decrypt3 manifest |
| GZIP containers (76) | 20/76 byte-exact (size + adler32) | `tools/round3-evidence/scoreboard_strict.txt` |
| GZIP containers (56) | NOT decoded — encode context unidentified; the EBOOT's own inflate provably rejects them too (emulator ground truth) | `tools/ROUND3-STATUS.md` sections B–D |
| COM containers (18, gzip idx 58–75, entries 709–735) | NOT decoded (same defect); partial clean prefixes show a "COM\0" container header (round 11); content type and per-character assignment unconfirmed | ROUND2/ROUND3 status docs |
| NDPP archive (entry 87, ~81 MB, 2,546 embedded GZIP) | Landed on main via PR #187; embedded containers share the same decode state (94/2,720 byte-exact in the round-3 archive scan) | round-3 session-2 scan |
| GMO -> GLB pipeline | Proven on a sample GMO (round 2, PR #388: converted, re-imported, front-rendered, viewed) | PR #388 |

## What's wired into the playable build

**Nothing yet — deliberately.** No T6-derived fighter, moveset, or
animation is live in `game/`, because the only T6 content that exists
in decoded form today is (a) the 20 small byte-exact containers
(mostly 1,088-byte records and two small files — no character meshes)
and (b) NDPP data whose main containers (idx0 class) do not fully
decode. Wiring placeholder or partial content into the build would
violate the acceptance target's terms (real fights between his
fighters with working movesets — not placeholders).

Existing wiring precedents this lane will follow once the decode
lands: PR #379 (No Mercy wiring), PR #382 (Tekken 3 wiring), PR #385
(full-wiring audit), PR #397 (wiring standard + gates).

## What's left before T6 content is playable

1. **The decode (gate G1/G2).** Identify the encode context of the 56
   failing containers via the PPSSPP live trace (named next step,
   ROUND3-STATUS.md section D). Until then the 18 COM containers —
   the presumed character content — cannot be inventoried per
   character, let alone converted.
2. **COM inventory per character (gate G4 completion).** From decoded
   COM data only; the "40 meshes / 18 COM files" figure is a roster-
   size estimate, not a measured count.
3. **Batch GMO->GLB (gate G3)** via the proven pipeline, one directory
   per character (per-character isolation: skeleton/animations/
   add-ons stay per-character), Blender import + front renders for
   samples, viewed before any claim.
4. **In-build wiring:** T6-derived fighters/movesets/animations into
   `roster/`, `moveset-library/`, and `game/` following the
   Tekken 3 / No Mercy precedents, with in-build verification
   evidence before any "playable" claim.

## Per-file status (76 DATA401 GZIP containers)

Full per-file scoreboard with first-failure evidence:
`tools/round3-evidence/scoreboard_strict.txt`.

- Byte-exact (20): gzip idx 19, 23, 25, 27, 29, 31, 33, 35, 37, 39,
  41, 43, 45, 47, 49, 51, 53, 55, 56, 57.
- Failing (56): all others; every one stops at a too-far distance
  under the standard composition that the game's own inflate also
  uses (proven equivalent by direct execution).
- COM set (18): gzip idx 58–75 — all in the failing set.
