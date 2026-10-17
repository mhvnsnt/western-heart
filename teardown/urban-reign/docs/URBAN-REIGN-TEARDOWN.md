# Urban Reign — Teardown

## Game #6 in Western Heart Chimera Build
- **Role:** Street-brawl systems — 4-player free-for-all, weapons, destructible
  environments, partner double-team combat
- **Developer:** Namco (ex-Tekken / Soulcalibur team)
- **Platform:** PlayStation 2 (2005)
- **ROM Status:** ⬇️ DOWNLOADING 2026-10-12 — `Urban Reign (USA).iso`
  (4.14 GB, Internet Archive `urban-reign-usa_202608`)
- **Local:** `~/workspace/game-reverse-engineering/urban-reign/`

## Why This Game (owner 2026-10-12)
Owner: "it's kind of a hybrid of the wrestling, the WrestleMania XIX and
No Mercy modes. And the Tekken modes." A Namco brawler built by the Tekken
team, with wrestling moves, weapons, and 4-player mayhem — the missing link
between Tekken Mode and Wrestling Mode.

## Known Features (from research)
- **60+ playable characters**, each with own fighting style (boxing, wrestling,
  karate, brawling, capoeira, kung fu); ~30 special moves + ~50 double-team
  attacks per character
- **Tekken guests:** Paul Phoenix and Marshall Law playable (Tekken 5-era models)
- **100-mission Story Mode** (Brad Hawk, brawler-for-hire, Green Harbor)
- **AI partner system:** double-team combo maneuvers — launch enemies into the
  air, partner catches and slams them
- **30+ weapons:** bats, pipes, bottles, shovels, 2x4s
- **Destructible environments:** back alleys, bars, rooftops, Chinatown,
  junkyards — furniture breaks, shelves shed boxes, cars/pinball machines shatter
- **Special arts meter:** builds on damage/dodges/hits; uncounterable super moves
- **Modes:** Story (100 missions), Free Mode, Challenge Mode (wave survival,
  solo or co-op), Versus (KO or points rules), **4-player Multiplayer**
  (multitap): head-to-head, team brawls, **Weapon Battle** (hold the weapon to
  win), **Destruction/Object Battle** (protect yours, smash theirs)

## Key Differences (for Western Heart design)
- NOT 1v1 (Tekken) and NOT ring-bound (wrestling) — free-roam arena brawling
- Weapons as core mechanic, not props
- Environment as weapon (walls, furniture, cars)
- Partner AI + double-team moves — no equivalent in the other five games
- Made by the Tekken team — animation DNA matches Tekken 7 models

## Chimera Design Question (owner to decide)
- **Option A — Third mode (BRAWL MODE):** Urban Reign systems stand alone as a
  third fighting mode alongside Tekken Mode and Wrestling Mode. 4-player
  free-for-alls, weapons, destructible arenas.
- **Option B — Merged into Wrestling Mode:** Urban Reign's street-brawl rules
  fold into the Wrestling Mode as its "hardcore/street fight" variant —
  weapons + no-ring + multi-man, alongside the No Mercy/WMXIX ring systems.

## TODO
- [ ] Finish ISO download + verify size
- [ ] Map PS2 disc file structure (ISO9660 listing)
- [ ] Identify character model format + animation format
- [ ] Document weapon system data layout
- [ ] Document arena/destructible-object data
- [ ] Extract Paul/Law guest models (compare to Tekken 7 versions)
- [ ] Owner decision: Option A (third mode) vs Option B (merged)
