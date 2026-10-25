# Urban Reign Phase 4 — Job 3: polish closures

## (a) char064 missing s16 group — GAP DOCUMENTED, exact shape proven

State: char064's shipped GLB holds **1197 of 1260 verts** (63 missing;
phase-4 verification: `textured-models/MANIFEST.json` char064 =
1197 verts / 1674 indices / **14 joints** — by far the smallest rig
in the set; next smallest is 25 joints).

What this phase established:

- char064 is not a truncated normal fighter: at 14 joints and 1197
  verts it is a genuinely smaller model (a minor fighter), and its
  PPK (605,824 B, local scratch copy size-verified in phase 3's
  census work) parses into the same chunk grammar as its siblings.
- The phase-1 `char064_vmanifest.json` (PR #429 branch) shows the
  early parse recovered only 640 verts from 2 parsed chunks with
  11 skipped vertex records across them — the shipped 1197 came from
  the completed phase-1 decoder, and the remaining 63 verts are one
  s16 group whose records the decoder's grammar does not accept.
- **Not closed:** locating the group requires re-running the phase-1
  vertex decoder over char064.ppk with per-group reject logging
  (the decoder lives on the PR #429 branch; this phase's window went
  to Jobs 1–2, and a blind re-parse without the reject log would
  only reproduce 1197). Exact next step: instrument the group loop
  to dump (chunk offset, group header, reject reason) for every
  rejected group in char064.ppk; the 63-vert group is the one whose
  header deviates (expected: a stride/type variant sibling groups
  don't use). No verts were fabricated to close the count.

## (b) 11 characters with ≥1 unproven accessory piece — GAP DOCUMENTED per mechanism

The unproven pieces share the phase-1/2 mechanism: a rigid piece
whose verts are single-bone weighted under the assumed node graph
(see (c)) — its skinning was never independently proven from file
relations the way the body pieces were (bind-matrix exactness,
max dev 3.7e-08, was proven for the skinned body verts, not for
these rigid attachments). Phase 2's char001 proof renders show the
consequence: the accessory piece swings wide at frames 47–70 of
pmot001 motion 0 while body edge distortion stays 0.04–0.06
(LBS-normal).

What would prove each piece (the phase-1 standard): locate the
piece's verts in the character PPK, show their weight block names
exactly one bone, and show the piece's rest transform equals that
bone's bind matrix within the same 3.7e-08-class deviation the body
verts achieved. That is a per-piece PPK excavation for 11
characters; it was not executed this phase (Jobs 1–2 consumed the
window, and the (c) result below means the honest fix may be a
graph correction that re-proves all of them at once). **No piece's
skinning is claimed proven by this phase.**

## (c) Node-graph hunt — SEARCH CLOSED, graph not in the shipped data searched

Standing assumption (phases 1–2): motion bone b → GLB node b
("H-index" mapping), documented in every artifact. This phase
searched for the true graph in:

- `gyuindex.bin` / `gyuindex_ppk.bin` — file indexes only; no node
  or bone-parent data (full parse in the Job-1 report).
- `general_index` files — slot↔global-ID only.
- motdat `.info`/`.bin` — move lists + sampled data; the `.bin`
  payload's 33 f32/frame layout is sampled **track** data in bank
  bone order, not a graph.
- SLUS_212.09 string tables — the named `.gyu` table (66 names) is
  a file list, not a graph; no bone-name or parent table strings
  exist in the ELF.
- Ghidra decompile of the pose evaluator path (`FUN_002918xx` /
  `FUN_00101628` neighbourhood): attempted twice, blocked by this
  VM (OOM kill, then import failure) — the one read not landed.

**Verdict:** the true node graph is not present as data in any
shipped file searched; if it exists anywhere it is compiled into
the SLUS pose-evaluator code or built at load from the PPK bone
records (the PPK's own bone-index region, type `0xae00` in the
phase-1 PPK notes, is the untested candidate). Impact statement
for shipped clips: the H-index mapping is **correct for the body**
where phase 2 proved it (embedded char001 animation sampled at
frame 24 reproduces the independently baked pose at max dev
1.8e-07) and **suspect exactly for the rigid accessory pieces**
in (b) — the swing residual is the measurable impact, bounded to
those pieces; no shipped body clip needs re-issue on this account.
Next discriminating test: decode char001 PPK's `0xae00` bone-index
region into an explicit parent list and diff it against the GLB
node order; a single differing parent for the accessory bone
closes both (b) and (c).
