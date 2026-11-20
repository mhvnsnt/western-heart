# ISO9660 reference extractor — `tools/re/iso9660/`

Reference tooling only. This directory lets a Western Heart contributor
list (and, on a machine they control, extract) a plain ISO9660 CD-ROM
image. It is not game content, it contains no game data, and no output
from it belongs in this public repo.

## What is here

- `iso9660_extract.py` — a Western Heart clean implementation of a
  minimal ISO9660 reader. It handles 2048-byte logical sectors (a plain
  `.iso`) and 2352-byte raw Mode-2 sectors (a `.bin`, data at offset 24).
  It is not a verbatim copy of the private GRE script of the same name:
  it was written for this repo, uses `argparse`, walks directories
  iteratively, and rejects directory-entry names that could escape the
  output directory (`/`, `\`, `..`).
- `proof/make_test_iso.py` — builds a tiny synthetic ISO9660 image from
  scratch (volume `WH-TEST`, one subdirectory, two small text files).
  It contains no commercial or game data.
- `proof/run_proof.sh` — runs the proof below. Everything it creates
  lives under `/tmp` and is deleted when it finishes.

## Provenance

The GRE private repo (`game-reverse-engineering`, `tools/`) holds a
minimal ISO9660 extractor for raw PS1 `.bin` images. That script carries
no licence header and is not cleanly reusable as-is, so it is **not**
copied here. This directory is the clean replacement, written to the
same public ISO9660 format, and the GRE original remains owed as
"not copied, replaced by this clean implementation" — see "Still owed"
below. If a future contributor confirms the GRE script's licence, the
two implementations can be compared and this note updated; until then,
treat this file as the only ISO9660 extractor in this repo.

## Use

```sh
# List only — extracts nothing, safe on any image you may inspect:
python3 tools/re/iso9660/iso9660_extract.py IMAGE.iso --list-only

# Extract — output directory MUST be private (see below):
python3 tools/re/iso9660/iso9660_extract.py IMAGE.iso --outdir /private/path/out
```

## Private-output rule (do not skip this)

Raw extracted output is routed to a **private** repo/location only —
never committed to this public repo, never pasted into a PR, issue, or
doc. The proof script enforces the same rule for its own output: it
works only under `/tmp` and deletes its work directory on exit.

Use this tool only on images you have a legal right to inspect, and
only for Western Heart reference work (format study, not asset reuse).
Commercial game files, models, textures, animations, audio, and ROMs
must not land in `western-heart` under any circumstances.

## Proof run

Run from the repo root:

```sh
sh tools/re/iso9660/proof/run_proof.sh
```

Proven 2026-11-02 on this VM (see PR description for the run): the
synthetic image lists as volume `WH-TEST` with 3 entries
(`DOCS/`, `HELLO.TXT`, `DOCS/INNER.TXT`), extraction reproduces both
text files byte-for-byte in both the 2048-byte and the 2352-byte raw
Mode-2 layouts, and the script prints
`PROOF PASS: synthetic ISO9660 listed and extracted, contents match`.
The proof uses only the synthetic image — no commercial image was
used, and no extracted output was kept.

## Still owed

- The GRE original `tools/iso9660_extract.py`: **not copied** (no
  licence header, not cleanly reusable as-is). Replaced here by the
  clean implementation above; no further copy is needed unless its
  licence is confirmed.
- Any real-disc workflow: owed, and it must keep its outputs private
  per the rule above.
