# Brutal Fist pull-in — Western Heart

Date: 2026-11-08. Lane agent 91c68548. Jay's order 2026-11-07 ~20:00: pull in the other
characters from Brutal Fist that Western Heart doesn't have, fill their inputs and
movesets in Tekken style (Tekken 7 inputs + button mapping), and give them animations
and full moveset/move-list data from Urban Reign and Urban Reign Redux characters.

NOTE ON STAGING: this deliverable first failed to write here with "Disk quota
exceeded" (os error 122) and was parked at `/var/tmp/brutal-fist-pullin/BRUTAL-FIST-PULLIN.md`;
a retry minutes later succeeded and it now lives at its proper path. **STAGING IS DONE**
(branch `brutal-fist-pullin`, commit `b391147`, 57 files, 9,473 insertions, tests 20/20 —
see §7). The **push to GitHub is blocked** on the connector's binary limit (see §7);
nothing is merged, nothing pushed to main.

## 1. Game identified — YES, with evidence

**"Brutal Fist" is Jay's own game.** Source repo: **`mhvnsnt/brutalfistgrokversiontenpointfive`**
(main branch, 881 files), one of 10 repos on Jay's GitHub
(`mhvnsnt/brutalfistgrokversion*` — base + two, three, four, five, six, seven, eight,
nine, tenpointfive). It is a Vite/TypeScript web game.

Evidence (files read from that repo):
- `src/data/bannonRoster.ts` (51,263 B) — the 27-fighter roster
- `src/data/bannonGlbRoster.ts` — GLB roster, all `rigStatus: "skinned"`, `playableGate: "PASS"`
- `src/engine/BrutalFistMoveCatalog.ts` (55,647 B) — 73 moves with measured frame data
- `src/engine/retarget/MoveLibrary.ts` (30,585 B) — clip naming; sources: Schwarzerblitz (MIT),
  BrutalfistbaseofTekken3Recompiled, Bannon, Mixamo
- `public/models/` — 76 GLBs

