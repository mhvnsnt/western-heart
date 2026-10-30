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
| Rage Drive | LOCKED 2026-10-24 22:04 CDT (corrected) as Rinne Kōgeki | Rinne Kōgeki (輪廻攻撃, "Rinne attack") — the powered move from Rinne. HISTORY, in order: proposed 22:01 CDT as Rinne Waza (輪廻技, RECOMMENDED; alt "Rinne Move"); REJECTED 22:03 CDT — user wants a different word than "waza" (the Rinne part was NOT objected to, only "waza"); Rinne Jutsu (輪廻術) was picked by widget 22:04 CDT and then REVERSED / VOID minutes later — Rage Drive is NOT Rinne Jutsu, do NOT wire Rinne Jutsu anywhere, and do NOT wire Rinne Waza anywhere. FINAL lock is Rinne Kōgeki. See the 2026-10-24 22:03–22:04 CDT section below. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal. |
| Power Crush | LOCKED 2026-10-24 22:03 CDT as Kongō | Kongō (金剛) — the armored strike. Proposed 22:01 CDT (RECOMMENDED; alt "Armor Strike"); LOCKED 22:03 CDT (user: "yeah I like that name"). See the 2026-10-24 22:03–22:04 CDT section below. The audit's implementation question (is armored-attack behaviour present generically?) is unchanged. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal-only status. |
| V-System | LOCKED 2026-10-24 22:03 CDT as Ōgi | Ōgi (奥義) — the skill/trigger/reversal/shift toolkit system. Proposed 22:01 CDT (RECOMMENDED; alts "Soul Arts," "Higi (秘技)"); LOCKED 22:03 CDT (user: "yeah I like that name"). V-component renames (Skill / Trigger / Reversal / Shift) are a FUTURE follow-up, NOT a blocker for this PR — do NOT propose component names here. See the 2026-10-24 22:03–22:04 CDT section below. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal-only status. |
| Break mechanics + guard-breaking mechanics | KEEP (corrected 2026-10-24 22:01 CDT) | KEEP existing names — break and guard break "can just stay the same" (user clarification 22:01 CDT). NO new shared name, NO shared term invented. This SUPERSEDES and CORRECTS the SHARED-NAME-PENDING label from 21:38 CDT (owner: "can be called the same thing" — that 21:38 history line is kept, the 22:01 correction immediately follows it in the 22:01 CDT section). Distinct from the Wall / Floor / Balcony Break KEEP (21:38 CDT) — this is an additional, separate KEEP for break + guard-break mechanics. |
| Rage (low-HP state itself) | LOCKED 2026-10-24 21:46 CDT | Short name Rinne (輪廻); full name Rinne Tensei (輪廻転生); Tensei (転生) also acceptable as a short form. See the 2026-10-24 21:46 CDT section below. Supersedes the OPEN/UNDECIDED label from 21:38 CDT. |
| Screw | LOCKED 2026-10-24 22:01 CDT as Floor Spin / Floor Form | Floor Form (Floor Spin) = the ground/floor form of the locked umbrella mechanic Spin Juggle. Forms phrasing confirmed 22:03 CDT: Air Form / Floor Form, Air Spin / Floor Spin, and Air Spin / Floor Juggle are all accepted phrasings for the SAME two forms — do NOT create extra forms.  Screw = T7 spinning-knockdown extender. Mechanic on main via PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24). This SUPERSEDES the "Spin Juggle proposed, NOT locked" status. See the 2026-10-24 22:01 CDT section below. (At 2026-10-24 21:38 CDT, WH on main had NEITHER Screw nor Tornado and used T6 Bound instead of Screw; that presence statement is superseded by the #1060 merge.) |
| Tailspin | COLLAPSED 2026-10-24 22:01 CDT into Floor Spin / Floor Form — NO third form | Tailspin was T8's rename of Screw; it does NOT become a separate locked form. It collapses into Floor Form (Floor Spin) (the ground/floor form of Spin Juggle; 22:03 CDT phrasing: Floor Form = Floor Spin = Floor Juggle form, same form).  Mechanic on main via PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24); the Screw/Tornado wiring in #1060 recognizes the tailspin flag. This SUPERSEDES the "Spin Juggle proposed, NOT locked" status. See the 2026-10-24 22:01 CDT section below. |
| Tornado | LOCKED 2026-10-24 22:01 CDT as Air Spin / Air Form | Air Form (Air Spin) = the air form of the locked umbrella mechanic Spin Juggle. Forms phrasing confirmed 22:03 CDT: Air Form / Floor Form, Air Spin / Floor Spin, and Air Spin / Floor Juggle are all accepted phrasings for the SAME two forms — do NOT create extra forms.  Tornado = T8's spinning-air extender (NOT "T8's rename of Screw" — Tailspin is the T8 rename of Screw). Mechanic on main via PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24); no longer missing per gap analysis. This SUPERSEDES the "Spin Juggle proposed, NOT locked" status. See the 2026-10-24 22:01 CDT section below. |

### Nuance preserved, not contradicted

- PR #1060 (combat) has MERGED to main (merge commit
  1b90ba55158b731b6923258fafb5669156642e64, verified
  2026-10-24), wiring Screw/Tornado on main. The names
  question is now live — the mechanic is present, its WH
  name is still pending ("Spin Juggle" proposed, NOT
  locked). SUPERSEDED 2026-10-24 22:01 CDT: Spin Juggle is
  now LOCKED, with forms Air Spin (air, ex-Tornado) and
  Floor Spin (ground/floor, ex-Screw); Tailspin collapses
  into Floor Spin, no third form (see the 22:01 CDT section
  below). This PR pre-invents NO names for it and changes
  NO code; it corrects only the mechanic-presence
  statement in this audit.
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
- STATUS UPDATE 2026-10-24 22:01 CDT: the proposed status
  above is SUPERSEDED — Spin Juggle is now LOCKED (umbrella
  mechanic; forms Air Spin, air form ex-Tornado, and Floor
  Spin, ground/floor form ex-Screw; Tailspin collapses into
  Floor Spin, NO third form). See the 22:01 CDT section
  below. The 👍-reaction history is kept, but the lock is
  the 22:01 CDT user decision, not the reaction. Do NOT
  rename code/HUD/docs strings to Spin Juggle / Air Spin /
  Floor Spin in this docs PR — wiring is a follow-up step.

