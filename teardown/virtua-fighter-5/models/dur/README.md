# Dural — VF5 model archives

- **Code:** `dur` · **Style:** Boss (chrome humanoid)
- **Source:** Virtua Fighter 5 PS3 (BLES00029), Ver.C
- **Release:** `vf5-ps3-v1` — https://github.com/mhvnsnt/western-heart/releases/download/vf5-ps3-v1/
- **WH use:** Zen's permanent base-mix layer (owner decision 2026-10-22). Dural's stance = Zen's stance.

## Archives

| File | Size | Inner files | Contents | Location |
|------|------|-------------|----------|----------|
| `dur.farc` | 760B | 2 | base: `dur_obj.bin` (4,688B decomp), `dur_tex.bin` (252B decomp) | in repo |
| `duritm.farc` | 25.5MB | 26 | body parts: `duritm003_obj.bin` (2.4MB), `duritm013_obj.bin` (1.8MB), `duritm023_obj.bin` (9.8MB), `duritm033_obj.bin` (21.5MB + 2.2MB tex) + 9 smaller parts | on release (large file, not in repo) |

## Extraction

`../tools/farc_extract.py` — FArC magic + BE u32 entries + gzip payloads. All 28 entries decompress cleanly (verified 2026-10-22).

Decompressed `*_obj.bin` → chrrox 3ds Max script; `*_tex.bin` → TXP.bms (QuickBMS).

## Motion status: NOT AVAILABLE

**VF5 PS3 motion data was never acquired.** The character `.farc` archives contain models (`*_obj.bin`) and textures (`*_tex.bin`) only. No motion files exist in any pulled archive.

See `docs/research/VF5-MOTION-GAP-2026-10-22.md` for the full technical assessment and acquisition path.

## Notes

HIGH priority — Zen's base stance depends on Dural's motion.
