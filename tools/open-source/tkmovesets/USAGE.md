# TKMovesets — Western Heart usage

Vendored upstream: Kiloutre/TKMovesets (GPL-3.0), a Windows/C++ tool that
extracts Tekken movesets from a running game's memory into `.tkmvst`
(TKM2) files, and can edit/re-import them (Tekken 7 import; extraction
for T7, TTT2, TREV, T6, T5). Do not try to build/run the extractor on
this Linux VM — that is not the workflow here.

## The Western Heart decode path lives in `tools/moveset-decode/`

* `tools/moveset-decode/tkm2_decode.py` — stdlib-only Python decoder:
  `.tkmvst` → readable JSON (header, blocks, T7 move list with names,
  startup/active frames, damage via hit conditions, hitbox data).
* `tools/moveset-decode/README.md` — the format documentation: the TKM2
  container (`TKMovesets2/LocalStorage/MovesetStructs.h`), the T7 inner
  layout (`TKMovesets2/GameSpecific/Structures/Structs_t7.h`), the
  pointer→index semantics from the extractors, per-game coverage and
  limits.
* `tools/moveset-decode/sample/` — spec-built validation fixture +
  ground truth + decoded output (clearly labeled: not a game
  extraction; no real `.tkmvst` exists on disk yet — see its README).

```bash
python3 tools/moveset-decode/tkm2_decode.py <file.tkmvst> --out decoded.json
```

Lane workflow: extract on a game machine with this tool (uncompressed),
bring the `.tkmvst` back, decode with the Python path, feed `moves[]`
into the Western Heart moveset pipeline.
