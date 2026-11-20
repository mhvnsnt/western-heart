# Tekken 6 PSP — ROUND 12 STATE (palette caller via registry table; NTPP pixel consumer = datatextureroot; B5 16B-record census; B3 anomalies; skeleton supersede doc)

Date: 2026-10-22. Branch: `teardown/tekken6-round12-caller-textureroot`,
stacked on `teardown/tekken6-round11-palette-xref` @ 9d794152 (PR #536 OPEN).
Workdir retained: `~/workspace/_t6r4-work/` (read-only this round; NEVER delete).
Clone reused: `~/workspace/_t6r9-clone` (sparse, teardown/tekken6 only).
VM RAM low (~1.6GB free measured round 11): Capstone targeted disassembly
is the primary asm route; capped-heap Ghidra only if a tiny scoped pass is
unavoidable. Disk tight: footprint minimal.

## Inherited verified truth (rounds 5–11, not re-derived)

- NDPP decode cracked (r9); BONE roles proven; bind composition = T·R only
  (scale does NOT propagate) — corrected skeletons are
  `models/idx{nn}_*_r11.glb` (tools/r11_skeleton_fix.py); r9/r10 skeleton
  GLBs carry the TRS defect and are SUPERSEDED (never build on them).
- PALETTE (round 11, JOB1-PALETTE-XREF.md): GE fragment emitter PROVEN —
  EBOOT @ 0x08ad161c `emit(obj, out, index)`: reads a 3×4 matrix from
  `obj->[0] + index*48`, emits 12× 0x2B + 0x0B (52B, byte-exact vs RAM
  fragments). Attract fragment pool = exactly 110 fragments → fragment
  index ↔ bone index. Emitter takes index as argument, has NO jal / NO
  data xref (jalr/vtable-called); sibling thunks referenced ONLY from
  the registry table at 0x08bcfdxx (also holds identity template @
  0x08bcfdf0). Elements at out+0x24/+0x28 pass through an extra
  computation involving obj+0x418. Route 3 (COM/census) negative.
  Route 2 (PPSSPP capture) feasibility note landed — capture is a
  separate parent lane, NOT this round.
- NTPP (round 11): NTPP class (RTTI @0x08b9c5b0, vtable 0x08b9c568) is a
  texture PLACEMENT/ANIMATION object — NO pixel path in any function
  (proven). Slot-4 items = embedded NTPP sections (magic + header;
  entropy 5.51). THE PIXEL CONSUMER IS ELSEWHERE: the
  `tcb_datatextureroot_t` load path / render-layer GE upload (GE
  commands 0xC0–0xE9 family) — named residual, unhunted.
- B3 (round 11): assignment landed labeled (28 anchor-proven / 5,206
  contiguity-inferred / 236 unassigned-stage) in
  round11-evidence/r11_b3_assignment.json. ANOMALIES KEPT: 5
  double-size segments (no hidden midpoint anchor via slot maps),
  stub segment 26, atypical closing anchors (BONE sizes 9,440/9,696 —
  not the 8,032/1,664 standards), a 42-strong stage cluster in
  segment 27's tail.
- B5 (round 11): stage idx24 slot-9 pages are NOT geometry and NOT
  floats (old "95% BE-float-sane" was a denormal artifact; pages are
  80.5% zero bytes). POSITIVE: sparse byte-record arrays, 16B/32B
  record period (autocorrelation r=0.763 @16), constant 0x800 word at
  page offset 52, small-enum byte alphabet; 40 pages × 138 = 5,520
  records; a 0x20B-record BE directory precedes the pages + an
  embedded NTPP @+0x1c0.

## Jobs

1. JOB 1 — PALETTE CALLER VIA THE REGISTRY TABLE: dump the 0x08bcfdxx
   registry table from the EBOOT (entry size + count from bytes + any
   code iterating it). Identify (a) which entry references the emitter
   @0x08ad161c; (b) sibling functions in the same registry class —
   especially any that LOOPS and calls through a register (jalr) with
   an index argument. Disassemble best candidate caller(s): extract
   the index computation feeding emit's `index` parameter AND the
   obj+0x418 computation for out+0x24/+0x28. PROOF if pinned: apply to
   idx00/idx01, build SKINNED GLB, gate on bind-pose reproduction
   (skinned bind == r9 unskinned T-pose within tolerance;
   skeleton-inside-mesh overlay VIEWED) → then batch all 12. If the
   registry trace closes without the caller, land the full trace +
   declare palette CAPTURE-ONLY with exact reason (valid terminal
   verdict for the static hunt).
2. JOB 2 — NTPP PIXEL CONSUMER `tcb_datatextureroot_t`: hunt its RTTI
   record + vtable the same way round 11 found NTPP's (string/RTTI
   scan → vtable → method set). Read load/upload methods for GE
   texture commands (0xC0–0xE9) and swizzle/CLUT loops: extract
   CODE-DERIVED pixel parameters (format enum mapping, swizzle on/off,
   CLUT format + location). Then decode ONE slot-4 embedded NTPP
   section's pixels with ONLY those parameters; render + VIEW:
   coherent = format proven → decode character-paired NTPP packages
   (round-7 pairings, proven only) → TEXTURED character GLBs
   (embedded images; textured front render VIEWED side-by-side vs r9
   untextured GLB, integrity identical). If datatextureroot also has
   no pixel path, land its full read + name the NEXT consumer in the
   chain from its call graph (one more hop max, then stop).
