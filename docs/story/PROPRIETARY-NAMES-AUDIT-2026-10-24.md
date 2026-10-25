# Proprietary Names Audit (Lane 6, 2026-10-24)

User directive (2026-10-24 19:29 CDT, still open at audit time):
audit CANON.md, SOUL-SYSTEMS.md, `docs/decisions/`,
`docs/research/`, MEMORY.md for proprietary names for the
systems below. Rule for this audit: a name counts as NAMED
only if a source says the owner locked/approved it (or canon
itself names it). A PROPOSAL is not a lock. Where no name
exists, the row says NEEDS NAME and offers OPTIONS — the
owner picks; this audit never decides a canon name itself.
Tekken names stay in technical files only, never in CANON.md
bios or in-universe writing. Game ships with NO famous names.

Audit scope actually searched (2026-10-24): `CANON.md`,
`docs/design/SOUL-SYSTEMS.md`, `docs/owner-directives.md`,
`docs/research/SOUL-URGE-SYSTEM.md`,
`docs/research/SOUL-GAUGE-MAPPING.md`,
`docs/research/FINISHER-DESIGN-2026-10-23.md`,
`docs/research/REALM-TRAVEL-CANON-2026-10-23.md`,
`game/js/rage.js`, `game/js/soulurge.js`,
`game/js/soul-systems.js`, `game/js/finisher.js`,
`game/js/stagebreaks.js`, `game/js/tag-relay.js`,
`game/js/v-system.js`, `game/js/spirit-actions.js`,
`game/js/soul-kindle.js`, `game/js/fighter.js`,
`game/js/movesets.js`, `game/js/game.js`, `game/assets/movesets/pantera.json`
(sample), `~/MEMORY.md`. Line numbers below are from those
files on main at audit time. Full-repo grep (moveset JSONs,
all docs) was NOT completed: the fresh clone was still
fetching at report time — see Gaps. Terms reported as "not
found" are "not found in the searched files", not a
whole-repo proof.

## Owner decisions — 2026-10-24 21:38 CDT (status update; no new names invented, no code changed)

Recorded exactly from the owner's 2026-10-24 21:38 CDT message.
This section changes STATUS labels only. It does not rename any
code tag, HUD string, or doc string, and it does not implement
any mechanic. Until the owner picks a replacement name, code
keeps the old strings, and no banner text shows for the
RENAME-PENDING items (the popup fix already removed the
banners). When the owner picks names, they get wired everywhere
the Tekken names appear (code tags, HUD, docs) — until then,
nothing is renamed.

### Updated status table

| Item | Status (2026-10-24 21:38 CDT) | Note |
|---|---|---|
| Wall Break | KEEP | Stays as-is in code/docs/UI. No longer a needs-name item. Owner: "they can still be called the same stuff". |
| Floor Break | KEEP | Same as Wall Break. |
| Balcony Break | KEEP | Same as Wall Break. |
| Rage Art | LOCKED 2026-10-24 21:51 CDT | Renamed to Ikari Jishin (怒り自身, "Rage Itself" in Japanese) — the super / Rage Art equivalent, the cinematic comeback unleashed FROM the Rinne state. See the 2026-10-24 21:51 CDT section below. Supersedes the RENAME-PENDING label from 21:38 CDT. |
| Rage Drive | RENAME-PENDING | Same as Rage Art. |
| Power Crush | RENAME-PENDING | Same as Rage Art. The audit's implementation question (is armored-attack behaviour present generically?) is unchanged by this message. |
| V-System | RENAME-PENDING | Umbrella decided to change; member names are NOT yet picked (see still-open list). |
| Break mechanics + guard-breaking mechanics | SHARED-NAME-PENDING | ONE term covers both, not two separate names. Owner: "can be called the same thing". The term itself is NOT yet picked. |
| Rage (low-HP state itself) | LOCKED 2026-10-24 21:46 CDT | Short name Rinne (輪廻); full name Rinne Tensei (輪廻転生); Tensei (転生) also acceptable as a short form. See the 2026-10-24 21:46 CDT section below. Supersedes the OPEN/UNDECIDED label from 21:38 CDT. |
| Screw | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN | T7 spinning-knockdown extender. WH on main has NEITHER Screw nor Tornado and uses T6 Bound instead of Screw. A WH name is needed only when/if the mechanic is implemented. |
| Tailspin | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN | T8's rename of Screw. Not a separate WH item to name unless/until implemented. |
| Tornado | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN | T8's spinning-air extender. Missing per gap analysis. This explanation supersedes this audit's earlier shorthand that called Tornado "T8's rename of Screw" — Tailspin is the T8 rename of Screw. |

### Nuance preserved, not contradicted

- PR #1060 (combat, unmerged, HELD until the popup play pass)
  implements Screw/Tornado on its branch. The names question
  reopens if/when #1060 lands. This PR pre-invents NO names
  for it and does NOT claim the mechanic is on main.
- NOTHING here blocks the #1076 popup deploy. Banners are
  already gone regardless of naming, and this naming PR is
  docs-only.

### LOCKED names — unchanged, restated, never re-opened by this PR

- Heat → SOUL URGE. Finisher system → KESSHOU 結章.
  Full-meter super → Nine-Soul Release 九魂解放 (Climax
  variance noted below, not resolved here). Spirit Release
  (foe in RAGE) → Reihou 霊放. Round-end verdict seal →
  Trial's Seal 試練の封. Urge context finisher → 魂 ACTION /
  Spirit Action. Fight lab → GUNGAKU 軍楽. Chess Kombat
  remake → Go Qombat.

### Still open — preserved, NOT dropped by this message

- Bound; Slow-mo finish; WWE entrance-tool repurpose;
  V-System members V-Skill / V-Trigger / V-Reversal / V-Shift
  (including V-Skill/parry); Urge Smash (carried forward as
  an open item per the 2026-10-24 21:38 tasking — the audit
  had listed Urge Smash inside the locked SOUL URGE family,
  and this PR does not resolve that tension; owner to
  confirm); proposed names awaiting owner pick — Soul Kindle
  for Ki Charge, Soul Relay for Tag; the Nine-Soul Climax vs
  Release variance (MEMORY + FINISHER-DESIGN "SOUL CLIMAX
  READY" vs implemented Release "SOUL RELEASE READY" —
  owner to confirm); the 魂 ACTION chord question (RP2+LK3,
  i.e. Right Punch + Left Kick, Tekken 2+3, vs 2+3+context —
  owner/combat lane to confirm).

