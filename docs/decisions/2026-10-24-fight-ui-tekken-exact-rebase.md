# Fight UI popups, Tekken-exact — #1032 REBASE (2026-10-24, UI follow-up lane)

## Why #1032 could not merge as-is

PR #1032 ("Fight UI popups match Tekken exactly: remove 18 mid-fight
banners", branch `feature/fight-ui-tekken-exact-20261024`, base main
`0674326`) was built on a stale base. Its diff is 110 files, and most of
it is NOT the banner fix: it deletes `game/js/t3-throw.js` outright
(285 lines), strips the paired-throw wiring out of `game/js/fighter.js`
(147 lines), strips reaction-pack loading out of `game/js/t3anims.js`
(80 lines), strips music rotation pools out of `game/js/music.js`,
deletes thousands of moveset lines, deletes voice files and research
docs, and deletes teardown tools. Merging it would repeat the PR #579
clobber: main-side work added after its base would be silently reverted.
This rebased branch does NOT bless any of that with an
owner-approved-revert label — those are stale-base losses, not
intentional reverts, so none of them are carried over.

## What this branch contains (and nothing else)

Current main `b509f179` + ONLY the 18 mid-fight banner removals from
#1032, plus the banner-related test and doc updates that keep CI honest:

| File | Removed (banner call sites) |
|---|---|
| `game/js/finisher.js` | `FINISHER — <name>` (1) |
| `game/js/game.js` | `surgeName` calls, player + AI surge presentation (2) |
| `game/js/main.js` | `V-TRIGGER «name TBD»`, `V-REVERSAL «name TBD»`, `V-SHIFT «name TBD» — BREAK!`, `V-SKILL PARRY «name TBD»` (4) |
| `game/js/rage.js` | `RAGE`, `RAGE ART` (2) |
| `game/js/soul-systems.js` | release, reihou, meter-ready `_banner` calls (3) |
| `game/js/soulurge.js` | `SOUL URGE`, `URGE SMASH` (2) |
| `game/js/spirit-actions.js` | spirit-action banner (1) |
| `game/js/stagebreaks.js` | `WALL BREAK`, `FLOOR BREAK`, `BALCONY BREAK` (3) |

Total: 18 call sites, all deletions. Comment rewordings that described
banners as announcements were updated to match (rage update docstring,
soul-systems header + update comment, soulurge smash docstring,
stagebreaks header note). Nothing else in those files changed.

