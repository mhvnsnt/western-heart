# Vain Abel Elias motion bank — precise gap (2026-10-23)

**Source priority: DOA4 teardown movelist FIRST
(`teardown/dead-or-alive-4/movesets/bass-armstrong/BASS-MOVELIST.md`,
triangulated DOA2/DOA5/DOA6, PR #218 in-repo copy — the file's
`doa_source`; curated in `game/assets/movesets/doa-bass.json`), DOA bank
(`game/data/moveset-library/banks/doa.json`, community movelist names)
second, T3 rows LAST (fallback only).** DOA4 ISO is on release per
teardown status — the extraction lane's target.

## Moveset status (done this pass — batch10-special-pull)

+8 documented DOA Bass moves pulled from `doa-bass.json` (52 → 60),
named to the file's "X (DOA Bass Y)" convention, `doa_move`/`doa_input`
/`anim_ref` kept:
`1,2` Double Palm (PP), `1,2,1` Combo Gong (PPP),
`1+2_doa` Hell Stab (P+K), `qcf+3` Drop Kick (236K),
`hcf+1+3` Fisherman's Buster (41236T),
`b+1+2` Arm Whip (4H mid-P hold),
`u/b+1+2_doa` Locking Hammer (8H high hold),
`d/b+1+2` Leg Split (2H low hold).
The DOA signature counter-holds (Arm Whip / Locking Hammer / Leg Split)
are documented as Tekken parry-style reversals per the source note.

Input collisions (documented in-file, keys disambiguated — nothing
overwritten): `1+2` taken by Front Facelock (DOA Bass H offensive hold);
`u/b+1+2` taken by Buffalo Rampage (DOA Bass 7P+K held).

**NOT pulled (precise):** doa-bass.json's "63214T — spinning throw" is
the same DOA input already in this file as "Powerbomb (DOA Bass
63214T)" — a documentation variance between the two DOA sources, not a
gap. Not double-added.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
60/60 moves stamped `"set": "FIGHT"`. No taunts in the file.

## The missing bank — FIGHT vs SHOW
- **FIGHT** — DOA4 ISO motion extraction (on release): stance/idle,
  the 60 moves' clips, holds, throws, block/hit/ko, locomotion →
  combat bank + moveset. The 60 moves already carry `doa:` anim_refs.
- **SHOW** — win pose / intro pose / taunts: no documented clips on
  disk — gap for the DOA4 extraction lane. Nothing stubbed.
