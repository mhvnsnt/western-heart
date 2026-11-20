# MADE adaptation specs — priority fighters (2026-10-24)

**Status of this file: SPECS ONLY, no clips.** Only Pantera's 3 ADAPT moves
have built clips (see `docs/anim/MADE-PANTERA-2026-10-24.md`). Everything
below is a precise adaptation spec (source bank + transform + gap) for the
remaining priority fighters, so the next build pass can produce clips
without re-researching. Nothing below is presented as a built clip, and
nothing below is labelled decoded.

**Buttons use LP1/RP2/LK3/RK4 everywhere.**

## Status vocabulary

- **SPEC** — limb, direction/stance, damage and startup are all in the
  moveset file; the build is fully specified except for the wiring
  precondition in the Pantera doc (loader `made` tier). Source row is
  named where one is known, else "row TBD by hit-frame match" (the
  `fighter.js` match rule: same buttons, same limb, same level, nearest
  decoded hit frame to startup — in the fighter's OWN bank only, never
  another character's clips).
- **NEEDS-SPEC** — the move description lacks something the build needs
  (rig/prop, timing, or range). No motion was invented for it. The missing
  item is named; the move is skipped until it arrives.
- **BANK-BLOCKED** — the fighter has no decoded T3 bank of their own
  (checked against `game/assets/anim/t3/` and `fighter.js` `bankIdFor`),
  so an own-bank ADAPT cannot be built at all. Borrowing another
  character's clips is forbidden by the fighter.js own-bank rule, so
  these wait on a bank, not on a clip author.

## Community first-check (all fighters, 2026-10-24)

Checked at library level (no account sign-in, no download claimed):
Mixamo (free, 2,000+ clips, bipedal humanoids only, no extra limbs/props
per its own FAQ — so no four-arm, tongue, satchel, chainsaw, tail or
beast clip can come from it); Rokoko free martial-arts pack (6 generic
FBX clips, Mixamo skeleton, 30fps — generic strikes only); CMU mocap
and Bandai Namco free mocap (generic locomotion/dance/combat bases).
**Result: no community clip was found matching any priority BUILD move**
(chainsaw, hand-cannon, four-arm mudra, tongue, satchel, acid, beast
maul/bite, transform). Generic community strikes remain a fallback base
for ADAPT strikes only, behind the fighter's own T3 bank — they were
not used for Pantera because the own-bank rows were closer and already
in-repo. Bandai Namco's release licence is research/personal-use —
check commercial terms before shipping anything sourced from it.

## Cape Jones / Cyborg X — Alisa base, gunjack bank (2 BUILD, both SPEC with prop gaps)

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Motion Mandatory [WH SIGNATURE] | LP1+RP2 (`1+2`) | armR / 19 / 18f (0.30s) | BUILD | SPEC (prop gap): armR extension + recoil, timed to 0.30s startup, as the hand-cannon burst; cannon prop geometry + projectile VFX are not in the 22-bone rig and are not specified in the file — prop/VFX work must precede or accompany the clip. Timing-only construction from the gunjack bank's arm-extension pose is the timing reference only. |
| Lullaby Hum [WH SIGNATURE] | d+LP1+RP2 (`d+1+2`) | armL / 16 / 15f (0.25s) | BUILD | SPEC (prop gap): dodge into a humming chainsaw flurry, armL-led, 0.25s startup; chainsaw-arm prop + hum audio cue are unspecified — same prop/VFX precondition as above. |

## Chatur — True Ogre base, ogre bank (5 moves + 2 stance loops)

Chatur's file gives damage but **no startup/active/recovery** for any
special — timing must be authored with the animation, not copied from a
Tekken row (per the canon-moves file's own open question 3).

| Move | Input | Dmg | Method | Spec / gap |
|---|---|---|---|---|
| GYOU'S MARK | f,f+RP2 (`f,f+2`) | 22 | ADAPT | SPEC: ogre-bank dash strike row, row TBD by hit-frame match (same buttons/limb, nearest hit frame); add armor visual state (game-side, not a clip). Timing to be authored — no frames in file. |
| FOURFOLD MUDRA | LP1+RP2+LK3+RK4 (`1+2+3+4`) | 28 | BUILD | NEEDS-SPEC (rig): all four arms strike at once. The 22-bone bank rig has two arms. No four-arm clip can be built on this rig — needs a four-arm rig/model decision first. Also collides with the Nine-Soul Release input (same buttons at full meter) — resolver precedence must be confirmed before wiring. |
| OVERSOUL SURGE | qcf+RP2 (`qcf+2`) | 30 | BUILD | SPEC (VFX gap): palms-forward spirit blast, long range, heavy; arm-extension pose from the ogre bank is the timing reference only; projectile VFX + range are game-side and unspecified. |
| REFUSED TO DIE | d+LP1+RP2 (`d+1+2`) | 0 | BUILD | NEEDS-SPEC (timing): armored temple-dance comeback loop; no frames, no loop duration, no cooldown value in the file. Loop shape is described (rises through the hit) but its timing is not — do not invent it. |
| BRIDGE OF ARMS | b+LP1+RK4 (`b+1+4`) | 0 | BUILD | NEEDS-SPEC (timing + rig): four arms weave a bridge, auto-parry mids for "one beat", then riposte. "One beat" is not a frame count, and the rig lacks the extra arms. Idle-to-stance loop + riposte are two separate builds once timing + rig exist. |
| TEMPLE DANCE (stance) | LK3+RK4 (`3+4`) | — | BUILD (loop) | NEEDS-SPEC (timing + rig): four arms rest in mudra positions, swaying; no loop duration or sway amplitude in the file. |
| BRIDGE (stance) | LP1+RK4 (`1+4`) | — | BUILD (loop) | SPEC-adjacent: the parry-stance loop half of BRIDGE OF ARMS; shares its NEEDS-SPEC timing/rig gaps. Counted as the second stance loop, not a second strike. |

## Pond — Master Raven base, NO own T3 bank (5 moves)

Pond's file gives damage but no frames (same timing gap as Chatur).
`bankIdFor` returns no bank for Pond (no Raven bank in
`game/assets/anim/t3/`), so the game currently has only the procedural
fallback for her.

| Move | Input | Dmg | Method | Spec / gap |
|---|---|---|---|---|
| BOUNDARY CROSSING | f,f+LK3+RK4 (`f,f+3+4`) | 20 | ADAPT | BANK-BLOCKED: rushing armored shoulder; needs a Raven bank before an own-bank ADAPT exists. |
| EGG GUARD | b+LP1+RK4 (`b+1+4`) | 12 | ADAPT | BANK-BLOCKED: protective 360° whirl, then settle; same bank precondition. |
| MIST VEIL | qcb+LK3+RK4 (`qcb+3+4`) | 10 | ADAPT | BANK-BLOCKED (+VFX gap): mist burst + strike from inside it; mist VFX unspecified. |
| STILL WATER | d+LP1+RP2 (`d+1+2`) | 0 | BUILD | NEEDS-SPEC (timing): perfectly-still counter stance; no frames or counter-window duration in the file. Loop + riposte are separate builds once timing exists. |
| TONGUE LASH | f+LP1+RP2 (`f+1+2`) | 18 | BUILD | NEEDS-SPEC (rig + range): frog-tongue strike, "far more range than her arms", snaps back fast. No tongue rig/prop and no numeric range in the file. |

## Megami — Jun Kazama base, NO own T3 bank (4 moves)

Megami's file is `canon_layer: true`; her base source is a TTT2 wiki
movelist, not a teardown bank. No Jun bank exists in
`game/assets/anim/t3/`.

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Kaimon (Opening) | GEN LP1+RP2 (`GEN 1+2`) | armR / 24 / 26f | ADAPT | BANK-BLOCKED: from Threshold Keeper, wall splat. Needs a Jun bank (or an owner ruling on a bound bank) before an own-bank ADAPT exists. |
| Sealed Door | d/b+LP1+RP2 (`d/b+1+2`) | armR / 30 / 34f | ADAPT | BANK-BLOCKED: unblockable gate-slam, slow + telegraphed. Same precondition. |
| Seal of the Shrine (Rage Art) | RAGE, d/f+LP1+RP2 | armR / 55 / 20f | ADAPT | BANK-BLOCKED: sealed door opens, shrine's wrath steps through. Same precondition. |
| Threshold Keeper | b+LP1+RP2~b | armR / 0 / 18f | BUILD | SPEC: Genjitsu-entered-backwards guard stance loop; 18f entry is given, loop shape is the guard itself. Buildable as a stance loop once the loader `made` tier exists; still needs a bank for the base pose (see BANK-BLOCKED above for the strike half). |

## Menajerii — Roger Jr. base, bound bank kuma (4 moves)

`bankIdFor` binds Menajerii to the **kuma** bank (bear bank), not a
Roger bank — no Roger bank exists. ADAPT specs below therefore name the
kuma bank as the bound bank and flag the proxy status; they do NOT
claim Roger rows exist.

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Boar's Commit | f+RP2+LK3 (`f+2+3`) | armR / 34 / 24f | ADAPT | SPEC (proxy-bank flag): armored shoulder charge, power crush; adapt the kuma bank's shoulder-charge generic action, retimed to 24f startup. Owner to confirm the kuma binding is acceptable for a Roger-based fighter. |
| Heron Strike | HRN LP1 (`HRN 1`) | armR / 26 / 16f | BUILD | NEEDS-SPEC (prop): single precise beak-strike from Heron's Patience. No beak prop/rig in the file. |
| Heron's Patience | b+LP1+LK3 (`b+1+3`) | armR / 0 / 14f | BUILD | SPEC: parry stance loop (beats highs/mids, feeds the boar); 14f entry given; loop = still, upright heron guard. |
| Serpent's Economy | d/b+RP2+LK3 (`d/b+2+3`) | legL / 22 / 16f | ADAPT | SPEC (proxy-bank flag): low crush counter, minimal motion; adapt the kuma bank's low row TBD by hit-frame match, with motion *reduced* (the canon note is minimal motion — do not substitute a big low kick). |

## Ryusan — Lucky Chloe base, NO own T3 bank (6 moves)

No Chloe bank exists in `game/assets/anim/t3/`; `bankIdFor` returns no
bank for Ryusan.

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Vitriol Spit | qcf+LP1 (`qcf+1`) | armR / 18 / 20f | BUILD | SPEC (VFX gap): mid acid projectile, lingering chip on block; spit animation = head/arm throw + projectile VFX (game-side, unspecified). |
| Corrosion Claw | d/b+LK3+RK4 (`d/b+3+4`) | armL / 22 / 17f | BUILD | SPEC (VFX gap): low claw rake, acid-tipped fingers; leaves a sizzling floor mark for the round (floor-mark VFX unspecified). |
| Don't Tell Me To Calm Down | b+RP2+LK3 (`b+2+3`) | both / 25 / 25f | BUILD | SPEC (VFX gap): power-crush shoulder charge, armor through one hit, then acid burst; burst VFX unspecified. |
| Jotei's Receipt | hcb+LP1 (`hcb+1`) | both / 40 / 12f | ADAPT | BANK-BLOCKED: command grab, break LP1; needs a Chloe bank before an own-bank ADAPT exists. |
| Acid Rain Dance | SCT, b+LK3+RK4 | legR / 28 / 18f | BUILD | SPEC (VFX gap): from SCT dance stance, spinning kick flinging acid droplets in an arc; droplets are the hitbox (ducking the leg still burns) — droplet VFX + hitbox rule are game-side, unspecified in clip terms. |
| Meltdown | d+LP1+RP2 (`d+1+2`) | both / 45 / 33f | BUILD | SPEC (VFX gap): full-body acid eruption, costs a full Nine-Soul Meter; floor smokes for the rest of the round (smoke VFX unspecified). |

## Tobi — Hwoarang base, hwoarang bank (6 moves)

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Courier's Dash | f,F+RK4 (`f,F+4`) | legL / 16 / 12f | ADAPT | SPEC: blurring dash-kick; adapt the hwoarang bank's dash-kick row TBD by hit-frame match, retimed to 12f startup; blur = game-side speed effect, not a clip. |
| Longleap | WR+LK3 (`WR+3`) | legR / 24 / 15f | ADAPT | SPEC: full-sprint leaping kick covering half the arena; adapt the hwoarang bank's leaping-kick row TBD by hit-frame match; root_t forward travel must be authored to the half-arena distance (distance value itself is not numeric in the file — confirm arena-distance constant before baking root travel). |
| Escape Soul Flurry | qcf+LK3 (`qcf+3`) | legR / 32 / 17f | ADAPT | SPEC: five-kick flurry at courier speed; adapt hwoarang bank kick rows in sequence (same pattern as Pantera's Battle Itself repeat), retimed to 17f startup; 5 hits must be counted in the clip's hit-window entries, not assumed. |
| Satchel Swing | SS+LK3+RK4 (`SS+3+4`) | armL / 20 / 18f | BUILD | NEEDS-SPEC (prop): sidestep spinning swing of the weighted courier satchel; left hand never leaves the strap. No satchel prop/strap rig in the file. |
| Tip-Off | b+LP1+RP2 (`b+1+2`) | armL / 12 / 10f | BUILD | SPEC (prop gap): quick shoulder-barge, left hand stays on the satchel strap so the shoulder does the talking; body motion is buildable from a hwoarang-bank shoulder row, but the strap-hand constraint needs the satchel prop decision (see Satchel Swing). |
| The Undelivered Letter | d+LP1+RP2 (`d+1+2`) | both / 50 / 36f | BUILD | NEEDS-SPEC (prop + VFX): opens the satchel, the letter comes out swinging, then goes straight back in; costs a full Nine-Soul Meter. Letter prop + "hits like a truck" impact VFX are unspecified. |

## Doc Frank — Bosconovitch base, bank-map conflict flagged (7 moves)

Conflict, not resolved by guessing: `docfrank.json` names
`t3_source: bosconovitch` (and a bosconovitch bank exists), while
`fighter.js` MOVESET_MAP binds `docfrank` to `gunjack`. The specs below
name the **bosconovitch** bank as the base-character bank (per the
owner's stated rule that Doc Frank "should be Dr bosconovitch stance,
movements, animations"), and the wiring PR must resolve the map entry
first — building on gunjack rows for a Bosconovitch-based fighter
would violate the own-bank rule.

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| Rocket Punch | d,d/f,f+LP1 (`d,d/f,f+1`) | armR / 16 / 12f | ADAPT | SPEC (prop/VFX gap): detachable rocket punch, fist fires off and returns; adapt the bosconovitch bank's straight-punch row TBD by hit-frame match for the launch/recovery body motion; detached-fist travel + return are prop/VFX, not clip. |
| Afterimage | b,b+LK3+RK4 (`b,b+3+4`) | both / 0 / 6f | ADAPT | SPEC: afterimage dodge — vanishes, reappears behind the opponent; body motion = crouch-vanish + reappear pose from bosconovitch bank rows TBD; teleport + 0.3s invulnerability are game-side state, not clip. |
| Energy Absorption | b,b+LP1+RP2 (`b,b+1+2`) | both / 4 / 12f | BUILD | SPEC (VFX gap): grab that drains opponent meter into Doc's charge; grab body motion from bosconovitch bank grab row, drain effect VFX unspecified. |
| Eye Laser Beam | d,d/f,f+LP1+RP2 | head / 18 / 17f | BUILD | SPEC (VFX gap): full-screen eye-laser projectile; head-aim pose from bosconovitch bank is the timing reference only; beam VFX + full-screen range are game-side. |
| Ki Blast | d/f+LP1+RP2 (`d/f+1+2`) | armR / 14 / 12f | BUILD | SPEC (VFX gap): palm ki blast, mid-range energy shot; palm-extension pose is the timing reference only; blast VFX unspecified. |
| Crayon Notes | LP1+RK4 (`P+K`) | armR / 20 / 17f | BUILD | NEEDS-SPEC (prop): takes notes mid-fight on a clipboard, in crayon, "filed on you". No clipboard/crayon prop in the file. |
| Peer Review | LP1+RP2 (`S`) | armR / 19 / 19f | BUILD | SPEC (VFX gap): gadget blast, footnoted; arm-extension pose is the timing reference only; gadget + blast VFX unspecified. |

## Deathfang, werewolf form — Iori base, heihachi bank (13 moves)

The 5 `wh:deathfang-wolf:sig:*` mix-ins plus the 8 KOF addendum moves
(`kofxv:` refs in `deathfang-werewolf.json`, `deathfang_original: true`).
Damage values on the addendum moves look like per-hit placeholders in
the file — confirm before tuning (per the canon-moves file). The human-
form TRANSFORM (`wh:deathfang:sig:23`, LP1+RP2+LK3+RK4) is **not** in
this count: it is still an open question whether it is a made animation
or a model/state swap, and it shares its input with Nine-Soul Release.

| Move | Input | Limb / dmg / startup | Method | Spec / gap |
|---|---|---|---|---|
| MOONFANG LUNGE | f,f+RP2 (`f,f+2`) | armR / 20 / 20f | ADAPT | SPEC: lunging beast strike; adapt the heihachi bank's lunging-strike row TBD by hit-frame match; beast-claw hand shape is model-side. |
| CHAINBREAK RUSH | b,b+RP2 (`b,b+2`) | armL / 16 / 21f | ADAPT | SPEC: rushing claw strike; heihachi bank rush row TBD by hit-frame match. |
| FERAL MAUL | qcf+LK3 (`qcf+3`) | armL / 17 / 17f | BUILD | NEEDS-SPEC (rig): beast maul; no claw/beast-arm rig in the file. |
| GRAVE BITE | d/f+LP1+RP2 (`d/f+1+2`) | armR / 18 / 18f | BUILD | NEEDS-SPEC (rig): bite attack; no jaw/beast-head rig in the file. |
| RISING MOONCLAW | ws+LP1+RP2 (`ws+1+2`) | armR / 15 / 15f | BUILD | NEEDS-SPEC (rig): rising claw uppercut; no claw rig in the file. |
| WEREWOLF: CHAIN MAUL | qcf+LP1 (wolf) | armL / 4 / 14f | ADAPT | SPEC: chained-claw ground swipe, filed KOF motion 236+A (wolf); adapt a heihachi bank low swipe row TBD by hit-frame match; damage placeholder — confirm. |
| WEREWOLF: FERAL REND | qcb+LP1 (wolf) | armR / 4 / 16f | ADAPT | SPEC: three-claw rending rekka, filed 214+A (wolf); heihachi bank rekka-style rows TBD; damage placeholder — confirm. |
| WEREWOLF: MOONFANG LEAP | f,n,d,d/f+RP2 (wolf) | both / 5 / 8f | ADAPT | SPEC: leaping chained bite uppercut, filed 623+C (wolf); heihachi bank leaping-uppercut row TBD; damage placeholder — confirm. |
| WEREWOLF: GRIEF PILEDRIVER | hcb,f+LP1+RP2 (wolf) | both / 6 / 12f | ADAPT | SPEC: command grab driving the opponent down by the chains, break LP1+RP2, filed 632146+AC (wolf); heihachi bank throw row TBD; damage placeholder — confirm. |
| WEREWOLF: GRIEF BURST | qcb,hcf+LP1+RP2 (wolf) | both / 9 / 14f | ADAPT | SPEC: werewolf flame nova off the shackles, filed 214632146+AC (wolf); heihachi bank burst-pose row TBD + flame-nova VFX (game-side); damage placeholder — confirm. |
| WEREWOLF: SHACKLE LUNGE | f,f+LK3+RK4 (wolf) | both / 4 / 18f | ADAPT | SPEC: running shoulder lunge dragging broken chains, filed 66+B+D (wolf); heihachi bank shoulder-lunge row TBD; damage placeholder — confirm. |
| WEREWOLF: NO FUTURE SLASH | qcf,hcb+LP1+RP2 (wolf) | both / 12 / 10f | ADAPT | SPEC: climax eight-slash rush, NO FUTURE tattoo ignites, filed 23663214+A+C (wolf); heihachi bank slash-flurry rows in sequence (Pantera Battle Itself pattern); damage placeholder — confirm. |
| TRANSFORMED: SHACKLE HOWL | LP1+RP2+LK3+RK4 (wolf) | both / 0 / 30f | ADAPT | SPEC: power-up howl, meter gain while transformed, filed "Start (transformed)"; heihachi bank howl/roar pose row TBD; shares input with Nine-Soul Release — resolver precedence must be confirmed before wiring. |

## Counts (priority list only)

- **Clips built: 3** — all ADAPT, all Pantera (Honest Hold LP1+RK4,
  Tail-Tip Lunge f+LP1, Battle Itself LP1+RP2).
- **Specs written (no clip yet): 54** — Cape Jones 2, Chatur 7, Pond 5,
  Megami 4, Menajerii 4, Ryusan 6, Tobi 6, Doc Frank 7, Deathfang
  werewolf 13.
- **Of those 54: NEEDS-SPEC 13** (Chatur 4, Pond 2, Menajerii 1, Tobi 2,
  Doc Frank 1, Deathfang 3); **BANK-BLOCKED 7** (Pond 3, Megami 3,
  Ryusan 1); **remaining SPEC 34** (buildable once the loader `made`
  tier exists, plus their named prop/VFX gaps).
- **Systems NOT built as clips (per task):** KESSHOU, Nine-Soul Release,
  Reihou, Trial's Seal, Soul Surge — runtime systems, not clips. None
  appears in the tables above.