Kept on purpose (Tekken-exact round/mode boundaries, per #1032's own
inventory): `ROUND n`, `FIGHT!`, `K.O.`, `DOUBLE K.O.` in
`game/js/game.js`; Trial's Seal in `game/js/soul-systems.js` (the
`_banner` helper stays because the seal still uses it); the practice
`RESET — DUMMY RESTORED` banner (not mid-fight, not in #1032's 18).
The `ui.banner` function and the `#surge-name` element stay in place;
only the mid-fight call sites are gone.

Also in this branch: `test/finisher.test.mjs` + `test/soul-systems.test.mjs`
banner expectations updated to the no-banner contract (same patch as
#1032), and the `SOUL-SYSTEMS.md` Nine-Soul Release row reworded from
`SOUL RELEASE READY` callout to the `ui.setSoulReady` meter-ready
indicator (with LP1+RP2+LK3+RK4 notation added). The original #1032
decision doc is NOT copied here: its inventory is reproduced above from
this branch's own diff, so this doc cannot drift from what actually
shipped. Deliberately NOT carried over from #1032: the SOUL-SYSTEMS.md
`HEAT` → `SOUL URGE` label fix (unrelated to banners; rides another PR).

## Preservation proof (main's lines survive)

Verified by diff against main `b509f179` before opening the PR:

- Diff files: 8 JS files + 2 test files + `SOUL-SYSTEMS.md` + the
  UI-followup files (manifest, index, T3 registry, GPU script, docs).
  `game/js/fighter.js`, `game/js/t3anims.js`, `game/js/t3-throw.js`,
  `game/js/music.js`, movesets, voices, and teardown tools are NOT in
  the diff — they are byte-identical to main.
- Paired-throw wiring intact: `game/js/fighter.js` still has
  `startThrowLock` with `_throwPairFor` / `_bindThrowPair` /
  `_startThrowPair` (the #1031 wiring #1032 would have reverted).
- Reaction-pack loading intact: `game/js/main.js` still calls
  `loadReactionPack` for every bank, and `game/js/t3anims.js` still
  exports `loadReactionPack` / `getReactionPack`.
- Removed-banner strings: zero remaining banner/`surgeName` call sites
  for all 18 strings across the 8 edited files (grep-verified).
- Syntax: `node --check` passes on all 8 edited JS files and both
  edited test files. Tests: `node test/soul-systems.test.mjs` →
  15 passed; `node test/finisher.test.mjs` → 30 passed, 0 failed
  (matches #1032's own claims exactly).

## Merge order + popup-lane coordination (read before merging)

- This PR's `game/js/main.js` diff is banner lines only (ui object).
  PR #1056's `main.js` change is a router edit on an old base, and
  #1061's stage-preload change lives in a different region. Merge with
  the real 3-way merge (`git_merge.py`): neither region overlaps the
  banner lines, so neither change is clobbered. Do NOT merge this PR
  by applying its old-base file copies anywhere.
- POPUP LANE JUMPS THE QUEUE (user 2026-10-24 20:56 CDT: popup fix is
  Priority #1, deploy FIRST; combos/anims are Priority #2 and follow
  only after the popup deploy is verified live). A dedicated popup-fix
  lane is auditing EVERY fight popup. This PR's 18 deletions are the
  #1032 subset of that audit — identical deletions merge cleanly under
  3-way merge, so the coordinator may merge either PR first and let
  the other rebase; do NOT merge both blindly without checking the
  overlap. This PR does NOT own the full popup audit: it does not
  touch `modes.js` / `episodes.js` / `heartmind.js` / `ranks.js`
  between-bout banners, any CSS sizes/positions, or the TBD naming
  path (see below). The popup lane owns those.
- The user's 20:56 verdict names "V shift", "rage", "time shift", "TBD
  stuff" popping up real big mid-fight. This PR removes exactly the
  V-System `«name TBD»` banners, the `RAGE` / `RAGE ART` banners, and
  the other 13 mid-fight banners above. If the user still sees big
  words after this deploys, the next suspects are the between-bout
  banners (`modes.js` FIGHT/WAVE/REBORN lines, which fire between
  bouts, not mid-exchange) — that is a playtest question for the
  popup lane, not a silent scope expansion here.

## TBD placeholder path: NOT deleted here (popup lane owns it)

This PR removes the 4 V-System `«name TBD»` banner CALLS. It does not
delete the TBD naming path: `game/js/v-system.js` still carries
`V-SKILL «name TBD»` names in its data, and the `main.js` V-System
comment still flags names as TBD pending owner approval. The popup
lane deletes the TBD placeholder path entirely (not resize, not
restyle). Playtest must confirm no `«name TBD»` text renders anywhere
during a fight; if it does, that is the popup lane's item.

## Tracked open items (recorded, not faked, not claimed done)

- ANNOUNCER CALL SITES (audio lane #1058 shipped the event table +
  pure resolver, `announcer-events.json/js`, for round-start/fight/KO/
  double-KO/perfect/time-up/draw/win — but NO `voice.announce()` call
  site exists in `main.js`, `game.js`, `modes.js`, `fighter.js`,
  `select-screen.js`, `episodes.js`, `versus-setup.js`,
  `stage-intros.js`, `combat-core.js`, or `wh-boot.js`). The engine
  (`voice.announce`) exists; the manifest holds 11 clips, ALL
  subtitle-only placeholders, file null — NO announcer audio bytes
  exist in the repo. Character-select has NO clip (needs-recording,
  clipId null, no line invented, no synth presented as final).
  Select-side wiring is a UI-lane follow-up AFTER #1056/#1058 merge
  (wiring it here would touch `select-screen.js` and fight the
  ui-sources gate + #1056); fight-side wiring belongs to the
  `fighter.js` owner.
- TREASURE MUSIC CALL SITE (audio lane #1058 contract): the engine
  reads the `wh_jukebox_v1` choice (same key #1056's UI writes), but
  treasure has NO music call site yet, so a stored treasure choice is
  read but UNPLAYED. Owed by whoever owns modes/music call sites.
  Victory jingle untouched.
- LIVE PHONE PLAYTEST (coordinator browser lane — this lane has no
  live browser): trigger rage, Soul Urge, wall/floor/balcony break,
  Soul Surge, Spirit Action, Nine-Soul Release, Reihou, and a finisher
  in a versus fight; confirm no big center text mid-fight while
  ROUND, FIGHT, and K.O. still show at round boundaries; confirm no
  `«name TBD»` text renders; confirm the online hub rows, collection
  hub, daily board button, howto LP1/RP2/LK3/RK4 rows, movelist,
  modewin, and reincarnate screens all render phone-first with no
  modal covering a preview.
