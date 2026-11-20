# UI + FRONT END + MENU SYSTEMS + MODES — "ANYTHING ELSE" SWEEP
## Lane 3, 2026-10-24 | Source: docs/research/GAP-ANALYSIS-EXPERIMENTAL-PROJECTS-2026-10-24.md (PR #1033 gap doc) + live repo files on main

Audit method: every file below was read from main (via GitHub API) and
grepped before any claim was made. "PRESENT" means the code was read,
not that the feature was playtested on a phone — live phone play
verification is delegated to the coordinator (parent browser lane).

## Named gaps — verdicts after this PR

| Gap | Before | After this PR | Source |
|---|---|---|---|
| Gap 12 Gallery | Forge placeholder only (`mainmenu.js` FORGE.gallery) | REAL screen: Endings / Episodes / Unlocked tabs, WH content only | T7 gallery SYSTEM STRUCTURE (gap doc); content from `game/js/story-endings.js` + `game/js/episodes.js` + `game/js/unlockables.js`. NEVER Tekken FMVs (canon law) |
| Gap 13 Treasure Battle | No mode (`treasure` absent from `modes.js`) | REAL mode: endless waves, chest after every win (10–50 coins + one still-locked unlockable), coins kept on loss, best-wave record | T7 Treasure Battle structure (gap doc); loot pays into `game/js/unlockables.js`; wave pattern follows Survival in `modes.js` |
| Gap 14a Favorites | Absent (zero matches in `select-screen.js`) | REAL: ★ SAVE FAVORITE + FAV 1–3 recall (fighter + attire chip) | T7 v5.10 favorite character+costume (gap doc Gap 14) |
| Gap 14b Last-attire memory | PARTIAL: `attires.js` persists attire per fighter; `select-screen.js` parks P1 cursor on last confirmed fighter (`wh.select.last.v1`) | Completed with an explicit per-fighter session record (`wh_select_last_attire_v1`) the favorites bar reads/writes | Same sources; the pre-existing persistence is NOT re-claimed as new |
| Gap 14c Tournament lock | Absent | REAL toggle in Options; when on, favorites bar shows the lock note, save/recall are refused, and a MutationObserver keeps attire chips disabled on select | T7 v5.10 tournament settings lock (gap doc Gap 14) |
| Gap 14d Streaming mode | Display already compliant: `menus.js` showVs renders fighter names, never player IDs | Toggle ships in Options and gates VS display via `vsDisplayName()`; online ID display remains the online lane's follow-up | T7 v5.10 streaming mode (gap doc Gap 14) |
| Gap 15 VS / result depth | VS: name + title + stage + mode only. Result: REMATCH / MAIN MENU only. Versus banter data existed but NO screen rendered it (zero callers in `menus.js`/`main.js`) | VS now adds rank (best tier from `wh_ranks` via `ranks.js`), W-L (new `versusWL` record written by `modes.js` on every versus bout), LOCAL BOUT label, and the picked banter exchange. Result adds CHANGE FIGHTER | Gap doc Gap 15; rank store `game/data/ranks.json` via `ranks.js`; banter picker `game/js/versus-banter.js` |
| Gap 20 Replay theater | Analysis only (`replay-analysis.js`); no save/share/theater UI | REAL theater: save / list / timeline review / analyze (via `analyzeReplay()`) / export JSON / import JSON / delete | T7 replay theater structure (gap doc); contract v1 from `replay-analysis.js`. Playback NOT claimed (see Honest gaps) |
| Gap 21 Frame overlay | Tables only (`frame-tables.js`); no live overlay | REAL toggle in Options + corner overlay polling `window.__game.p1/p2` (`attackName`/`attack`/`state` from `game.js`); numbers shown ONLY when numeric on the live object, else "frames n/a" | Gap doc Gap 21; `frame-tables.js` shape for field names |
| Gap 11 Jukebox (UI side) | Forge placeholder only | REAL UI: per-mode soundtrack choice (menu / arcade / treasure / versus), only available tracks listed | T7 jukebox structure (gap doc); engine rule from `music.js` (`_available`: file or remote). Engine playback wiring is the AUDIO lane's follow-up, NOT claimed here |

## "Anything else" sweep — everything else checked

