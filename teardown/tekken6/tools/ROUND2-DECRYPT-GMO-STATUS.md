# Tekken 6 PSP — Teardown ROUND 2: decrypt6 status, COM/GMO inventory

Date: 2026-10-20. Lane: teardown sweep lane 2 (decrypt6 + remaining ~10%).
Method: Ghidra 12.1.4 headless decompilation of the decrypted EBOOT
(MIPS Allegrex), the lane's own restored round 1–11 working files
(recovered byte-exact from release `tekken6-recon-20261016`, tar sha256
`2c738b24f46395960e463fd03c637b038a0942590c0055b9ef3fe1bc9d77afcc`),
and strict decodes scored by size + adler32.

## 1. Baseline reproduced

The round-10 decoder state reproduces exactly: **20 of 76** DATA401
"GZIP" containers decode byte-exact. In round 2 all 20 were re-verified
with the strict oracle: uncompressed size match AND adler32 of the output
equals the stream trailer (the wrapper at 0x8b559c8 returns that trailer
as the expected adler). The 20 exact containers are the fixed-block /
small ones: gzip idx 19, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45,
47, 49, 51, 53, 55, 56, 57.

## 2. SOLVED in round 2 — code-length repeat semantics (the "header bug")

Rounds 4–11 read the EBOOT as: repeat symbol 19 = (10 extra bits, base 3),
symbol 27 = (18 extra bits, base 11). **That reading was wrong**, and it
poisoned every downstream conclusion (including the round-9/11 "proofs"
that the EBOOT inflate cannot read these files — their bit accounting
started from the broken header).

Correct semantics, now in `tools/tekken6_gzip.py`:

- symbol 16 = repeat previous length, count = 3 + getbits(2)
  (confirmed in the Ghidra decompilation of the CL reader at 0x8b55fa4)
- symbol 19 = zero run, count = 3 + getbits(3)
- symbol 27 = zero run, count = 11 + getbits(7)

i.e. exactly RFC 1951 symbols 17/18, renumbered to 19/27 in the game's
code-length alphabet (whose order table at EBOOT 0x8bd6346 is
[16,19,27,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15] — byte-exact in the
binary).

Proof: with these counts, the dynamic header of **every one of the 76
containers** parses to an exactly Kraft-complete code
(sum of 2^-len = 1.00000 for both the lit and dist tables; container 3,
which the old semantics blew up to 1236 lengths against a 315-length
table, now totals exactly 315). After this fix the failure mode of all
56 dynamic containers is uniform and clean: decode proceeds through
literals and matches and stops at the first distance that exceeds the
output produced so far. No header desync remains anywhere.

## 3. Ghidra evidence (decompiled 2026-10-20, this lane)

Environment note: the EBOOT's e_flags (0x70000003, MIPS32R2) makes
Ghidra's ELF loader abort ("Unsupported MIPS32 rel6 variant"); the
working recipe was a patched copy (arch nibble zeroed) or raw-region
imports at base 0. Full-program analysis OOMs on this box; region
imports (0x8b54000–0x8b57000) + targeted seeds work. The decompiler
truncates at the Allegrex BITREV (stock Ghidra 12.1.4 MIPS Sleigh has no
Allegrex variant), so the main loop is evidenced by decompilation of its
entry/helpers + Ghidra's own listing of the match path.

- Wrapper `0x8b559c8` (decompiled): validates the zlib header via
  `0x8b55ab0`, requires `(cmf & 0xf) == 8`, requires `(flg & 0x20) == 0`
  (**FDICT rejected — no preset dictionary**), calls inflate
  `0x8b55bf0`, copies the 4-byte adler trailer to its out-param.
- Header validator `0x8b55ab0` (decompiled): CMF/FLG mod-31 check;
  extracts the dictionary id only when FDICT is set (the wrapper never
  lets that path reach inflate).
- Inflate `0x8b55bf0` (decompiled): table base `0x8bd6340`; stored-block
  branch with the LEN/NLEN complement check; dynamic branch reading
  3-bit code lengths in the ORDER table; fixed branch copying the table
  block 0x8bd6340–0x8bd63ac.
- CL reader / builder `0x8b55fa8` → `0x8b560b4` (decompiled): input is
  halfwords `(length << 9) | symbol`, nonzero lengths only, symbol
  order; builder stores negated lengths while assigning codes; symbol
  16 handled as count = 3 + getbits(2) repeating the previous length.
