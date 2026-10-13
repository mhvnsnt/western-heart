# URBAN REIGN — Teardown for Western Heart

**Role in Chimera Build (owner 2026-10-12):** GAME #6 — street-brawl systems. *"It's kind of a hybrid of the wrestling, the WrestleMania XIX and No Mercy modes. And the Tekken modes."*
**Developer:** Namco (ex-Tekken / Soulcalibur team)
**Platform:** PlayStation 2 (2005)
**Last updated:** 2026-10-13 (teardown sweep)

---

## What's Extracted and Documented

### ISO — Download In Progress (ACTIVE LANE)
- `Urban Reign (USA).iso` — 4.14 GB, Internet Archive `urban-reign-usa_202608`
- Destination: `~/workspace/game-reverse-engineering/urban-reign/`
- **Status 2026-10-13 ~02:30 EDT:** ~260MB of 4.14GB received (~6%), slow connection (~0.3MB/s), ETA ~2–3 hours. **Lane `urban-reign-redownload` is actively running and heartbeating** — do NOT duplicate the download.
- NOTE: 4.14GB exceeds the browser file-grant upload size limit — TeraBox upload of this ISO will need a non-browser path.

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

- **ISO not landed yet** — file-structure mapping and stage extraction start when the download completes (active lane owns this; the sweep does not duplicate it).
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

1. Download lands → verify size (4,140,924,928 bytes) and checksum; map file structure
2. Extract stages (back alleys, bars, rooftops, Chinatown, junkyards) → chimera stage targets
3. Extract Paul/Law models + motion data; catalog weapon/prop models
4. Owner decision: Option A (BRAWL MODE) vs Option B (merged into Wrestling Mode)
5. Push this TEARDOWN.md + redownload-lane results into western-heart main (branch→PR→merge)