| Element | Verdict | Evidence |
|---|---|---|
| Main menu structure (rail + slide-in submenus + player card + news) | PRESENT | `game/js/mainmenu.js` (T8-style rail, SUBMENUS), `game/index.html` screen-menu |
| Character select (T7 teardown layout, T8 grid, attire chips, LP1 punch = attire 1 / kick = attire 2) | PRESENT | `game/js/select-screen.js`, `select-t7.css`, `select-t8.css` |
| Stage select (sticky header, preview pane, tier-grouped grid) | PRESENT (Lane 4) | `game/index.html` screen-stage, `main.js` buildStageSelect |
| Options (sound / graphics / controls) | PRESENT, extended by this PR | `game/js/menus.js` openOptions |
| Versus setup (T7 GAME OPTION: fight count, round time, guard damage, stage mode) | PRESENT | `game/js/versus-setup.js`, `game/js/rules.js` |
| Pause / loading / records / story dialogue screens | PRESENT | `game/js/menus.js` buildOverlays |
| Side-games menus (Go Qombat, Trader's Mimic) | PRESENT as mode cards + modes | `mainmenu.js` sidegames submenu, `modes.js` qombat/trader |
| Story menus (Trial, episodes, Heart and Mind Within) | PRESENT as mode cards + modes | `mainmenu.js` story submenu, `modes.js` story, `episodes.js`, `heartmind.js` |
| HUD (health, Nine-Soul Meter, timer, round pips, pause button, mode tag) | PRESENT | `main.js` ui object, `game/index.html` hud |
| Loading screens (real progress + creep cap) | PRESENT | `game/js/load-progress.js` |
| Creation suite menus (sub-menus + categories) | NOT RESTRUCTURED HERE — see below | Suite lives outside `game/` (`customization/creation-suite-ui/index.html`, reached from `main.js` mode-create). Its sub-menu structure was NOT traced to PRs #770/#773/#775/#776/#777/#778 in this pass, so any claim about it would be UNSOURCED. It is NOT flattened or rebuilt by this PR; a dedicated creation-suite pass must source its structure first |
| Shop system | NO standalone shop screen found in `game/`; currency/loot hooks exist (`identity.js` economy, `unlockables.js`) | Marked as a follow-up, not invented here |
| Dialogue system | PRESENT (story beats + versus banter data + intro system) | `menus.js` playStoryBeats, `versus-banter.js` |
| Minigame menus | PRESENT via side-games submenu + `side-games.html` | `mainmenu.js`, `game/side-games.html` |
| Big center-screen fight popups | AUDITED: zero "WALL BREAK"/"TIME BREAK"-style text in any file touched (`mainmenu.js`, `menus.js`, `main.js`, `versus-setup.js`). The existing `round-banner` (`main.js` ui.banner, 1400ms transient) is Tekken-style round announcement and was left untouched | UI IMMERSION LAW honored; no new fight popups added |

## Honest gaps (not papered over)

1. **Replay fight playback**: no recorder has merged to main
   (`replay-analysis.js` header: worker 29's recorder "has NOT merged
   to main yet"). The theater therefore offers timeline review +
   analysis + share, not deterministic playback. Unblock: recorder
   merge, then theater plays via the same contract events.
2. **Jukebox engine wiring**: the UI stores per-mode soundtrack
   choices (`wh_jukebox_v1`, read via `getJukeboxSoundtrack()`); the
   music engine does not yet read them. Unblock: audio lane reads
   the store in `music.js` track selection (engine file, not this
   lane's).
3. **Online connection bars**: local bouts honestly show LOCAL BOUT.
   Measured 0–5 bars render only when the netplay layer supplies a
   measurement (`vsMetaLines` accepts a number); no measurement is
   invented for local play. Unblock: online lane exposes connection
   quality to `showVs`.
4. **Creation-suite menu structure**: UNSOURCED in this pass (see
   table). No teardown-based restructure is claimed.
5. **Shop system**: no standalone shop screen; not invented here.
6. **Live phone play verification**: this lane cannot use a live
   browser. Code-level checks done instead (see PR Proof). Live
   phone playtest of every new screen is delegated to the
   coordinator as parent browser work.

## Mobile conformance (this PR)

- Every new tappable element uses the PR #1018 `tap()` pattern
  (touchend + click, 12px scroll-drag guard, 600ms dedup) — the
  helper is exported from `game/js/ui-gaps.js` for reuse.
- Every new button is >= 44px (`ui-gaps.css`: 48px min-height).
- No hover-only controls. Overlays scroll; the favorites bar wraps.
- The favorites bar sits BELOW the select preview panes (in the
  hints row) and never covers a preview. Gallery/jukebox/replay
  overlays open from the main menu only, never over a fight or a
  select preview.
- Button names in all new user-facing text: LP1/RP2/LK3/RK4.
