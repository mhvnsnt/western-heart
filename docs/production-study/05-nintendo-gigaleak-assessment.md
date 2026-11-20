# Nintendo Gigaleak — Honest Access Assessment + Structure Lessons

**What it was:** ~2TB+ of internal Nintendo data in waves on 4chan, July 2020
onward. Source code, prototypes, art assets, hardware docs. N64/GameCube/Wii era.

**Access status:** Live mirrors on archive.org (checked 2026-10-12):
- `archive.org/details/nintendo_gigaleak`
- `archive.org/details/gigaleak-compiled-roms-1` (401MB compiled ROMs)
- `archive.org/details/gigaleak-source-code-ezbuild-collection_202409` (buildable source + SDKs)

NOT downloaded into this library — Nintendo is the most litigious company in
games. Documented for awareness.

**What's actually useful for Western Heart (from public write-ups, not downloads):**

1. **How Nintendo organized game projects in the 90s.** The leak showed
   complete source trees: how code, art, sound, and tools were laid out in one
   repo. The lesson: ONE repo per game, with `src/`, `assets/`, `tools/`, and
   `docs/` separated from day one. Western Heart follows this.

2. **Prototype-to-release evolution.** Unreleased prototypes (Star Fox 2, etc.)
   showed how Nintendo iterated: playable prototype FIRST, art later. Matches
   the Riot method (prototype the core mechanic first) and our own grey-box rule.

3. **Asset naming discipline.** 90s Nintendo had strict naming conventions for
   every asset — the same discipline Tekken 7's prefix system shows. Pros name
   everything systematically; amateurs name things "final_v2_REAL."

**Verdict:** The Gigaleak's era (90s console) is too far from a modern UE
fighting game to be a direct template. Its value is organizational philosophy,
not file formats. Our direct technical template is the tekkenmods docs.