### Unchanged by this message

- KEEP (2026-10-24 21:38 CDT): Wall Break, Floor Break,
  Balcony Break — unchanged.
- RENAME-PENDING (2026-10-24 21:38 CDT): Rage Art, Rage
  Drive, Power Crush, V-System — unchanged; new names
  still NOT picked, options still owed to the user.
  FINAL UPDATE 2026-10-24 22:03–22:04 CDT (corrected):
  this snapshot is SUPERSEDED — Rage Art is LOCKED
  21:51 CDT as Ikari Jishin, Rage Drive is LOCKED
  22:04 CDT (corrected) as Rinne Kōgeki, Power Crush is
  LOCKED 22:03 CDT as Kongō, V-System is LOCKED
  22:03 CDT as Ōgi. NO rename-pending item remains from
  the 21:38 CDT list. See the 22:03–22:04 CDT section
  below. Rinne Waza (rejected 22:03 CDT) and Rinne Jutsu
  (picked then voided 22:04 CDT) are NOT wired anywhere.
- SHARED-NAME-PENDING (2026-10-24 21:38 CDT): break
  mechanics + guard-breaking mechanics, one term — still
  NOT picked. CORRECTION 2026-10-24 22:01 CDT: this entry
  is SUPERSEDED / CORRECTED — break + guard break are now
  KEEP ("can just stay the same"), NO new shared name.
  See the 22:01 CDT section below. The 21:38 CDT history
  line above is kept.
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
  NOT picked, options still owed to the user. UPDATE
  2026-10-24 22:01 CDT: these are now OPTIONS-PENDING
  PROPOSALS ONLY (not bare RENAME-PENDING, not locked) —
  Rage Drive → Rinne Waza (輪廻技, RECOMMENDED; alt
  "Rinne Move"); Power Crush → Kongō (金剛, RECOMMENDED;
  alt "Armor Strike"); V-System → Ōgi (奥義, RECOMMENDED;
  alts "Soul Arts," "Higi (秘技)"), system name first,
  V-component renames WAIT until the system name is picked.
  See the 22:01 CDT section below. Do NOT wire until the
  user picks. FINAL UPDATE 2026-10-24 22:03–22:04 CDT:
  these three are now LOCKED, and NO rename-pending item
  remains from the 21:38 CDT list — Rage Drive → Rinne
  Kōgeki (輪廻攻撃, corrected 22:04 CDT; Rinne Waza
  rejected 22:03 CDT, Rinne Jutsu picked then voided
  22:04 CDT, neither wired anywhere); Power Crush →
  Kongō (金剛, locked 22:03 CDT); V-System → Ōgi (奥義,
  locked 22:03 CDT; V-component renames are a future
  follow-up, not a blocker). See the 22:03–22:04 CDT
  section below.
