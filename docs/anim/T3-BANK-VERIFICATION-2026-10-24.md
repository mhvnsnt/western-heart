# T3 Animation Bank Verification — 2026-10-24

Button names used everywhere in this report: LP1 = Left Punch = Tekken 1,
RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Method — file wiring only, no guesses

A moveset entry maps to a T3 bank row ONLY if a file actually attaches that
row to that move (`t3_row` / `anim_t3` on the moveset entry, or the decoded
T3 moveset table that the bank's `hit_frames.json` names as its source).
JSON labels are NOT wiring: a row whose label says "jab" but whose clip
jumps AND jabs is not a jab clip. Verification here uses, together:

1. The bank file itself (`rows.pack.json` `rows` dict, `hit_frames.json`,
   `reactions.pack.json`, `skeleton.json`, the 30 `t3_*.json` action clips).
2. The runtime wiring on main (`game/js/t3anims.js` `T3_BANKS` /
   `SOURCE_TO_BANK`, `game/js/fighter.js` `bankIdFor` / `FIGHTER_BANK`).
3. Clip-motion evidence from `docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md`
   (forward-kinematics scan: hip-Y trajectory, limb extension, foot lift,
   root travel — not labels). That audit covered 8 fighters only; see §5.

This report does NOT re-run the audit tool against main, and it was NOT
play-verified on a live build. Rewire status below is "audit-documented",
not "re-verified in this pass". Anything without an exact file row is
marked UNMAPPED. No closest-match fill was used. No Tekken 8 data was used
for any Tekken 7 character. No full-game repack was used.

## What exists: 22 bank directories, 22 runtime keys

`game/assets/anim/t3/` on main holds 22 character directories plus the
shared `reactions.json`. `T3_BANKS` holds 22 keys mapping onto those 22
directories (the `heihachi` key points at `heihachi_on_jin/`, and
`heihachi_ownrig` points at `heihachi/` — two keys, two directories, one
divmot13 motion stream). Mokujin has NO bank: divmot15 is absent from the
disc image (BNS entry 295, size 0, proven in
`docs/anim/T3-REMAINDER-BANKS-20261020.md` §4). That absence is correct —
no bank was fabricated for him, and no fighter references him as a source.

Every directory holds the same action-clip set (stance/neutral, intro,
light, medium, heavy, grab, block, hit, launch, KO, win LP1/RP2/LK3/RK4,
walks, dash, crouch, backdash, jumps, sidesteps) plus `skeleton.json`,
`hit_frames.json` and `reactions.pack.json`. 21 of 22 directories also hold
`rows.pack.json`. The exception is §4, finding 1.

Row counts below are the size of the `rows` dict inside each
`rows.pack.json` (format `wh-anim-pack/1`), counted from the file on main
on 2026-10-24. Hit-frame counts are the size of the `rows` dict inside
`hit_frames.json` (format `wh-hitframes/1`). Reaction counts are the size
of the `rows` dict inside `reactions.pack.json` (keyed by MOVE SLOT in hex,
not by bank row — see the pack's own `keys` note) and match
`reactions.json` `coverage` (`wanted` = `baked`, `missing` = 0 for every bank).

| Bank directory | divmot source | rows.pack rows | hit_frames rows | reactions slots | T3_BANKS key(s) |
|---|---|---:|---:|---:|---|
| anna | divmot17_anna | 213 | 305 | 427 | anna |
| armorking | divmot03_king | 187 | 379 | 568 | armorking |
| bosconovitch | divmot18_bosconovitch | 647 | 305 | 374 | bosconovitch |
| bryan | divmot12_bryan | 160 | 210 | 317 | bryan |
| eddy | divmot08_eddy | 211 | 254 | 276 | eddy |
| forestlaw_on_law | divmot20_forestlaw | 198 | 120 | 156 | forestlaw |
| gon | divmot19_gon | 148 | 186 | 241 | gon |
| gunjack | divmot16_gunjack | 238 | 273 | 275 | gunjack |
| heihachi | divmot13_heihachi | NONE — no rows.pack.json | 237 | 288 | heihachi_ownrig |
| heihachi_on_jin | divmot13_heihachi | 195 | 237 | 288 | heihachi |
| hwoarang | divmot06_hwoarang | 187 | 241 | 363 | hwoarang |
| jin | divmot09_jin | 220 | 277 | 312 | jin |
| julia | divmot10_julia | 175 | 225 | 298 | julia |
| king_on_pantera_leoman | divmot03_king | 256 | 379 | 568 | king |
| kuma | divmot11_kuma | 164 | 212 | 246 | kuma |
| law | divmot01_law | 219 | 275 | 346 | law |
| lei | divmot02_lei | 262 | 313 | 381 | lei |
| nina | divmot05_nina | 203 | 308 | 418 | nina |
| ogre | divmot14_ogre | 189 | 211 | 268 | ogre |
| paul | divmot00_paul | 168 | 230 | 308 | paul |
| xiaoyu | divmot07_xiaoyu | 230 | 296 | 386 | xiaoyu |
| yoshimitsu | divmot04_yoshimitsu | 215 | 278 | 264 | yoshimitsu |

Totals counted this pass: 4,685 row clips across the 21 row packs present;
7,368 reaction slots across the 22 reaction packs. Shared file:
`game/assets/anim/t3/reactions.json` — 633 reaction records, 418
throw-victim slots, 58 close reactions, per
`docs/anim/T3-REACTIONS.md`.

Notes on the counts, from the files themselves:

- Bosconovitch is the only full move-index bake (647 rows); every other
  bank's row pack is a referenced-rows bake (148–262 rows). A referenced
  pack is NOT a missing bank — it is a pack that only bakes rows a moveset
  actually references — but a move whose row is not in the pack has no
  exact clip in that bank, and falls to donor/match/generic (§3).
- `rows.pack.json` `missing`: 0 for every bank except bosconovitch (1:
  row 1073741823) and forestlaw_on_law (1). Those two missing entries are
  recorded, not filled.
- Armorking and king_on_pantera_leoman share divmot03_king, and their
  hit-frame row counts are identical (379) and their reaction slot counts
  are identical (568) — same motion, different rigs (King's own rig vs
  the Pantera/Leo-man rig). Heihachi and heihachi_on_jin likewise share
  divmot13 (237 hit-frame rows, 288 reaction slots each).
- Most banks bake on 18 bones; king_on_pantera_leoman bakes on 22. The
  reaction packs name 22 canonical bones with identity joints where the
  source rig lacks them (pack `bones_note`).

## 1. How a fighter gets a bank (runtime wiring, main)

`game/js/t3anims.js`:

- `T3_BANKS`: the 22 keys in the table above.
- `SOURCE_TO_BANK`: king→king, demonio→jin, jin→jin, bryan→bryan,
  xiaoyu→xiaoyu, yoshimitsu→yoshimitsu, gunjack→gunjack, deviljin→jin,
  paul→paul, lei→lei, nina→nina, hwoarang→hwoarang, eddy→eddy,
  julia→julia, anna→anna, bosconovitch→bosconovitch, heihachi→heihachi,
  armorking→armorking, armor-king→armorking, ogre→ogre, kuma→kuma,
  panda→kuma, gon→gon, law→law, forestlaw→forestlaw.

`game/js/fighter.js` `bankIdFor` (order matters):

1. `armor-king` → `armorking` (hard override).
2. `FIGHTER_BANK` overrides, code-confirmed on main 2026-10-24:
   awapop→nina, torch→anna, kingtyrant→eddy, kai→eddy, tou→paul,
   gyou→hwoarang, zen→null (UNMAPPED, owner decision 2026-10-24 — Zen is
   neither Heihachi nor Julia), rave→lei, yukihyo→armorking,
   nightwolf→julia, chatur→ogre, dorowani→gon, menajerii→kuma,
   gashadokuro→kuma, aotsuki→kuma, silvertongue→xiaoyu,
   docfrank→bosconovitch, tobi→hwoarang, buffalo-bill→law.
3. Otherwise the moveset's `anim_bank`, else its `t3_source`, else
   `MOVESET_MAP`, mapped through `SOURCE_TO_BANK`. No match → null →
   embedded locomotion + procedural, never another character's clips
   (isolation doctrine, stated in both files).

Per-move row clips are guarded (`_t3RowClipForMove` in fighter.js): a row
clip plays ONLY when the move's own `t3_source` maps to the bound bank.
Binding a fighter to their base's bank therefore changes their ACTION
clips (stance, light, medium, heavy, block, walk) but cannot play a third
character's per-move clips. Proxy-table moves keep falling back to the
bank's generic actions until the moveset lane rebuilds them on the true
base table. That guard is the reason "bound to the right bank" and
"every move plays its exact clip" are two different claims — this report
keeps them separate.

## 2. Which WH fighters use each bank (code-confirmed + flagged)

"Direct" = a `FIGHTER_BANK` override or a `SOURCE_TO_BANK` source name on
main. "Flagged proxy" = the 2026-10-20 BANK-TABLE substitution list; those
bindings were flagged in that document and were NOT re-verified fighter by
fighter in this pass, so they are listed as flagged, not as verified.

| Bank | Direct WH fighters (main, 2026-10-24) | Flagged proxy / note |
|---|---|---|
| king_on_pantera_leoman (king) | pantera (source king); all other king-source fighters keep this bank per the armor-king override comment | kronos, zangief, hugo, marduk, cainelias, ryuji-rock — flagged size-class stand-ins in BANK-TABLE 2026-10-20, not re-verified here |
| jin | demonio (source demonio→jin) | zui, kinpo, waterfall, scimitar, michiko, purplerain, chordz — flagged Jin stand-ins (their bases debut in T6/T7 or have no T3 stream); kinpo/scimitar are proxy-bank cases in the motion audit, not own-bank |
| bryan | skull (source bryan) | burger (Bob has no T3 bank; Bryan bank disclosed as proxy in the audit), bruno, negativo, thor, slice, baek — flagged |
| gunjack | samura1 (source gunjack) | cyborgx (Cape Jones; Alisa debuts T6, flagged), docfrank FORMS (base docfrank is fixed to bosconovitch; the forms' own data is gunjack-sourced) |
| yoshimitsu | phantom (source yoshimitsu) | — own-bank |
| xiaoyu | sakura (source xiaoyu), silvertongue (override) | star, nightwolf (old) — nightwolf is now julia by override; do not use the old xiaoyu binding |
| heihachi_on_jin (heihachi) | diablo (source heihachi) | deathfang, dio, iori, sunra, tou (old) — tou is now paul by override; zen is now null, NOT heihachi |
| heihachi (ownrig) | NONE — no fighter binds `heihachi_ownrig` | Actions-only bank (§4) |
| armorking | armor-king (hard override), yukihyo (override) | — same divmot03 motion as king, King's own rig |
| paul | tou (override) | — |
| lei | rave (override) | byou — REMOVED 2026-10-21 (owner: Lei is Rave, not Byou); byou keeps its own moveset's bank until its base is named |
| nina | awapop (override) | — |
| hwoarang | gyou (override), tobi (override) | — |
| eddy | kingtyrant (override), kai (override) | — |
| julia | nightwolf (override) | — canon base Julia; owner 2026-10-20 order names Wolf Hawkfield (Virtua Fighter) for clips, but no VF motion exists in-repo, so Julia stands, flagged |
| anna | torch (override) | — |
| bosconovitch | docfrank (override) | — only bank with a full 647-row pack; his moves carry `t3_source` + `anim_ref` and, per BANK-TABLE, 0/102 carried `t3_row` at that date — re-check before claiming his per-move clips fire |
| ogre | chatur (override) | — True Ogre motion (divmot14) |
| kuma | menajerii (override), gashadokuro (override), aotsuki (override) | Panda shares Kuma's T3 bank (SOURCE_TO_BANK panda→kuma) |
| gon | dorowani (override) | — |
| law | buffalo-bill (override) | — Marshall Law motion (divmot01) |
| forestlaw_on_law | NONE confirmed in `FIGHTER_BANK` | Forest Law motion (divmot20) posed on Law's body; bound only if a moveset names `forestlaw` as `anim_bank`/`t3_source` — no such fighter was confirmed in this pass |

No bank bound (null → embedded/procedural, correct per isolation):
zen (owner decision 2026-10-24), vainabel, mariposa, ryuji, and the
DOA / Virtua Fighter / Street Fighter guests with no decoded bank — see
BANK-TABLE's "No bank bound" list. Unbound is NOT a failure; a wrong bank
would be.

## 3. Generic fallback — where a real row does NOT exist

Runtime clip choice, as replicated by the motion audit from fighter.js
`_attackClipPlan`, first match wins inside the fighter's OWN bank:
own row → notation row (same input's T3 basic) → `anim_t3` row → donor
(closest animated move in the same moveset) → match (bank attack pool by
buttons, then limb, then level, nearest startup) → generic (bank
light/medium/heavy action clips; grab for throws).

Only the first three steps can be exact. Donor, match and generic are
limb/level-correct AT BEST — a hook is not a jab even when both are
standing punches. Any move that reaches donor/match/generic is therefore
NOT verified exact in this report, even if it plays something plausible.

Known generic-fallback facts from the files:

- `t3_grab.json` is byte-identical to `t3_heavy.json` in every bank
  (documented in T3-REMAINDER-BANKS §2). A throw that plays `t3_grab`
  is playing a heavy-attack clip, not its throw clip. Exact throw clips
  live in the reactions packs (thrower + victim slots, §6), not in
  `t3_grab.json`.
- A string is a SEQUENCE. No single row is a multi-hit sequence clip, so
  string enders resolved to a single row are sequence-UNMAPPED in
  principle even when the bound clip preserves the string's opening
  character (audit §"Jumping-move restoration bindings").

## 4. Findings — wrong mappings and gaps

### Finding 1 — `heihachi/` has actions but NO row pack (per-move UNMAPPED)

`game/assets/anim/t3/heihachi/` contains `hit_frames.json`,
`reactions.pack.json`, `skeleton.json` and the 30 action clips, but NO
`rows.pack.json` (HTTP 404 on main, 2026-10-24; the directory listing
confirms it). `T3_BANKS.heihachi_ownrig` points at this directory, but
`bankIdFor` never returns `heihachi_ownrig`, so no fighter currently
depends on it — the gap is latent, not live. The live Heihachi bank is
`heihachi_on_jin/` (195 rows). Fix path: bake `heihachi/` rows with the
same `t3_row_bake.py` command BANK-TABLE records, or remove the
`heihachi_ownrig` key's implication that it is a complete bank. Do NOT
point fighters at `heihachi/` until its row pack exists.

### Finding 2 — Motion audit (8 fighters, 5 banks): 1,554 HARD remain

`docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md`, pressable moves only, same
audit code before and after its 33-move fix (11 basic rewires + 22
jumping-move restoration bindings):

| Fighter (bank) | Checked | HARD after fix | Variant HARD (unchanged) |
|---|---|---|---|
| pantera (king) | 762 | 236 | 98 |
| burger (bryan, proxy) | 471 | 151 | 60 |
| demonio (jin) | 665 | 174 | 79 |
| diablo (heihachi_on_jin) | 559 | 156 | 76 |
| kinpo (jin, proxy) | 429 | 108 | 79 |
| phantom (yoshimitsu) | 937 | 553 | 73 |
| scimitar (jin, proxy) | 268 | 54 | 78 |
| skull (bryan) | 605 | 122 | 59 |
| Total | 4,696 | 1,554 | 602 |

Headline: the audit is a simulation/scan, not play verification, and its
rewires are audit-documented, not re-verified in this pass. Do not quote
its "after" numbers as "fixed on main" without re-running
`tools/combat-qa/anim_motion_audit.py` against current main.

### Finding 3 — UNMAPPED basics (no verified replacement row in-bank)

From the audit's basics tables (LP1/RP2/LK3/RK4):

- demonio LP1 — row 41, starts-airborne; UNMAPPED.
- kinpo LP1 — row 35, starts-airborne (body 2.00 m vs neutral 1.03 m at
  hit); UNMAPPED. kinpo is a proxy-bank case (Asuka has no T3 bank).
- scimitar LP1 — row 184, chord button mask LP1+RK4, armR, level s,
  travel 1.63 m; UNMAPPED, and ~20 donees play 184 via donor.
- diablo LP1 — row 46, starts-airborne; UNMAPPED (no clean Heihachi LP1
  row: slot-318 is a back-step RIGHT-arm punch, armR 0.83 / armL 0.10 —
  wrong arm for LP1; the `2,1` ender uppercut travels 0.67 m).
- phantom LP1 — row 62, starts-airborne; UNMAPPED.
- phantom RP2 — row 307, crouch clip + travel; UNMAPPED.
- phantom RK4 — row 243, chord row, armL, level u — an arm motion for a
  legR high kick; UNMAPPED. All button-8 high standing rows in the
  Yoshimitsu bank lift the foot ≤ 0.14 m, i.e. they are not kicks by foot
  lift.
- burger LK3 — row 65, jump clip; UNMAPPED (only high candidate, bryan
  row 106, has a foot that never leaves the ground).
- skull LK3 — row 63, jump clip; UNMAPPED (mid candidates bryan row 135
  back-variant travels 1.29 m, row 188 is a string ender with foot
  +0.12 m for a mid kick — neither verified).

Verified basics from the same tables, for contrast (audit-documented):
pantera all four (LP1→110, RP2→99, LK3→264, RK4→216 kept); burger
LP1→172, RP2→100, RK4→104 (LK3 UNMAPPED above); skull LP1→172, RP2→100,
RK4→104; diablo RP2→157 kept, LK3→153 kept, RK4→104; phantom LK3→123;
demonio RP2→220 kept, LK3→195 kept, RK4→199 kept with soft level
mismatch (T7 high vs mid-height shape); kinpo/scimitar RP2/LK3/RK4 kept
with the same proxy-bank caveats. Stepping residuals remain on several
"fixed" jabs (travel 0.52–0.53 m vs the audit's 0.50 m threshold) — motion
correct, not stationary.

### Finding 4 — Chord-as-string: 35 motion-HARD, 66 literal

- Motion-verified HARD string enders on chord rows, post-fix: 35
  (pantera 4, demonio 7, diablo 8, kinpo 3, scimitar 13, burger/skull/
  phantom 0). Chord rows involved: king 220, jin 184/177/231, heihachi
  145/135/190/152. All 35 are UNMAPPED for the string-ender reason: a
  string needs a verified sequence clip and no such row exists in-bank.
  No string ender was rewired to a single-hit row.
- Literal branch-mask scan, post-fix: 66 string enders whose played row
  has a multi-bit branch mask (pantera 17, demonio 11, diablo 11, kinpo 7,
  phantom 5, scimitar 15, burger 0, skull 0). The gap between 66 and 35 is
  chord-branch rows whose MOTION matches the ender (e.g. pantera
  `f,f,F+3` → king row 113, a legL kick by foot lift 1.35 m — the chord
  mask is a T3-tree artifact, not the motion) plus throw moves, which are
  exempt: chord branches are legitimate for throws (LP1+LK3 / RP2+RK4).
- Legacy `strings` arrays (NOT consumed by fighter.js; passed through by
  moveset-library.js only): 6 per-hit-mapped entries with a single-button
  hit on a chord row (pantera `2,1` hit LP1 → row 220; demonio `4,1` and
  `4,1,2` hit LP1 → row 184; kinpo same 2; scimitar `1,2` hit LP1 → row
  184). If those arrays are ever consumed, they need the same
  sequence-clip fix. Do not "fix" them by guessing a single row.
- Row 38, named in the task brief: the audit's pantera history shows the
  old LP1 family (rows 38/44) as jumping-1-family slots 3337–3343 — feet
  0.75/0.78 m off the ground at frame 0. A label saying "jab" does not
  make a jumping clip a jab. Any wiring still pointing a standing LP1 at
  a jumping-1-family row is wrong on motion, whatever the label says.

### Finding 5 — Worst remaining mismatches (audit, post-fix)

pantera: `2,1` → row 220 (chord jump sequence for a jab-uppercut
string); `d/f+4` → row 135 (no-kick-motion + limb). demonio: LP1 → row 41
airborne + 40+ donees; `4,1` → row 184 chord/wrong-arm. diablo:
`f+3` → row 135 (chord row, limb). phantom: RK4 → row 243 chord arm
motion + 12 stance variants; LP1 → row 62 airborne + donees. scimitar:
LP1 → row 184 + ~20 donees. skull/burger: LK3 jump rows above; `1+2` →
notation row 41 jump. These are the moves that must NOT be filled with a
donor/match clip and called fixed.

### Finding 6 — 17 bank directories have NO motion audit

The audit covers only the king, bryan, jin, heihachi_on_jin and
yoshimitsu banks (5 directories). The other 17 directories — anna,
armorking, bosconovitch, eddy, forestlaw_on_law, gon, gunjack, hwoarang,
julia, kuma, law, lei, nina, ogre, paul, xiaoyu, plus heihachi (ownrig)
— have row packs, hit frames and reaction packs, but NO published
hip-Y / limb-trajectory / root-travel motion verdict in this pass.
Their status is UNVERIFIED FOR MOTION, not verified. Do not extend the
audit's 8-fighter numbers to them.

### Finding 7 — Reaction/throw discrepancy to resolve, not guess

`reactions.json` `banks.forestlaw_on_law` records 6 throws, but its
`coverage.forestlaw_on_law` records 0 throws (and 0 thrower clips, 5
victim slots only, no escape slots). Every other bank's coverage throws
count matches its bank entry. Forestlaw's throw pairing is therefore
FLAGGED INCONSISTENT — use neither number as a throw count until
`tools/anim/t3_reaction_tables.py` is re-run and the two entries agree.
All other banks: coverage `missing` = 0 in every role (guard, hit,
chain, throw, victim, escape, air, collapse).

## 5. T3-as-fallback rule, applied

Where Tekken 7 data is not available, a T3 bank is the fallback ONLY with
exact verification: the move's file row + the clip's hip-Y trajectory,
limb trajectory and root movement vs the Tekken 7 move's properties
(wavu T7 pages, mirrored in-repo under `docs/t7t8-reference/` per the
audit). Where the T3 clip does not exactly match the Tekken 7 move, the
move is UNMAPPED — never filled with a wrong animation, a donor clip, or
a class-correct substitute. The UNMAPPED list in §4 is the current
application of that rule for the audited fighters. For the 17 unaudited
banks, the rule has not yet been applied move by move.

## 6. Throw → receiver pairings (file pairings only)

Source: `game/assets/anim/t3/reactions.json` (633 records of 21 words;
`g_reactionRecords` at EXE 0x80010CE8; `g_throwVictimSlots`, 418 entries
at 0x800174C4; 58 close reactions; 6 air kinds) plus each bank's
`reactions.pack.json` (slots keyed by hex move slot). The pairing rule,
from `docs/anim/T3-REACTIONS.md`:

- An attacking move row's +0x32 names the defender's reaction. Below
  0x1000 → a `g_reactionRecords` record (front / front-crouch / counter /
  counter-crouch / side1 / side1-crouch / side3 / side3-crouch / back /
  back-crouch / guard / guard-crouch / down / down-other slots, plus
  push-back words). 0x1nnn → throw-victim slot nnn.
- Slot lookup: defender's own bank first; if the defender's bank does not
  define the slot, the slot comes from the OPPONENT's bank. That is how a
  throw's victim move — defined only in the thrower's bank — reaches the
  victim. Verification in that document states every slot named by a
  bank's own records is defined by that bank, so the lookup always lands.
- A throw is a PAIR: thrower clip + victim clip from the same table.
  Never invent a receiver clip, never reuse the thrower's clip for the
  victim, never fall back to the generic `t3_hit.json` for a throw victim
  when the table names a victim slot.

Throw counts per bank (from `reactions.json` `banks[].throws`;
forestlaw flagged in Finding 7): anna 86, armorking 176, bosconovitch 67,
bryan 47, eddy 35, forestlaw 6 (disputed — see Finding 7), gon 24,
gunjack 45, heihachi 40, heihachi_on_jin 40, hwoarang 48, jin 58,
julia 52, king_on_pantera_leoman 176, kuma 37, law 59, lei 59, nina 101,
ogre 36, paul 58, xiaoyu 56, yoshimitsu 31.

## 7. What this verification does NOT claim

- No live-build play verification (phone portrait, human navigation).
  The audit is simulation/scan only by its own statement.
- No re-run of the motion audit against current main; §4.2–§4.5 numbers
  are the audit document's numbers, quoted with that caveat.
- No per-move verdict for the 17 unaudited bank directories.
- No claim that a fighter "bound to the right bank" plays exact clips
  for every move: binding controls action clips; per-move exactness
  requires the move's own row, and donor/match/generic steps are not
  exactness.
- No Tekken 8 data, no full-game repack, no guessed row was used anywhere
  in this report.

## 8. GPU job specs (prepared, NOT run — Kaggle delegation)

CPU/GPU split, stated plainly: GitHub API fetches, web text-fetch
research, JSON verification and PR creation in this report are
CPU/I-O-bound and stay on the VM — a GPU gives zero benefit there, and
no GPU quota should be spent on them. The GPU-acceleratable work is
batch clip analysis, batch T3-vs-T7 cross-checking, retargeting math and
render proofs. Full ready-to-run specs (script names, repo input paths,
exact outputs, GPU memory estimates) are in the companion document
`docs/anim/T3-GPU-JOB-SPECS-2026-10-24.md`, prepared for execution via
browser delegation on the user's Kaggle notebook (2x Tesla T4, 15 GB
each):
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
Jobs: (1) batch clip analysis across all 22 banks — extends the audit to
the 17 unaudited directories, 4–8 GB on one T4; (2) batch T3-row vs
T7-property cross-check across the full roster, 1–2 GB; (3) throw →
receiver pairing verification, <1 GB; (4) community-clip retargeting /
conversion (only after an inspected download lands), 4–12 GB;
(5) render proofs for fix candidates, 8–12 GB. No Kaggle run is claimed
in this report; no number here comes from a GPU run.

## 9. Next steps (in order)

1. Bake `heihachi/` `rows.pack.json` (or drop the `heihachi_ownrig`
   implication) — Finding 1.
2. Re-run `tools/combat-qa/anim_motion_audit.py` against current main and
   confirm or correct the audit's 33 rewire claims before quoting them as
   live.
3. Resolve the forestlaw throw-count discrepancy (Finding 7) by
   re-running `tools/anim/t3_reaction_tables.py`.
4. Extend the motion audit, bank by bank, to the 17 unaudited
   directories — anna, armorking, bosconovitch, eddy, hwoarang, julia,
   kuma, law, lei, nina, ogre, paul, xiaoyu first (they have direct WH
   fighters); forestlaw, gon, gunjack after.
5. For every UNMAPPED basic and every one of the 35 motion-HARD string
   enders: either find a verified exact row in-bank, or leave UNMAPPED.
   Do not fill with donor/match/generic and call it fixed.
6. Re-check docfrank's `t3_row` coverage (BANK-TABLE said 0/102 at
   2026-10-20) — his 647-row pack only fires when moves carry rows.
