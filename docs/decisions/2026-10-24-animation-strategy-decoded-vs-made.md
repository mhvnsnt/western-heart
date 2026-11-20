# Animation strategy: DECODED vs MADE (2026-10-24)

Owner directive 2026-10-24: "log in the documents the right way to do this."
Companion method doc: `docs/handoffs/COMBAT-RIGHT-WAY-2026-10-24.md`.
This doc is the animation half of that method. It replaces guessing with a
two-lane rule: an animation is either DECODED from a real game file, or MADE
for a canon move — and it is labelled as whichever it is, never the other.

Button names in this doc use the on-screen form: LP1 (left punch, Tekken 1),
RP2 (right punch, Tekken 2), LK3 (left kick, Tekken 3), RK4 (right kick,
Tekken 4).

## 1. DECODED animations — what they are

A DECODED animation is motion bytes taken from a shipped game, with a
recorded source file, a recorded row/slot, and a move it provably belongs
to. "Same class" is not decoded. A jumping punch is not a standing jab,
even though both are strikes — that exact class-match mistake is what the
owner punished on 2026-10-24 (Pantera's LP1 mapped to a jumping-punch row
instead of the standing jab, and the second press of the string still
played a throw row).

### 1.1 What is decoded and in the repo today (2026-10-24)

- **Tekken 3 banks — decoded, in the repo.** 22 banks under
  `game/assets/anim/t3/`: anna, armorking, bosconovitch, bryan, eddy,
  forestlaw_on_law, gon, gunjack, heihachi, heihachi_on_jin, hwoarang,
  jin, julia, king_on_pantera_leoman, kuma, law, lei, nina, ogre, paul,
  xiaoyu, yoshimitsu. Rows per move live in each bank's `rows.pack.json`.
  These are the logged fallback when no T7 animation exists — see
  `docs/anim/PROCEDURAL_AUDIT.md`. Fallback is not a synonym for the real
  T7 animation, and a T3 clip must never be labelled as T7.
