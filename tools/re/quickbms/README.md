# QuickBMS reference scripts — `tools/re/quickbms/`

Reference tooling only. This directory gives a Western Heart
contributor PSP-era archive/model script *patterns* to study when
writing their own archive tooling, plus a static linter to check any
`.bms` script they write. It is not game content and it contains no
game data.

## What is here

- `scripts/BRS-Extract.bms`, `scripts/BRS-Model-Data.bms`,
  `scripts/BRS-Dig-For-Bones.bms` — verbatim, unmodified BSD-3-Clause
  scripts from the upstream project documented in
  `scripts/SOURCE.md` (archive extraction, model-data digging, and
  bone/skeleton digging patterns). Their licence is in
  `scripts/LICENSE` and their headers are kept intact. The game those
  scripts were written for is named only in `scripts/SOURCE.md`,
  which is the doc about pulling that game's data; no other
  Western Heart doc needs to name it.
- `bms_lint.py` — a Western Heart clean implementation of a QuickBMS
  script linter (balanced blocks, known commands, unterminated
  strings). It is not a verbatim copy of the private GRE linter of
  the same name, which carries no licence header and is not cleanly
  reusable as-is.
- `proof/run_proof.sh` — runs the proof below.

## Why lint-only on Linux x86_64

The 32-bit `quickbms` binary segfaults on x86_64 Linux (verified
2026-10-16 in the GRE staging notes) and upstream ships no 64-bit
Linux build. So on this platform scripts are validated statically
with `bms_lint.py` — never executed against a game archive here.
Running QuickBMS itself, if a contributor does so on a platform where
it works, is their own local step, outside this repo.

## Use

```sh
# Lint the bundled reference scripts (proof):
sh tools/re/quickbms/proof/run_proof.sh

# Lint any .bms script you are writing:
python3 tools/re/quickbms/bms_lint.py my-script.bms
```

## Private-output rule (do not skip this)

If you ever run one of these scripts (or a script patterned on them)
against an archive, route **all raw output to a private
repo/location only** — never commit it to this public repo, never
paste it into a PR, issue, or doc. No commercial game file, model,
texture, animation, audio, or ROM belongs in `western-heart` under
any circumstances. Use these patterns only on data you have a legal
right to inspect, and only for Western Heart reference work.

## Proof run

Run from the repo root:

```sh
sh tools/re/quickbms/proof/run_proof.sh
```

Proven 2026-11-02 on this VM: `bms_lint.py` reports `OK` for all
three bundled `.bms` scripts and the script prints
`PROOF PASS: all bundled .bms scripts lint-clean`. No QuickBMS
binary was executed, no game file was read, and nothing was written
to disk except stdout.

## Still owed

- The GRE `tools/quickbms-scripts/` automation wrappers
  (`extract.py`, `extract-fld-audio.py`, `Scripts/shared/`,
  `Scripts/build/`): **not copied**. They are game-specific
  automation tied to that project's directory layout and to a `.env`
  file (which is never copied anywhere). A clean Western Heart
  extraction runner, if ever wanted, is a separate PR with its own
  private-output routing — it is not claimed here.
- The GRE linter `bms_lint.py`: **not copied** (no licence header).
  Replaced here by the clean implementation above.
- A working QuickBMS run (as opposed to a lint): **not proven**,
  blocked on the 32-bit Linux segfault above. Lint-clean is the only
  claim made for these scripts.
