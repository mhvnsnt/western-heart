# Aider + Continue.dev evaluation for the WH agent crew (2026-10-23)

**Verdict up front:**
- **Aider: USEFUL, with caveats.** Adopt it as a crew power tool for narrow, well-specified
  multi-file edits. It runs fully headless, is git-native (every change becomes a reviewable
  commit), and was verified end-to-end on this VM. It does NOT replace crew judgment — it is a
  deterministic "apply + lint + commit" loop around an LLM edit step.
- **Continue.dev: NOT recommended for the crew.** It is IDE-first (VS Code/JetBrains); the crew
  works headless on VMs with no IDE in the loop. Its headless `cn` CLI exists but adds nothing
  over Aider for our workflow, and its strengths (autocomplete, in-IDE chat) don't apply to us.

---

## 1. Aider — what was tested

**Install (this VM, 2026-10-23):** `aider-chat 0.86.2` into `~/workspace/venvs/aider`
(python venv; system pip is PEP-668 locked, VM `/tmp` is a 512 MB tmpfs that is nearly full,
so `TMPDIR` had to be redirected — see §5).

**Honest footprint note:** the task brief said "lightweight, no heavy deps." Reality: the
`aider-chat` wheel is 377 KB but the installed venv is **~639 MB** (tree_sitter_language_pack
184 MB, scipy 105 MB, litellm 64 MB, numpy 75 MB, networkx 17 MB…). scipy/sounddevice/soundfile
are direct deps (voice-input features). On a disk at 93–94%, that is not nothing.

**Test methodology:** no LLM API key exists on this VM, and none was provisioned for this task,
so the *intelligence* side (does it pick the right edits) was **not** tested. What WAS tested,
rigorously, is the *mechanics* loop, using a mock OpenAI-compatible server (`/tmp`,
stdlib-only Python) returning canned SEARCH/REPLACE blocks:

1. `aider --show-repo-map` — repo-map generation on a scratch git repo.
2. Full loop: `aider --model gpt-4o --yes-always --message "<3-file task>"` against the mock —
   prompt → repo map → model response → SEARCH/REPLACE application → lint → auto-commit → exit.

**Test repo** (`~/workspace/scratch/aider-test`, NOT the game repo): a 3-file mini "game system"
(`fighters.py`, `moves.py`, `game/ui/select.py`). Task: add fighter `dummy` to the roster, give
it a `body_slam` move, add a `roster_count()` helper — a 3-file cross-cutting edit.

**Results — all green:**
- Aider built the repo map (tree-sitter signatures; data files listed by name) and sent it with
  the prompt (~7 KB system + map).
- It auto-added the target files to the chat when the model emitted edits for them (no manual
  `/add` needed in `--message` mode).
- Applied all 3 SEARCH/REPLACE blocks, ran its lint pass, and auto-committed:
  `0758291 Add Test Dummy fighter to roster, moves, and select screen` (+ `Co-authored-by`
  trailer). All files compile; `git show --stat` = 3 files, 6 insertions.
- Exit code 0, token/cost accounting printed. Fully non-interactive — no TTY needed.

**Also confirmed from `--help`/docs (not live-tested):** `--dry-run` (no file writes),
`--test-cmd` + `--auto-test` (run a test command after edits), `--apply FILE` (apply canned
edit blocks without any LLM — the deterministic path), `/undo` (revert last commit),
`--yes-always`, `--no-auto-commits`, per-file read-only adds.

**Maintenance status (third-party reports, not independently verified):** comparison write-ups
dated 2026 describe Aider as slowed — last PyPI release 0.86.2 (Feb 2026), ~1.7k open issues.
It is not archived and 0.86.2 is what installed today, but expect slow model-support updates.
Pin the version in crew runbooks; re-check before upgrading.

## 2. Aider — how the crew should use it

Aider's value to the crew is NOT "another agent that edits files" — our subagents already do
that directly. Its value is three mechanical things agents are sloppy at:

1. **Repo-map context packing** — tree-sitter signature map of the repo, so a terse instruction
   ("add X to every fighter data file") reaches the right files without the agent pasting them.
