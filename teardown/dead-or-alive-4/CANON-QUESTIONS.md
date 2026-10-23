# DOA4 → Western Heart: Canon Questions for the Owner (2026-10-21)

No DOA4 fighter is registered in the Western Heart roster by this
lane. Canon assignment is an owner decision that has not been made.
Everything DOA4 is staged under `teardown/dead-or-alive-4/` only
(see `phase7/WIRING-INVENTORY.md`). These are the exact decisions
needed before any DOA4 content can go live in `game/`, framed the
way SCII's canon conversion was framed: what enters, as whom, in
which slot, with what name.

## Q1 — Entry mode: guests or canon-mapped?

Do DOA4 fighters enter Western Heart as:

- (a) **Guest fighters** — themselves, under their own names, in
  guest slots (the SCII guest precedent), or
- (b) **Canon-mapped reskins** — DOA4 models/moves mapped onto
  existing Western Heart canon characters as attires, or
- (c) **New canon characters** — DOA4 fighters converted into
  original Western Heart characters (renamed per RENAME-MAP rules,
  bios written by the owner)?

## Q2 — Which fighters?

DOA4's roster is ~23 fighters plus Alpha-152. Packages on disk are
NOT yet identified per character (148 chr packages are indexed by
container + number only; identification is a content pass that has
not been run — see the wiring inventory). Before identification
work is aimed, the owner needs to say which DOA4 fighters he wants
at all: all of them, a shortlist, or none until identification is
done.

## Q3 — Names and rename log

For any fighter entering under (b) or (c): what is the Western
Heart name? Every proprietary name that is changed must be logged
in the repo RENAME-MAP — the lane will not invent names.

## Q4 — Movesets

Six fighters have core move lists staged (16–26 moves). Does the
owner want (a) DOA4-native move lists as-is (DOA inputs translated
to the game's Tekken-style input scheme), (b) moves remapped onto
existing Western Heart movesets, or (c) full DOA4 lists completed
first (100+/fighter per the full-moveset law — a large data pass
that has not been run)?

## Q5 — Stages

stg.afs holds 27 stage packages (parsed, not batched to GLB). Do
DOA4 stages enter the game's stage list, and under the same
guest/canon treatment as Q1?

## Q6 — Order of work once decided

After Q1–Q5, the remaining technical gates are: package→character
identification, texture binding beyond pkg00, and animation clips
(anm index format). Which of these should the next lane take
first — playable-static fighters (models + movesets, no DOA4
animations) or animation decode first?
