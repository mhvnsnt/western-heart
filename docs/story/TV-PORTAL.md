# The TV Portal — how Cape Jones and Western Heart ("Immortal Qombat") connect

**Both canons:** Cape Jones is at home in his living room playing *Immortal Qombat* (= western-heart) on his CRT TV. The TV pulls him in; he flies into the game world through the screen. The show (`mhvnsnt/cape-jones`) wraps the game; the game contains Cape's house as a stage.

## The doors (each one is a file, both directions)
| Door | Show side (cape-jones) | Game side (western-heart) |
|---|---|---|
| Cast | `shared/cast/cast.json` (mirror, via `shared/cast/sync_cast.sh`) | `shared/cast/cast.json` (canonical, `build_cast.py`) |
| Place | living room / house / neighborhood (`3d-assets/`) | `stages/cape-house/STAGE-SPEC.md` |
| Motion | show anims retargeted onto WH rigs → render test ground | `anims/show/INDEX.json` (separate from fight moves) |
| Story | episodes use `CLIP-INDEX.json` scenes | cutscenes / pre-fight / heart-and-mind consume `anims/show/CLIP-INDEX.json` |
| Hook | episode beat: Cape plays → CRT glow → pulled in | story mode opener: scenes `portal_01..03` |

## Hook beats (scene ids in CLIP-INDEX.json)
1. `portal_01_couch` — Cape on the couch, controller, purple LED wash, laughing at the game.
2. `portal_02_pull_in` — CRT flicker (cape-jones `tools/crt-tv`), he stands up, gets pulled through.
3. `portal_03_arrival` — lands in a WH arena; first fighter (Pantera in the proof) greets → pre-fight.
4. `return_home` — fighters visit Cape's house in show episodes (cast member scenes).

Owner decision needed: which fighter greets Cape first, and whether Cape is playable in WH (a `cape-jones.glb` already exists in `game/assets/models/`, facing -Z).
