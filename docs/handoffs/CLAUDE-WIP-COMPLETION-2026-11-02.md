# Claude WIP completion — 2026-11-02

Owner order (2026-11-02): "Get all this done that didn't land or that was infinite left open, then get it done 100%, and also add to any of the parts or systems that did get done or landed but aren't 100% complete." Claude is out on his weekly limit until Nov 6 10:00 AM; this lane (Ashes) picked up his open PRs #1486/#1488/#1489 and audited his landed #1491/#1492/#1493. **No deploy was made** — the republish stays held for the owner's playtest.

Main when the lane started: `9a2e6d60`. Main when it finished: `d9a02cfb`.

## What was open, and what happened to it

| PR | State found | Outcome |
|---|---|---|
| #1488 select-screen sweep | open draft, mergeable, checks green (one stale-payload instruction-gate failure at 01:05Z, superseded by a green re-run at 01:07Z) | Marked ready, **merged as-is**: merge commit `48b2b1e2` |
| #1486 suite Phase 1 + attire switch fix | open draft, CONFLICTING | Hunk-by-hunk supersession audit (scratch analysis, 10 files, 3-way merge per file): most was already landed by #1475/#1490/#1491/#1492/#1488. The still-missing remainder was hand-merged and landed as successor **PR #1494, merged `6a34bf70`**. #1486 closed with a pointer comment (6575359151) |
| #1489 suite Phase 3 morph targets | open draft, CONFLICTING, stacked on #1486 | Audit first: the "templates baked without morph targets" lead was **wrong for this branch** — its GLBs carry 168 targets each (independently verified, below). Conflicts were only 3 files / 1 hunk each. Landed as successor **PR #1495, merged `e1be1b5d`**. #1489 closed with a pointer comment (6575704684) |
| (follow-up #1489 itself disclosed) game scene never reads morph state | `game/js/custom-fighter.js` byte-identical to pre-Phase-3 main; `morph_targets` silently dropped | **PR #1496, merged `d9a02cfb`**: passthrough + application in the game scene (below) |

## #1494 — what the #1486 salvage kept, and what it dropped

Kept (verified absent on main before, present after): select-screen attire cycling (`cycleAttire()` — the △ button previously always re-picked attire 1), `game/select.css` attire-state styles, `game/index.html` attire label span, `game/js/asset-config.js` remoteBase fallback for shell-bundled models, the suite left sliding panel (`suite.js` slide-in + left-aware `viewer.setInsets()`, `suite-t7.css` left rail + landscape topbar fix), generic template names/body types in `body-templates.json`, WORKLOG diagnostics.
Dropped: the `attires.js` hunk (its 3-way merge result is byte-identical to main after #1488 — superseded) and the branch's stale ORDER-doc Status (main's kept; the phase table was rewritten to landed reality).
Never done: no file was taken wholesale from the stale branch, so #1490's POSE & PICTURE and #1491's jsDelivr suite loader are intact (merged `suite.js` verified to contain both `fetchRepoJson` and the slide-in hunks).

## #1495 — Phase 3 morph targets, landed

- 9 template GLBs re-baked (Blender + MB-Lab), blob-identical to #1489's head. Independent verification during the audit: two GLBs (powerhouse 2,071,032 B, striker-w 2,028,340 B) were downloaded and parsed — `extras.targetNames` = 168, 168 targets on every primitive, 71-joint skins, meshopt + quantization; all 9 are 2,028,340–2,099,592 B (18,523,980 B total).
- Catalog `customization/templates/morph-sliders.json`: 84 sliders (Body Morphing 32 in 10 groups, Face Deformation 52 in 12 groups) → 168 targets per template.
- Suite side: `customization/creation-suite-ui/js/morph-targets.js` (`applyMorphTargets`), suite BODY/FACE windows, values saved to `body.morph_targets` / fighter state / localStorage / attire record; proof frames + probe output in `customization/creation-suite-ui/proof-pass/phase3-morphs/` (portrait + landscape).
- Tests: `packages/creation-suite/test/morph-targets.test.js` (7 node tests) + `tools/creation-suite/morph_probe.cjs`.
- Conflict resolutions: suite boot keeps #1491's `fetchRepoJson` and adds `loadMorphCatalog()`; the suite importmap keeps #1492's game-vendor three path and adds the meshopt decoder entry; ORDER doc status rewritten.

## #1496 — morph state now reaches the game scene

- `game/js/custom-fighter.js`: `customFighterToRoster` now returns `morphTargets` (from `body.morph_targets`), `template`, and `baseGlb` instead of dropping them.
- New `game/js/morph-apply.js`: game-side twin of the suite's application module (identical `<id>+` / `<id>-` convention, clamped −1..1, stale slider targets reset, non-slider targets untouched, no-target models a no-op).
- `game/js/fighter.js`: `Fighter._applyCharMorphs()` runs in `_build` and after the transform model swap (`_doModelSwap`); the live-influence count is stored on `model.userData.morphInfluencesApplied`.
- Tests: `game/tests/morph-apply.test.mjs` — 6 node tests, run locally before push (6 pass) and in CI (game-unit-tests green).

**Still open (owner-gated, deliberately not shipped):** the in-fight model still resolves through the `custom` slot (legacy Soldier base, which has no morph targets), so influences only land when the built model carries targets. Swapping the in-fight/select model to the fighter's template GLB is the remaining Phase 4b step; it changes which rig the fight animation binds to (MB-Lab 71-joint template vs the current base) and needs a fight-animation proof + playtest before it ships. The ORDER doc's Phase 4b row says the same.

## Audit of the landed systems (#1491 / #1492 / #1493) — numbers from actual runs at 9a2e6d60

Raw outputs: lane scratch `~/workspace/_claude-wip-finish-20261102/out/` (plan.md/json, stance.md/json, xray logs) and `analysis-audits.md` in the same folder.

### Move clip coverage — `tools/anim/plan_coverage_audit.mjs` (note: not tools/input-verify/)
59 fighters, 16,696 moves: **1,403 would play no clip — all of them in the 6 fighters with no T3 bank**: megami 324/324, zen 324/324, pond 312/312, ryusan 226/226, ryuji 142/142, vainabel 75/75. **The other 53 fighters are at 0.** Tool caveat (its own header): real T7 clips are not loaded in Node, so it is conservative. Cross-check: the repo's `docs/movesets/MOVE-CLIP-COVERAGE-2026-11-02.md` from #1491 reports the identical table.
- pond / ryusan / megami are SmutBase-six fighters — their moves coverage is owned by the running SmutBase lane (their canon bases per the 2026-10-23 decisions doc: Raven / Lucky Chloe / Jun Kazama). tobi, chatur, menajerii are already at 0 here.
- zen, ryuji, vainabel have no bank assigned at all; assigning a bank is a canon/base decision, not a step-plan promotion — **owner-gated, not fabricated here.**

### Stance reachability — `tools/input-verify/stance_reachability_audit.mjs`
55 fighters, 15,737 inputs, 5,577 stance-prefixed: engine context 2,859 · stance-entered 1,258 · chain-throw 97 · **NO ENTRY 1,363 (can never fire)**. #1491's fixes cut this from 2,237 → 1,363; the remainder is concentrated: byou 257, phantom 164, rave 126, koreshi 111, pond 80, cyborgx 65, torch 44, pantera 40, awapop 39, zui 36, bruno 35 (15 fighters at 0). Biggest unentered prefixes: TACKLE 118, DRU 96, NSS 91, SNA 56, DRG 48, KIN 48, PHX 42, LAB 39 (pond), SAV 35, PAN 33, FLE 33, DES 32. These are stance-entry mechanism gaps (no move/engine context enters the stance), **not** step-plan rows — the Pantera promotion rule does not apply to them, and no promotions were fabricated. They need per-stance engine work or owner adjudication, easiest first: single-fighter prefixes (LAB/SZN pond, SAV bruno, DES cyborgx) before cross-roster ones (TACKLE).

### #1492 (suite starts on live build; arena ring) — VERIFIED COMPLETE, and live
Both halves are on main and inside the shell-only deploy set by construction (`tools/deploy/build_pages.py` ROOTS include `game/**` and `customization/creation-suite-ui/**`; all three runtime files are small text). Stronger: the live `deploy-manifest.json` is exactly #1492's merge commit `212e7fb6` (shell-only, 2,139 files, delta "3 updated, 0 added, 0 removed" — its three runtime files). Nothing remained to fix.

### #1493 (X-ray anatomy jsDelivr fallback) — VERIFIED COMPLETE on main; rides the held republish
- Code on main: `game/js/xray.js` prefetches page-first, then `ASSET_CONFIG.jsdelivrBase + '/' + rel` on failure.
- The browser check (`tools/proof-harness/xray_anatomy_live_check.cjs`) could not be re-run from this VM (live run: proxy tunnel failure to the Pages host; local run: Chromium target crash in the sparse checkout) — environment limits, not game failures. Claude's documented run for #1493 (page 404 → jsDelivr loads, PASS) stands in `docs/proof/2026-11-02/xray-anatomy-live/README.md`.
- Fallback leg verified directly by this lane: all **43** fighters that have `roster/<fighter>/anatomy/anatomy-layers.json` on main return HTTP 200 with valid `wh.anatomy-layers/2` JSON from `cdn.jsdelivr.net/gh/mhvnsnt/western-heart@main/...` (42 on first pass; skull's single 403 was transient — 200 on three retries). Fighters with no anatomy directory on main (e.g. burger, negativo, star) have nothing to resolve.
- Live-build note: the live deploy is still #1492's commit, so the X-ray fix reaches players with the next republish — which is held for the owner's playtest by the standing order, same as #1475/#1494/#1495/#1496.

### Creation suite end-to-end (after this lane)
Template select (#1475 + #1494 generic data) → body/face morphs (#1495, applied live in the suite preview) → attires/parts (suite) → pose & picture (#1490, saves to the on-device portrait store) → save (suite record) → game side: `custom-fighter.js` reads the suite key and now carries morphs/template into the roster object, and `Fighter._build` applies morphs to the built model (#1496). The one remaining seam is the Phase 4b model swap noted above.

## Merge record (all verified on main by re-reading main's HEAD after each merge)
- #1488 → `48b2b1e2` · #1494 → `6a34bf70` · #1495 → `e1be1b5d` · #1496 → `d9a02cfb` (main HEAD at lane end, before this handoff doc's own PR)
- Every PR: instruction-gate + all guards + game-unit-tests + menu-touch-e2e green before merge; no file deletions in any of them.
- #1486 and #1489 closed as superseded, with pointer comments (6575359151, 6575704684).

## Not in this lane's scope (untouched, still running elsewhere)
SmutBase-six model/texture/moves lane (owns pond/ryusan/tobi/menajerii/megami/chatur models — including their bank/coverage work), Steam wave-5 store lane, the B2 bucket uploads, and the held republish.
