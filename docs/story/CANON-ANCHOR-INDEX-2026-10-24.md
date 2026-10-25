# Canon Anchor Index (Lane 6, 2026-10-24)

Every item this PR pulls or adds, with its canon anchor — or
an honest flag where there is none. Grades:

- ANCHORED — canon text directly supports it (file + line).
- PRECEDENT — canon has a parallel case; the item leans on
  it but canon does not state the item itself.
- SYSTEM — a game system, not a canon claim. No location,
  being, or backstory is asserted for it.
- SYSTEM-TEXT — new game text (dialogue, walk lines) using
  canon figures/places. The text is new writing, NOT canon.
- NON-CANON-ANCHORED — no anchor found; flagged, not hidden.
  (Nothing in this PR needed this grade — the grade exists
  so the next lane cannot quietly skip it.)

Canon file: `CANON.md` on main (1,607 lines, audited
2026-10-24). Tekken/MK names appear here as source labels
only, never as in-universe writing.

## Campaign layer

| Pulled / added item | Grade | Anchor / note |
|---|---|---|
| Roads between descent stages (roads, not portals) | ANCHORED | CANON.md L28: "the lands where souls fight, the roads between them, the shrine where it ends." L1391: "the long walks between the lands — the tunnels, the stairs, the desert." Also `docs/research/REALM-TRAVEL-CANON-2026-10-23.md` §1.1 (roads as vessels between organs). |
| Threshold → Masks road (past the hung faces) | ANCHORED | CANON.md L1363–1367: the Threshold keeps a Face — faces "hung like masks in a green room." |
| Furnace → Still Point road (stairs that count the climber back) | ANCHORED | CANON.md L1347–1362: Octagonal Shrine Par-fang "climbed by stairs that count the climber back"; the shrine is the Source, still (L38). |
| Five inner stages (Threshold, Masks, Drowning, Furnace, Still Point) | SYSTEM (existing) | From `game/js/heartmind.js` + `docs/modes/HEART-AND-MIND-INSIDE.md`. The Still Point leans on the Shrine's stillness (L38) as precedent; the inner rooms themselves are the mode's design, not canon locations. |
| Party of souls descending together; switch between fights | SYSTEM + PRECEDENT | System: Scenario Campaign partner model (structure only). Precedent (not a rule): SHA's three-way split — one soul, three vessels, "when one is hurt, the other two feel the grain shift" (CANON.md L407+ table + split passage); KAI's two moods (King Tyrant / Star, one sea twice). Canon never states parties descend together — this PR does not claim it does. |
| Stage journal (cleared-stage records) | SYSTEM | Scenario Campaign journal structure (data only, no prose). Explicitly NOT canon's Threshold Book (CANON.md L1363–1372: the illustrated record of the head-world) — different object, not conflated. |
| Soul embers (HP restore between waves) | SYSTEM (existing) | From `heartmind.js` + mode design doc. Devil Within health-gem analog (structure only). Not a canon object. |
| Shadow self (final boss: yourself, unmasked) | SYSTEM + PRECEDENT | System: mode design doc. Precedent: the Assembled Soul in the last room "wearing every style the climber has ever survived, including the climber's own" (CANON.md L1347–1362). The shadow self is not claimed to BE the Assembled Soul. |
| Ragdoll contexts (launch / KO / wall-splat / floor-drop) | SYSTEM | Owner law (2026-10-23: contextual only), not canon. Physics lane owns the engine. |
| Colour-settling as progress signal | ANCHORED (hook only, no visual change) | CANON.md L1381–1386: "Colour is how the trial tells the truth when words would lie… Its colours *settle*." This PR records clears only; it changes no arena colours (arena colour lock). |
| Yarn story: Trader at the crossroads | SYSTEM-TEXT | Trader is canon (CANON.md L477–481: Phantom Marketplace, buys/sells elemental forces; "All transactions are final"). The crossroads dialogue is new game writing, not canon text. The Trader's fighting style (mimicry) is NOT used here. |
| Ink story: Trial gate, nine lights, descent rooms | SYSTEM-TEXT | Trial inscribed in stone (CANON.md L457); nine souls as fragments (L407+); descent rooms are the mode's stages. Dialogue is new writing. |
| Soul Surge as adventure-mode transform analog | ANCHORED | CANON.md L447 (channel another soul for ten seconds), L1398 (surge is memory). Same name as versus Surge, second mode — not a second system. |
| Nine Souls roster mapping (RIN→Demonio, BYOU→Zui, TOU→Pantera, SHA→Saku Ra+Kinpo+Awa Pop, KAI→King Tyrant+Star, JIN→Phantom, RETSU→Skull, ZEN→Unvesseled, GYOU→Unvesseled + splinter in Cape Jones) | ANCHORED | CANON.md L407+ table (vessels column), verbatim. ZEN/GYOU unvesseled status and the GYOU splinter in CYBORG X are canon text in the same section. Rank ladder (53 tiers) is owner-built, not canon text — it is cited from the brief, not from CANON.md, and is unchanged by this PR. |

## Customization slots

| Slot group | Grade | Anchor / note |
|---|---|---|
| Face slots: face, facial-hair, face-paint, eyes, nose, mouth | ANCHORED | CANON.md L48–50 (three eyes/noses/mouths; "the face is not cosmetic"), L1342 ("The Reincarnation is the only character creator the Western Heart has ever needed"). |
| All other slots (head, hair, body, accessories, colours, costume, effects, aura) | SYSTEM | No canon claim. Trader's marketplace is NOT a clothing shop (CANON.md L477–481: forces only). |

## Names in this PR (see audit for full table)

| Name | Grade | Note |
|---|---|---|
| Soul Urge, KESSHOU, Nine-Soul Release, Reihou, Trial's Seal, Soul Surge, 魂 ACTION, Go Qombat, Gungaku | NAMED | Locked / canon / owner-named per the audit. Used as-is. |
| Naming status after 2026-10-24 21:38 CDT (+ options pending 21:40–21:42 CDT) | See audit | Updated status lives ONLY in `docs/story/PROPRIETARY-NAMES-AUDIT-2026-10-24.md` (KEEP / RENAME-PENDING / SHARED-NAME-PENDING / OPEN/UNDECIDED / EXPLAINED-NOT-NAMED / OPTIONS-PENDING). This index keeps no second list. Unnamed systems are still not named in any new dialogue or banter; they are referred to by description or not at all until the owner picks (audit options are proposals, not canon — including the 21:40–21:42 CDT "Spin Juggle" and Rinne/Ikari Jishin options, none decided). |
| Shrine体系 | USER-LOCKED NAME (2026-10-24 20:04 CDT) | The TempleOS-inspired mode's in-game name. This PR does not touch that mode; the name appears here only as a discipline note. TempleOS attribution stays in technical docs only, never in-game. Never "TempleOS" in-game. STANDING CREDITS (user 2026-10-24 20:33 CDT, Shrine lane): the mode's end credits MUST say "In memory of Terry Davis, RIP". |

## Explicit non-claims (so nothing drifts into canon by accident)

- No new locations, beings, backstory elements, or forces
  are introduced by this PR. Road `walk` lines describe
  walks between existing stages; they name no new place.
- New dialogue (Yarn/Ink stories, heartmind beats) is game
  script, not canon text, even when it quotes canon figures.
- The party, the journal, the roads layer, the slot
  taxonomy, and the ragdoll gate are systems. Canon
  supports some of them (roads, face slots, surge) and is
  silent on the rest — silence is reported as SYSTEM, not
  filled with invented lore.
- All characters in new content are adults. No minor
  character is introduced, aged, or written about here.