## Owner decisions — 2026-10-24 21:46 CDT (Rinne lock; docs only, NO wiring yet)

Recorded exactly from the owner's 2026-10-24 21:46 CDT
message. This section changes STATUS labels only. It does
not rename any code tag, HUD string, or doc string, does
not implement any mechanic, and does not wire Rinne into
the game. Wiring is HELD until the naming lane confirms
the code touchpoints listed at the end of this section.
When wired, Rinne appears ONLY as a small HUD tag/gauge
(full form Rinne Tensei where space allows) — NEVER as a
big mid-fight banner. The popup law still applies.

### Locked

- Rage state (low HP, pre-death/reincarnation flare) is
  now LOCKED: short name Rinne (輪廻); full name Rinne
  Tensei (輪廻転生); Tensei (転生) also acceptable as a
  short form. The Rage state moves from NEEDS NAME /
  OPEN/UNDECIDED to LOCKED. Pronunciation note (voice
  dictation only): the user pronounces it "Rene" — the
  correct romanization is Rinne. Use Rinne in all text;
  never use "Rene" as the name.

### Reserved concept — future form, mechanic NOT designed, NOT wired

- Amatsu Rinne (天津輪廻) = the extra-powerful /
  leveled-up / transformed form of Rinne. RESERVED
  CONCEPT ONLY. The mechanic is NOT designed yet ("we'll
  try and figure out how to incorporate"). Do NOT
  implement or wire it as a current system. It is recorded
  here as a future form in this names doc ONLY. Amatsu
  Rinne is NOT the Rage state name.

### Banked name — reserved only, assigned to NOTHING

- Ikari Jishin (怒り自身, "Rage Itself" in Japanese) =
  BANKED for another thing. It is NOT the Rage state, and
  it is NOT assigned to any system yet. Reserved name
  only. Do NOT assign it to Rage Art, Rage Drive, Power
  Crush, V-System, or anything else without explicit user
  direction. Unassigned possibilities ONLY (never
  assignments): it COULD be Rage Art, Rage Drive, Power
  Crush, V-System, or something else — the user has not
  said. This RESOLVES the tension flagged in PR #1085:
  Ikari Jishin appearing both as a Japanese "Rage Itself"
  candidate and as a Rage-state option. It now names
  nothing yet.
- STATUS UPDATE 2026-10-24 21:51 CDT: this banked status
  is SUPERSEDED — Ikari Jishin is now LOCKED as the super
  / Rage Art equivalent (see the 21:51 CDT section below).
  It is no longer a banked name assigned to nothing, and
  it is still NOT the Rage state (Rinne owns that).
- Consequence for the 21:40–21:42 CDT options list below:
  Rinne / Rinne Tensei / Tensei are no longer options —
  they are the lock. Amatsu Rinne and Ikari Jishin are no
  longer Rage-state options either — Amatsu Rinne is the
  reserved future form, Ikari Jishin is the banked name
  (as of 21:46 CDT; superseded 21:51 CDT — see the
  STATUS UPDATE note above).
  The options list below is kept as history of what was
  proposed 21:40–21:42 CDT; it no longer describes a live
  pick.

### Still proposed, NOT locked

- Spin Juggle (descriptive name for Screw / Tailspin /
  Tornado) remains PROPOSED, not locked. The user reacted
  👍 to the message containing it but has NOT explicitly
  confirmed it. A 👍 reaction is NOT confirmation. Keep it
  in OPTIONS-PENDING until the user says so explicitly.
  Do NOT record it as locked; do NOT rename code/HUD/docs
  strings to it.

### Unchanged by this message

- KEEP (2026-10-24 21:38 CDT): Wall Break, Floor Break,
  Balcony Break — unchanged.
- RENAME-PENDING (2026-10-24 21:38 CDT): Rage Art, Rage
  Drive, Power Crush, V-System — unchanged; new names
  still NOT picked, options still owed to the user.
- SHARED-NAME-PENDING (2026-10-24 21:38 CDT): break
  mechanics + guard-breaking mechanics, one term — still
  NOT picked.
- All other still-open items from PR #1085 are preserved,
  NOT dropped: Bound; Slow-mo finish; WWE entrance-tool
  repurpose; V-System members V-Skill / V-Trigger /
  V-Reversal / V-Shift (including V-Skill/parry); Urge
  Smash tension (still open — this task does NOT resolve
  it; owner to confirm); proposed Soul Kindle for Ki
  Charge and Soul Relay for Tag; Nine-Soul Climax vs
  Release variance; 魂 ACTION chord question (RP2+LK3,
  i.e. Right Punch + Left Kick, Tekken 2+3, vs
  2+3+context).
- NOTHING here blocks the #1076 popup deploy — and at the
  time of this commit #1076 has in fact merged to main
  (merge 0f19b91e9f27b27ed5c20955dfc31c2bdb5a92c0), so
  this docs PR sequences AFTER it. This PR is docs-only,
  and banners are already gone regardless of naming.

### Code touchpoints LISTED for future wiring — NOT changed in this PR

The following sites were found by searching main; they are
listed here so the wiring lane can confirm them. NO file
below was edited in this PR, and no string below was
renamed to Rinne in this PR:

- `game/js/rage.js` (checked on current main after the #1076 merge) — Rage header and comments, `RAGE_THRESHOLD = 0.25`, `isRaging` check, `RageSystem` per-match director, `ui.setRage` calls. The old `ui.banner('RAGE')` call site is GONE on current main (removed by the #1076 popup deploy): `update()` now applies the rage aura + health-bar tag only, with the comment "No center-screen text — Tekken shows rage via red aura + red lifebar only". Any future Rinne HUD tag uses this small tag/gauge path only; it must NOT become a big mid-fight banner.
- `game/js/main.js` — UI `setRage(id, on)` (the HUD tag/gauge hook; toggles the `${id}-rage` health-bar element class `on`, i.e. `p1-rage` / `p2-rage`).
- `game/js/fighter.js` — `_rageOn` state flag and `setRageAura(on)` (the aura hook).
- `game/js/soul-systems.js` — Reihou: `canReihou` checks the foe's `_rageOn`, and firing purges the foe's rage for the round (`_rageUsed`).
- `docs/design/SOUL-SYSTEMS.md` — the RAGE row and the "Reihou is the counter to rage" sentence (to be reworded to Rinne when wired, not now).
- This audit doc itself — the Rage (state) rows and the Options section above (updated in this PR only as status labels, not as code wiring).
- NOT a state touchpoint: the synthesized `RAGE ART` / `RAGE DRIVE` move names in `game/js/rage.js` belong to the still-RENAME-PENDING Rage Art / Rage Drive items, not to the Rinne state lock. Wiring the Rinne state tag does NOT rename them.

## Owner decisions — 2026-10-24 21:51 CDT (Ikari Jishin lock; docs only, NO wiring yet)

Recorded exactly from the owner's 2026-10-24 21:49–21:51 CDT
messages. This section changes STATUS labels only. It does
not rename any code tag, HUD string, or doc string, does
not implement any mechanic, and does not wire Ikari Jishin
into the game. Wiring is a FOLLOW-UP step, not this PR.
When wired, the super's cinematic beats / HUD indicators
carry the name — NEVER a big mid-fight banner for the name
itself (popup law still applies: the super's cinematic is
not banner text).

### Locked — the super

- Ikari Jishin (怒り自身, "Rage Itself" in Japanese) is now
  LOCKED as the super, i.e. the Rage Art equivalent: the
  cinematic comeback move unleashed FROM the Rinne state.
  Rage Art moves from RENAME-PENDING (2026-10-24 21:38 CDT)
  to LOCKED (renamed to Ikari Jishin).
- System structure, stated explicitly: Rinne (state, low HP)
  → Ikari Jishin (super, used from Rinne). Rinne is the
  state; Ikari Jishin is the move used from that state —
  the same shape as Tekken, where Art/Drive require Rage.
- History of this pick, kept straight: at 21:49 CDT the user
  self-corrected mid-message — Ikari Jishin "can be the
  rage state... hold on, no, it's something else" — and
  CONFIRMED it is NOT the rage state, then asked "so what
  are we going to make the Ikari Jishin?" The options
  delivered at 21:49 CDT were: (1) RECOMMENDED — the super
  / Rage Art equivalent (the cinematic comeback unleashed
  FROM Rinne; "Rage Itself" = the ultimate expression of
  rage); (2) the drive move / Rage Drive equivalent
  (powered-up move from Rinne, weaker fit); (3) NOT a
  transformation — Amatsu Rinne already owns the
  leveled-up/transformed-form-of-Rinne slot, so Ikari
  Jishin as a transformation would collide. At 21:51 CDT
  the user PICKED option (1) by widget. This lock is a
  USER PICK, not a lane recommendation recorded as an
  assignment — the 21:49 recommendation is now the user's
  assignment. Options (2) and (3) are rejected / ruled
  out by this pick, not live alternatives.

### Superseded banked status — history, not a current item

- Ikari Jishin's 21:46 CDT BANKED status (reserved name
  only, assigned to nothing) is SUPERSEDED by this
  assignment. Record it as superseded history, NOT as a
  current banked item. There is no longer a banked Ikari
  Jishin waiting for an assignment — it has one.
- What this does NOT change: Ikari Jishin is still NOT
  the Rage state. Rinne (輪廻) / Rinne Tensei (輪廻転生)
  owns the Rage state, locked 21:46 CDT.

### No collision with Amatsu Rinne

- Amatsu Rinne (天津輪廻) remains the RESERVED future
  form of Rinne — extra-powerful / leveled-up /
  transformed form, mechanic NOT designed, NOT wired.
  It is NOT the super, and Ikari Jishin does NOT take a
  transformation slot: the 21:49 CDT collision note stands
  (Amatsu Rinne already owns that slot), and this pick
  avoids it by assigning Ikari Jishin to the super instead.

### Still rename-pending after this lock

- Rage Drive, Power Crush, V-System — still
  RENAME-PENDING (2026-10-24 21:38 CDT); new names still
  NOT picked, options still owed to the user.
- Shared break/guard-break name — still
  SHARED-NAME-PENDING (one term, not picked).
- Spin Juggle (descriptive name for Screw / Tailspin /
  Tornado) — still PROPOSED, not locked. A 👍 reaction is
  NOT confirmation; this lock does not confirm it.
- All other still-open items from PR #1085 are preserved,
  NOT dropped: Bound; Slow-mo finish; WWE entrance-tool
  repurpose; V-System members V-Skill / V-Trigger /
  V-Reversal / V-Shift (including V-Skill/parry); Urge
  Smash tension (still open — this task does NOT resolve
  it; owner to confirm); proposed Soul Kindle for Ki
  Charge and Soul Relay for Tag; Nine-Soul Climax vs
  Release variance; 魂 ACTION chord question (RP2+LK3,
  i.e. Right Punch + Left Kick, Tekken 2+3, vs
  2+3+context).
- Screw / Tailspin / Tornado entries are left UNTOUCHED
  by this update: their EXPLAINED-NOT-NAMED /
  MECHANIC-NOT-ON-MAIN labels are the subject of a
  separate drift-correction lane (main has since merged
  Lane 1 combat PR #1060 wiring Screw/Tornado, so those
  labels are stale), and that lane's correction — if it
  lands on this branch — is preserved verbatim, not
  duplicated here. If it has not landed, the correction
  is still owed and is flagged, not taken over, here.
- NOTHING here blocks the #1076 popup deploy — #1076 has
  merged to main, this docs PR sequences AFTER it, and
  naming changes nothing about banners (already gone).

### Code touchpoints LISTED for future Ikari wiring — NOT changed in this PR

The following sites were found by searching current main
(head dc3039918b22d3e685bfe20ba0356714fbe4034f, at the
time of this commit); they are listed here so the wiring
lane can confirm them. NO file below was edited in this
PR, and no string below was renamed to Ikari Jishin in
this PR. The synthesized `RAGE ART` names that the 21:46
CDT section noted as belonging to the then-RENAME-PENDING
Rage Art item are NOW the Ikari touchpoints:

- `game/js/rage.js` (verified on current main) — header
  L7: "RAGE ART: cinematic armored super. Input 1+2 while
  raging" (LP1+RP2, i.e. Left Punch + Right Punch, Tekken
  1+2); L59 `ensureRageMoves` synthesizes + registers
  R.1+2 (rage art) and RD.3+4 (rage drive) per fighter
  from their own real T3 strike data; L79 the synthesized
  move name `${...} — RAGE ART` with `rageArt: true` (L85)
  and `RAGE_ART_DAMAGE = 32` (L28, notation `R.1+2` L30);
  L183–190 `rageArtHit` — the cinematic beat (hitstop +
  flash + brief slow-mo) calling `ui.rageArtFlash()`.
  When wired, these `RAGE ART` strings / the `rageArt`
  flag / the `rageArtHit` beat become Ikari Jishin; the
  Rage Drive strings in the same file (`RAGE DRIVE`,
  `rageDrive`) do NOT — Rage Drive is still
  rename-pending.
