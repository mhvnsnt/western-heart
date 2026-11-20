# DOA / Virtua Fighter Moveset Conversion — 2026-10-19

Owner order 2026-10-19: DOA + Virtua Fighter movesets and fighters, all set up
to Tekken-style inputs and the game's fighting style.

## What shipped

6 new schema-v2 moveset files in `game/assets/movesets/`, wired into
`MOVESET_IDS` in `game/js/movesets.js` (85 moves total):

| File | Fighter | Source game | Moves |
|---|---|---|---|
| `doa-kasumi.json` | Kasumi (ninja striker) | DOA5 Last Round | 16 |
| `doa-bass.json` | Bass Armstrong (grappler) | DOA5LR / DOA Ultimate | 18 |
| `doa-hayabusa.json` | Ryu Hayabusa (ninja) | DOA5 Last Round | 14 |
| `vf-akira.json` | Akira Yuki (bajiquan) | VF5 Final Showdown | 17 |
| `vf-sarah.json` | Sarah Bryant (kickboxer) | VF5FS | 10 |
| `vf-kage.json` | Kage-Maru (ninja) | VF5FS | 10 |

These are MOVESET DATA files (usable via `getFighterMoveset` / the moveset
editor). They do not add roster fighters — roster canon is the owner's pick
(see "Fighter candidates" below).

## Federation input mapping (extends MOVESET-SCHEMA.md)

DOA → Tekken (per schema): `P`→`1`/`2`, `K`→`3`/`4`, `T`→`1+3`/`2+4`,
numpad→Tekken dirs (`6`→`f`, `236`→`qcf`, `63214`→`hcb`, `66`→`f,f` …).
Strings alternate limbs (`PPKKK` → `1,2,3,4,3`).

DOA holds (new — schema had no mapping): DOA's signature counter-hold system
maps to Tekken parry-style reversal chords, `move_class: "special"`:
- high hold (`8H`) → `u+1+2`
- mid punch hold (`4H`) → `b+1+2`
- mid kick hold (`6H`) → `f+1+2`
- low hold (`2H`) → `d/b+1+2`

The existing `TekkenBuffer.pressChord` resolves these — no input-system changes
needed. DOA directional throws (`6T`, `41236T`) → `f+1+3`, `hcf+1+3`
(the `parseSpecialInput` dir+chord path already handles these).

VF → Tekken: `P`→`1`/`2`, `K`→`3`/`4`, `P+K`→`1+2`, `P+G` (throw) → `1+3`,
`K+G` → `3+4`, numpad dirs as above. VF crouch-dash (`33`) → Tekken `d/f`.
VF sabaki/deflect (Akira's Gaimon Chouchu) → `hcb+1+2` special reversal.
VF guard (`G`) → the game's existing hold-block. Akira's just-frame Knee
(`K+G`, release G after 1f) → `3+4` special; the 1-frame timing is NOT modeled
in the WH input buffer — noted per move.

## Data sources + licenses

| Source | Used for | License |
|---|---|---|
| SuperCombo Wiki DOA5LR movelists (frame tables) | DOA frame-data format, Momiji 236 reference | CC-BY-SA |
| Team Ninja official DOA5LR patch notes (ver1.03–2.00) | Kasumi/Hayabusa/Bass real notations, 6T/63214T damage | Official (facts) |
| GameFAQs "Dead or Alive Ultimate" movelist (Jimbo) | Bass strike damage numbers (12/20/5/30/26/12) | Community FAQ (facts) |
| deadoralive.fandom.com command lists | Bass/Tina holds + throw names | CC-BY-SA |
| gamerevolution VF5 FAQ/walkthrough | Akira full VF5 movelist | Guide (facts) |
| VFDC Orange Book guide | Akira 6P = 14f, -6/+4 (real frame data) | Community (facts) |
| segaretro.org VF1 movelists | Sarah/Kage core movelists | CC-BY-SA |
| /vg/ VF writeup (pastebin) | Akira 66P/3P+K/46P/Knee properties | Community (facts) |

Documented but NOT pulled: none — all sources above are facts/community data,
no proprietary assets used. No game ROMs, no ripped animations.

## Honesty notes

- `proxy: false` on all six — this IS the source-game data, converted, not a
  stand-in bank.
- Frame data marked `note: "frame data estimated from archetype"` wherever the
  source didn't give real frames. Real frames used: Akira 6P (14f, VFDC),
  Kasumi 6T (60 = 50+10, TN ver2.00), Bass 63214T (62, TN v1.03),
  Bass strikes (GameFAQs damage).
- Damage: DOA5LR 270HP → WH 100HP (×0.37). VF5FS source-game HP was NOT
  verified in research — VF damage is archetype-scaled to WH 100HP and every
  VF move carries the note. Do not present VF damage as source-verified.
- `anim_ref` values (`doa:bass/palm-jab` …) are editor preview refs per the
  schema registry; no DOA/VF animation clips ship with this change.

## Fighter candidates (owner picks — NOT canon)

Converted and ready: Kasumi, Bass, Hayabusa (DOA); Akira, Sarah, Kage (VF).
Natural next wave per community prominence: Ayane, Tina, Jann Lee (DOA);
Jacky, Wolf, Pai, Lau (VF). Say the word and their movelists get converted
the same way.

## System gap audit — Tekken/DOA/VF standards vs WH (2026-10-19)

Present: Tekken 1/2/3/4 + chords + motion specials (`TekkenBuffer`),
throws (1+3/2+4, unblockable), strings, soul meter (rage-equivalent),
arena walls, block (hold), dodge/sidestep (Shift), hitstun/launch states.

| Gap | Standard | Priority |
|---|---|---|
| Tech roll / ukemi | Tekken/VF/DOC: ground recovery options | **P1** — oki game doesn't exist without it |
| DOA-style holds | NEW with this change (data) — needs fighter.js reversal resolution | **P1** — data ships, engine must honor the counter window |
| Wall game (wall splat / wall combos) | Tekken/VF: walls are a full subsystem | **P2** — walls are currently just bounds |
| Floor/wall breaks | Tekken 7/8 | P3 |
| VF-style sabaki resolution | NEW data (`hcb+1+2`) — needs engine parry frames | P2 (with holds) |
| Throw escapes | Tekken 1+3/2+4 escapes; VF 3-direction | P2 |
| Rage art / comeback mechanic | Tekken rage; DOA power blow | P3 (soul meter exists — extend it) |
| Ring-out | VF signature | P3 (arena-dependent) |
| DOA cliffhanger / danger zones | DOA | P4 |

Recommended build order: tech roll → hold/sabaki engine resolution →
throw escapes → wall splat → rage extension.
