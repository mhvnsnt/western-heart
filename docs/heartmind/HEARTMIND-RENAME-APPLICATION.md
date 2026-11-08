# HeartMind rename application — CONFIRMED rows only

**Date:** 2026-11-08
**Lane:** rename-application (`rename/heartmind-canon`), branch + PR below
**Map:** `HEARTMIND-RENAME-MAP.md` (538 lines, §§0–§5) — this file applies the
map's CONFIRMED rows only. PROVISIONAL and PROPOSED names were left untouched.
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf` (main HEAD, confirmed by
`git ls-remote` at the time of this pass).
**Jay calls:** see `HEARTMIND-JAY-CALLS.md` — every PROPOSED name and rule
needing Jay's call, with map citations.

**Counts (25 CONFIRMED rows: 14 DW + 6 UR + 5 Redux):**

| Verdict | DW | UR | Redux | Total |
|---|---|---|---|---|
| Already in code | 0 | 5 | 5 | **10** |
| Waits on decode | 14 | 0 | 0 | **14** |
| Applied (code change to a map row) | 0 | 0 | 0 | **0** |
| NOT VERIFIED in code (flagged, see §6) | 0 | 1 | 0 | **1** |

Plus **1 code change applied outside the rows** (§5): a player-visible string
the grep pass found still using a source proper noun where a CONFIRMED canon
name exists (`game/js/mainmenu.js:55`).

**How each row was checked:** the 5 HeartMind files (`game/js/heartmind.js`,
`brawler.js`, `heartmind-campaign.js`, `menus.js`, `mainmenu.js`) were read
from a HEAD-clean tree (verified `git status` clean for those files) and
`git grep HEAD` / `git ls-files` were used where the working tree is sparse,
so every citation below is HEAD content, not a stale copy. DW index checks
read `~/workspace/devil-within-decode/repo/teardown/tekken5/dw-motion-index.json`
directly (242 files; group sizes match the map exactly). Redux checks read
the zips on disk in `~/workspace/urban-reign-redux/` directly, including
first-hand SHA-256 sums. Line numbers below are HEAD line numbers. No fresh
full clone exists: a full clone is impossible in this workspace (the HEAD
tree is ~14.3 GB and the disk quota blocks it — two attempts failed "Disk
quota exceeded"), so the branch was built via the Git Data API from verified
tree SHAs per the NO-SPARSE-COMMIT LAW (see §7). The branch differs from
HEAD only in the two committed files, so every citation below except
`mainmenu.js:55` is unchanged from HEAD by construction; `mainmenu.js:55`
was verified via the PR diff patch.

---

## §1 — Devil Within CONFIRMED rows (14/14 waits on decode)

All 14 are the same shape: the **name is already canon in code** (stage and
boss display names), but the **decoded data the row maps is not on disk yet**,
so nothing can be wired and nothing was faked. The archive-pull decode is
still running under another agent; no decoded `.dat` contents exist in
`teardown/tekken5/` (only the index + format docs).

### Boss bodies — `gym_init_obj_boss*` (4 rows, all waits on decode)

| DW file | Canon name | Index evidence | Name already in code | Verdict |
|---|---|---|---|---|
| `gym_init_obj_boss1.dat` | WARDEN OF THE THRESHOLD — body/init | `dw-motion-index.json` groups[6]/files[0] | `game/js/brawler.js:87` `warden: 'WARDEN OF THE THRESHOLD'`; header `:9` | waits on decode |
| `gym_init_obj_boss2.dat` | THE MASKS — body/init | groups[6]/files[1] | `brawler.js:88` `masks: 'THE MASKS'`; header `:10` | waits on decode |
| `gym_init_obj_boss3.dat` | THE DROWNED OGRE — body/init | groups[6]/files[2] | `brawler.js:89` `ogre: 'THE DROWNED OGRE'`; header `:11` | waits on decode |
| `gym_init_obj_boss5.dat` | THE UNMASKED — body/init | groups[6]/files[3] | `brawler.js:650` `name: 'THE UNMASKED'`; `:1311` `setNames(..., 'THE UNMASKED')` | waits on decode |

What is owed per row: the decoded init-object body data, when the decode
lands it. The display names need no change.

Confirmed absence (map §1, verified in the index): `gym_init_obj_boss4`
does NOT exist as a file — the index records it only in
`gaps_found_in_manifest[2]` ("boss init objects are 1, 2, 3, 5 only").
The SOUL SPHERE needs no body, by design. No gap to fill.

### Wave echoes — `gym_init_obj_mon*` (6 rows, all waits on decode + FLAG)

| DW file (map) | Canon name | Verdict |
|---|---|---|
| `gym_init_obj_mon01.dat` … `mon06.dat` | Wave echo — archetypes 01–06 | waits on decode |

- **FLAG — map filenames do not match the index.** The index's init_obj
  group (21 files, groups[6]) holds SIX monster init objects, but under
  archetype names, not numbers: `mon_power1`, `mon_power2`, `mon_speed1`,
  `mon_standard1`, `mon_standard2`, `mon_tricky1` (files[6..11]). The
  map's `mon01`–`mon06` labels match no filename in the index
  (`grep -c` = 0 for each). Group-level mapping holds (6 wave-enemy init
  objects → wave echoes); per-file identity waits on the decode, which must
  use the index's real filenames. Coordinator: the map's mon rows need a
  filename correction when the decode lands.
- What is already in code: the wave-echo enemy kind — `brawler.js:58`
  (`t: echo | brute | gunner`), wave tables `:61–81` (all `t: 'echo'`),
  kinds `:96`, spawn `:1176` (`type: 'echo'`). What is owed: the 6 archetype
  bodies from the decode.

### Stage text — `moj_stg*` (4 rows, all waits on decode)

| DW file | Canon name | Index evidence | Stage name already in code | Verdict |
|---|---|---|---|---|
| `moj_stg00.dat` | THE THRESHOLD — stage text | groups[9]/files[0] | `heartmind.js:44` `name: 'THE THRESHOLD'` | waits on decode |
| `moj_stg01.dat` | THE GALLERY OF MASKS — stage text | groups[9]/files[1] | `heartmind.js:47` `name: 'THE GALLERY OF MASKS'` | waits on decode |
| `moj_stg02.dat` | THE DROWNING ROOM — stage text | groups[9]/files[2] | `heartmind.js:50` `name: 'THE DROWNING ROOM'` | waits on decode |
| `moj_stg04.dat` | THE STILL POINT — stage text | groups[9]/files[3] | `heartmind.js:56` `name: 'THE STILL POINT'` | waits on decode |

What is owed per row: the decoded stage intro/lore text, when the decode
lands it. The stage names need no change. (The full five-stage list,
including THE FURNACE at `heartmind.js:53`, is already canon in code.)

Confirmed absence (map §1, verified in the index): `moj_stg03` does NOT
exist — the index records it in `gaps_found_in_manifest[1]` and in the
moj_stg group note ("moj_stg03 ABSENT"). THE FURNACE has no DW stage-text
donor; its text comes from canon. No gap to fill.

---

## §2 — Urban Reign CONFIRMED rows (5 already in code, 1 not verified)

### Already in code

| UR row | Canon name | Evidence (file + line) | Verdict |
|---|---|---|---|
| 31 movesets wired | Wired Descent donors | `git ls-files game/assets/movesets/` → **31** `ur-charNNN.json` files (of 220 moveset files); `git show HEAD:game/assets/movesets/ur-char001.json` — `"fighter": "ur-char001"`, `"proxy": false`, `"bank": "pmot001.ppk"` (native bank); `street-reign.json` proxy; `ur-native-index.json` present; `git ls-files game/assets/models/street-reign/` → **72** models | already in code, no change |
| 60 fps bar | Descent tempo | Engine timing base is 60 fps: `game/js/frame-data-schema.js:16` ("Timing base: 60 fps"); `game/js/fighter.js:1128` ("60 fps logic-frame"); `game/js/hitstop-tekken-draft.js:16` ("Frames are at 60 fps"); brawler runs on `requestAnimationFrame` (`brawler.js:1432`, `:1439`). The map's label "Descent tempo" appears nowhere in code (`git grep HEAD`: 0 hits) — it is the canon name for the tempo; no UI string uses another name | already in code, no change |
| Free Mode | Any-fighter Descent | Rule true in code: `heartmind.js:8` ("Pick ANY fighter"); `brawler.js:21` ("CHARACTER SELECT, NOT FORCED JIN: any WH fighter plays the descent"). No "Free Mode" string exists in code (`git grep HEAD`: 0 hits). No change | already in code, no change |
| Glen Kluger | Cain Elias — moveset source | Canon doc: `CANON.md:1273` (owner's words: "Moveset: Glen Kluger (Urban Reign biker gang leader) or a fitting Tekken character"); roster: `game/js/roster-full.js:356` (`{ id: 'cainelias', name: 'CAIN ELIAS', title: 'The Deadman', ... moveset: 'cainelias' }`); moveset list: `game/js/movesets.js:54` (`'cainelias'`) | already in code, no change — with the note below |
| UR gang / story names | DROPPED | `git grep HEAD` over `game/js` + `game/index.html`: **0 hits** for "Brad Hawk" and **0 hits** for "Green Harbor". No UR story name reaches the game | already in code, no change |

**Glen Kluger note (recorded, not a rename):** the wired animation bank for
Cain Elias is King (`game/js/fighter.js:104` — `'cainelias': 'king'`), i.e.
the "fitting Tekken character" alternative CANON.md:1273 allows — not a Glen
Kluger UR bank. The identity mapping (Glen Kluger → Cain Elias's moveset
source) is true as the map states it; the bank wiring is a separate fact for
the coordinator, not something this rename lane changes.

### NOT VERIFIED in code — region damage (1 row, flagged)

| UR row | Canon name | What was checked | Verdict |
|---|---|---|---|
| Body-region damage | Region damage | The mechanic is measured in UR (TEARDOWN-PART-C §6b: head / upper / lower each injured, then destroyed; direction = body region). In WH code at HEAD: **no** "region damage" / "body region" string anywhere (`git grep HEAD`: 0 hits across `game/js`, `CANON.md`, `DESIGN.md`, `ROSTER.md`); combat uses hit levels (`h`/`m`/`l`, `game/js/combat-core.js:18–35`) and the brawler deals flat damage (`brawler.js:950` — `dmg = phb.move.damage * p.stats.power`, no per-region multiplier). | **NOT VERIFIED — nothing to rename.** No player-visible string uses another name for it, so no (c) edit is owed; no decode is awaited (the UR mechanic is already measured). Whether the mechanic is implemented, planned, or only named in the map is a build question for the coordinator. This lane did not invent an implementation and did not mark the row "already in code" without file + line evidence. |

---

## §3 — Redux CONFIRMED rows (5/5 already in code — workspace sources)

All five are sources on disk in `~/workspace/urban-reign-redux/`, verified
first-hand by this lane (sizes + SHA-256 + zip listings). None of them is a
game-code change; the map's CONFIRMED rows for Redux are about the sources
existing and being verified.

| Redux row | Canon name | Evidence | Verdict |
|---|---|---|---|
| Mod Manager 0.5 V97 zip | Redux build source | `Urban.Reign.Redux.Mod.Manager.0.5.V97.zip`, **1,176,180,939 B** on disk; SHA-256 `ad222bad1d0cd1a03672bc88e0132e63ceb15ce0129a406b69b925ceb2f0f6d6` — matches the author's hash (map §3) | already in code (workspace source), no change |
| Editor 0.5 | Redux build tools | `Urban.Reign.Redux.Editor.0.5.zip`, **54,476,021 B** on disk; SHA-256 `883387a9d3b78e7c38270697dfe46ddc72dc4958b062bbdb7e1c86f32cc3f7ef` — matches the author's hash; zip holds **1,081 files** (non-dir), matching the map's count | already in code (workspace source), no change |
| `roster-lib` | Decode tools | Inside the Editor zip: `Source/vendor/` = **87 files**; `gyu_decode.py`, `ppk_index.py`, `vmd_mesh.py` all present (under `Source/vendor/roster-lib/` + `toolnative/` / `native/`) | already in code (workspace source), no change |
| `Source/editor/` | Editor source | Inside the Editor zip: **36 files** | already in code (workspace source), no change |
| `Source/web/` | Web reference | Inside the Editor zip: **15 files** | already in code (workspace source), no change |

Note: the Redux all-in-one package is still NOT on disk (Google Drive
quota-blocked; retry Sun Nov 8 ~7:18 PM CST per the map). That row is
UNMEASURED in the map and is not a CONFIRMED row — nothing was done about it
here.

---

## §4 — Verification pass: "Devil" / "Jin Kazama" / "Ogre" / "Force" in HeartMind code

Grepped `game/js/heartmind.js`, `brawler.js`, `heartmind-campaign.js`,
`menus.js`, `mainmenu.js` (HEAD content), plus a `game/`-wide sweep for
context. Classification: **canon-correct** / **covered by a CONFIRMED rename**
/ **needs a Jay call (PROPOSED) — left alone**.

### "Devil"

| Occurrence | Player-visible? | Classification |
|---|---|---|
| `mainmenu.js:55` — menu description "…Tekken 5 Devil Within style. Pick a soul and descend." | **YES** | **Covered by CONFIRMED rename → changed (§5).** The mode's canon name is HeartMind (§0); "Devil" never appears in a HeartMind name (§5.3). |
| `roster-full.js:93` — DIABLO title `'The Devil Soul'` | **YES** | **Needs a Jay call — left alone.** No CONFIRMED replacement name exists. Map §5.3 says the phrase belongs in canon docs only, never in game UI — but gives no UI replacement. Listed as Jay call #14. |
| `attires.js:232` — DIABLO Attire 2 label `'ATTIRE 2 · DEVIL GOD'` | **YES** | **Needs a Jay call — left alone.** Same as above; no CONFIRMED replacement. Listed as Jay call #14. |
| `brawler.js:2–3, 5, 16–18, 43, 172, 621, 814, 857, 875, 1154, 1167, 1236, 1284` ("DEVIL WITHIN BRAWLER" header; "Devil Gauge analog"; "Devil Within's healing gems"; "Devil Within packs/clones/auto-face…") | No — code comments | **Provenance attribution, not HeartMind names. Left alone.** This lane's (c) rule covers player-visible strings only; rewording comments is not a rename and was not ordered. |
| `heartmind.js:5–6, 13–14, 20, 367` ("Devil Within-style action mode"; "T5 Devil Within skeleton"; "Devil Within brawler") | No — code comments | Same — left alone. |
| `heartmind-campaign.js:7` ("T5 Devil Within skeleton") | No — code comment | Same — left alone. |
| `fighter.js:688, 923, 955, 3127` ("Devil Within devil-form analog"; "Devil Jin needs a FULL Devil Gauge") | No — code comments | Same — left alone. |
| `game/index.html:437` (HTML comment) | No — comment | Same — left alone. |
| `stage-levels.js:20`, `stagebreaks.js:5` ("Devil's Pit" — a Tekken stage reference in comments) | No — comments | Same — left alone. |
| `transform-cinematic.js:9, 77` ("Devil Jin-style") | No — comments | Same — left alone. |

### "Jin Kazama"

- **Zero hits in the 5 HeartMind files.** Canon-correct.
- Elsewhere in `game/` (context, not changed): `roster-full.js:13` (RIN
  `base: 'Jin Kazama'`) and `:64` (DEMONIO `base: 'Jin Kazama'`) — data
  provenance fields, not rendered by `select-screen.js` (no `.base` render
  found there); `moveset-library.js:93` (`jin: 'Jin Kazama'` lookup);
  `moveset-browser.html:261` (same lookup); `assets.js:279–282` (comments);
  `game/README.md:43`. The map lists no CONFIRMED rename for the `base`
  field, and the Jin rule itself is a Jay call (§5.1, Jay call #10) — so all
  of it was left alone. JIN the soul (刃) is untouched: `heartmind.js`
  NINE table, `soul-spirit.js:38` (EM-Jin law comment).

### "Ogre"

- Display names are canon: `brawler.js:89` `'THE DROWNED OGRE'`, `:650`
  `'THE UNMASKED'`, `:1311` setNames. "Ogre" never appears alone in any UI
  string — **canon-correct** per the §5.2 collision rule.
- `brawler.js:73, 89, 96, 135, 224, 635–636` — internal kind key `'ogre'`
  (wave/boss spawn logic). A code identifier, not a player-visible string;
  renaming it would churn spawn logic for no player benefit. Left alone.

### "Force"

- **Zero capital-"Force" in the 5 HeartMind files.** The strings that exist
  use the canon form: `menus.js:89` ("elemental forces"), `mainmenu.js:53`
  ("Five forces") — **canon-correct** (the five elemental forces, §0).
- `DESIGN.md:55` — "Force Claiming" already exists as the system name.
- Whether DW Force = Force Claiming is a Jay call (§5.4, Jay call #13) —
  left alone.

---

## §5 — The one code change applied

**Branch:** `rename/heartmind-canon` (from HEAD `3334ebf`) — PR: https://github.com/mhvnsnt/western-heart/pull/1644 (OPEN, MERGEABLE, not merged)

| File | Change | Map citation |
|---|---|---|
| `game/js/mainmenu.js:55` | Menu description "Per-character 3D beat-em-up campaigns, Tekken 5 Devil Within style. Pick a soul and descend." → "Per-character 3D beat-em-up campaigns. Pick a soul and descend." (the source-proper-noun clause removed; no new wording invented) | §0 (mode's canon name is HeartMind; "Devil" never appears in a HeartMind name), §5.3, owner law "no source-game character names" (`docs/rules/NO-SOURCE-CHARACTER-NAMES.md`) |

Why this edit and no other: it is the only player-visible string in the
HeartMind files that uses a source proper noun where a CONFIRMED canon name
exists. Everything else "Devil" is either a comment, or a player-visible
string with no CONFIRMED replacement (Jay calls #14). The ui-sources gate
is satisfied: `game/js/mainmenu.js` is already listed under screens in
`game/ui_sources.json` (lines 54, 188); no new screen and no structural UI
change was made.

**Tests:** `node --check game/js/mainmenu.js` + the HeartMind covering
tests — see §7. No test covers the menu description string directly (no test
file references `mainmenu.js` or "HEART AND MIND WITHIN").

**Deletions:** none. `git diff --diff-filter=D` is empty (see §7).

---

## §6 — Map discrepancies found while applying (for the coordinator, not Jay)

1. **init_obj `mon` filenames (affects 6 CONFIRMED rows).** The map's
   `gym_init_obj_mon01`–`mon06` match no filename in
   `dw-motion-index.json`. The index's six monster init objects are
   `mon_power1`, `mon_power2`, `mon_speed1`, `mon_standard1`,
   `mon_standard2`, `mon_tricky1`. The map's `tk05/tk09–12/tk14–17/tk19/tk21`
   rows likewise match no index filename — the index has `tk_power1/2`,
   `tk_speed1`, `tk_standard1/2`, `tk_tricky1` (6 files) plus
   `testchr1–3`, `gym_init_obj_devil`, `gym_init_obj_jin`. (Those tk/testchr
   rows are UNMEASURED in the map, so they are outside this lane; the mon
   rows are CONFIRMED, so the filename mismatch is recorded here.) The
   decode lane must use the index's real filenames.
2. **Map §5.3 vs the nine-souls canon record.** The map says "Diablo — the
   Devil Soul, one of the nine souls (CANON.md)". `NINE-SOULS-CANON.md`
   (2026-11-08, sourced per claim from the repo's canon docs) lists the
   nine souls as RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, ZEN, GYOU — no
   Diablo. The map's parenthetical looks wrong; the rename application did
   not depend on it (DIABLO's UI strings went to Jay calls on the "Devil"
   rule alone), but the map should be corrected by whoever owns it.
3. **"Region damage" CONFIRMED status vs code.** See §2 — the name and the
   per-region mechanic are not evidenced in WH code at HEAD, although the
   map marks the row CONFIRMED. The map's CONFIRMED claim for this row rests
   on the measured UR mechanic (Part C §6b), not on the name existing in WH
   code or canon docs. Coordinator to decide whether the row's status, or
   the implementation, is the thing that needs work.

---

## §7 — Branch, PR, verification

- **Clone: BLOCKED, with the law-sanctioned fallback used instead.** A fresh
  FULL clone was attempted twice (workspace, then /var/tmp) and failed both
  times with "Disk quota exceeded". The HEAD tree is ~14.3 GB of blobs
  (measured via the GitHub API recursive tree — truncated at 60,859 entries,
  14,291,430,810 bytes), far beyond the workspace quota headroom (~500 MB
  proven writable). The commit was therefore built via the Git Data API from
  verified tree SHAs, exactly as the NO-SPARSE-COMMIT LAW prescribes
  ("When in doubt, build the commit via the Git Data API from verified tree
  SHAs — never from a working tree you haven't verified", `AGENTS.md`
  L132–139): base commit `3334ebf`, base tree
  `52e2204aca2a1ca5ce27a2b06a453069a36de3b1`; `mainmenu.js` HEAD blob
  `73e6ab642b967a1aed522e1111c637296460dbef` hash-verified before editing;
  both new blobs hash-verified against local `git hash-object` before the
  tree was built. No sparse or partial checkout was used anywhere.
- **Branch:** `rename/heartmind-canon` from HEAD `3334ebf`.
- **Commit:** `29e355f86a2ca0e582c672c8e0ae7ec5c0fc8116` (1 commit, ahead by 1,
  behind by 0).
- **PR:** https://github.com/mhvnsnt/western-heart/pull/1644 — OPEN,
  MERGEABLE, **not merged** (this lane does not merge).
- **Deletion check:** compare API base...head — 2 files modified, **0 files
  removed** (`WORKLOG.md` +40/−0, `game/js/mainmenu.js` +1/−1). The
  `mainmenu.js` patch was read back and is exactly line 55.
- **Tests run:** `node --check game/js/mainmenu.js` on the edited file —
  pass. No test covers the menu description string (no test file references
  `mainmenu.js` or "HEART AND MIND WITHIN"). CI on the PR:
  `game-unit-tests` **pass** (1m15s), `instruction-gate` **pass** (after the
  PR body was fixed to add the Law-15 sections — it first failed on the
  missing sections, not on the change), `canon-names`, `clobber-guard`,
  `coverage-guard`, `deletion-guard`, `guard`, `pr-safety-guard`,
  `rig-guard`, `ui-sources`, `material-gate` all **pass**. Still **pending**
  at report time: `budgets`, `speed-quality`, `menu-touch-e2e`
  (mergeStateStatus UNSTABLE = checks still running, not a failure).
- **WORKLOG:** entry appended in the branch (`WORKLOG.md`, 40 lines).