- `game/js/main.js` (verified on current main) — UI
  `rageArtFlash()` (L190, toggling the `#rage-flash`
  element): the flash-indicator hook for the super's
  cinematic beat. This is a flash/HUD indicator, not
  banner text, and wiring must keep it that way.
- `game/js/fighter.js` (verified on current main) — L285
  `rageArt: !!mv.rageArt` flag passthrough, and L1742
  comment "unblockables and Rage Arts break it".
- `docs/design/SOUL-SYSTEMS.md` (verified on current
  main) — L15 "a purged fighter cannot re-enter rage
  that round (no Rage Art)" and L17 "Release 30 dmg ≈
  a T7 Rage Art at WH scale (rage.js 32)": both sentences
  to be reworded to Ikari Jishin when wired, not now.
- This audit doc itself — the Rage Art rows and the
  Options section (updated in this PR only as status
  labels, not as code wiring).
- NOT an Ikari touchpoint: the Rinne state sites listed
  in the 21:46 CDT section (`RAGE_THRESHOLD`, `isRaging`,
  `RageSystem`, `ui.setRage`, `_rageOn`, `setRageAura`)
  belong to the Rinne state lock, not to the super.
  Wiring Ikari Jishin does NOT rename them, and wiring
  Rinne did NOT rename the super strings.

