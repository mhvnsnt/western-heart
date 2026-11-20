# Dead or Alive 6 — Teardown

**Game:** Dead or Alive 6 (Team Ninja / Koei Tecmo, March 1, 2019)
**Platform target:** PC/Steam (App ID 838380)
**Status:** Mechanics documented. Full game pull BLOCKED (see below).
**Teardown date:** 2026-10-13

---

## Pull status

**BLOCKED — disk.** The PC install is ~50GB+ (80GB per Steam requirements). Local
disk is at 93% (7.8GB free). A full download is not possible on this machine.

**What was done instead:**
- Full combat mechanics documented from competitive community sources
  (`DOA6-MECHANICS.md`) — triangle system, 4-way holds, stun system, break
  gauge, Fatal Rush, throws, sidestep attack, stage mechanics, roster, file
  formats. This is the federation payload: the mechanics layer Western Heart
  takes from DOA6.
- No DOA6 copy found on Archive.org (checked 2026-10-13).
- Known sources: Steam (paid), ElAmigos repack (~30GB compressed), RUNE release.

**To complete the pull when disk allows:**
1. Acquire DOA6 PC (Steam purchase or repack) on a machine with 80GB+ free.
2. Map the install: character `.g1m` models, `.g1t` textures, stage files, UI.
3. Pull the community g1m/g1t converters (PULL-IN DIRECTIVE) and extract.
4. Character models feed the reskin pipeline (Bass, Tina, Hayabusa, Kasumi, etc.
   are on the owner's rename/reskin list).

---

## File formats (known)

| Type | Format | Notes |
|---|---|---|
| Models | `.g1m` | Koei Tecmo proprietary; community converters exist |
| Textures | `.g1t` | Koei Tecmo proprietary; community converters exist |
| Engine | Team Ninja in-house | DOA5 lineage |

---

## What's federated into Western Heart

See `DOA6-MECHANICS.md` for the full breakdown. Summary:

- **Triangle system** → reaction table overlay on the move resolver
- **4-way holds** → new counter category in moveset slots
- **Stun system + slow escape** → stun state machine with defender counterplay
- **Break gauge** → per-round resource meter (Break Blow / Break Hold)
- **Fatal Rush** → universal beginner string per fighter
- **Sidestep Attack** → movement-to-offense bridge

Tekken inputs remain the base. DOA6 contributes the counter/hold/stun layer.
