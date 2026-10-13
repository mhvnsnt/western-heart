# URBAN REIGN — Teardown for Western Heart

**Role in Chimera Build (owner 2026-10-12):** GAME #6 — street-brawl systems. *"It's kind of a hybrid of the wrestling, the WrestleMania XIX and No Mercy modes. And the Tekken modes."*
**Developer:** Namco (ex-Tekken / Soulcalibur team)
**Platform:** PlayStation 2 (2005)
**Last updated:** 2026-10-13 (full teardown sweep)

---

## What's Extracted and Documented

### ISO — Downloaded, Verified, Safe on GitHub Release (DONE 2026-10-13)
- `Urban Reign (USA).iso` — 4.14 GB, Internet Archive `urban-reign-usa_202608`, verified.
- **Safe storage:** GitHub Release `urban-reign-iso-v1` (https://github.com/mhvnsnt/western-heart/releases/tag/urban-reign-iso-v1) — split into 8×500MB parts (GitHub 2GB/file limit). Reassemble: `cat urban-reign-500m.part_* > "Urban Reign (USA).iso"`.
- **Teardown (PR #23 merged):** AFS structure mapped, **7 stage PPKs identified** (back alleys, bars, rooftops, Chinatown, junkyards + 2 more). See commit `b1cc587`.
- NOTE: 4.14GB exceeds the browser file-grant upload size limit — TeraBox upload of this ISO needs a non-browser path (owner manual).

### Research (done, no ISO needed)
- Documented in `docs/URBAN-REIGN-TEARDOWN.md`:
- **60+ playable fighters**, each with own style (boxing, wrestling, karate, brawling, capoeira, kung fu); ~30 special moves + ~50 double-team attacks per character
- **Tekken guests:** Paul Phoenix and Marshall Law (Tekken 5-era models) — direct chimera-relevant assets
- **100-mission Story Mode** (Brad Hawk, brawler-for-hire, Green Harbor)
- **AI partner system:** double-team combos — launch enemy into the air, partner catches and slams
- **30+ weapons:** bats, pipes, bottles, shovels, 2x4s
- **Destructible environments:** back alleys, bars, rooftops, Chinatown, junkyards — furniture breaks, shelves shed boxes, cars/pinball machines shatter
- **Special arts meter:** builds on damage/dodges/hits → uncounterable super moves
- **Modes:** Story, Free, Challenge (wave survival), plus 4-player free-for-all brawling

---

## What's Blocked and Why

- **Stage PPK extraction** — 7 stage PPKs identified in the AFS structure but not yet extracted to geometry. PS2 stage format needs RE (next lane).
- **Design question open (owner decision needed):** Option A — third **BRAWL MODE** vs Option B — merged into Wrestling Mode. Added to CHIMERA-BUILD.md 2026-10-12.

---

## Chimera Build Value

- **The missing link between Tekken Mode and Wrestling Mode** — a Namco brawler built by the Tekken team, with wrestling moves, weapons, and 4-player mayhem
- **Double-team combat:** AI partner launch-and-catch slams → template for chimera tag/team mechanics
- **Weapon + destructible-environment systems:** 30+ weapons and breaking environments are chimera stage-design targets
- **Tekken guests (Paul/Law):** Tekken 5-era models of characters already in the chimera roster → alt-model/reference material
- **Special arts meter:** proven super-move economy to mirror against chimera design

---

## Next Steps

1. Extract the 7 stage PPKs → geometry (PS2 stage format RE)
2. Extract Paul/Law models + motion data; catalog weapon/prop models
3. Owner decision: Option A (BRAWL MODE) vs Option B (merged into Wrestling Mode)