- Match path (Ghidra listing): distance extra-bit count comes from the
  Allegrex CLZ at `0x8b55e08` minus 0x1e at `0x8b55e0c`, i.e.
  neb = 30 − clz32(base), and the DIST table at 0x8bd63bc is standard
  DBASE − 1, so **dist = DBASE[dsym] + extra** in standard terms —
  the distance formula is standard deflate. The copy loop
  (0x8b55e20–0x8b55e38) copies from out−dist with a bounds error
  (0x80000104/0x80000108) if dist > out_len.

## 4. STILL OPEN — main-loop length composition (the last decrypt defect)

With headers and distances settled, lengths are the remaining defect.
Measured on container 0 with standard LBASE/LEXT: 104,054 bytes produced
vs 105,472 expected (−1,418 over 9,460 matches); container 4 overshoots
by 508 — the error is per-symbol, not a constant offset. The game's
length table (0x8bd637c) packs each base into a signed halfword; the
loop takes `sra s4, v0, 4` (0x8b55de8) after a BITREV (0x8b55de4) and
fetches extra bits through the shared getbits at 0x8b55e70/0x8b55e8c,
which derives the bit count from the entry descriptor itself
(`sra t2, t2, 0x1c` at 0x8b55e8c). The four direct readings of that
composition (−(X>>4) ± extra, ± 1) were emulated against container 0 and
all desync within the first matches (first bad distance at out≈50), so
the getbits contract is part of the formula and fragments are not enough
to pin it.