## Options pending — user 2026-10-24 21:40–21:42 CDT (ALL PROPOSED, NONE DECIDED)

This section is SEPARATE from the 2026-10-24 21:38 CDT
decisions above. Nothing here is decided, wired, or renamed.
Every item carries "user pick pending". Do NOT present any
option below as a final name, and do NOT rename code, HUD,
or doc strings to any of them.

SUPERSESSION NOTE 2026-10-24 21:46 CDT: the Rage-state
options below are SUPERSEDED as a live pick — see the
2026-10-24 21:46 CDT section above. Rinne / Rinne Tensei /
Tensei are now the LOCKED Rage state name; Amatsu Rinne is
the reserved future form; Ikari Jishin was banked 21:46 CDT
and names nothing yet AS OF THAT SECTION — SUPERSEDED
2026-10-24 21:51 CDT (see 21:51 CDT section): Ikari Jishin
is now LOCKED as the super / Rage Art equivalent. It is
still NOT the Rage state name. The Spin Juggle proposal
below is NOT superseded — it remains PROPOSED, not
locked.

### Rage state (low HP) — direction + options (user pick pending)

- Direction asked: what would Tong-Nou's world call it —
  tied to the game's reincarnation function (right before
  dying → reincarnation), divine + heavenly + Japanese
  sounding.
- The user LIKES "Rage Itself" as a term, but it must
  CONNECT to one of the other systems (not stand alone).
  Proposed connection (NOT decided): "Rage Itself" = the
  state; Rage Art/Drive equivalents are techniques used
  FROM that state (as in Tekken, where Art/Drive require
  Rage).
- "Rage Itself" IN JAPANESE is a candidate for one of the
  renamed systems (literal: 怒りそのもの ikari sono mono;
  tighter game term: 怒り自身 ikari jishin). Recorded here
  as delivered; which system (if any) it names is NOT
  decided — note Ikari Jishin also appears in the five
  options below, and the owner pick will clarify.
- Options delivered 2026-10-24 21:42 CDT — USER PICK
  PENDING on each, verbatim:
  1. Rinne (輪廻) — user pick pending 21:40–21:42 CDT; LOCKED 2026-10-24 21:46 CDT (see 21:46 CDT section).
  2. Rinne Tensei (輪廻転生) — user pick pending 21:40–21:42 CDT; LOCKED 2026-10-24 21:46 CDT as the full name.
  3. Tensei (転生) — user pick pending 21:40–21:42 CDT; LOCKED 2026-10-24 21:46 CDT as an acceptable short form.
  4. Amatsu Rinne (天津輪廻, constructed compound from real
     words, not a set phrase) — user pick pending 21:40–21:42 CDT; RESERVED FUTURE FORM 2026-10-24 21:46 CDT, mechanic not designed, NOT the Rage state name.
  5. Ikari Jishin (怒り自身) — user pick pending 21:40–21:42 CDT; BANKED 2026-10-24 21:46 CDT, reserved name only, assigned to NOTHING; LOCKED 2026-10-24 21:51 CDT as the super / Rage Art equivalent (see 21:51 CDT section) — banked status SUPERSEDED, not current.
- Status effect (updated 2026-10-24 21:46 CDT): the Rage
  state is no longer OPEN/UNDECIDED — it is LOCKED as
  Rinne / Rinne Tensei (Tensei acceptable short form).
  The list above is now history of the 21:40–21:42 CDT
  proposals, not a live pick. Do NOT present Amatsu Rinne
  or Ikari Jishin as the Rage state name.

### Juggle spin (Screw / Tailspin / Tornado) — descriptive proposal (user pick pending)

- The user barely knows these from Tekken's
  titles/descriptions and wants a DESCRIPTIVE name where
  you know what it is from the name.
