# Canon Archive — Western Heart / Eastern Mind

This directory is the archived record of the game's canon, notes, and
development history, compiled from the owner's recorded words so that the
record lives **in this repo**, where anyone working on the game can find it.

## The standing rule

**Canon, notes, and development records for this game are committed to this
repo as they are created.** The assistant's private memory (`~/MEMORY.md` and
the daily notes under `~/memory/`) is a *working copy only* — never the only
home of anything about this game. If a fighter's canon, a design decision, a
rename, a playtest verdict, or a standing directive exists only in the
assistant's memory, that is a defect: it gets pushed here.

Owner's order (2026-10-23):

> "when I tell you to merge and push everything to main, I mean all the
> Canon, all the notes, all the development conversations, like if it
> couldn't find none of the canon for the fighters, what doesn't make sense
> is that it couldn't find it in none of the development conversations.
> Like everything should have been getting pushed to the repo or at least a
> trace of something."

## Contents

| File | What it holds |
|---|---|
| `CANON-MASTER.md` | Every fighter's recorded canon in one master record — identity, appearance/model, story, connections, base/moves, open gaps. Compiled only from recorded owner material. Fighters with nothing recorded are listed as such; nothing is invented. |
| `DEV-NOTES-ARCHIVE.md` | The game's development notes and decisions, organized by date and topic: roster decisions, renames, systems, teardown findings, playtest verdicts, and standing owner directives for the game. Each section cites its source file and date. |

## Relationship to the rest of the repo

- `CANON.md` (repo root) remains the character bible — the authored,
  in-universe text. This archive is the **record behind it**: what the owner
  actually dictated, decided, and corrected, and when.
- `roster/<fighter>/CANON.md` files (where they exist) hold the per-fighter
  working canon. This archive does not replace them; it guarantees the
  material also exists in one compiled, searchable place.
- `RENAME-MAP.md` remains the log of proprietary renames. `CANON-MASTER.md`
  cites it rather than duplicating it.

## Compilation rules used for this archive

1. **Recorded material only.** Every statement traces to the owner's
   recorded words in `~/MEMORY.md`, the daily development notes in
   `~/memory/2026-*.md`, the game's docs in `~/workspace/agent-ops/`, or
   docs already in this repo. Where nothing is recorded, the fighter is
   listed with "no canon recorded yet."
2. **Attribution by traits, not by typed name.** The owner dictates by
   voice; speech-to-text garbles names (Zen/Ren, Zui/"Zooey"). Canon is
   attributed by the character's recorded traits, per the owner's
   canon-anchor rule (2026-10-21).
3. **Base names are scaffolding.** Tekken / Street Fighter / other source
   names in mapping contexts (e.g. "Steve Fox → Zui") are transitional
   asset references, not identities. A fighter's identity is always the
   Western Heart character.
4. **Game material only.** Personal, legal, financial, marketplace, and
   other-project material in the source notes was excluded. Mixed entries
   contributed only their game part.
5. **Conflicts are flagged, not resolved silently.** Where two recorded
   statements disagree, both are recorded and the conflict is marked OPEN
   for the owner.

*Compiled 2026-10-23 from `~/MEMORY.md` (1,059 lines), `~/memory/2026-*.md`
daily notes (2026-10-05 – 2026-10-23), `~/workspace/agent-ops/` game docs,
and this repo's own `CANON.md`, `RENAME-MAP.md`, and `roster/*\/CANON.md`
files.*