- Shared break/guard-break name — still
  SHARED-NAME-PENDING (one term, not picked). CORRECTION
  2026-10-24 22:01 CDT: this entry is SUPERSEDED /
  CORRECTED — break + guard break are now KEEP ("can just
  stay the same"), NO new shared name. See the 22:01 CDT
  section below. The 21:38 CDT history line is kept.
- Spin Juggle (descriptive name for Screw / Tailspin /
  Tornado) — still PROPOSED, not locked. A 👍 reaction is
  NOT confirmation; this lock does not confirm it.
  SUPERSEDED 2026-10-24 22:01 CDT: Spin Juggle is now
  LOCKED (umbrella; Air Spin + Floor Spin; Tailspin
  collapses into Floor Spin, NO third form). See the
  22:01 CDT section below. Do NOT rename code/HUD/docs
  strings to it in this docs PR — wiring is a follow-up.
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
SUPERSESSION NOTE 2026-10-24 22:01 CDT: the Spin Juggle
proposal below IS now superseded — Spin Juggle is LOCKED
22:01 CDT (umbrella; Air Spin + Floor Spin; Tailspin
collapses into Floor Spin, NO third form). See the
22:01 CDT section below. The proposal text below is kept
as history of what was proposed 21:40–21:42 CDT; it no
longer describes a live pick.

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

### Juggle spin (Screw / Tailspin / Tornado) — LOCKED 2026-10-24 22:01 CDT (proposal history below)

> STATUS UPDATE 2026-10-24 22:01 CDT: LOCKED — Spin Juggle is the umbrella mechanic; forms are Air Spin (air form, ex-Tornado) and Floor Spin (ground/floor form, ex-Screw). Tailspin collapses into Floor Spin — NO third form. History preserved: Screw = T7 spinning-knockdown extender; Tailspin = T8's rename of Screw; Tornado = T8's spinning-air extender (Tornado is NOT "T8's rename of Screw"). This supersedes the "Spin Juggle proposed, NOT locked" status in this section. The proposal text below is kept as history; it is NOT a live pick. Do NOT rename code/HUD/docs strings to Spin Juggle / Air Spin / Floor Spin in this docs PR — wiring is a follow-up step, and when wired it must respect popup law (small HUD tag/gauge + cinematic only, never a big mid-fight banner for a name itself).

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
| Rage Drive | Rinne Kōgeki (輪廻攻撃, "Rinne attack") | LOCKED 2026-10-24 22:04 CDT (corrected) as Rinne Kōgeki, the powered move from Rinne. History: proposed 22:01 CDT as Rinne Waza (rejected 22:03 CDT — "waza" only, Rinne part not objected to); Rinne Jutsu picked by widget 22:04 CDT then REVERSED / VOID — NOT Rinne Jutsu, do NOT wire Rinne Waza or Rinne Jutsu anywhere. See 22:03–22:04 CDT section. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal. |
| Power Crush | Kongō (金剛) | LOCKED 2026-10-24 22:03 CDT as Kongō, the armored strike. Proposed 22:01 CDT (RECOMMENDED; alt "Armor Strike"). Implementation question unchanged. See 22:03–22:04 CDT section. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal-only status. |
| Spin Juggle (umbrella mechanic) | Spin Juggle | LOCKED 2026-10-24 22:01 CDT (umbrella; forms Air Spin + Floor Spin — see 22:01 CDT section; supersedes the "Spin Juggle proposed, NOT locked" status). Forms phrasing confirmed 22:03 CDT: Air Form + Floor Form, Air Spin / Floor Spin, and Air Spin / Floor Juggle are all accepted phrasings for the SAME two forms — do NOT create extra forms. See 22:03–22:04 CDT section. |
| Screw | Floor Form (Floor Spin) | LOCKED 2026-10-24 22:01 CDT as Floor Spin, confirmed 22:03 CDT as Floor Form (Floor Spin / Floor Juggle phrasings also accepted, same form), the ground/floor form of Spin Juggle (Screw = T7 spinning-knockdown extender; mechanic on main via PR #1060 merge 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24; 2026-10-24 21:38 CDT presence statement superseded; "Spin Juggle" proposal pending 21:40–21:42 CDT — SUPERSEDED by the 22:01 CDT lock) |
| Tornado (T8 spinning-air extender) | Air Form (Air Spin) | LOCKED 2026-10-24 22:01 CDT as Air Spin, confirmed 22:03 CDT as Air Form (Air Spin phrasing also accepted, same form), the air form of Spin Juggle (Tornado = T8's spinning-air extender, NOT "T8's rename of Screw"; mechanic on main via PR #1060 merge 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24; 2026-10-24 21:38 CDT presence statement superseded; "Spin Juggle" proposal pending 21:40–21:42 CDT — SUPERSEDED by the 22:01 CDT lock) |
| Tailspin (T8 rename of Screw) | Floor Form (collapsed) | COLLAPSED 2026-10-24 22:01 CDT into Floor Spin / Floor Form — NO third form (Tailspin was T8's rename of Screw; mechanic on main via PR #1060 merge 1b90ba55158b731b6923258fafb5669156642e64, verified 2026-10-24; 2026-10-24 21:38 CDT presence statement superseded; "Spin Juggle" proposal pending 21:40–21:42 CDT — SUPERSEDED by the 22:01 CDT lock) |
| Bound | — | NEEDS NAME |
| Wall Break | Wall Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Floor Break | Floor Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Balcony Break | Balcony Break (kept as-is) | KEEP (2026-10-24 21:38 CDT) |
| Break + guard break | break / guard break (kept as-is) | KEEP (corrected 2026-10-24 22:01 CDT; supersedes SHARED-NAME-PENDING from 21:38 CDT — NO new shared name; distinct from the Wall / Floor / Balcony Break KEEP above — see 22:01 CDT section) |
| Slow-mo finish | — | NEEDS NAME (or owner rules it needs none) |
| V-System (SFV-derived) | Ōgi (奥義) | LOCKED 2026-10-24 22:03 CDT as Ōgi, the skill/trigger/reversal/shift toolkit system. Proposed 22:01 CDT (RECOMMENDED; alts "Soul Arts," "Higi (秘技)"). V-component renames are a FUTURE follow-up, NOT a blocker — do NOT propose component names here. See 22:03–22:04 CDT section. Supersedes the bare RENAME-PENDING label from 21:38 CDT and the 22:01 CDT proposal-only status. |
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
> STATUS UPDATE 2026-10-24 22:01 CDT: OPTIONS-PENDING — PROPOSAL ONLY, NOT locked. Proposal delivered 22:01 CDT: Rinne Waza (輪廻技, RECOMMENDED; alt "Rinne Move"). Do NOT wire until the user picks. The options below (Ember Drive, Wrath Strike, Last Surge) are audit history, NOT the 22:01 proposal and NOT picks.
> STATUS UPDATE 2026-10-24 22:03–22:04 CDT: FINAL LOCK — Rinne Kōgeki (輪廻攻撃, "Rinne attack"). HISTORY, in order: Rinne Waza REJECTED 22:03 CDT — user wants a different word than "waza"; the Rinne part was NOT objected to, only "waza" was. Alternatives then pending: Rinne Jutsu (輪廻術, recommended), Rinne Kōgeki (輪廻攻撃), Rinne Strike, Rinne Move. Rinne Jutsu was picked by widget 22:04 CDT and then REVERSED / VOID minutes later (user: "let's not go with Rinne Jutsu, let's go with Rinne Kōgeki"). Rage Drive is NOT Rinne Jutsu. Do NOT wire Rinne Waza anywhere. Do NOT wire Rinne Jutsu anywhere — that pick is VOID, and Rinne Jutsu is NOT left here as a live pending alternative either; it appears ONLY as voided history. FINAL lock: Rinne Kōgeki. See the 22:03–22:04 CDT section below.
- Found as Tekken name only: `game/js/rage.js` L10, L59,
  L93; `game/js/movesets.js` L660 (comment).
- Options: (a) Ember Drive — keeps the drive shape,
  proprietary word; (b) Wrath Strike — pairs with
  Trial Wrath; (c) Last Surge — NOT recommended if
  picked alongside Soul Surge (collision risk); listed
  only so the owner can reject it explicitly.

### Power Crush (armored attack that absorbs hits)
> STATUS UPDATE 2026-10-24 21:38 CDT: RENAME-PENDING — owner decided it changes; new name NOT yet picked. Implementation question below is unchanged.
> STATUS UPDATE 2026-10-24 22:01 CDT: OPTIONS-PENDING — PROPOSAL ONLY, NOT locked. Proposal delivered 22:01 CDT: Kongō (金剛, RECOMMENDED; alt "Armor Strike"). Do NOT wire until the user picks. The options below (Iron Soul, Unbroken Guard, Ember Wall) are audit history, NOT the 22:01 proposal and NOT picks. Implementation question below is unchanged.
> STATUS UPDATE 2026-10-24 22:03 CDT: LOCKED as Kongō (金剛), the armored strike (user: "yeah I like that name"). See the 22:03–22:04 CDT section below.
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
> DRIFT CORRECTION (mechanic presence only, 2026-10-24): the MECHANIC-NOT-ON-MAIN presence statement above is SUPERSEDED — the mechanic is now on main via PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64, verified). The name status is UNCHANGED: still EXPLAINED-NOT-NAMED, "Spin Juggle" still proposed, NOT locked.
> STATUS UPDATE 2026-10-24 22:01 CDT: LOCKED as Floor Spin — the ground/floor form of Spin Juggle (umbrella mechanic, locked 22:01 CDT). This SUPERSEDES the drift correction's name-pending statement above (mechanic presence is UNCHANGED: still on main via #1060). Tailspin collapses into Floor Spin, NO third form.
> FORMS PHRASING 2026-10-24 22:03 CDT: Floor Spin is also accepted as Floor Form (and the Air Spin / Floor Juggle phrasing is accepted for the same two forms). SAME two forms under Spin Juggle — do NOT create extra forms. See the 22:03–22:04 CDT section below. The options below (Soul Spiral, Still Spin, Trial Turn) are superseded history, NOT picks. Do NOT rename code/HUD/docs strings to Spin Juggle / Floor Spin in this docs PR — wiring is a follow-up step.
- At audit time, NOT found as a system in searched files:
  zero hits in `fighter.js` / `movesets.js` / `game.js`.
  (Superseded for main by PR #1060, which wires Screw /
  Tornado in `game/js/combat-core.js` and `game/js/fighter.js`.)
  Moveset hits
  for "screw" are King throw NAMES, not the mechanic:
  `pantera.json` L9363 "Screwdriver (MMD7)", L22517
  "Mid-Air Leg Screw", L24358 "Screwdriver", L24768
  "Leg Screw".
- Options: (a) Soul Spiral — the launched soul spins
  before the follow-up; (b) Still Spin — spin at the
  still point of the juggle; (c) Trial Turn.

### Tornado (T8 spinning-air extender)

> HEADING CORRECTION 2026-10-24 22:01 CDT: the prior heading "(T8's rename of Screw)" was an erroneous shorthand and is corrected here. Tornado = T8's spinning-air extender; Tailspin = T8's rename of Screw. Do NOT re-shorthand Tornado as "T8's rename of Screw."
> STATUS UPDATE 2026-10-24 21:38 CDT: EXPLAINED-NOT-NAMED / MECHANIC-NOT-ON-MAIN — see the 2026-10-24 21:38 CDT section above for the corrected explanation (Tornado = T8's spinning-air extender; Tailspin = T8's rename of Screw). Name needed only when/if implemented. "Spin Juggle" proposal pending — NOT decided.
> DRIFT CORRECTION (mechanic presence only, 2026-10-24): the MECHANIC-NOT-ON-MAIN presence statement above is SUPERSEDED — the mechanic is now on main via PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64, verified). The name status is UNCHANGED: still EXPLAINED-NOT-NAMED, "Spin Juggle" still proposed, NOT locked.
> STATUS UPDATE 2026-10-24 22:01 CDT: LOCKED as Air Spin — the air form of Spin Juggle (umbrella mechanic, locked 22:01 CDT). This SUPERSEDES the drift correction's name-pending statement above (mechanic presence is UNCHANGED: still on main via #1060).
> FORMS PHRASING 2026-10-24 22:03 CDT: Air Spin is also accepted as Air Form (and the Air Spin / Floor Juggle phrasing is accepted for the same two forms). SAME two forms under Spin Juggle — do NOT create extra forms. See the 22:03–22:04 CDT section below. The options below (same three as Screw, or split Soul Storm / Soul Spiral) are superseded history, NOT picks. Do NOT rename code/HUD/docs strings to Spin Juggle / Air Spin in this docs PR — wiring is a follow-up step.
- At audit time, NOT found in searched files (same grep as Screw).
  (Superseded for main by PR #1060, which wires Screw /
  Tornado in `game/js/combat-core.js` and `game/js/fighter.js`.)
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
> STATUS UPDATE 2026-10-24 22:01 CDT: OPTIONS-PENDING — PROPOSAL ONLY, NOT locked. Proposal delivered 22:01 CDT: Ōgi (奥義, RECOMMENDED; alts "Soul Arts," "Higi (秘技)") — SYSTEM NAME ONLY. System name FIRST; V-component renames (Skill / Trigger / Reversal / Shift) WAIT until the system name is picked — do NOT propose component names now. Do NOT wire until the user picks.
> STATUS UPDATE 2026-10-24 22:03 CDT: LOCKED as Ōgi (奥義), the skill/trigger/reversal/shift toolkit system (user: "yeah I like that name"). V-component renames are a FUTURE follow-up, NOT a blocker for this PR. See the 22:03–22:04 CDT section below. The options below (Soul Arts / Vessel Arts / Trial Arts families, with member names) are audit history, NOT the 22:01 proposal and NOT picks; "Soul Arts" appears in the 22:01 proposal only as an alternative SYSTEM name, not as member names.
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
  now LOCKED (2026-10-24 22:03–22:04 CDT, corrected —
  see 22:03–22:04 CDT section: Rage Drive → Rinne
  Kōgeki, Power Crush → Kongō, V-System → Ōgi;
  superseding the bare RENAME-PENDING label and the
  22:01 CDT proposals-only status; Rinne Waza rejected
  22:03 CDT, Rinne Jutsu picked then voided 22:04 CDT,
  neither wired anywhere);
  break + guard-breaking mechanics are now KEEP
  (corrected 2026-10-24 22:01 CDT — "can just stay the
  same", NO new shared name; superseding and correcting
  SHARED-NAME-PENDING from 21:38 CDT); Rage
  (low-HP state) is LOCKED 2026-10-24 21:46 CDT as Rinne /
  Rinne Tensei (Tensei acceptable short form) — the five
  21:40–21:42 CDT options are resolved as: Rinne family =
  lock, Amatsu Rinne = reserved future form (mechanic not
  designed), Ikari Jishin = locked 21:51 CDT as the super
  (no longer banked); Screw / Tailspin / Tornado are
  now LOCKED 2026-10-24 22:01 CDT as Spin Juggle (umbrella;
  Air Spin / Air Form, air form ex-Tornado, + Floor Spin /
  Floor Form, ground/floor form ex-Screw; Tailspin
  collapses into Floor Spin / Floor Form, NO third form;
  forms phrasing confirmed 22:03 CDT — Air Form / Floor
  Form, Air Spin / Floor Spin, and Air Spin / Floor
  Juggle are the SAME two forms) and the mechanic is NOW
  on main via
  PR #1060 (merge commit 1b90ba55158b731b6923258fafb5669156642e64,
  verified 2026-10-24 — the 21:38 CDT presence statement
  is superseded), with the "Spin Juggle" descriptive
  proposal SUPERSEDED by the 22:01 CDT lock (the 👍 reaction
  was history, not the lock). Still outstanding: Bound, Slow-mo
  finish, WWE entrance-tool repurpose, V-System members,
  Soul Kindle + Soul Relay proposals, Climax/Release
  variance, 魂 ACTION chord confirmation. None are decided
  by this audit. FINAL UPDATE 2026-10-24 22:03–22:04 CDT
  (corrected): NO rename-pending item remains from the
  21:38 CDT list — Rage Drive is LOCKED as Rinne Kōgeki,
  Power Crush as Kongō, V-System as Ōgi. V-System
  members (Skill / Trigger / Reversal / Shift renames)
  and the Amatsu Rinne mechanic design are FUTURE
  follow-ups, NOT blockers for this PR. The other items
  in this list (Bound, Slow-mo finish, WWE entrance-tool
  repurpose, Soul Kindle / Soul Relay proposals,
  Climax/Release variance, 魂 ACTION chord confirmation)
  remain open as listed.

## Docs drift correction — Screw / Tailspin / Tornado mechanic status (2026-10-24; docs only, NO renaming, NO code)

- What changed: ONLY the mechanic-presence statement. The
  2026-10-24 21:38 CDT audit said Screw/Tailspin/Tornado
  were MECHANIC-NOT-ON-MAIN (WH on main had NEITHER Screw
  nor Tornado, used T6 Bound instead of Screw, Tornado
  missing per gap analysis; PR #1060 unmerged, held until
  the popup play pass). That presence statement is now
  STALE and is SUPERSEDED by this correction: PR #1060
  (feat(combat): Power Crush, Screw/Tornado, wall splat,
  recoverable, Soul Urge wiring, item gate, per-move
  hitbox lookup, Lane 1) MERGED to main — merge commit
  1b90ba55158b731b6923258fafb5669156642e64, merged
  2026-10-25T02:47:19Z, verified via the GitHub API and
  confirmed as an ancestor of main. Its patch wires Screw
  (T7) / Tornado (T8) combo extenders in
  `game/js/combat-core.js` and `game/js/fighter.js` and
  recognizes the tailspin flag. The mechanic is therefore
  MECHANIC-ON-MAIN. The corrected entries are: the updated
  status table, the summary table, the Screw and Tornado
  per-system sections, the nuance bullet, and the closing
  summary — all in this file, and nowhere else.
- What did NOT change: NAMES. Screw / Tailspin / Tornado
  remain EXPLAINED-NOT-NAMED. "Spin Juggle" remains
  PROPOSED, NOT locked — a 👍 reaction is NOT
  confirmation, and this correction does NOT confirm it.
  No name is locked, invented, or assigned here. UPDATE
  2026-10-24 22:01 CDT: this names-pending statement is
  SUPERSEDED for names only (mechanic presence above is
  UNCHANGED) — Spin Juggle is now LOCKED 22:01 CDT
  (umbrella; Air Spin + Floor Spin; Tailspin collapses
  into Floor Spin, NO third form). See the 22:01 CDT
  section below. The
  explanations are preserved exactly: Screw = T7
  spinning-knockdown extender; Tailspin = T8's rename of
  Screw (not Tornado); Tornado = T8's spinning-air
  extender. This correction does NOT re-shorthand Tornado
  as "T8's rename of Screw."
- Also unchanged by this correction: KEEP Wall Break,
  Floor Break, Balcony Break; RENAME-PENDING Rage Drive,
  Power Crush, V-System; SHARED-NAME-PENDING break +
  guard-break (one term, not picked); LOCKED Rinne /
  Rinne Tensei (Tensei acceptable short form) and LOCKED
  Ikari Jishin as the super / Rage Art equivalent, with
  Amatsu Rinne RESERVED as a future form (mechanic not
  designed) and all prior locked names; and all still-open
  items (Bound; Slow-mo finish; WWE entrance-tool
  repurpose; V-System members; Urge Smash tension; Soul
  Kindle / Soul Relay proposals; Nine-Soul Climax vs
  Release variance; 魂 ACTION chord question).
- UPDATE 2026-10-24 22:01 CDT to the paragraph above: its
  RENAME-PENDING and SHARED-NAME-PENDING clauses are
  SUPERSEDED — Rage Drive / Power Crush / V-System are now
  OPTIONS-PENDING proposals only (Rinne Waza / Kongō /
  Ōgi, NOT locked), and break + guard break are now KEEP
  ("can just stay the same", NO new shared name). Its
  LOCKED Rinne / Ikari Jishin, Amatsu Rinne RESERVED, and
  still-open items are UNCHANGED.
- FINAL UPDATE 2026-10-24 22:03–22:04 CDT to the above:
  the three proposals are now LOCKED — Rage Drive →
  Rinne Kōgeki (corrected 22:04 CDT; Rinne Waza rejected
  22:03 CDT, Rinne Jutsu picked then voided 22:04 CDT,
  neither wired anywhere), Power Crush → Kongō
  (22:03 CDT), V-System → Ōgi (22:03 CDT). NO
  rename-pending item remains from the 21:38 CDT list.
  Spin Juggle forms phrasing is confirmed 22:03 CDT
  (Air Form / Floor Form = Air Spin / Floor Spin =
  Air Spin / Floor Juggle, same two forms).
- Supersession note: the 2026-10-24 21:51 CDT section's
  flag that the Screw / Tailspin / Tornado entries were
  "left UNTOUCHED" pending a separate drift-correction
  lane is now SATISFIED by this correction landing on
  this same branch (PR #1085) — that flag is history, not
  a live "still owed" item. The 21:38 CDT, 21:40–21:42 CDT,
  and 21:46 CDT sections are likewise kept as history;
  their mechanic-presence statements are superseded only
  as listed above, and their name decisions are untouched.
- Scope: docs only. NO code, HUD, moveset, banner, or
  mechanic changes in this correction. Merging this docs
  PR changes no code. NOTHING here blocks the #1076
  popup deploy — #1076 has merged to main, this docs PR
  sequences AFTER it, and naming changes nothing about
  banners (already gone). No live-browser visit and no
  play pass applies to a docs correction; none is claimed.

## Owner decisions — 2026-10-24 22:01 CDT (Spin Juggle lock; break/guard-break KEEP correction; three proposals only; docs only, NO wiring yet)

> STATUS UPDATE 2026-10-24 22:03–22:04 CDT: this 22:01 CDT section is HISTORY, not final status. Its Spin Juggle lock and break/guard-break KEEP stand (forms phrasing extended 22:03 CDT — see below); its three proposals are SUPERSEDED as follows: Power Crush → Kongō LOCKED 22:03 CDT; V-System → Ōgi LOCKED 22:03 CDT; Rage Drive → Rinne Waza REJECTED 22:03 CDT, Rinne Jutsu picked then VOID 22:04 CDT, FINAL lock Rinne Kōgeki 22:04 CDT (corrected). No rename-pending item remains from the 21:38 CDT list. See the 22:03–22:04 CDT section at the end of this file for the final locked set. Do NOT read this 22:01 section's "proposals only" language as current status, and do NOT wire Rinne Waza or Rinne Jutsu anywhere.

Recorded exactly from the owner's 2026-10-24 22:01 CDT
message. This section changes STATUS labels only. It does
not rename any code tag, HUD string, or doc string, does
not implement any mechanic, and does not wire Spin Juggle,
Air Spin, Floor Spin, Rinne Waza, Kongō, or Ōgi into the
game. Wiring is a FOLLOW-UP step, not this PR. When wired,
a name must respect popup law: small HUD tag/gauge +
cinematic only, NEVER a big mid-fight banner for a name
itself.

### Locked — Spin Juggle (umbrella) + Air Spin + Floor Spin

- Spin Juggle is now LOCKED: the umbrella mechanic.
  Forms = Air Spin (air form, ex-Tornado) + Floor Spin
  (ground/floor form, ex-Screw). Exactly two forms.
- Tailspin collapses into Floor Spin — NO third form.
  Tailspin does NOT become a separate locked form.
- History preserved exactly, not rewritten: Screw = T7
  spinning-knockdown extender; Tailspin = T8's rename of
  Screw; Tornado = T8's spinning-air extender. Tornado is
  NOT re-shorthanded as "T8's rename of Screw" — Tailspin
  is the T8 rename of Screw.
- This SUPERSEDES the prior "Spin Juggle proposed, NOT
  locked" status in every place it appears: the updated
  status table (Screw / Tailspin / Tornado rows), the
  summary table (Spin Juggle / Screw / Tornado / Tailspin
  rows), the per-system sections (Screw, Tornado, and the
  Juggle-spin options section), the 21:46 CDT "Still
  proposed" note, the 21:51 CDT "Still rename-pending"
  note, the Options-pending supersession note, the nuance
  bullet, the closing summary (Gaps item 2), and the
  drift-correction section's names-pending statement.
  Each of those places now carries a 22:01 CDT
  supersession note; the prior proposal text is kept as
  history, not deleted.
- Mechanic presence is UNCHANGED by this lock: the
  mechanic is on main via PR #1060 (merge commit
  1b90ba55158b731b6923258fafb5669156642e64, verified
  2026-10-24). This lock names the mechanic; it does not
  re-implement it.
- The 👍 reaction history is kept, but the lock is the
  22:01 CDT user decision, not the reaction.

### Correction — break + guard break: KEEP, no shared name

- 21:38 CDT history, kept verbatim: break mechanics +
  guard-breaking mechanics were recorded as
  SHARED-NAME-PENDING, owner: "can be called the same
  thing", one term, not picked.
- 22:01 CDT correction, immediately after that history:
  the user clarified that break and guard break "can just
  stay the same" — NOT a new shared name. Recorded as
  KEEP: keep existing names for break + guard-break
  mechanics. NO shared term is invented here, and no
  shared term is to be invented from the 21:38 CDT line.
- This SUPERSEDES / CORRECTS the SHARED-NAME-PENDING
  entry in every place it appears: the updated status
  table (Break mechanics + guard-breaking mechanics row),
  the 21:46 CDT "Unchanged" list, the 21:51 CDT "Still
  rename-pending" list, the closing summary (Gaps item 2),
  and the drift-correction section's "Also unchanged"
  paragraph. Each now carries a 22:01 CDT correction
  note; the 21:38 CDT history line is kept.
- Distinct KEEP, not a duplicate: Wall Break / Floor
  Break / Balcony Break were already KEEP (21:38 CDT,
  "they can still be called the same stuff"). This
  break + guard-break KEEP is an additional, distinct
  KEEP for the break + guard-break mechanics — it does
  not change, merge with, or re-open the Wall / Floor /
  Balcony Break KEEP.

### Proposals only — do NOT wire until the user picks; never record as locked

- Rage Drive → Rinne Waza (輪廻技, RECOMMENDED; alt
  "Rinne Move"). OPTIONS-PENDING / PROPOSAL ONLY.
- Power Crush → Kongō (金剛, RECOMMENDED; alt "Armor
  Strike"). OPTIONS-PENDING / PROPOSAL ONLY. The
  implementation question for Power Crush (is
  armored-attack behaviour present generically?) is
  unchanged.
- V-System → Ōgi (奥義, RECOMMENDED; alts "Soul Arts,"
  "Higi (秘技)"). OPTIONS-PENDING / PROPOSAL ONLY.
  System name FIRST; V-component renames (Skill /
  Trigger / Reversal / Shift) WAIT until the system name
  is picked — record that sequencing explicitly, and do
  NOT propose component names now.
- None of the three proposals above is LOCKED. Do NOT
  rename any code, HUD, moveset, or banner string to
  Rinne Waza / Kongō / Ōgi anywhere in this PR, and do
  NOT present any of them as a lock in any table, section,
  or summary. The earlier audit options for these systems
  (Rage Drive: Ember Drive / Wrath Strike / Last Surge;
  Power Crush: Iron Soul / Unbroken Guard / Ember Wall;
  V-System: Soul Arts / Vessel Arts / Trial Arts families
  with member names) are audit history, NOT the 22:01
  proposals and NOT picks — except that "Soul Arts"
  appears in the 22:01 V-System proposal only as an
  alternative SYSTEM name, not as member names.

### Locked so far — consolidated list (verified in this section)

- Rinne / Rinne Tensei (輪廻 / 輪廻転生; Tensei (転生) also
  acceptable short form) — the Rage state, LOCKED
  2026-10-24 21:46 CDT. NOT altered here except by this
  cross-reference.
- Ikari Jishin (怒り自身) — the super / Rage Art
  equivalent, the cinematic comeback unleashed FROM the
  Rinne state, LOCKED 2026-10-24 21:51 CDT. NOT altered
  here except by this cross-reference.
- Amatsu Rinne (天津輪廻) — the extra-powerful /
  leveled-up / transformed form of Rinne. RESERVED
  concept only: mechanic NOT designed, NOT implemented,
  NOT wired. Do NOT wire it as a current system.
- Wall Break / Floor Break / Balcony Break — KEEP
  (21:38 CDT).
- Spin Juggle + Air Spin + Floor Spin — LOCKED
  2026-10-24 22:01 CDT (this section; Tailspin collapses
  into Floor Spin, NO third form).
- Break + guard break — KEEP (corrected 2026-10-24
  22:01 CDT; supersedes SHARED-NAME-PENDING 21:38 CDT).

### Everything else unchanged

- RENAME-PENDING items that remain pending are now ONLY
  the three proposal items above (Rage Drive, Power
  Crush, V-System — as proposals, not as bare pending).
  There is no other bare RENAME-PENDING item left from
  the 21:38 CDT list, and no proposal above is a lock.
- All still-open items are preserved unchanged: Bound;
  Slow-mo finish; WWE entrance-tool repurpose; V-System
  members (pending the system pick, per the sequencing
  above); Urge Smash tension; Soul Kindle / Soul Relay
  proposals; Nine-Soul Climax vs Release variance;
  魂 ACTION chord question (RP2+LK3, i.e. Right Punch +
  Left Kick, Tekken 2+3).
- LOCKED Rinne and Ikari Jishin entries are NOT altered
  here except to cross-reference this section. Amatsu
  Rinne stays RESERVED, never wired.
- Scope: docs only. NO game code, HUD, moveset, or
  banner file is in this update. NO string was renamed
  to Spin Juggle / Air Spin / Floor Spin / Rinne Waza /
  Kongō / Ōgi anywhere in code. NOTHING here blocks any
  popup deploy — naming changes nothing about banners
  (already gone). No live-browser visit and no play pass
  applies to a docs update; none is claimed.

## Owner decisions — 2026-10-24 22:03–22:04 CDT (Ōgi + Kongō locks; Rinne Waza rejected; Rinne Jutsu picked then VOID; Rinne Kōgeki final Drive lock; docs only, NO wiring yet)

Recorded exactly, in order, from the owner's 2026-10-24
22:03 CDT and 22:04 CDT messages. This section changes
STATUS labels only. It does not rename any code tag, HUD
string, or doc string, does not implement any mechanic,
and does not wire Ōgi, Kongō, Rinne Kōgeki, or any other
name in this section into the game. Wiring is a FOLLOW-UP
step, not this PR — for THIS docs PR, still docs only, no
code/HUD/moveset/banner string changes. When wired, a name
must respect popup law: small HUD tag/gauge + cinematic
only, NEVER a big mid-fight banner for a name itself.
This section does NOT rewrite the 22:01 CDT section to
hide what happened: the 22:01 proposals, the 22:03
rejection, and the 22:04 pick-then-reversal are all kept
as history below, and the FINAL status is the corrected
set at the end of this section.

### 22:01 CDT — history (proposals only, carried forward from the 22:01 CDT section)

- Rage Drive → Rinne Waza (輪廻技, recommended; alt
  "Rinne Move") — PROPOSAL ONLY at 22:01 CDT.
- Power Crush → Kongō (金剛, recommended; alt "Armor
  Strike") — PROPOSAL ONLY at 22:01 CDT.
- V-System → Ōgi (奥義, recommended; alts "Soul Arts,"
  "Higi (秘技)") — PROPOSAL ONLY at 22:01 CDT.
- Spin Juggle LOCKED at 22:01 CDT (umbrella; Air Spin
  ex-Tornado + Floor Spin ex-Screw; Tailspin collapses
  into Floor Spin, no third form).
- Break + guard break KEEP at 22:01 CDT (correction to
  the 21:38 CDT SHARED-NAME-PENDING entry).

### 22:03 CDT — locks + rejection

- Spin Juggle forms LOCKED as Air Form + Floor Form.
  The user accepts either phrasing — Air Spin / Floor
  Spin, Air Form / Floor Form, or Air Spin / Floor
  Juggle — for the SAME two forms under the Spin Juggle
  umbrella. Do NOT create extra forms: there are still
  exactly two forms (air + ground/floor), whatever
  phrasing is used. Floor Juggle is a phrasing for the
  floor form, NOT a third form, and NOT a separate
  system.
- V-System → Ōgi (奥義) LOCKED 22:03 CDT (user: "yeah I
  like that name"). Ōgi is the skill/trigger/reversal/
  shift toolkit system.
- Power Crush → Kongō (金剛) LOCKED 22:03 CDT (user:
  "yeah I like that name"). Kongō is the armored strike.
- Rage Drive: Rinne Waza REJECTED 22:03 CDT. The user
  wants a different word than "waza". Note explicitly:
  the Rinne part of the name was NOT objected to — only
  "waza" was. Do NOT wire Rinne Waza anywhere.
- Alternatives then pending user pick (22:03 CDT, as
  delivered): Rinne Jutsu (輪廻術, recommended), Rinne
  Kōgeki (輪廻攻撃), Rinne Strike, Rinne Move. These were
  live alternatives at 22:03 CDT only — see the 22:04 CDT
  correction below for their final disposition. Do NOT
  present Rinne Strike or Rinne Move as live alternatives
  after the round closed.

### 22:04 CDT — widget pick, THEN IMMEDIATELY REVERSED (correction supersedes the pick)

- Rage Drive → Rinne Jutsu (輪廻術) was picked by widget
  22:04 CDT — and then, minutes later, the user reversed
  it: "let's not go with Rinne Jutsu, let's go with Rinne
  Kōgeki."
- Rage Drive is NOT Rinne Jutsu. Do NOT wire Rinne Jutsu
  anywhere. That pick is VOID.
- Do NOT leave Rinne Jutsu in this doc as LOCKED, and do
  NOT leave it as a live pending alternative either —
  the naming round is complete, so Rinne Jutsu appears
  ONLY as voided history (picked then reversed), in this
  section, in the Rage Drive per-system section, and in
  the status/summary tables' history notes — never as a
  current name, never as a pending pick.
- The correction message supersedes the widget pick.
  The LAST message wins for final status; the widget
  pick is history, not the lock.

### FINAL LOCKED SET — this is what the status tables, summary tables, and closing summary show

- State (low HP): Rinne (輪廻), full Rinne Tensei
  (輪廻転生), Tensei short also OK.
- Super (from Rinne): Ikari Jishin (怒り自身).
- Drive (powered move from Rinne): Rinne Kōgeki
  (輪廻攻撃) — "Rinne attack".
- Future powered/transformed form of Rinne: Amatsu Rinne
  (天津輪廻) — mechanic NOT designed, NOT implemented, do
  NOT wire.
- Armored strike: Kongō (金剛).
- System (skill/trigger/reversal/shift toolkit): Ōgi
  (奥義).
- Juggle: Spin Juggle (umbrella) → Air Form + Floor
  Form (Air Spin / Floor Spin phrasings both accepted;
  Air Spin / Floor Juggle phrasing also accepted as the
  same two forms).
- Keep: Wall Break, Floor Break, Balcony Break, break,
  guard break.
- No rename-pending items remain from the 21:38 CDT
  list. Rage Drive is NOT open — it is locked as Rinne
  Kōgeki.
- Explicit negatives, so no lane can re-open them by
  mistake: Rinne Waza is REJECTED (do NOT wire it);
  Rinne Jutsu is PICKED-THEN-VOIDED (do NOT wire it,
  do NOT list it as locked or pending); Tailspin is NOT
  a third form (it collapses into Floor Form); Tornado
  is NOT "T8's rename of Screw" (Tailspin is).

### Follow-ups — future work, NOT blockers (do not block this PR on them)

- V-component renames under Ōgi (Skill / Trigger /
  Reversal / Shift renames) — future work.
- Amatsu Rinne mechanic design — future work.
- Neither follow-up blocks this docs PR, and neither
  re-opens any locked name above.

### Everything else unchanged

- All still-open items other than the closed 21:38 CDT
  rename list are preserved unchanged: Bound; Slow-mo
  finish; WWE entrance-tool repurpose; Soul Kindle /
  Soul Relay proposals; Nine-Soul Climax vs Release
  variance; 魂 ACTION chord question (RP2+LK3, i.e.
  Right Punch + Left Kick, Tekken 2+3); Urge Smash
  tension.
- LOCKED Rinne and Ikari Jishin entries are NOT altered
  here except to cross-reference this section. Amatsu
  Rinne stays RESERVED, never wired.
- Scope: docs only. NO game code, HUD, moveset, or
  banner file is in this update. NO string was renamed
  to Rinne Kōgeki / Kongō / Ōgi / Spin Juggle / Air Form /
  Floor Form anywhere in code. NOTHING here blocks any
  popup deploy — naming changes nothing about banners
  (already gone). No live-browser visit and no play pass
  applies to a docs update; none is claimed.
