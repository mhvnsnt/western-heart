# Decision: DOA4 ISO reassembly resume (worker 69, 2026-10-22 ~18:30 CDT)

## Owner instruction (verbatim quote)
"Reassemble the DOA4 ISO (30/30 chunks, 7.8GB) from release `doa4-iso-v1` (large files to Releases/external storage, NEVER /tmp or local clutter)."

## Status
IN PROGRESS. Worker 59's session died on a runtime infrastructure failure
("restart drain in progress") with 8.5/30 chunks downloaded. Worker 69
resumed the download 2026-10-22 ~18:25 CDT.

## Method
- New resume script `dl-resume.sh` (node-based manifest parse; the old
  `download.sh` used `python3 -c` for JSON — kept bash/curl for the transfer).
- FRESH downloads only, no `curl -C` resume: the 2026-10-16 status doc
  records that resume corrupted files (servers ignoring Range headers,
  duplicate data appended). Partial `doa4-250m.part_09.tmp` was discarded
  and re-downloaded fresh.
- Every chunk sha256-verified against `manifest.json` before acceptance;
  already-verified chunks (01-08) skipped via hash check, not size check.
- Staging dir: `~/workspace/w59/doa4-iso/` (established by worker 59;
  NOT /tmp — the 7.8GB assembly must survive VM restarts).

## Manifest facts
- 30 chunks, 7,834,892,288 bytes total (matches the 2026-10-16 verified size:
  29x262,144,000 + 232,716,288).
- Source: `https://github.com/mhvnsnt/western-heart/releases/download/doa4-iso-v1/`.

## Why the ISO matters (dependency chain)
The 2026-10-16 extraction produced the chr*.afs / mot.afs / anm.afs files
from this ISO, but `~/workspace/doa4-bass/doa4.iso` no longer exists on the
VM. Reassembly is the prerequisite for: (a) re-running `doa4_decode3.py`
end-to-end verification, (b) the MdlGeo/ObjGeo assembly RE for the roster
renders, (c) mot.afs/anm.afs animation ground truth for Vain Abel.

## Note on the GLB repair
The 165-GLB header repair (TEXCOORD_0 byteOffset) was done WITHOUT the ISO
via a surgical header patch (`glb-header-repair.mjs`, mirrors
`write_glb_fixed`); BIN chunks byte-identical. See
`docs/decisions/2026-10-22-w69-glb-repair.md`.