Named next steps (in order):
1. PPSSPP live trace: breakpoint at 0x8b55bf0 while the game loads a
   GZIP container; log (symbol, length, dist) triples for container 0
   and fit the exact composition from ground truth. (PPSSPP is already
   local at tools/ppsspp/; TEARDOWN.md's live-run notes apply.)
2. An Allegrex-capable Ghidra Sleigh (none ships with 12.1.4) so the
   decompiler no longer truncates at BITREV 0x8b55de4.
3. Unicorn emulation of 0x8b559c8: harness was built this round but the
   run stalled at 0% CPU under this VM's multi-lane contention; retry on
   a quiet box.

## 5. COM / GMO inventory (the remaining ~10%)

### The 18 large containers (gzip idx 58–75, IDX entries 709–735)

Decompressed sizes 450,636–703,400 bytes each (9.4 MB total). Partial
decodes (clean prefixes) show a "COM\0" container: u32be version 1,
magic, u32le fields. **Content type is NOT confirmed** — round 11's
warning stands: do not call these character models until a full decode
exists. They are blocked on §4. Per-character assignment is impossible
until they decode; when they do, the per-character isolation law (§7)
applies to whatever they contain.

The other decoded container of note: gzip idx 0 (entry 454) is an NDPP
container whose 13-entry section table chains exactly to its 105,472
bytes even under the current partial decode.

### NDPP archive (bin_e6.2, IDX entry 87) — already landed

- 81 MB archive holding 2,546 embedded GZIP containers (customization
  parts) and 950 NDPP bounding volumes.
- On western-heart main since PR #187: `teardown/tekken6/models/
  NDPP-FORMAT.md`, `models/ndpp_bounding_volumes.glb` (1,103 boxes /
  357 sections), `models/tools/build_glb.py`, `extract_boxes.py`.

### GMO → GLB pipeline — PROVEN, waiting on decrypt

Tooling (from the recon tree, `work/tooling/` in release
`tekken6-recon-20261016`):

| Stage | Tool | License |
|---|---|---|
| GMO parse | PiosGmoLibrary (Pionome) — full chunk parser: Model/Bone/Part/Arrays/Mesh/Material/Motion | see §8 |
| GMO → JSON | gmo2json (lane-written thin glue over the library) | ours |
| JSON → GLB | json2glb.py via Blender 4.0.2's own glTF exporter | Blender GPL |
| GIM → PNG | puyotools CLI | see §8 |
| Skinning reference | PSP-GMO-Loader (iOS reference loader) | see §8 |

Proof on file: 21 real PSP GMO samples (Dissidia characters) in
testdata; `cloud.gmo` converts to `cloud.glb` (411,572 bytes; 9,048
verts; 1,881 tris; 1 model). **Round-2 verification:** the GLB was
re-imported in Blender 4.0.2 headless and rendered front view by this
lane — `tools/proof/cloud_front.png` — a complete, coherent T-posed
character (spiky hair, torso, weapon in right hand, baggy pants,
boots). The pipeline is ready the moment decrypted GMO data exists;
what's missing is the decrypted Tekken 6 GMO payloads, not tooling.

### What is NOT yet converted

- 0 of the 18 COM containers (blocked on §4).
- The 2,546 embedded customization GZIPs (same custom-deflate defect;
  they unblock with §4).
- Tekken 6 character GMO models: 0 — no decrypted GMO payload has been
  produced yet by any round. The often-quoted "40 character meshes"
  figure is the roster size, not a mesh count found in the data.

## 6. Research / pull-in log (round 2)

Research findings that mattered (full notes:
`teardown/tekken6/docs/PSP-RE-RESEARCH-2026-10-20.md`):

- No published Tekken 6 PSP DATA401/GZIP format work exists; rounds
  1–11 + this round are the state of the art. No quickBMS script covers
  this format (quickBMS itself is GPL-2.0).
- The disc carries only two PRX modules (libpsmfplayer.prx 32,144 B,
  psmf.prx 6,800 B — Sony PSMF video). There is **no pack/openPac PRX
  on the disc**, so the GZIP decoder is in the EBOOT (settled §3) or a
  firmware module; the EBOOT-side evidence is conclusive for the
  wrapper/inflate pair above.
- PPSSPP (local AppImage) remains the live-trace route for §4 step 1.
- tkdr-recomp (Tekken Dark Resurrection PSP recompilation project)
  exists as ecosystem reference; no game data, nothing to pull for
  this format.

Pull-ins used this round (all pre-existing local/team tooling; nothing
new vendored into the repo):

| What | Source | License | Where it landed | What it unlocked |
|---|---|---|---|---|
| Ghidra 12.1.4 + JDK 21 | NSA Ghidra (team tools dir) | Apache-2.0 | used from tools/ghidra/ (not vendored) | §3 decompiled evidence |
| Unicorn 2.1.4 + Capstone 5.0.7 | pip (lane venv) | BSD / BSD | lane scratch only | word-level ID of the 2 Allegrex opcodes blocking Ghidra (BITREV 0x8b55de4, CLZ 0x8b55e08); emulation harness for §4 step 3 |
| pycdlib | pip (system) | LGPL | used, not vendored | ISO directory read (PRX inventory, §6) |
| PiosGmoLibrary / PSP-GMO-Loader / puyotools | GitHub (recon tree) | no license file found for PiosGmoLibrary / PSP-GMO-Loader → **documented, not re-pulled**; puyotools is GPL-family per its repo | already in release tekken6-recon-20261016 `work/tooling/` | the proven GMO pipeline of §5 |
| ShrineFox P4GModelConverter | GitHub | no license file → documented, not pulled | — | alternative GMO path, unused |

## 7. Per-character isolation (standing law, owner 2026-10-20)

All Tekken 6 PSP decoded data stays namespaced per character
end-to-end. When the COM containers and GMO payloads decode:

- Each character's meshes, skeleton, MOTA animations and add-ons are
  stored under that character's own directory only.
- Each converted GLB is fully self-contained: its OWN skeleton and its
  OWN animation clips, no shared rig or shared mutable state.
- Conversion runs process one character at a time with independent
  state; a fix for one character can never shift another's stance.
- Nothing in this round's tooling shares state across files:
  `tekken6_gzip.py` decodes one container per invocation, stateless.

## 8. Scoreboard

- DATA401 bulk decrypt: done (round 3, global keys) — 478 files.
- GZIP containers byte-exact: **20/76** (adler-verified, round 2 re-run).
- Dynamic headers: **76/76 parse Kraft-exact** after the round-2 fix.
- Remaining decrypt defect: 1 (length composition, §4).
- COM containers decoded: 0/18 (blocked on the same defect).
- GMO→GLB conversions of Tekken 6 data: 0 (no decrypted payload yet);
  pipeline proven on 21/21 sample GMOs + rendered proof.
- ISO: re-downloaded this round from release `tekken6-psp-v1` and
  sha256-verified byte-exact
  (`b5e52660a52caeca351e93c54bb4db0011325af0c1e3c67230bddde8f7cecf44`).
  Note: the local copy was removed from this lane's scratch dir by an
  external disk process at ~18:40 CDT after verification; the file is
  intact on GitHub in two repos and re-fetchable (proven today).
