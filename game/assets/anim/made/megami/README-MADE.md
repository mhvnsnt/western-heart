# Megami (Jun Kazama, TTT2 base) — MADE animation specs

**STATUS: MADE — NOT DECODED. Read this first.**

Every spec in this directory is **MADE**: authored from documented move
descriptions, never from a decoded Tekken clip. No file here may be
described, wired, or presented as decoded, extracted, or play-verified
Tekken animation. When Grok's TTT2 Jun extraction lands (GitHub issue
#866, comment 6390143525), these MADE specs are to be **replaced** by
decoded clips, not kept alongside them as if they were decoded.

- Fighter: Megami — Shrine Soul, temple guardian of a sealed door.
- Tekken base: Jun Kazama, **Tekken Tag Tournament 2 (TTT2)** — Jun is
  NOT in Tekken 7 (story ghost only), so no T7 pull can supply her.
- Buttons: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
  LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.
- Frame rate for all startup values quoted here: 60 fps, as given in
  the canon-moves file. Where a value is not documented, the spec says
  so — it does not invent one.

## Sources actually read (not invented)

- TTT2 Jun movelist, Tekken Wiki:
  https://tekken.fandom.com/wiki/Jun_Kazama/Tekken_Tag_Tournament_2_Movelist
  — gives move name, input, damage, hit range/level. It does **not**
  give startup frames. No startup value in the Jun-core file below
  comes from that page.
- Canon moves file: `canon-moves-needing-made-animations-2026-10-24.md`
  (Megami section) — gives the 4 canon moves' inputs, damage,
  startup, and canon descriptions. Those 4 startup values ARE quoted,
  because that file gives them.
- `game/assets/movesets/megami.json` (main) — tekken_base Jun Kazama
  (TTT2), canon_layer true. No decoded anim bank exists for Megami:
  `game/assets/anim/` on main contains only `t3/` and `oss/`.

## Community first-check (done 2026-10-24, no Jun match found)

- Mixamo (free library, Adobe account): generic punch/kick/idle
  categories exist, but no Jun-matched clip and no Jun string was
  verified, and no file was downloaded here. Generic ≠ Jun.
- CMU mocap database: Subject 135 (Martial Arts) is karate kata —
  Bassai, Empi, Front Kick, Gedanbarai, Heiansyodan, Mawashigeri,
  Syutouuke, Yokogeri — plus generic Subject 86 jumps/kicks/punches
  and Subject 2 punch/strike. Kata, not Kazama-style Jun strings;
  no shrine-guard, gate-slam, wall-splat throw, or Genjitsu/Izumo
  stance. Not used as a base.
- Rokoko free martial-arts pack: 6 free FBX clips (Mixamo skeleton,
  30 fps) + 263 free assets + 10 free fight/weapon clips. Move lists
  were not enumerated in the sources checked, so no match to any
  Megami/Jun move is claimed. Not used as a base.
- Bandai Namco Research free mocap (3,000+ BVH moves, fighting
  included): a style-transfer research dataset for research/personal
  use, with no per-move Jun index verified. Not used as a base.

Conclusion: no community clip was adopted. These specs are authored
pose/choreography specs, not retargets.

## What is in this directory

- `megami-canon-made.json` — the 4 canon moves, MADE. Startup values
  are the documented ones from the canon file. Recovery/total
  duration is NOT documented for these moves and is marked
  `timing_status: NEEDS-SPEC` where it is missing — an animator must
  set it; this spec does not guess it.
- `megami-jun-core-made.json` — 16 Jun-core MADE pose specs, built
  only from the TTT2 movelist's documented input / damage / hit
  level. Startup is NOT documented on that page and is marked
  `timing_status: NEEDS-SPEC` for every core move. Do not wire frame
  data from these specs; wire poses only, and replace with decoded
  TTT2 clips when they land.

## NEEDS-SPEC (flagged, not papered over)

- Jun stance / idle / guard pose: the TTT2 movelist page gives no
  guard description and no decoded clip exists. No guard pose is
  authored here. Needs either the TTT2 extraction or an owner
  eye-check of a proposed guard.
- Seal of the Shrine (Rage Art) hit count / hit sequence: canon note
  says "the sealed door opens and the shrine's wrath steps through"
  but gives no hit count. Spec gives opening + strike phases only.
- Recovery and total duration for all 4 canon moves and all 16 core
  moves: undocumented. Set from TTT2 extraction, not from this spec.
- Threshold Keeper hold-loop foot placement / facing detail: canon
  note says "Genjitsu entered backwards — she guards the threshold,
  never crosses it" but gives no footwork diagram. Animator to
  confirm with owner before wiring.

## NOT play-verified

Nothing here has been played in the live game. No claim of
play-verification is made. Verification requires the decoded TTT2
clips (issue #866, comment 6390143525) or an owner eye-check of
renders built from these specs.
