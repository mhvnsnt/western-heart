# tools/vf5 — Virtua Fighter 5 (PS3) extraction

Worker 45, 2026-10-22. Reverse-engineered from release `vf5-ps3-v1` (BLES00029).

## farc_extract.py

Extracts Sega `.farc` archives.

```
python3 farc_extract.py <archive.farc> <outdir>
```

Format: `FArC` magic + BE u32 header + per-entry `[name\0][offset BE u32][comp_size BE u32][decomp_size BE u32]` + gzip payloads. Validated: decompressed size matches header for all entries (18 character + 38 stage archives).

## vf5extract.py

Converts decompressed `*_obj.bin` model files to OBJ.

```
python3 vf5extract.py <model_obj.bin> <out.obj>
```

Format (all little-endian):
- Magic `0x05062500`, chunk count at +0x04, chunk offset table at +0x40
- Mesh chunk: bounding sphere (4 floats) at +0x08, submesh count at +0x20
- Second header at +0x54: bounding sphere, then `vcount` at +0x20, `pos_rel` at +0x24, `end_rel` at +0x28
- Positions: `chunk_base + pos_rel`, `vcount` × 12-byte LE f32 triplets (validated: `pos_rel + vcount*12 == end_rel`)
- Indices: u16 triangle strips with degenerate restarts; located per-chunk (global scan + per-gap fallback); max index < vcount
- `SKIN` blocks per chunk contain bone weights (parsed, not yet converted to glTF skin)

Renders: see `~/workspace/tpose-render/` pattern; this round used Blender 4.5.3 Cycles 32spp, white world, 1080×1440.

## mon/msk

- `mon` = Eileen (Monkey Kung Fu)
- `msk` = El Blaze (Lucha Libre) — verified by render