3. JOB 3 — B5 16B-RECORD FIELD CENSUS: across all 5,520 records
   (40 pages × 138): per-byte-position entropy + value alphabet;
   anchor on the constant 0x800 word at page offset 52 (record 3's
   bytes 4–5 — check EVERY page's record 3 vs page-level). Correlate
   record fields with the 0x20B directory records (count/offset
   agreement). Test hypotheses (state each verdict): per-record =
   (id/enum, offset, size) index entries? instance placements without
   floats (fixed-point)? material/texture references into the
   embedded NTPP @+0x1c0 (record → NTPP item mapping = TEXTURE/OBJECT
   index, not geometry)? Land field map + first decoded record class
   with proof; NO stage GLB unless a position field proves out and
   renders coherently (viewed).
4. JOB 4 — B3 ANOMALIES: (a) 5 double-size segments: scan interiors
   directly for BONE magics / kao_ / MODEL_HEAD strings / 8,032+1,664
   size signatures (not just slot maps) — split if midpoint anchor
   proves, else bound the anomaly (two costume sets? 2P variant?
   state discriminating evidence); (b) stub segment 26: census its
   containers' classes; (c) closing anchors' BONE 9,440/9,696:
   bone-count math (header 64 + 4N + 12N + 12N + 12N ... solve N for
   both — nonstandard N identifies a different skeleton class: state
   it); (d) segment 27's 42-strong stage cluster: one stage or
   several (cross-read the 16 known stage packages' pattern)?
5. JOB 5 — SUPERSEDE DOC: short committed note (WIRING-INVENTORY
   round-12 section + a line in teardown/tekken6/models/ docs if
   present): r11 skeleton GLBs supersede r9/r10 skeleton GLBs (TRS
   defect; errors up to 597.3 units) — all future skeleton work uses
   r11. Additions-only; superseded files stay, labeled.

## Results

- BOOTSTRAP: branch created from 9d794152 (PR #536 head), this file
  committed (0b79d3d) + PR #550 opened before analysis.
- JOB 1 (PALETTE / REGISTRY) — TRACE CLOSED, caller found inlined,
  palette CAPTURE-ONLY for unit→bone: NO registry entry references
  the emitter @0x08ad161c (exhaustive negative over every reference
  mechanism). The zone = jump tables + default-filled arrays + two
  indirection cells (→ thunks 0x08ad1614/0x08ad160c; consumers
  @0x08ad1490 list for-each, @0x08ad08f8, template consumer node-
  builder @~0x08ad1850). The caller is the INLINED builder
  @0x08ad1890: index rule PROVEN sequential identity (fragment i ↔
  pose-matrix i at obj->[0], pointers at obj+0x18[i], count byte
  @obj+0x41f; 48B/64B stride paths selected by byte @obj+0x41d;
  emitters @161c/@1724 are the paths' leaf twins). obj+0x418
  composition read (out+0x24/+0x28 from obj->[1] ∘ obj+0x418+3;
  +0x2c raw). Per-unit selection is game-side (model class) and
  not statically reachable → no skinned GLBs; static hunt closed.
  Evidence: `round12-evidence/JOB1-REGISTRY-CALLER-VERDICT.md` + `dis/`.
- JOB 2 (DATATEXTUREROOT) — FULLY READ, NO PIXEL PATH: no
  standalone class vtable/type_info exists for the root; only
  tcb_pointer_t<T> instantiations (vtables 0x08b94028/0x08b94078/
  0x08b940c8) whose complete method set (0x08893e80–0x08894080)
  is ctor/dtor/reset pointer thunks — no load method, no GE
  commands, no pixel parameters → no code-derived decode, no
  textured GLBs. One hop named (archive loader → tk sprite/
  texture renderer), chain declared, static NTPP hunt closed.
  Evidence: `round12-evidence/JOB2-DATATEXTUREROOT-VERDICT.md` + `dis/`.
- JOB 3 (B5 CENSUS) — GRID CORRECTED + CLASS DECODED: pages tile
  slot 9 exactly on the 448B-head grid (rounds 10/11 extraction
  was +2,096-shifted; its 40th table entry is a 0 terminator).
  Every page IS an NTPP section (records 0–5 byte-identical
  header in all 40; +16=0x890, +24=0x800). The brief's 0x800
  premise resolved: header field @+24, 40/40 (plus a second BE
  0x800 at in-page 2,148 in 37/40). Directory record 3 agrees
  (0x28 × 0x8a0). Field census over 5,240 payload records landed;
  verdicts: (id,offset,size) REJECTED; fixed-point placements
  REJECTED; texture-reference SUPERSEDED (pages are the sections;
  payload = GIDX-block records). Payload render VIEWED — no
  coherent image, no pixel claim. No stage GLB.
  Evidence: `round12-evidence/JOB3-B5-CENSUS.md`,
  `round12-evidence/r12_b5_fieldmap.json`,
  `round12-evidence/r12_b5_payload_44x48.png`.
- JOB 4 (B3 ANOMALIES) — ALL FOUR RESOLVED/BOUNDED: (a) doubles:
  direct decoded-byte scan, ZERO hidden BONE/anchors; two kits,
  one anchor, 18–29 shared duplicate parts (modal controls 0) —
  bounded as a second costume/form-class kit; not split.
  (b) Segment 26 = compact reduced kit (29 containers) under the
  129-bone anchor. (c) SOLVED: 9,440 = 129 bones, 9,696 = 132
  bones (N at BONE +16; size formula verified exact on
  N=22/110/129/132/146); heads standard 22 — expanded-body
  skeleton class. (d) Segment-27 cluster: 34 distinct signatures
  over 42 containers = multi-stage object pool, stays
  unassigned. Evidence: `round12-evidence/JOB4-B3-ANOMALIES.md`,
  `round12-evidence/r12_b3_anomalies.json`.
- JOB 5 (SUPERSEDE DOC) — LANDED: WIRING-INVENTORY round-12
  section (above) + `models/SKELETON-SUPERSEDE.md`: r11 skeleton
  GLBs supersede r9/r10 (TRS defect, up to 597.3 units); all
  future skeleton work uses r11. Additions-only; no deletions.