- **Tekken 3 hit reactions and throws — decoded, in the repo (PR #1003).**
  `game/assets/anim/t3/reactions.json` plus
  `game/assets/anim/t3/<bank>/reactions.pack.json` for all 22 banks:
  7,368 clips, 1,331 thrower clips each paired with its victim clip,
  decoded from the T3 EXE tables. Contract: `docs/anim/T3-REACTIONS.md`.
  Test: `test/t3-reactions.test.mjs`.
- **Tekken 7 animations — decoded count in the repo: 0 of 51.**
  `teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md` records T7 animation
  coverage as 0 of 51. No WH fighter currently has a decoded full
  T7 move → animation set in the repo. Frame data is not animation:
  TheBigTuna T7 data (35 characters, wired for damage in PR #1000 and
  PR #1002) gives moves and properties, not animation IDs, and no
  community dataset has move → animation IDs. The `.mvl` file is
  display-only. Saying a fighter "has T7 animations" today is false
  unless a TKMovesets or mot.bin extraction below has landed for them.

### 1.2 Decoded paths that are NOT yet in the repo

In priority order, per `docs/handoffs/COMBAT-RIGHT-WAY-2026-10-24.md` §3:

1. **Live TKMovesets extraction (authoritative for T7).** Kiloutre
   TKMovesets (GPL-3.0) run against a running T7 on Grok's box or the
   owner's PC. Output: `t7_<CHAR>.json` + `anim/*.bin`, with the move
   struct's animation name and address. This is the only path that gives
   exact move → animation pairs for T7 characters.
2. **mot.bin reverse engineering.** Where mot.bin files for a character
   already exist on Grok's box or in the private repo, RE them in
   parallel. Live extraction stays authoritative; mot.bin RE is the
   backup, and any mot.bin result must be cross-checked against the
   live extraction before it is trusted.
3. **Steam pak extraction.** `teardown/tekken7/T7-STEAM-EXTRACTION.md`
   (47 GB, on the owner's machine). A heavier path; use it only if
   live extraction and mot.bin RE both stall.
4. **Older Tekken extraction (TTT2 / T6 / T5 / T3).** Only where the
   character exists in that game and the newer path is blocked:
   - TTT2: the path for Jun (see §4) and a fallback for fighters whose
     T7 extraction is blocked.
   - T6: `DATA401` is still encrypted — not a usable path until that
     changes. Do not claim T6 coverage that does not exist.
   - T5: `TK5DATA2` motions are named but not extracted — same rule.
   - T3: already decoded (22 banks, §1.1). T3 is fallback-only, never
     a substitute labelled as a newer game's animation.

### 1.3 Where decoded output goes

Decoded output goes to the private repo `mhvnsnt/game-reverse-engineering`
under `teardown/tekken7-steam/extracted-movesets/` (or similar) — never
raw game files in the public western-heart repo. Only the wired,
per-fighter result lands in western-heart, with source + row recorded
in the moveset file and the audit below re-run.

## 2. MADE animations — what they are

A MADE animation is motion created for a canon move that has no Tekken
equivalent — a move invented for Eastern Mind / Western Heart canon, not
a Tekken move with a missing clip. MADE is a legitimate lane, not a
cover story for a missing decode: if a Tekken move exists, the answer is
extraction (§3), not making something up.

### 2.1 When a move qualifies as MADE

- The move exists only in WH canon (a KESSHOU variation, a canon
  technique, a creature/being move with no Tekken counterpart).
- No Tekken base move matches it by input, body part, height, and
  effect — checked against the moveset, not assumed.
- It is labelled MADE in the moveset entry, the editor, and any doc
  that lists it. A MADE clip is never labelled DECODED, T7, or T3.

### 2.2 Methods, in order

1. **Adapt a decoded clip.** Take a decoded T7/T3 clip for the closest
   real move and adapt it (retarget, re-time, re-pose the ending) so
   the result matches the canon move's properties. The source clip,
   the adaptation, and the property check are all recorded.
2. **Blend decoded clips.** Blend two or more decoded clips (for
   example a decoded entry + a decoded strike) where the canon move is
   a combination of real motions. Record every source clip; a blend
   of two guesses is still a guess and is not allowed — every input
   clip must itself be decoded.
3. **Build from properties.** Where no decoded clip is close enough,
   build from the move's recorded properties: input (LP1/RP2/LK3/RK4
   and directions), startup/active/recovery, hit level, range, and
   damage. The property sheet is the spec, and the built clip is
   checked against it frame by frame.
4. **Community libraries.** Use a community motion library only when
   its licence allows it, its source is recorded, and the clip is
   retargeted and checked the same way as a built clip. A library clip
   with no provenance is not a source.

### 2.3 Verification — MADE is not done until it is played

A MADE clip passes only when all of these hold:

1. **Property check.** Startup, active, recovery, hit level, and
   range match the move's recorded properties.
2. **Audit check.** `node tools/anim/attack_anim_audit.mjs` per fighter:
   0 strikes on throw rows, 0 throws on strike rows, 0 generic
   fallbacks. A string's second press is checked too, not just the
   first hit — the 2026-10-24 failure was exactly a second press
   still playing the old throw row.
3. **Touch-play check.** `tools/proof-harness/touch_play.mjs` on a
   build containing the clip, phone landscape, touch only, the way
   the owner plays (VERSUS → 1V1 → CHOOSE FIGHTERS → fight). The
   screenshots are viewed, not just generated.
4. **Replacement rule.** Per `docs/anim/PROCEDURAL_AUDIT.md`, a MADE /
   procedural clip is replaced with the real decoded clip the moment
   one exists for that move. MADE is a bridge, not a permanent stand-in
   for a Tekken move.

## 3. EXTRACTION vs CREATION decision tree

Ask in order. Stop at the first YES.

1. **Does a Tekken move with this input and effect exist?**
   - YES → **EXTRACT.** Do not make, adapt, or class-match anything.
     Run the §1.2 path for that character's game (T7 live extraction
     first for T7 characters). Until it lands, the move is UNMAPPED
     in the editor (§5) — never a guessed clip.
   - NO → go to 2.
2. **Is the move a WH canon move with no Tekken equivalent?**
   - YES → **MAKE.** Follow §2.2 in order and §2.3 for verification.
     Label it MADE everywhere.
   - NO → the move is not specified well enough to do either. Stop,
     get the canon move or the Tekken source identified, and do not
     fill the slot with a placeholder clip.
3. **Does a decoded clip already exist for this exact move?**
   - YES → wire that clip, with its source and row, and re-run the
     audit. Do not re-make it.
   - NO → back to 1: the extraction request for that character is
     the work, not a substitute clip.

Two bans that apply to both lanes:

- **No class-matching.** "Both are strikes" is not a mapping. Map by
  specific move: input, limb, height, startup, and effect.
- **No mislabelling.** A T3 clip is T3. A MADE clip is MADE. A
  T7 clip is T7 only when it came from a T7 extraction. The editor
  and the moveset must agree with the doc, or the doc is wrong and
  gets fixed.

## 4. The 940 blocked slots

**Status (2026-10-24): blocked, not filled, and not to be guessed.**

| WH fighter | Tekken base | Why blocked |
|---|---|---|
| Pond | Raven | No decoded set for Raven |
| Ryusan | Lucky Chloe | No decoded set for Lucky Chloe |
| Megami | Jun | No decoded set for Jun |

Total: **940 animation slots** across these three characters, as
reported in issue #866 comment `6389250251` (2026-10-24). The
per-character split of the 940 is not stated in that comment and is
not invented here — count it from the movesets once the extractions
land, not before.

Why frame data and T3 rows cannot unblock them:

- TheBigTuna frame data gives moves and properties, not animations.
- T3 rows for these bases do not exist in the decoded 22 banks
  (§1.1) — there is no Raven, Lucky Chloe, or Jun T3 bank to borrow,
  and borrowing another fighter's bank would be the class-match
  mistake, not a fix.

### Paths to unblock, per character

- **Pond (Raven) and Ryusan (Lucky Chloe) — live TKMovesets extraction.**
  Requested in #866 comment `6389250251`: full Raven and Lucky Chloe
  extractions (`t7_RAVEN.json` + `anim/*.bin`,
  `t7_LUCKYCHLOE.json` + `anim/*.bin`) on Grok's box with T7 running,
  output to the private repo. Backup in parallel: mot.bin RE if
  Raven / Lucky Chloe mot.bin files already exist.
- **Megami (Jun) — TTT2 extraction first.** Jun is a TTT2 character,
  not a T7 roster character, so a T7 live extraction cannot produce a
  Jun set. The #866 comment requests Jun through TKMovesets; that
  request needs retargeting to a TTT2 extraction (Jun's TTT2 kit is
  already the documented source for Megami's moveset additions) plus
  mot.bin RE in parallel where Jun mot.bin files exist. Do not
  report Jun as "requested via T7 extraction" without this caveat —
  the request as written cannot land for Jun, and the TTT2 path is
  the one that can.
- **All T7 characters — the wider request.** #866 comment
  `6388949909` requests live TKMovesets extraction for ALL T7
  characters (King first, then the rest), because exact move →
  animation mappings are the blocker for the whole roster, not just
  these three. The 940 are the counted blocked slots; the uncounted
  remainder is every other T7 character's move → animation mapping,
  still at 0 of 51 decoded (§1.1).
- **Flagged, not counted:** the same #866 comment flags Ryuji and
  Vain Abel as also blocked, with their Tekken bases still to verify
  ("likely same three"). They are NOT folded into the 940 until
  their bases are verified — verify first, count second.

Until an extraction lands, these 940 slots stay UNMAPPED in the
editor (§5). That is the correct state, not a failure to fill them:
an honest UNMAPPED beats a wrong clip the owner has to playtest out
of the game.

## 5. Editor status (PR #998, merged)

PR #998 ("Create-A-Move List editor for creation suite",
`packages/creation-suite/src/movelist-editor.js`) is merged. The
editor shows an animation for every move that has one, or UNMAPPED
with a specific reason for every move that does not — mapping
statuses are `correct`, `wrong`, `approximate`, and `unmapped`, and
an entry with no animation reference and no bank/row is `unmapped`
and is never silently hidden. "UNMAPPED" is therefore a work list,
not an error to paper over: each UNMAPPED entry names why (no
decoded set for its base, extraction pending, canon move awaiting
a MADE clip, or a wrong mapping removed pending the right one).

## 6. Joystick fix status — merged, do NOT duplicate

- **PR #1001** — "fix(input): joystick center — dynamic mode +
  deadzone, any-touch=down fixed" (`game/js/input.js`). Merged.
- **PR #1003** — "Fix touch joystick (every touch read as DOWN) +
  decoded T3 hit reactions/throws + combat right-way doc". Merged
  (main tip `374a6a462`). Its joystick part is `dynamicPage: true`
  in nipplejs, so the stick centre is re-read on every touch
  instead of being stored once at boot while the fight HUD was
  hidden (the stored `{0,0}` vs real centre cause documented in
  `docs/handoffs/COMBAT-RIGHT-WAY-2026-10-24.md` §2).

Both fixes are in. **Do not open another joystick-centre fix, do not
re-apply either change, and do not "fix" the joystick again on a
report without first reproducing it on the live build.** The only
joystick work left is verification: run the touch probe
(`tools/proof-harness/stick_probe.mjs`) and the touch harness
against the live site, and report what the live site actually does.
If the live site still misbehaves, the cause is a new bug or a stale
deploy — find it with the probe before touching `game/js/input.js`.

## 7. MOD damage status — all T7 characters wired

- **PR #1000** — "Wire TheBigTuna MOD damage values into 8 WH
  moveset T7 blocks". Merged.
- **PR #1002** — "Wire TheBigTuna MOD damage values into remaining
  WH moveset T7 blocks". Merged.

Together they wire MOD damage values into all T7 characters' moveset
blocks. Damage wiring is done; it does not fix animations, and it
must not be cited as animation progress. A move can now have the
right damage and still play the wrong clip — that is exactly the
state the #866 extraction requests exist to end.

## 8. Non-T7 characters — the same rule, other games' data

Owner directive 2026-10-24: "for every character even the ones that
aren't in t7." The decision tree (§3) applies to every fighter,
not just T7 ones:

- A fighter whose base is not in T7 gets its decoded motion from
  the game its base IS in (TTT2, T6, T5, T3 — see §1.2), or, where
  the fighter is not a Tekken character at all, from the game /
  community source that actually holds that fighter: WWE and other
  wrestling-game data, Fire Pro, Yakuza, Gang Beasts, and community
  motion libraries, under the same rules — recorded source,
  recorded licence, exact-move mapping, never class-matching, and
  labelled by its real source.
- Where no such source exists, the move is a MADE move (§2) or it
  stays UNMAPPED (§5). Borrowing another fighter's moves or stance
  because a source is missing is banned — see
  `docs/handoffs/COMBAT-RIGHT-WAY-2026-10-24.md` §3 item 4.
- Tekken names stay in technical files (moveset docs, wiring specs,
  this doc). They never go in CANON.md bios or in-universe writing.

## 9. What "done" means for this strategy

- Every move in every moveset is DECODED (with source + row), MADE
  (with method + property check), or UNMAPPED (with a specific
  reason) — no fourth state, no silent generic clip.
- The audit shows 0 strikes on throw rows, 0 throws on strike rows,
  0 generic fallbacks, for every fighter, including string
  continuations.
- The touch harness passes on the live build for the fighters
  touched, with screenshots viewed.
- The 940 blocked slots shrink only when extractions land and are
  wired — never by re-labelling a fallback or a MADE clip as decoded.