Ruled out (web-search hits only, NOT Jay's game, NOT used):
- "Brutal: Paws of Fury" (1994 Gametek — animal fighters) — different game
- "Kakuto Chojin: Back Alley Brutal" (Xbox 2002, 13 fighters) — different game

## 2. Roster compare — 26 new characters

Western Heart `game/js/roster-full.js`: **59 ids, 59 unique** (verified programmatically).
Brutal Fist roster: **27 fighters**. Only overlap: **Cain Elias** (WH id `cainelias`,
"The Deadman", base Undertaker, already in WH). The `titan` regex match was only
KRONOS's title "The Titan Cyclone" + surge "TITAN'S WRATH" — not a Titan fighter.

**Pull-in set = 26 new characters** (all except Cain Elias).

Full Brutal Fist roster (27): bannon, maime, onyx, cain_elias, cipher, stick_up, echo,
cody, hall_nighter, static, viper, kobra, aaron_ruben, hollow, edwin_kennedy, pablo,
tyneshia, triple_xxx, el_toro_de_oro, stan_combs, brutus, titan, master_sensei,
wreck_patterson, jager, finxsse, tarzanian_devil.

## 3. Files pulled — from Jay's own repo only

Source: `mhvnsnt/brutalfistgrokversiontenpointfive` (Jay's repo). No commercial game
files, no piracy/ROM/leak sites. Local copies in `~/workspace/brutal-fist/`:

| File | What it is |
|---|---|
| `bannonRoster.ts`, `bannonGlbRoster.ts`, `bannonCharacterManifest.json`, `bannonGlbSourceInventory.ts` | Roster + GLB roster + manifest (manifest `characters: []` — empty) |
| `BrutalFistMoveCatalog.ts`, `SchwarzerblitzMoveCatalog.ts`, `MoveLibrary.ts` | Move catalogs + retarget library |
| `bf-roster-movesets.json` | 27 entries: id, name, role, style, bio, model, 20-slot defaultMoveSet |
| `bf-move-catalog.json` | 73 moves with frames @60fps, damage, hit/block advantage, inputSequence |
| `models/` — 26 GLBs, 23,280,592 B (22.2 MB) | Default attire per character; per-file SHA-256 in `models/SHA256SUMS.txt` |
| `MODEL-INVENTORY.md` | Model verification report |
| `ur-banks.json` | All 31 UR native banks: 1,151 clips, 484 named (extracted from repo HEAD) |
| `UR-DONOR-POOL.md` | Urban Reign donor-pool report |
| `donor-map.json` | Per-character UR donor bank + per-slot clip mapping (built, see §5) |
| `build-donor-map.js`, `build-wh-movesets.js` | The two builder scripts (mechanical rules, no hand edits) |
| `wh-movesets/` — 26 JSONs | WH schema-v2 movesets, one per new character (see §4) |

Model verification (child agent cc842d65): **26/26 OK, 0 FAILED. All valid GLB v2,
1 skin each. 25 have 58 joints (52 `mixamorig:`-named); MAIME_skinned.glb has 22 joints,
Mixamo-style names WITHOUT colon, no fingers — a reduced rig. ALL 26 have 0 embedded
animations — BF characters animate entirely from external banks.** (That is why the UR
donor mapping in §5 is the animation source.)

## 4. Tekken-style movesets — built, 26 files, 286 moves

Format: Western Heart schema v2, copied from `game/assets/movesets/cainelias.json`
(frame convention "T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP").
Each file: 11 moves (1, 2, 4, d+3, b+1+2, f+1+2, 1+3, f+2, f+4, string, signature)
+ 1 string entry. Validation: **286 moves, 0 missing damage, 0 missing anim_ref,
0 duplicate clip assignments, no 1+2+3+4 input anywhere** (that chord is WH's
Nine-Soul Release — signatures use f,f+1+2 power / d/b+1+2 throw, per Cain Elias precedent).

T7 input map (per BF slot): lightAttack → `1`, heavyAttack → `2`, lowKick → `d+3`,
highKick → `4`, counter → `b+1+2`, grappleInitiate → `f+1+2`, primaryThrow → `1+3`,
extraMove1 → `f+2`, extraMove2 → `f+4`, primaryCombo → string (`1,2,3` etc. from the
BF catalog `inputSequence`, LP/RP/LK/RK → 1/2/3/4), signature → `f,f+1+2` or `d/b+1+2`.

Timing: **BF catalog frames / 60** (primary, measured). Damage: **NOT BF damage**
(BF HP 10000 vs WH 100; BF finisher 80 vs jab 8 = 10×, WH signature 30 vs jab 7 = 4.3× —
no single scale factor works) and UR has no damage. Damage comes from the per-bank WH
aggregate table (`game/assets/{bank}_moves.json`, WH scale, measured):

| T3 bank | light (1) | medium (2) | heavy (4) | grab (1+3) |
|---|---|---|---|---|
| king | 7 | 15 | 24 | 24 |
| jin | 6 | 15 | 24 | 24 |
| bryan | 7 | 15 | 21 | 21 |
| xiaoyu | 6 | 15 | 24 | 24 |
| heihachi | 7 | 15 | 21 | 21 |
| yoshimitsu | 6 | 15 | 25 | 25 |

Slot → tier: 1→light, 2→medium, d+3→light, 4→heavy, b+1+2→medium, f+1+2→medium,
1+3→grab, f+2→medium, f+4→heavy, string→heavy, signature→**30 power / 32 throw**
(WH signature tier, measured from cainelias.json: Tombstone 32, Last Ride 30).

T3 source bank by BF role: king = grappler/power (8), jin = balanced (4),
bryan = striker/kick (5), xiaoyu = agile/speed (4), heihachi = power broker/heavy (2),
yoshimitsu = tricky/showman (3). FIGHTER_BANK for these characters = their T3 source
bank until a UR clip binding exists in the engine (see §8).

**The 16 unmeasured BF moves** (15 signatures + bf_spinning_kick, used by 6 characters)
have no catalog frame data. They use **BF category means, flagged in the JSON**
(`donor_framed: true`, `timing_source: 'bf-category-mean'`): signature 20 / 2.7 / 45.8
frames, kick 11.6 / 3 / 22 frames (startup / active / recovery). Damage for them still
comes from the table above (signature tier / heavy tier). These 16 are flagged, not hidden.

## 5. UR / Redux donor animation mapping

**Urban Reign:** 31 fighters with native banks (**1,151 clips, 484 named**), 41 proxy-only
(no native bank), 829 general-pool motions anonymous/unassigned. **No UR frame data
exists** — named moves are names on clips, not a frame-data table; clips carry frames +
duration_s only. **UR fighter identities/styles are UNMEASURED for all 72** (id only,
char001–char072). Donor assignment is therefore by named-coverage rank + duration
match, NOT by style guess — except 3 assignments proven from the motdatName semantics
themselves:

- **char016 → master_sensei** — karate names (karatek, seiken, shoryu, majinsensho)
- **char041 → tarzanian_devil** — capoeira names (capo*, revelsao, duplo, bagua)
- **char021 → viper** — elbow/knee names (hiji, hiza, tokuuti)

Each BF character gets **one distinct UR donor bank** (26 of 31 used; 5 unused:
char004, char005, char070, char071, char072 — the weakest-named). Per slot, the clip
is picked by (a) name-semantics class match (kick/strike/grapple/string keyword table,
from the names themselves), (b) duration closest to the BF move total frames / 60,
(c) **no clip used twice for one character**. Result: **237/286 named donor moves,
49/286 anonymous-but-real clips** (real clip, measured frames/duration, just unnamed).
Known limit: UR clips run long vs BF single hits (UR captures include full recovery) —
the engine binding pass trims to the BF active window.

**Urban Reign Redux: 0 usable animations/movesets.** Only 5 fighters' 44 named moves
(names + clip ids, no bytes/frames) are reachable on disk; all Redux motion is locked
inside unbuilt `.urmod` payloads / the unfetched all-in-one (Drive quota retry Sun Nov 8
~7:18 PM) behind a Windows-only build step. Redux contributes nothing to this mapping
until the all-in-one arrives or the Mod Manager build runs on Windows.

## 6. Per-character table

| BF fighter | Role / style | T3 bank | UR donor bank | Model file | Moves |
|---|---|---|---|---|---|
| Aaron Ruben (aaron_ruben) | Technical Grappler / Ring General | king | ur-char002 (pmot002.ppk) | AARON_RUBEN.glb | 11 |
| Bannon (bannon) | Protagonist / Power Wrestler | king | ur-char042 (pmot042.ppk) | BANNON_rigged.glb | 11 |
| Brutus (brutus) | Unstoppable Juggernaut | king | ur-char032 (pmot032.ppk) | BRUTUS.glb | 11 |
| Cipher (cipher) | Agile Disruptor / Speed Fighter | xiaoyu | ur-char045 (pmot045.ppk) | CIPHER.glb | 11 |
| Cody (cody) | Toxic Pawn / Former Manager | jin | ur-char022 (pmot022.ppk) | CODY_sober.glb | 11 |
| Echo (echo) | Psychological Threat / Aerial | xiaoyu | ur-char046 (pmot046.ppk) | ECHO.glb | 11 |
| Edwin Kennedy (edwin_kennedy) | Corporate Mastermind / Power Broker | heihachi | ur-char061 (pmot061.ppk) | EDWIN_KENNEDY.glb | 11 |
| El Toro de Oro (el_toro_de_oro) | Luchador / Golden Bull | king | ur-char030 (pmot030.ppk) | EL_TORO_DE_ORO.glb | 11 |
| Finxsse (finxsse) | Showman / Power-Agility Hybrid | xiaoyu | ur-char060 (pmot060.ppk) | NPC_FINXSSE.glb | 11 |
| Hall Nighter (hall_nighter) | Powerhouse Enforcer | king | ur-char058 (pmot058.ppk) | HALL_NIGHTER.glb | 11 |
| Hollow (hollow) | Phantom / Psychological Warfare | yoshimitsu | ur-char063 (pmot063.ppk) | HOLLOW.glb | 11 |
| Jager (jager) | Predator / Hunter | bryan | ur-char044 (pmot044.ppk) | JAGER.glb | 11 |
| Kobra (kobra) | Street Fighter / Chaos Agent | bryan | ur-char043 (pmot043.ppk) | KOBRA.glb | 11 |
| Maime (maime) | Technical Striker | jin | ur-char020 (pmot020.ppk) | MAIME_skinned.glb | 11 |
| Master Sensei (master_sensei) | Martial Arts Master / Discipline Incarnate | heihachi | ur-char016 (pmot016.ppk) | MASTER_SENSEI.glb | 11 |
| Onyx (onyx) | Power Brawler | bryan | ur-char056 (pmot056.ppk) | ONYX_street.glb | 11 |
| Pablo (pablo) | Mythic Powerhouse / Bull of the Ring | king | ur-char003 (pmot003.ppk) | PABLO.glb | 11 |
| Stan Combs (stan_combs) | Corporate Architect / Manager Fighter | jin | ur-char055 (pmot055.ppk) | STAN_COMBS_gear.glb | 11 |
| Static (static) | Electric Striker / Speed Brawler | bryan | ur-char054 (pmot054.ppk) | STATIC.glb | 11 |
| Stick-Up (stick_up) | Agile Disruptor / Speed Fighter | xiaoyu | ur-char059 (pmot059.ppk) | STICKUP.glb | 11 |
| Tarzanian Devil (tarzanian_devil) | Wildman Luchador / Hardcore High Flyer | yoshimitsu | ur-char041 (pmot041.ppk) | TARZANIAN_DEVIL_skinned.glb | 11 |
| Titan (titan) | Colossus / Immovable Object | king | ur-char001 (pmot001.ppk) | TITAN.glb | 11 |
| Triple XXX (triple_xxx) | Showman / High-Flying Entertainer | yoshimitsu | ur-char062 (pmot062.ppk) | TRIPLE_XXX.glb | 11 |
| Tyneshia (tyneshia) | Street Queen / Technical Brawler | jin | ur-char057 (pmot057.ppk) | TYNESHIA.glb | 11 |
| Viper (viper) | Assassin / Strike Specialist | bryan | ur-char021 (pmot021.ppk) | VIPER.glb | 11 |
| Wreck Patterson (wreck_patterson) | Wrecking Machine / Demolition Expert | king | ur-char031 (pmot031.ppk) | WRECK_PATTERSON.glb | 11 |

Per-character detail (bio, full BF defaultMoveSet, BF signature name, donor clip per
slot, timing source flags) is in `~/workspace/brutal-fist/donor-map.json` and
`~/workspace/brutal-fist/wh-movesets/bf-<id>.json`. Example (Bannon, king / ur-char042):
1 Bannon Jab dmg 7 startup 0.050 `ur:ur-char042:ur_m044` (moco_huntingh2);
2 Cross dmg 15 / 0.100 `ur_m045` (moco_huntingh3); 4 High Kick dmg 24 / 0.200 `ur_m011`
(cbtd_nc01_lkhigh); d+3 Low Kick dmg 7 / 0.067 `ur_m040` (moco_dvkhit); b+1+2 Reversal
dmg 15 / 0.017 `ur_m019` (unnamed); f+1+2 Clinch dmg 15 / 0.100 `ur_m046`
(moco_sp_paknage_f); 1+3 Powerbomb dmg 24 / 0.267 `ur_m017` (unnamed); f+2 Uppercut
dmg 15 / 0.167 `ur_m016` (unnamed); f+4 Body Slam dmg 24 / 0.200 `ur_m012`
(cbtd_nc02_lklow); string 1,2,3 Jab-Cross-Hook dmg 24 / 0.050 `ur_m008`
(cbco_tp_total_b); signature f,f+1+2 Beast Mode dmg 30 / 0.333 `ur_m009`
(cbco_tp_total_f).

Status per character: **moveset BUILT (11/11 moves, validated), model ON DISK (verified
GLB), STAGED on branch `brutal-fist-pullin` (commit `b391147`, see §7), NOT YET PUSHED
(connector binary limit, §7), NOT YET PLAYED live (see §8).**

## 7. Staging — DONE locally; push to GitHub BLOCKED on the connector's binary limit

**STAGED (2026-11-08 ~03:00):** branch **`brutal-fist-pullin`**, commit **`b391147`**
("Brutal Fist pull-in: 26 fighters from Jay's Brutal Fist game"), in
`~/workspace/brutal-fist/western-heart` — **57 files, 9,473 insertions, working tree clean.**
- 26 GLBs → `roster/bf-<id>/attires/attire1/model-rigged.glb`
- 26 moveset JSONs → `game/assets/movesets/bf-<id>.json`
- 26 roster entries (`game/js/roster-full.js`), 26 MODEL_URLS (`game/js/assets.js`),
  26 FIGHTER_BANK entries (`game/js/fighter.js`), 26 MOVESET_IDS (`game/js/movesets.js`),
  26 index entries (`game/assets/movesets/index.json`, with real moves/inputs/bytes per file)
- Identity: `Muse <muse@western-heart.local>` (same as the DW decode lane)
- **Tests: 20/20 pass, 0 fail** — `node --test` on the 6 suites covering the changed
  files (owner-model-first, roger-bank-coverage, own-slot-banks, moveset-slot-hijack,
  material-resolve, model-response-guard). Full log: `~/workspace/brutal-fist/test-run-final.log`.
  Three failures on the way were all pre-existing sparse-checkout gaps (missing
  `tools/anim/node_game_env.mjs`, `game/vendor/three.module.js`,
  `game/data/owner-models.json`, `game/vendor/addons/loaders/GLTFLoader.js`,
  `game/data/canon-sizing.js`) — fixed by adding just those files to the checkout,
  none caused by this lane's changes.

**PUSH BLOCKED — exact blocker:** the GitHub connector's `push_files` accepts
**UTF-8 text only, max 16 MiB** (connector doc `references/snapshot-push.md`:
"a snapshot commit creating or updating UTF-8 files, without deletions, local Git
history, tags, branches, file modes, symlinks, or binary contents"; "non-UTF-8
content ... reject the whole snapshot"). This lane's snapshot is **26 binary GLBs,
22,280,592 B (22.2 MB)** — binary AND over the size cap. The clone's remote is plain
`https://github.com/mhvnsnt/western-heart.git` with **no credential helper**, so a
direct `git push` has no auth path from this VM, and the connector doc forbids
starting a separate auth flow (gh/PATs/tokens). **No partial push was made:**
pushing only the text files would leave a broken branch (26 roster entries pointing
at model files that don't exist on the branch), and the snapshot procedure requires
the user's agreement to omit files. **What the parent needs to do:** push branch
`brutal-fist-pullin` (commit `b391147`) via a binary-capable route (authenticated
git push from a checkout with credentials, or Jay's machine), then open the PR
against main — **do NOT merge to main without the parent's verification, do NOT
push to main.** (Note: the Break 5 stuck connector-write card from the Piece 1 lane
is gone — pending approvals are empty as of this write — so the connector queue is
clear; the binary limit is the only push blocker.)

Earlier quota history (for the record): the first full clone failed on disk quota,
a sparse partial clone succeeded after quota eased; the quota hog is
`~/workspace/video-mocap` (57G) — parent's triage call, not this lane's to delete.
Do NOT touch `~/workspace/western-heart-fix/repo` (Piece 1 fix agent's sparse clone,
branch `fix/piece1-breaks`) or `~/workspace/western-heart-movesets/repo` (moveset
lane's clone).

## 8. What is NOT done / owed

- **Live playthrough: OWED.** Nothing counts as done until a character loads and fights
  on a model in a live playthrough (headed, phone-size, real gameplay video). Not claimed.
- **UR clip engine binding: NOT DONE in this lane.** No moveset JSON anywhere references
  `ur_m` clips in `anim_ref` yet and no UR clip binding exists in `fighter.js` — the
  `anim_ref: ur:<charNNN>:<clip>` values in these 26 files are the mapping for that
  binding; building it is the template-library lane / program coordinator's follow-up.
  Until it exists, these characters fight on their T3 source bank (FIGHTER_BANK, §4).
- **Redux: 0 usable** until the all-in-one arrives (Drive retry Sun Nov 8 ~7:18 PM) or
  the Mod Manager build runs on Windows.
- **16 BF moves run on category-mean timing** (flagged `donor_framed: true`) — real frame
  data for those signatures + bf_spinning_kick does not exist in the BF catalog.
- **49/286 donor clips are unnamed** (real clips, just no motdatName) — the name is
  missing, not the motion.
- **MAIME is a reduced rig** (22 joints, no fingers) — flagged in MODEL-INVENTORY.md.
- **Stick-Up's BF signature is `bf_cipher_strike`** (Cipher's signature) in the BF roster
  itself, while the catalog also defines an unused `bf_leap_of_faith` (Stick-Up's Leap of
  Faith). The moveset uses the roster's value (`bf_cipher_strike`); the discrepancy is
  BF's own data, not this lane's invention.
- **Cipher's roster model field says `CIPHER_feral.glb`** but the GLB roster's Default
  attire is `CIPHER.glb` (feral/minion are attires). The moveset/model use the Default
  `CIPHER.glb`.
