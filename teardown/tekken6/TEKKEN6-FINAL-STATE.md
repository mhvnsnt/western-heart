# TEKKEN 6 (PSP) — FINAL STATIC STATE

The static account of the Tekken 6 teardown sweep, closed at
round 15 (PR #705's stack: rounds 13 #558 → 14 #705 → 15, this
round). Everything below is stated with its round/PR citation.
What is not listed as 100% is named as a residual — no rounding.

## 100% static (proven, shipped in-tree)

| Item | State | Citation |
|---|---|---|
| Containers | **76/76** DATA401 top-level files decrypted and adler-exact; the full sector/bulk cipher chain is in-tree (`tools/bulk_decrypt.py`, `tools/decode_all76.py`, `tools/sector_cipher.py`) | rounds 2–5 (PR #446 decode gate), `WIRING-INVENTORY.md` |
| NDPP meshes | **3,444/3,444 slice part sections decoded** to GLBs (3,039 in round 13 + all 405 round-13 failures recovered in round 14 via the cracked VTYPE color-format 7 = RGBA8888, decoder `tools/r14_ndpp_decode.py`); two runs sha256-identical; gate renders viewed | round 13 (PR #558), round 14 (PR #705), `tools/round14-evidence/JOB2-VTYPE7-VERDICT.md` |
| Character packages | **24 character slot GLBs** (12 packages × slots 0+10, the full NDPP set of the character packages) | round 9, confirmed complete round 10 (PR #520) |
| Skeletons | The **r11 skeleton set only** (body + head per package), superseding r9/r10 (TRS defect); BONE size formula verified exact (N = 22/110/129/132/146) | round 11 (PR #536), `models/SKELETON-SUPERSEDE.md`, round 12 (PR #550) |
| Movesets — verbatim layer | **18/18 COM files** decoded byte-exact (sha256 in each JSON); 7,341 name records carried verbatim with offsets + `record_hex` | rounds 6/7 (PR #489) |
| Movesets — notation layer | **COMPLETE after round 15.** Glyph map: 8 tap directions + 8 hold directions (rings E000–E00F) + all 15 button subsets (E015–E023) — every codepoint proven by exact decodes against cited T6 notation. v3 JSONs: 6,814 notation-carrying moves, **6,814 fully decoded, 0 partial** (round 14: 6,209/605; round 15 closed the tail) | round 14 (PR #705), round 15 `tools/round15-evidence/JOB1-GLYPH-TAIL.md`, `movesets/t6psp-*-moveset-v3.json` |
| COM slot classification | All 31 pointer-table slots classified across 18 files (size/entropy/first-bytes). Tail records = empty MOTA stubs (closed). Count-word 176 = external structural count (closed). Tail-zone MOTA placement proven by parser (108/108 cross-validated) | round 13 (PR #558), round 15 `tools/r15_tailzone_parse.py` |
| Stages | **Verdict (closed): stage packages carry no NDPP geometry** — placement (slot 0/11) + texture containers (slots 7/9 NTPP) + BE directory (slot 8); the one decodable stage-class section is a 2×2 ground-plane quad, shipped + render viewed. There is no arena geometry in the packages to extract | round 13 (PR #558) |

## Capture-class (statically terminal — do NOT re-hunt)

| Item | Why static is terminal | Unlock |
|---|---|---|
| NTPP texture pixels + CLUT | The image descriptor (+0x08 format, +0x0a w, +0x0c h, +0x28 pixels) is populated only by parameterized constructors from caller-supplied scalars; no EBOOT code derives them from NTPP section bytes — exhaustive negative over the handler, the descriptor class, every caller chain, and a serialized-descriptor scan of 59 sections | **One PPSSPP GE capture session** (spec: `PPSSPP-LIVE-RUN-GUIDE.md` + rounds 12/13 verdicts) |
| Palette unit→bone (skinning) | Index rule proven = sequential identity at the builder; the game-side per-unit selection (model class, vtable 0x08b918b8) is observable only live — rounds 11/12 terminal negatives | **The same PPSSPP capture session** — one capture unlocks both this and NTPP pixels |

## Named residuals (static, not capture-class)

1. **COM tail-zone payload schemas** (slots 25/26/30 payloads):
   layout + sub-structures proven in round 15 (fixed 604B
   12B-periodic slot-25 head table; shared u16 sub-table in
   slot 26; slot 30's 564B payload shared byte-exactly by the
   two King-family files), field semantics unproven. Next hop
   named in the round-15 verdict: the EBOOT consumer
   caller-chain, or the same PPSSPP session's RAM dump.
2. **E00D (U/B, hold u/b)**: assigned by font ring position
   only; it occurs 0 times in the corpus, so no move decode
   depends on it. It closes automatically if the font atlas is
   ever captured.
3. **E00B (B)**: the weakest glyph proof of round 15 (dash
   second-stroke family + hold-ring position; see the JOB1
   doc's honesty note). First candidate for re-examination if
   the font atlas is captured.

## Owner-pending (canon — not engineering)

- Per-character canon decisions that sit with the owner
  (character naming/mapping into Western Heart, which parts
  kits belong to which character — segment assignment in the
  parts batch remains contiguity-INFERRED and unmerged into the
  12 proven character packages until he rules).

## Input reproducibility chain (proven round 14, re-verified round 15)

GitHub release `tekken6-psp-v1`, asset `tekken6-psp.iso`
sha256 `b5e52660a52caeca351e93c54bb4db0011325af0c1e3c67230bddde8f7cecf44`
== release digest → in-tree `tools/bulk_decrypt.py` → bulk
container scan → `tools/decode_all76.py` outputs → the 18 COM
files sha256-verified against the round-7 moveset JSONs
(round 14: 18/18; round 15: re-verified 18/18 before Jobs 1/2).
Any future lane can regenerate every input byte-exactly from
the release alone; no local-only input exists.
