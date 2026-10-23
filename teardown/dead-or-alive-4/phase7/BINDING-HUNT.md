# Material→Texture Binding Hunt — Phase 7 (bounded, 2026-10-21)

Phase 6 left this gap: no index inside ObjGeo/ObjInfo records maps
a mesh to one of its package's TX2D textures (the only candidate
field, ObjGeo item `+0x030`, takes just {2, 7, 32, 52} — a shader
class). Only 3 assignments were proven for chrone pkg00, by
render/alpha evidence. This phase ran one bounded hunt in the three
places the brief named. **Result: not found in any of them.**

## 1. XEX data/strings — NOT FOUND

All printable strings (≥6 chars) in `default_pe.bin` matching
texture/material patterns were dumped and read. Everything that
surfaced is one of:

- XDK shader-compiler strings (`texld`, `TEXCOORD`, HLSL error
  text) — toolchain, not game data.
- Sampler uniform names from the game's shader set
  (`TextureSampler0..8`, `Tex1Color..Tex8Color`) — shader-side
  slots, no per-mesh mapping.
- Avatar texture paths (`D:\dat\avatar\partstex\*.ctb`) — the avt
  avatar system, not chr fighters.

No per-package or per-mesh texture-name table exists in the XEX
strings. (A binary, non-string table in .data was not exhaustively
excluded — that is a Ghidra data-flow job, noted as future work,
not silently assumed away.)

## 2. chrthree TX2D-only sub-package directory — NOT FOUND

Re-fetched the sub-package at chrthree file offset `0x6E7C800` this
lane (release range fetch, `tools/phase7/fetch.py`): directory =
`XPR2` (f1 `0xFF4`, f2 `0x19B000`, f3 `0x30` = 48) followed by 48
`TX2D` records whose f1 walks the descriptor block at the exact
40-byte descriptor stride (0x304, 0x32C, 0x354, …), f2 = 0x28,
f3 = 0x304 constant. At `+0x310` the descriptor data begins
(`00030001 00000000 FFFF0000 FFFF0000…`). There is no parent-package
reference and no mesh index anywhere in the directory — these
bundles do not carry binding information either.

## 3. mot/stg package heads — NOT FOUND

The 256KB heads of mot.afs and stg.afs fetched this lane contain
no XPR2/USER/VBUF/IBUF/TX2D directory records at all in their
opening span (they open with float streams — phase-7 findings
§1.2), so no binding record hides in a mot/stg header table.

## Where the binding most likely lives (hypotheses, not claims)

- **Draw-order convention:** the game may bind textures in the
  order ObjGeo objects are drawn against a fixed sampler-slot
  scheme (the `TextureSampler0..8` uniforms above) — i.e. the
  binding is in the *shader assignment per draw*, which phase 6
  already recorded as the ObjGeo `+0x030` shader class. Testing
  this means rendering candidate assignments per shader class and
  judging coherence, package by package — the phase-6 pkg00 method
  (which DID prove 3 assignments) scaled up, not a table lookup.
- **.data binary tables in the XEX** keyed by package index —
  needs the Ghidra data-flow route, unbounded relative to this
  phase's budget.

The hunt is documented; the gap stays open and is listed as
wiring blocker #2 in `phase7/WIRING-INVENTORY.md`.
