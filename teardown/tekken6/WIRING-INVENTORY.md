# Tekken 6 PSP — Wiring Inventory (round 3, 2026-10-20)

Per the owner acceptance target (2026-10-20 ~20:57 CDT) and the wiring
standard in PR #397 (gates G1–G4). This is the honest state of T6
content on its way into the playable western-heart build.

## What's decrypted / decoded

| Layer | State | Evidence |
|---|---|---|
| PSP ISO | Byte-exact on release `tekken6-psp-v1` | sha256 `b5e52660…` (round-2 scoreboard) |
| DATA401 sector cipher | SOLVED with a round-5 correction: the cipher runs ONE call per 1024-byte block. The round-3 bulk was decrypted per-2048, corrupting every odd 1024-byte block of every file — `bulk_decrypted.bin` on disk is therefore WRONG past each file's first kilobyte and must be regenerated with `tools/bulk_decrypt.py` before any further use | `tools/ROUND5-STATUS.md` F12/F13, `tools/bulk_decrypt.py` |
| GZIP containers (76) | **76/76 byte-exact (size + adler32)** — round 5: bodies are plain zlib once decryption is correct; there is no custom gzip and no encode context | `tools/decode_all76.py`, `tools/round5-evidence/r5_inventory_summary.json` |
| COM containers (18, gzip idx 58–75, entries 709–735) | **18/18 decoded byte-exact.** Each plaintext is a COM container (`00 00 00 01 "COM\0"` + a count-like word 7–16, 176 total across the set); per-character assignment + inner mesh extraction is the next step (G4) | `tools/decode_all76.py` inventory |
| NDPP archive (entry 87, ~81 MB, 2,546 embedded GZIP) | Landed on main via PR #187; the round-3 embedded scan (94/2,720) ran on the corrupted bulk — a re-scan on the corrected bulk is now unblocked and owed | round-3 session-2 scan |
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

1. **The decode (gate G1/G2) — DONE (round 5, PR #446).** The
   PPSSPP live trace + RAM diff found it: no encode context exists —
   our own sector-cipher driver used the wrong call granularity
   (per-2048 instead of per-1024), corrupting odd blocks. 76/76
   adler-exact; the game's loader byte-matches plain zlib in live
   traces. The 18 COM containers are decoded and inventoried; what
   remains is per-character inventory (below), not decoding.
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

- Byte-exact (76/76, round 5): ALL gzip idx 0–75 (size + adler32),
  via `tools/decode_all76.py` on the correctly decrypted regions.
  The round-3 scoreboard (20 pass / 56 fail) was an artifact of the
  corrupted round-3 bulk, not of the containers.
- COM set (18): gzip idx 58–75 — all decoded; each holds one COM
  container (count-like word 7–16 after the COM header).
