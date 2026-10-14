# WESTERN HEART — Playable Web Build (v1)

A playable 3D fighting game in the browser: **PANTERA** vs **DEMONIO** in the
**SHRINE OF THE BLADE**. Forked from the `tk-fighting-game` engine template
(`assets/free-pull-1/tk-fighting-game/`), Western-Heart-ified end to end.

> WESTERN HEART — a lost multiverse bastard child. Familiar enough to pick
> up, strange enough to never put down.

## Run it

Any static file server works (ES modules need http, not `file://`):

```bash
cd game
python3 -m http.server 8080
# open http://localhost:8080
```

No build step. No CDN — Three.js and its addons are vendored in `game/vendor/`.
Works identically on GitHub Pages (serve the `game/` folder).

## The fighters

| Fighter | Style | Soul Surge | AI |
|---|---|---|---|
| **PANTERA** | Grappler (pro-wrestling chain-throw style). Purple tights, black pads/boots, red trim — per `prototype/fighters/pantera.json`. Power 1.3 / Defense 1.2. | **PANTHER'S WRATH** — purple/red panther aura burst | Aggressive, closes distance, hunts command grabs |
| **DEMONIO** | Mishima-style karate — precise, fundamental, the "honest" style (`ROSTER.md`: "The Demon Soul", Jin-style body donor). | **COLD FLAME** — cold blue-white flame burst | Balanced, fundamental spacing |

> Note: `ROSTER.md` gives Demonio no stats or colors, so this build assigns
> balanced-attacker numbers (speed 4.8 / power 1.05 / defense 1.0) and a cold
> blue-white palette derived from his "cold blue-white flame soul" Soul Surge.
> Tune in `game/js/characters.js` when canon lands.

Both fighters use REAL rigged models (Mixamo skeletons, no placeholders):
- **Pantera** (`game/assets/models/pantera.glb`, 7MB): the real P1 body —
  18 textured parts (purple tights, black pads/boots, red trim, jaguar mask)
  from `roster/pantera/tail-rig/pantera_body.glb`, rigged in Blender with
  manual region weights. Verified coherent in rest + animated poses.
- **Demonio** (`game/assets/models/demonio.glb`, 22MB): Tekken 7 Steve Fox
  FBX base (`teardown/models/tekken7/steve-fox-t7-fbx.zip`), same rig pipeline,
  reskinned cold blue-white via engine tint (0.6 strength). HONEST GAP: this
  is a Steve Fox body, not a Jin Kazama model. The T7 Jin MDL (Source engine)
  could not be converted — Blender Source Tools needs Windows Crowbar,
  SourceIO needs Python 3.11 (Blender 4.0.2 has 3.10), srctools Model is a stub.
  The Jin MDL pipeline is a known gap; Demonio plays as the Jin-based fighter
  on a Steve Fox body until a real Jin converts.
Mocap Idle/Walk/Run base layer + CCD inverse-kinematics combat layer — strikes
genuinely reach for the opponent. Standing separation rule respected: no
wrestler character models.

## Systems

- **Nine-Soul Meter** (0–100, 9 soul segments): land a light hit +8, heavy +11,
  take damage +6, block +4. All 9 souls lit = Soul Surge ready.
- **Soul Surge**: costs the full meter. 0.24s startup (punishable) / 0.20s
  active / 24 damage before defense scaling. Character aura burst + screen flash.
- **Command grab** (Pantera's bread and butter): unblockable at close range,
  launches the victim. Press **P+K together** (touch) or **J+K / U** (keyboard).
- Frame-data combat: startup/active/recovery, hitboxes vs hurtboxes, blocking
  with 12% chip + blockstun, i-frame dodges, knockback, launchers, hitstop,
  camera shake, impact particles, combo popups.
- Match flow: best of 3 rounds, 60s timer, round pips, animated HP bars,
  K.O. / DOUBLE K.O. / victory screens.

## Controls

| Action | Touch | Keyboard |
|---|---|---|
| Move | Left joystick | `A` / `D` or arrow keys |
| Jump | Joystick up | `W` / Up |
| Punch | `P` | `J` |
| Kick | `K` | `K` |
| Command grab | `P`+`K` together | `J`+`K` together or `U` |
| Soul Surge | `S` (full meter) | `L` |
| Block (hold) | `B` | `Space` |
| Dodge | `D` | `Shift` |

## The stage — SHRINE OF THE BLADE

Per `prototype/stages/shrine.json`: stone temple courtyard at dusk. Warm
directional setting-sun (`#ff9a5c`) over cool ambient (`#2a2a4a`), stone floor,
dark wood temple panels, glowing paper lanterns on posts (warm point lights),
tōrō stone lanterns at the arena edges, falling maple leaves, and a deep
indigo → ember orange gradient sky. Arena 16.8 wide.

## Audio

Fully procedural Web Audio: punch/kick/grab impacts, whooshes, Soul Surge
risers (Pantera's is a deep roar-rise, Demonio's a cold shimmer), blocks,
K.O. stinger, round bell, and a taiko-drums + breathy-flute battle loop.
Zero audio files.

## Performance

- Device pixel ratio capped at 2
- Low-poly procedural geometry, one shadow-casting light, instanced leaves
- Fixed 120Hz combat sim decoupled from rendering
- Audio + loop auto-pause when the tab hides

## Debug

Open with `?demo=1` for CPU-vs-CPU (AI plays both fighters) — handy for
unattended round-completion verification.

## Known gaps (v1)

- Demonio stats/colors are assigned, not canon (see note above).
- Grabs are single-hit launchers; the multi-stage chain-throw sequences from
  `prototype/combat/COMBAT-DESIGN.md` are not implemented yet.
- No crouch/low blocking yet (block covers everything while standing).
- No rematch character re-pick from the result screen (REMATCH replays the
  same pairing).
- Music is a procedural taiko loop; the sourced taiko + shakuhachi recordings
  in shrine.json are still TBD.
