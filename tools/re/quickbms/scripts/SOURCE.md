# Source provenance — `scripts/`

The three `.bms` files in this directory and `LICENSE` are **verbatim,
unmodified copies** of BSD-3-Clause scripts from the upstream project:

- Upstream repo: https://github.com/BRS-PSP-Research-Initiative/Original-Quickbms-Scripts
- Licence: BSD-3-Clause, copyright 2025 Brad D — see `LICENSE`, which
  is also copied verbatim. The scripts' own headers ask that the
  header and licence be kept for derivative works; they are kept here.
- Staged in the private GRE repo (`game-reverse-engineering`,
  `tools/quickbms-scripts/psp-brs/`) and pulled there 2026-10-16.
  This Western Heart copy re-uses the upstream scripts, not GRE's
  private staging, and keeps the upstream licence intact.

The scripts' headers note that only the documentation and tools — not
any game or its assets — fall under that copyright. No game data,
archive, model, texture, animation, or audio file is included here,
and none may be added: this directory is script patterns only.

## What was deliberately NOT copied

- The upstream `Game/` region directories (empty placeholders for a
  user's own ripped copy) — not included, and this repo gives no
  instructions to fill them.
- The upstream `extract.py` / `extract-fld-audio.py` automation and
  `Scripts/shared/` + `Scripts/build/` wrappers — game-specific
  automation tied to that project's directory layout and to a `.env`
  file. Not copied; see "Still owed" in the parent README.
- The upstream README's logo image and its rip-and-extract walkthrough
  — not copied. The parent README here documents lint-only reference
  use instead.