- Proposed (NOT decided): "Spin Juggle" — one mechanic
  covering all three (Screw = ground-spin form, Tailspin =
  T8's word for Screw, Tornado = air-spin form).
- Status effect: NONE. Do NOT present "Spin Juggle" as the
  juggle name, do NOT rename code/HUD/docs strings to it,
  do NOT implement Screw/Tornado on this message. The
  2026-10-24 21:38 CDT EXPLAINED-NOT-NAMED /
  MECHANIC-NOT-ON-MAIN status and the PR #1060 nuance
  above stand unchanged.

## Summary table

| System (Tekken name) | WH name | Status |
|---|---|---|
| Heat (T8) | SOUL URGE (+ Urge Burst / Smash / Dash / Engager, Urge gauge, Urge pip) | LOCKED 2026-10-22 |
| Finisher system | KESSHOU 結章 "the Closing Chapter" | LOCKED 2026-10-23 |
| Full-meter super | Nine-Soul Release 九魂解放 | LOCKED 2026-10-23 (but see Climax variance below) |
| Spirit Release (foe in RAGE) | Reihou 霊放 | LOCKED 2026-10-23 |
| Round-end verdict seal | Trial's Seal 試練の封 | LOCKED 2026-10-23 |
| Full-meter channel of another soul | Soul Surge | CANON-NAMED (name is canon's own) |
| Context finisher (URGE on + context) | 魂 ACTION | NAMED 2026-10-23 |
| Chess Kombat remake (Go-based) | Go Qombat | NAMED 2026-10-23, implementation not found in `game/js` |
| Fight-lab dummy mode (TTT2 Combot equiv.) | Gungaku 軍楽 | LOCKED 2026-10-22 |
| Immortal Qombat mode (Sun Rā) | 不死クォンバット Immortal Qombat | NAMED (distinct from Go Qombat — do not conflate) |
| Ki Charge (T7) | Soul Kindle — PROPOSAL ONLY | NEEDS OWNER PICK |
| Tag (TTT2) | Soul Relay — PROPOSAL ONLY | NEEDS OWNER PICK |
| Rage (state) | Rinne 輪廻 (full: Rinne Tensei 輪廻転生; Tensei 転生 also acceptable short form) | LOCKED 2026-10-24 21:46 CDT (was OPEN/UNDECIDED 21:38 CDT; options pending 21:40–21:42 CDT, now resolved — see 21:46 CDT section; pronunciation note: user says "Rene" by voice dictation, correct romanization Rinne) |
| Rage Art | Ikari Jishin 怒り自身 "Rage Itself" | LOCKED 2026-10-24 21:51 CDT as the super / Rage Art equivalent, the cinematic comeback unleashed FROM the Rinne state (was RENAME-PENDING 21:38 CDT; banked-name history 21:46 CDT superseded — see 21:51 CDT section) |
| Rage Drive | — | RENAME-PENDING (2026-10-24 21:38 CDT; new name not yet picked) |
| Power Crush | — | RENAME-PENDING (2026-10-24 21:38 CDT; new name not yet picked; implementation question unchanged) |
| Screw | — | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN (2026-10-24 21:38 CDT; "Spin Juggle" proposal pending 21:40–21:42 CDT — NOT decided) |
| Tornado (T8 spinning-air extender) | — | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN (2026-10-24 21:38 CDT; "Spin Juggle" proposal pending 21:40–21:42 CDT — NOT decided) |
| Tailspin (T8 rename of Screw) | — | EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN (2026-10-24 21:38 CDT; "Spin Juggle" proposal pending 21:40–21:42 CDT — NOT decided) |
| Bound | — | NEEDS NAME |
| Wall Break | Wall Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Floor Break | Floor Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Balcony Break | Balcony Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Slow-mo finish | — | NEEDS NAME (or owner rules it needs none) |
| V-System (SFV-derived) | — | RENAME-PENDING (2026-10-24 21:38 CDT; new name not yet picked; member names still open) |
| WWE entrance-tool repurpose | — (working title only) | NEEDS NAME |

## NAMED — with source, line, date

### Heat → SOUL URGE — LOCKED
- `game/js/soulurge.js` L2–3: "USER-LOCKED NAME 2026-10-22:
  'Soul Urge' is the official name — use it everywhere (UI,
  docs, code, comments)." Rename table L9–17: Heat → Soul
  Urge; Heat Bar → Urge gauge; Heat Burst → Urge Burst
  (2+3); Heat Engager → Urge Engager; Heat Smash → Urge
  Smash (2+3 during Urge); Heat Dash → Urge Dash (1+2 during
  Urge); Heat Energy pip → Urge pip.
- `docs/research/SOUL-URGE-SYSTEM.md` L3 (name user-locked
  2026-10-22), L19–24 (rename table).
- `docs/owner-directives.md` L160–161: "Soul Urge — NAME
  LOCKED (2026-10-22)."
- Cleanup note (NOT a naming gap): "HEAT"/"heat" still
  appears in comments — `game/js/fighter.js` L1609,
  `game/js/movesets.js` L635–637, `game/js/game.js` L418,
  `game/js/spirit-actions.js` header, `docs/design/SOUL-SYSTEMS.md`
  Interactions line. The rename is locked; the remnants are
  comments, not user-facing names. A comment-sweep PR may
  clean them; it must not change behaviour.

### KESSHOU 結章 — LOCKED (finisher system)
- `docs/design/SOUL-SYSTEMS.md` L8 (owner decision
  2026-10-23): KESSHOU, meter full + victim < 25% HP, on the
  killing blow, victory outro, per-fighter variants.
- `game/js/finisher.js` header (gates: Nine-Soul Meter full +
  opponent HP < 25%), L31, L70–71 (KESSHOU variants).
- `docs/research/FINISHER-DESIGN-2026-10-23.md` L173+
  (proposal "KESSHOU — the Closing Chapter", recommended;
  adopted per SOUL-SYSTEMS.md).
- `~/MEMORY.md` L102 (user approved name, 2026-10-23).
- Gates restated (do not conflate): full meter + victim
  < 25% HP, Tekken-style complex inputs for the finisher
  path, NO one-hit kill from full health, lethal variants
  RARE under special conditions only.

### Nine-Soul Release 九魂解放 — LOCKED, with a Climax variance to resolve
- `docs/design/SOUL-SYSTEMS.md` L9 (2026-10-23): meter full,
  cost 100, input 1+2+3+4 at full meter, unblockable super,
  30 dmg × variant power, HUD callout "SOUL RELEASE READY".
- `game/js/soul-systems.js` L3, L11 (`LABELS.release =
  'NINE-SOUL RELEASE 九魂解放'`).
- VARIANCE (owner question, not decided here):
  `~/MEMORY.md` L103 (2026-10-23) lists "Nine-Soul
  Climax/Release (九魂極)" as its own system, and
  `docs/research/FINISHER-DESIGN-2026-10-23.md` (2026-10-23)
  proposed "NINE-SOUL CLIMAX (九魂極)" as the meter-state
  name with callout "SOUL CLIMAX READY" — but
  SOUL-SYSTEMS.md and `soul-systems.js` implement
  "SOUL RELEASE READY" and 九魂解放. Question for the
  owner: is Climax the ready-state name and Release the
  fired super, or is Climax superseded by Release? Until
  answered, code and HUD use Release; do not print
  "SOUL CLIMAX READY" anywhere.

### Reihou 霊放 "Spirit Release" — LOCKED
- `docs/design/SOUL-SYSTEMS.md` L10 (2026-10-23): foe is in
  RAGE, cost 50, input 1+4 (LP1+RK4), foe's rage purged for
  the round, 6 dmg.
- `game/js/soul-systems.js` L1 (owner 2026-10-23), L5, L11
  (`LABELS.reihou = 'REIHOU 霊放'`).
- Separate from KESSHOU, from Release, and from Trial's
  Seal — never merged in docs or code.

### Trial's Seal 試練の封 — LOCKED
- `docs/design/SOUL-SYSTEMS.md` L11 (2026-10-23): round ends
  by KO and winner ≥ 50% HP, or KO came from a soul system;
  automatic; decisive verdict seal banner + `matchStats.seals`;
  not a death.
- `game/js/soul-systems.js` L7, L11.
- "Automatic banner" in the brief = this: no input, no
  cost. Separate from KESSHOU.

### Soul Surge — CANON-NAMED
- `CANON.md` L447: "a fighter can invoke a Soul Surge —
  channeling one of the *other* eight souls for ten seconds,
  borrowing its signature techniques. This is not a
  mechanic layered onto the fiction. It *is* the fiction."
  Also L1398 ("The Soul Surge is memory, not magic").
- `game/js/fighter.js` L8–9, L50 (surge move, cost 100);
  `docs/research/SOUL-GAUGE-MAPPING.md` L11, L20.
- Status reasoning: the name comes from canon itself, not
  from a rename decision — it needs no owner rename pick.
  `game/js/heartmind.js` uses Soul Surge as the
  transform-meter analog in adventure mode; that is the
  same name in a second mode, not a second system.

### 魂 ACTION — NAMED
- `game/js/spirit-actions.js` L1 (canon, owner 2026-10-23),
  L4–6 (player-visible label '魂 ACTION', ja '魂アクション';
  "The source game's term must never appear on screen").
- `docs/design/SOUL-SYSTEMS.md` Interactions: fires from
  2+3 while URGE is on + a context trigger (wall-crush,
  ground-stomp, back-turned, stun-burst, prop-strike).
- Open input question (not a name gap): the brief states
  RP2+LK3 while URGE active; the code gates on URGE on +
  context. Combat lane to confirm the chord mapping;
  this audit reports code as found and does not invent it.

### Go Qombat — NAMED, implementation not found
- `~/MEMORY.md` L96–99 (user 2026-10-23): Chess Kombat
  (MK Deception) pulled as a Just Fun strategy side mode,
  renamed Go Qombat (user's spelling), based on Go (囲碁),
  fight-for-square, health handicaps by piece rank, power
  squares, single-use spells.
- Implementation: no `go-qombat` module in `game/js` (main
  listing, audited 2026-10-24). `game/js/modes.js` L276,
  L326–334 has `qombat` = 不死クォンバット Immortal Qombat
  (WH original, Sun Rā canon) — a DIFFERENT mode. Do not
  conflate the two. Go Qombat wiring is a modes-lane
  follow-up.

### Gungaku 軍楽 — LOCKED (found in audit, not in brief list)
- `docs/owner-directives.md` L162–163 (2026-10-22): fight
  lab / programmable training dummy mode (TTT2 Combot
  equivalent), name locked.

## PROPOSED ONLY — owner pick still needed

### Soul Kindle (T7 Ki Charge) — PROPOSAL
- `game/js/soul-kindle.js` L2, L12–13: "WH canon mapping
  (PROPOSED — needs owner approval): 'SOUL KINDLE'".
  Input 1+2+3+4; next landed hit is a guaranteed
  counter-hit; kindled fighter takes +10% damage, cannot
  block during the flash. Below full meter the same press
  is Soul Kindle per SOUL-SYSTEMS.md L9 note; at full
  meter it is Nine-Soul Release. The proposal is coherent;
  it is still not locked.

### Soul Relay (Tag) — PROPOSAL
- `game/js/tag-relay.js` L20–25: "WH canon mapping
  (PROPOSED — needs owner approval): 'SOUL RELAY' —
  partners are soul-fragments of one being relaying vessels
  mid-trial. Canon precedent: SHA's three-way split
  (Saku Ra / Kinpo / Awa Pop) and KAI's two moods (King
  Tyrant / Star). Proposed mechanical names: Relay Assault
  / Relay Crash / Relay Throw."
- Mechanics themselves are implemented (raw tag, tag
  assault, tag crash, tag throw, red health — L2–18). Only
  the name awaits the owner.

## NEEDS NAME — no proprietary name in any searched source

Options below are OPTIONS ONLY, grounded in canon
vocabulary (Trial, Soul, Ember, Seal, Still Point, Verdict).
None is canon until the owner picks it. Each row states
what was searched so the owner can see the gap is real.

### Rage (state: ≤ 25% HP, once per round)
> STATUS UPDATE 2026-10-24 21:46 CDT: LOCKED — Rinne (輪廻), full name Rinne Tensei (輪廻転生), Tensei (転生) also acceptable as a short form. Pronunciation note (voice dictation only): the user pronounces it "Rene" — correct romanization is Rinne; never use "Rene" as the name. This supersedes the 2026-10-24 21:38 CDT OPEN/UNDECIDED label and the 21:40–21:42 CDT options-pending label. The options below (Trial Wrath, Last Ember, Soul Blaze) are superseded audit history, NOT picks. Amatsu Rinne (天津輪廻) is a RESERVED future form (mechanic not designed, not wired); Ikari Jishin (怒り自身) was BANKED 2026-10-24 21:46 CDT (reserved name only, assigned to nothing) — SUPERSEDED 2026-10-24 21:51 CDT: Ikari Jishin is now LOCKED as the super / Rage Art equivalent (see 21:51 CDT section); it is still NOT the Rage state. Code/HUD wiring is HELD until the naming lane confirms the touchpoints listed in the 21:46 CDT section; when wired, small HUD tag/gauge only, never a big mid-fight banner.
- Found as Tekken name only: `game/js/rage.js` L7 header,
  L25 (`RAGE_THRESHOLD = 0.25`), L34 (`isRaging`).
- Options: (a) Trial Wrath — the trial's anger at the
  wounded soul, still the fighter's to spend; (b) Last
  Ember — the soul burning lowest burns brightest, fits
  the soul-ember vocabulary; (c) Soul Blaze — pairs with
  Soul Urge / Soul Surge without colliding with either.
  Note: Reihou is documented as "the counter to rage"
  (SOUL-SYSTEMS.md Interactions) — whichever name is
  picked, that sentence must be reworded to match.

### Rage Art (R.1+2 while raging; cinematic armored super, 32 dmg)
> STATUS UPDATE 2026-10-24 21:38 CDT: RENAME-PENDING — owner decided it changes; new name NOT yet picked. Options below are still proposals, not picks.
> STATUS UPDATE 2026-10-24 21:51 CDT: LOCKED — renamed to Ikari Jishin (怒り自身, "Rage Itself" in Japanese), the super / Rage Art equivalent, the cinematic comeback unleashed FROM the Rinne state (user widget pick 21:51 CDT, from the 21:49 CDT options; the 21:49 recommendation is now the user's assignment). This supersedes the RENAME-PENDING label above and the 21:46 CDT banked status of Ikari Jishin. The options below (Ember Verdict, Final Word, Wrath Blow) are superseded proposals, kept only as audit history — they are NOT picks. Code/HUD wiring to Ikari Jishin is a FOLLOW-UP step (touchpoints listed in the 21:51 CDT section); when wired, cinematic beats / HUD indicators only, never a big mid-fight banner for the name itself.
- Found as Tekken name only: `game/js/rage.js` L7, L15,
  L59, L79; `game/js/fighter.js` L1551 (comment), L1587.
- Options: (a) Ember Verdict — the wounded soul's
  verdict blow (kept distinct from Trial's Seal, which is
  a banner, not a blow); (b) Final Word — one armored
  statement before the round ends; (c) Wrath Blow —
  pairs with Trial Wrath if Rage takes that name.

### Rage Drive (RD.3+4 while raging; powered-up strike)
> STATUS UPDATE 2026-10-24 21:38 CDT: RENAME-PENDING — owner decided it changes; new name NOT yet picked. Options below are still proposals, not picks.
- Found as Tekken name only: `game/js/rage.js` L10, L59,
  L93; `game/js/movesets.js` L660 (comment).
- Options: (a) Ember Drive — keeps the drive shape,
  proprietary word; (b) Wrath Strike — pairs with
  Trial Wrath; (c) Last Surge — NOT recommended if
  picked alongside Soul Surge (collision risk); listed
  only so the owner can reject it explicitly.

### Power Crush (armored attack that absorbs hits)
> STATUS UPDATE 2026-10-24 21:38 CDT: RENAME-PENDING — owner decided it changes; new name NOT yet picked. Implementation question below is unchanged.
- NOT found as a system in searched files: zero hits for
  "power crush" in `fighter.js`, `movesets.js`, `game.js`
  (grep 2026-10-24). What DOES exist and must not be
  confused with it: (a) per-move `armor: true` flags on
  synthesized rage/urge moves; (b) moveset `crush:
  "low"/"high"` property (e.g. `pantera.json` L1676,
  L1795) = high/low evasion, a different mechanic;
  (c) "Power Bomb" = a King throw name (`pantera.json`
  L423, L431). Implementation question for the combat
  lane: is armored-attack behaviour present generically,
  or does Power Crush need implementing as well as
  naming? This audit cannot answer that from the
  searched files.
- Options: (a) Iron Soul — the soul holds its ground;
  (b) Unbroken Guard — armored advance, Tekken-free
  wording; (c) Ember Wall — pairs with Last Ember.

### Screw (T7 juggle-spin state)
> STATUS UPDATE 2026-10-24 21:38 CDT: EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN — T7 spinning-knockdown extender; WH on main uses T6 Bound instead. Name needed only when/if implemented. "Spin Juggle" proposal pending 2026-10-24 21:40–21:42 CDT — NOT decided, NOT the name.
- NOT found as a system in searched files: zero hits in
  `fighter.js` / `movesets.js` / `game.js`. Moveset hits
  for "screw" are King throw NAMES, not the mechanic:
  `pantera.json` L9363 "Screwdriver (MMD7)", L22517
  "Mid-Air Leg Screw", L24358 "Screwdriver", L24768
  "Leg Screw".
- Options: (a) Soul Spiral — the launched soul spins
  before the follow-up; (b) Still Spin — spin at the
  still point of the juggle; (c) Trial Turn.

### Tornado (T8's rename of Screw)
> STATUS UPDATE 2026-10-24 21:38 CDT: EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN — see the 2026-10-24 21:38 CDT section above for the corrected explanation (Tornado = T8's spinning-air extender; Tailspin = T8's rename of Screw). Name needed only when/if implemented. "Spin Juggle" proposal pending — NOT decided.
- NOT found in searched files (same grep as Screw).
  Decision shape is the owner's: one shared name for the
  juggle-spin state (recommended — Screw and Tornado are
  the same state across eras), or two era-split names.
- Options: same three as Screw, or (if split) Tornado →
  Soul Storm, Screw → Soul Spiral.

### Bound (T6 juggle-bounce state)
- NOT found as a system in searched files: "bound" hits
  in `fighter.js` (L116, L695, L712, L759, L1287, L2336,
  L2342) are T3 animation-bank binding, not the juggle
  mechanic. No Bound flag in `movesets.js` / `game.js`.
- Options: (a) Soul Bounce — plain, ownable; (b) Earth
  Rebound — the ground returns the fighter (Earth =
  Octagonal Shrine element, CANON.md L38); (c) Trial
  Bounce.

### Wall Break / Floor Break / Balcony Break
> STATUS UPDATE 2026-10-24 21:38 CDT: KEEP — owner: "they can still be called the same stuff". These stay as-is in code/docs/UI and are NO LONGER needs-name items. The options below are superseded and kept only as audit history.
- Implemented with Tekken names + types: `game/js/stagebreaks.js`
  header L4–15 (floor / wall / balcony), L29
  (`WALL_BREAK_BONUS = 8`), L30 (`FLOOR_BREAK_BONUS =
  12`), breakables `type: 'floor'|'wall'|'balcony'`.
  Walls are also called "spirit barriers" in the stage
  defs (a framing phrase, not a locked system name).
- Standing UI law (~/MEMORY.md L46): NEVER big
  "WALL BREAK" / "TIME BREAK" text across the screen
  during fights. A proprietary name is still needed for
  small labels, docs, and records — the UI law bans the
  big text, it does not name the mechanic.
- Options (one family, three members — owner may pick
  the family or name each separately): (a) Barrier /
  Floor / Ledge Sunder — "Sunder" family (Wall Sunder,
  Floor Sunder, Ledge Sunder); (b) Spirit Break family
  (Spirit Wall Break → "Barrier Break" — note: keep
  distinct from "spirit barriers" phrasing or embrace
  it deliberately); (c) Threshold Break family (the
  trial's thresholds give way — Wall Threshold, Floor
  Threshold, Ledge Threshold).

### Slow-mo finish (match-deciding KO slow motion)
- Found as Tekken-named presentation: `game/js/rage.js`
  L13, L172–199 (`RAGE_SLOWMO_SCALE = 0.12`,
  `RAGE_SLOWMO_TIME = 1.5`).
- Options: (a) Still Moment — the still point, at the
  KO (canon-adjacent: the Shrine is "still", CANON.md
  L38); (b) Final Heartbeat — the head-world's pulse
  (CANON.md L1387: "the head has a pulse"); (c) owner
  may rule this needs NO name (presentation detail,
  not a system) — that ruling itself should be recorded
  when made.

### V-System (V-Skill / V-Trigger / V-Reversal / V-Shift)
> STATUS UPDATE 2026-10-24 21:38 CDT: RENAME-PENDING — owner decided the V-System name changes; the new name and the member names are NOT yet picked. Options below are still proposals, not picks.
- `game/js/v-system.js` L26: "all user-facing names are
  «name TBD» placeholders flagged for user approval
  (owner directive 2026-10-22). Code keys stay neutral
  (vskill/vtrigger/vreversal/vshift)." Also
  `docs/owner-directives.md` L237: "Eastern Mind names TBD."
- Options (umbrella + members, owner picks the set):
  (a) Soul Arts family — Soul Skill / Soul Trigger /
  Soul Reversal / Soul Shift (collision risk with Soul
  Surge/Urge/Soul Kindle noted — owner to judge);
  (b) Vessel Arts family — Vessel Skill / Vessel
  Trigger / Vessel Reversal / Vessel Shift (leans on
  vessel vocabulary, CANON.md L407+); (c) Trial Arts
  family — Trial Skill / Trial Trigger / Trial
  Reversal / Trial Shift.

### WWE entrance-tool repurpose (out of story-lane scope, listed complete)
- `docs/owner-directives.md` L234–236: repurposed toolset
  (cutscene + taunt creation only, NOT full entrances)
  "needs a proprietary WH name — TBD with the user;
  working title `WH_CINEMATIC_TOOLS_WORKING_TITLE`
  until approved."

## Rules restated (so the next lane cannot re-break them)

- NEVER conflate the four separate systems: KESSHOU
  (finisher) ≠ Nine-Soul Release (super) ≠ Reihou
  (rage purge) ≠ Trial's Seal (automatic banner).
  Each has its own gates, cost, and input in
  `docs/design/SOUL-SYSTEMS.md` L8–11.
- NEVER conflate Go Qombat (Go-based Chess Kombat
  remake, named, unwired) with Immortal Qombat
  (不死クォンバット, WH original, wired in `modes.js`).
- NEVER conflate T6 PSP "SP Rage" effect-item names
  (`teardown/tekken6-customization-research.md` §2) with
  the Rage combat system.
- NEVER conflate moveset `crush` (high/low evasion),
  "Power Bomb" (throw name), or "Screwdriver"/"Leg
  Screw" (throw names) with Power Crush / Screw systems.
- NEVER print "SOUL CLIMAX READY" until the owner
  resolves the Climax/Release variance above.
- In-universe writing (CANON.md bios, banter lines,
  story dialogue) uses ONLY the NAMED column. NEEDS
  NAME systems are referred to by description ("the
  armored blow", "the spin state") or not at all, until
  the owner picks. `game/js/versus-banter.js` now
  carries this rule in its header (this PR).

## Gaps

1. Full-repo grep not completed (clone still fetching
   at report time). Unblock: re-run the term sweep
   (`Rage`, `Power Crush`, `Screw`, `Tornado`, `Bound`,
   `Wall/Floor/Balcony Break`, `Rage Art`, `Rage Drive`)
   over a fresh clone and amend this doc if any
   additional name surfaces. No name in this audit
   depends on that sweep except the NEEDS NAME rows'
   "not found" claims, which are scoped to the searched
   files above.
2. Owner picks outstanding (updated 2026-10-24 21:38 CDT,
  options added 2026-10-24 21:40–21:42 CDT):
  Wall Break / Floor Break / Balcony Break are now KEEP and
  are no longer outstanding; Rage Art is LOCKED
  2026-10-24 21:51 CDT as Ikari Jishin (the super / Rage
  Art equivalent, from Rinne) — its RENAME-PENDING label
  and Ikari Jishin's 21:46 CDT banked status are both
  superseded; Rage Drive / Power Crush / V-System are
  still RENAME-PENDING (decision made, replacement not
  picked); break + guard-breaking mechanics are
  SHARED-NAME-PENDING (one term, not picked); Rage
  (low-HP state) is LOCKED 2026-10-24 21:46 CDT as Rinne /
  Rinne Tensei (Tensei acceptable short form) — the five
  21:40–21:42 CDT options are resolved as: Rinne family =
  lock, Amatsu Rinne = reserved future form (mechanic not
  designed), Ikari Jishin = locked 21:51 CDT as the super
  (no longer banked); Screw / Tailspin / Tornado are
  EXPLAINED-NOT-NAMED and the mechanic is not on main,
  with the "Spin Juggle" descriptive proposal pending (NOT
  decided — a 👍 reaction is not confirmation). Still outstanding: Bound, Slow-mo
  finish, WWE entrance-tool repurpose, V-System members,
  Soul Kindle + Soul Relay proposals, Climax/Release
  variance, 魂 ACTION chord confirmation. None are decided
  by this audit.