2. **SEARCH/REPLACE application discipline** — exact-match blocks, lint after edit, one commit
   per change. Fewer half-applied edits than freehand agent editing.
3. **Atomic commit-per-task** — every aider run ends in a reviewable commit on a branch.

**When to reach for it:**
- Mechanical cross-cutting edits: rename a field/key across N data files, add a column to every
  roster entry, propagate a constant, small refactors with a crisp spec.
- NOT for: architecture decisions, canon-sensitive writing, anything needing game feel, large
  ambiguous refactors (spec it first, or don't aider it).

**Crew workflow (runbook):**
```bash
# 0. ALWAYS on a feature branch, never main. Commit or stash first.
# 1. Dry run first for anything touching >5 files:
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
    -u ALL_PROXY -u all_proxy -u NO_PROXY -u no_proxy \
  ~/workspace/venvs/aider/bin/aider \
    --model <model> --yes-always --dry-run \
    --message "SPEC: <crisp, file-scoped instruction>"

# 2. Real run (edits + auto-commit):
  ... same, without --dry-run, optionally: --test-cmd "<repo test command>"

# 3. ALWAYS review the diff yourself before pushing / opening a PR:
git show HEAD --stat && git diff HEAD~1 HEAD
```
- `--yes-always` is required headless (otherwise it blocks on "not a terminal" prompts).
- The `env -u ...` proxy unset is **mandatory on this VM** — see §5.
- Set `OPENAI_API_KEY` / `OPENAI_API_BASE` (or the provider's equivalents) from the crew's
  approved credential flow; never bake keys into commands or files.
- Prefer `--test-cmd` pointing at the repo's real test/verify command so aider iterates on
  failures itself.
- Keep prompts file-scoped and explicit ("in `game/js/*.js`, rename X to Y") — vague prompts
  get generic edits, same as with any agent.

**Limitations (be honest about these):**
- **BYOK inference.** Aider is free software; every run bills the model provider. It is not a
  "free resource" in the user's maximize-free-resources sense unless pointed at a local model
  (Ollama — heavy, and a real quality drop for edit tasks). Budget per-run cost; the mock test
  showed token accounting works, so cost is at least visible.
- **Intelligence untested here.** The mock proved the loop, not the judgment. First real-key
  run should be a small, reviewable task.
- **Edit format is exact-match.** SEARCH blocks must match character-for-character; on huge
  minified/generated files (some game JS) this can flake — prefer `whole` format or smaller
  target files there.
- **Not lightweight on disk** (639 MB venv). Fine to keep installed; don't reinstall casually.
- **Maintenance is slow** — pin `aider-chat==0.86.2`, re-evaluate on upgrade.
- **It will happily commit garbage** with `--yes-always` — the human/agent review step is not
  optional. This matches the repo's "reviewable commits" culture, but only if someone reviews.

## 3. Continue.dev — research findings

Evaluated from docs/comparisons (per task brief: no VS Code extension install — and there is
no VS Code on this VM anyway).

**What it is:** open-source (Apache-2.0) AI coding platform: VS Code + JetBrains extension
(chat / edit / agent modes, tab autocomplete), a **headless CLI** (`cn`, `npm i -g
@continuedev/cli`, needs Node 20+), config via `config.yaml`, BYOK against Anthropic/OpenAI/
Google/OpenAI-compatible endpoints or local models via Ollama. Agent mode has real tools
(`read_file`, `create_new_file`, `edit_existing_file`, grep/glob, repo map, MCP servers).

**Headless mode exists:** `cn -p "prompt"` runs without a TTY, `--format json` for scripting,
session resume (`cn --resume` / `cn ls`). So "Continue needs an IDE" is not the full story —
the CLI can be scripted.

**Why it's still not the pick for the crew:**
1. **No IDE in our loop.** The crew runs as headless subagents via shell. Continue's
   differentiating strengths — autocomplete, in-IDE chat/apply, inline diffs — are all
   editor surfaces we don't have. What's left (`cn -p` agent runs) duplicates Aider's role.
2. **Less git-disciplined.** Aider's whole design is "every change is a commit, `/undo`
   reverts it" — that maps 1:1 onto this repo's review culture (instruction-gate PRs,
   never-clobber merges, verify-by-playing). Continue's agent edits land as working-tree
   changes you then commit yourself; more room for the "finished but never delivered" failure
   mode the user has already flagged.
3. **Heavier setup for the same job.** Node 20+ toolchain + `config.yaml` model/provider
   wiring per VM, versus aider's single venv + env vars. On a 94%-full disk, less is more.
4. **Same BYOK cost.** No cost advantage over Aider; both meter through the model provider.
5. **Project health signals are mixed** in third-party comparisons (one Aug-2026 write-up
   describes it as unmaintained-ish and recommends pinning) — treat as unverified, but it
   argues against betting crew workflow on it without a re-check.

**Where Continue.dev DOES make sense:** the user's own hands. If M.Dogg ever edits code in
VS Code with a model key, Continue's autocomplete + in-IDE agent is the nicer daily driver
than a terminal tool. That's a human-workstation call, not a crew call.

## 4. Comparison (crew-relevant axes only)

| Axis | Aider | Continue.dev |
|---|---|---|
| Headless / no-TTY operation | ✅ `--message` + `--yes-always`, verified exit-0 | ✅ `cn -p`, JSON output — not tested here |
| Git-native (commit per change, undo) | ✅ core design | ❌ working-tree edits, manual commit |
| Multi-file edits in one task | ✅ verified (3 files, 1 commit) | ✅ (agent mode w/ tools) |
| Repo context | tree-sitter repo map (sigs) | local index + `@`-providers + repo map |
| Install weight on this VM | 639 MB venv (measured) | Node 20+ + npm pkg (not measured) |
| Inference cost | BYOK (metered) | BYOK (metered) — no advantage |
| Fits "no IDE" crew | ✅ terminal-native | ❌ IDE-first; CLI is a second-class path |
| Maintenance signal (3rd-party) | slowed, pinned 0.86.2 OK | mixed — verify before adopting |

## 5. Environment quirks found (record for future crew work)

1. **pip on this VM:** system pip is PEP-668 locked → use a venv. VM `/tmp` is a 512 MB tmpfs
   at ~80% → set `TMPDIR=~/workspace/scratch/pip-tmp` (or similar) for installs, and clean it
   after. `pip install` also needed `--break-system-packages`-avoidance via the venv only.
2. **`no_proxy` breaks all httpx-based tools.** The VM's `NO_PROXY`/`no_proxy` contains
   *unbracketed* IPv6 literals (`fd8b:4f84:7d32:99::1`). Any httpx client construction
   (aider, litellm, openai SDK, and anything else built on httpx) crashes with
   `InvalidURL: Invalid port: ':1]'` — even for localhost. Fix: `env -u NO_PROXY -u no_proxy`
   (plus the `*_PROXY` vars) around the tool call. This will bite future Python HTTP tooling
   too — sanitize or unset.
3. **Aider first-run prompts** ("Add .aider* to .gitignore?", git name/email) block headless
   runs — pre-seed `.gitignore` and git config, or always pass `--yes-always`.

## 6. Recommendation

1. **Adopt Aider for the crew**, scoped: mechanical multi-file edits on feature branches, dry-run
   first, human/agent diff review before PR, `--test-cmd` where a verifier exists. Install lives
   at `~/workspace/venvs/aider` (aider-chat 0.86.2, pinned).
2. **Do not adopt Continue.dev for the crew.** Revisit only if the crew ever gains an IDE in
   the loop. Fine as a human-workstation option for the user.
3. **Next step to de-risk:** one small real-key Aider run (e.g., a 2–3 file rename in the game
   repo on a scratch branch) to validate *judgment* quality with the crew's actual model, since
   this eval validated mechanics only. Budget a few cents of inference.
4. **Watch the disk:** 639 MB for the venv at 93–94% disk. If space gets critical, the venv is
   reinstallable from this doc's §1 — but prefer keeping it warm.

*Eval method note: Aider installed and tested live on this VM 2026-10-23 (mock-LLM loop);
Continue.dev evaluated from official docs + third-party comparisons, no install performed.
Test scratch repo at `~/workspace/scratch/aider-test`; mock server script was ephemeral
(`/tmp`, removed). Game repo was not touched by the test.*
