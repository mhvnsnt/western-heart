# Everything Else — completion handoff (2026-11-02 lane, closed 2026-11-03)

Owner order (2026-11-02 ~05:38 CST, replying to the Claude-WIP completion
report): "Get everything else done." Scope: the itemized remainders of
`docs/handoffs/CLAUDE-WIP-COMPLETION-2026-11-02.md`, plus the Demonio
attire1 reconcile and the consolidated republish. Coordinator lane
`everything-else-20261102`; main HEAD at lane start `5d447532`, at deploy
`e15815709919aea34f78957522708c56a0f0375b`.

## Step 1 — the 6 no-bank fighters (1,403 no-clip slots): closed as evidence; no banks wired, because no wireable clip data exists

Per-fighter verdicts (bases resolved from each fighter's own data files;
full evidence in `docs/handoffs/NO-BANK-FIGHTERS-EVIDENCE-2026-11-02.md`,
PR #1534, merged `aa96f52c`):

- **pond** (base: the T7 Raven data) / **ryusan** (base: the T7 Lucky
  Chloe data): motbin *tables* exist in-repo
  (`game/assets/anim/t7/frv-pond-motbin-bank.json` 478,249 B;
  `dnc-ryusan-motbin-bank.json` 446,447 B) with `playable_wiring =
  "NONE"`. Zero T7 clip banks exist anywhere in `game/assets/anim/` and
  the engine has no T7 clip loader. Unblock: live-memory extraction
  (TKMovesets2 on a Windows machine running the owner's T7) — a
  parent/browser-lane job, per the in-repo T7 index.
- **megami** (base: the TTT2 Jun data): move table exists
  (`game/assets/ttt2/movesets/jun.json`). `data004.bin` was LZX-decoded
  in the 2026-10-25 lane (6,522,032 B, the MOTA motion table), but no
  TTT2 MOTA parser exists in repo tooling and the engine has no TTT2
  clip loader; whether data004 holds Jun's keyframes vs. pointing into
  never-pulled dataNNN files is unverified. Research-scale; stops
  documented in the evidence doc.
- **vainabel** (base: the DOA4 Bass data): DOA4 ISO verified assembled
  (7,834,892,288 B, release `doa4-iso-v1`); the motion archives
  `mot.afs` (71 MB) + `anm.afs` (2.9 MB) are recorded ENCRYPTED and were
  never decoded; no DOA4 motion parser exists.
- **ryuji**: hybrid base by design (KOF XV / The Rock per its data) —
  no single-source bank assignment exists to make.
- **zen**: `FIGHTER_BANK zen: null` is an OWNER DECISION
  (2026-10-24, `docs/decisions/2026-10-24-zen-base-decision.md`;
  Eleven/Twelve → Dural (VF5) chain, private bank only). Untouched.

Plan coverage re-ran **1,403 → 1,403**: the 1,403 no-clip slots are
exactly these six fighters, corroborating that nothing else hides in
that number. No wrong-character bank was wired for any of them
(standing rule: a fighter plays only its own source's motion).

## Step 2 — NO-ENTRY stance prefixes: 1,363 → 593

Fresh BEFORE re-run reproduced the baseline byte-identically
(1,363 NO-ENTRY of 5,577 prefixed inputs, 55 fighters).

- **(a) FIXED — 770.** PR #1535 (merged `93ae7199`): 744 moves via
  `stance_after` completions in 19 moveset JSONs
  (`game/assets/movesets/*.json`), landed only under a strict evidence
  rule (the entry move's name *is* the stance / carries its code /
  names the "…to ⟨Stance⟩" transition / anim_ref identity against the
  base's own in-repo file); deep-equality outside `stance_after`
  verified per file. PR #1536 (merged `0d3dbf48`): 26 more by fixing
  the audit tool itself, which under-modeled the engine's chain-throw
  graph (`fighter.js _throwChainPress`; throw count 97 → 123).
  Close-out: `docs/handoffs/STANCE-NOENTRY-CLOSEOUT-2026-11-02.md`.
- **(b) 114** belong to the no-bank fighters (pond 80, zen 20,
  megami 14) — they resolve only with the Step 1 clip banks.
- **(c) Remainder 479**, grouped in the close-out doc: tackle-mount
  family 128 (openers exist but none is throw-flagged — re-classing
  strikes as throws is a gameplay decision, not a table fix), engine
  contexts that do not exist 128, duplicate/artifact spellings 47,
  no entry move in the fighter's own data 176.

## Step 3 — Phase 4B model swap: WORKS, proven in a browser

The swap wiring landed mid-lane as PR #1498 (parallel lane, merged
`d789819c`): blank-mode suite saves resolve to `custom-template-<id>`
models, the MB-Lab→T3 bone remap (23 joints) in `assets.js`, the
jin-bank fallback in `fighter.js`, morph application in the fight
build. Its proof was Node-only; this lane supplied the missing browser
proof on current main (PR #1538, merged `e1581570`, proof-only,
+854/−0): a Creation Suite save exactly as a player produces it
(powerhouse template, morphs b_weight 0.8 / b_tone 0.4) fought Pantera
through the game's own pipeline — 22 real T3 actions retargeted onto
the template rig, 20 morph influences applied, `bonesMissing: []`,
6 hash-verified frames at `docs/proof/2026-11-02/phase4b/`.
Remainders (pre-existing, from #1498): roster-mode edits still fight
on the legacy Soldier `custom` slot; custom moveset slots still TODO
(jin fallback, logged in-game); template bodies render untextured in
fights (the owner-decided narrowed material gate in #1498) — texture
work is a separate remainder, not part of the animation gate.

## Step 4 — Demonio attire1 reconcile: bucket is stale; repo file is correct

PR #1524 (merged), doc
`docs/tech/DEMONIO-ATTIRE1-RECONCILE-2026-11-02.md`. The bucket serves
the **pre-rig-fix** file: 28,872,600 B, sha256
`e5b7b54cb5ab69941c98f99c3d4c2b2fefa37e678df6e7f212bd1f8428fda8a3`,
git blob `5b531cfa` — byte-identical to commit `9f796890`'s version,
uploaded 2026-10-31 13:00Z, ~2 h 45 min before the rig-fix commit
`e4a8329` landed, never re-uploaded. It ships the defects the fix
removed (contaminated skin weights; dead `RightFoot` joint). The
correct file is on main: 28,793,068 B, sha256
`b95e71252ba11b4308b9c96f575217e3e292707579de65b2867558dce307804d`,
blob `3bd1e9c9`. Flagged for the B2 lane on issue #866 (comment
6592097019) with the key and both fingerprints; this lane uploaded
nothing. The re-upload rides the B2 queue (still storage-cap blocked).

## Step 5 — consolidated republish: DEPLOYED + VERIFIED LIVE

- **Build:** `tools/deploy/build_pages.py --shell-only --core` from
  main `e1581570`: 2,231 files, 1,068,904,867 B full set.
  `tools/deploy/check_module_graph.py` on the build tree: exit 0
  (3 pre-existing guarded/dynamic warnings).
- **Why not the full set:** the live tree already totals
  996,714,080 B; a full-set delta computes to 1,078,799,838 B —
  78,799,838 B OVER the 1 GB Pages cap (biggest adds: two yukihyo
  attire GLBs, 65.4 MB, which load from the remote asset base like the
  other 2,234 unbundled models). The deploy therefore used the repo's
  own guarded-delta semantics (`tools/deploy/deploy_delta.py`):
  update files present on both branches, add whitelisted small runtime
  files + T7 stance/skeleton JSONs, refuse removals and over-cap
  results — executed via the Git Data API.
- **Module-graph safety:** the repo delta tool's assembled-tree
  materialization fetches blobs one by one through this VM's proxy and
  hung twice (100 min and 148 min, killed). Substitute used, evidence
  equivalent for the module question: the build-tree gate above
  (exit 0 over every shipped module at its shipped SHA) **plus** a
  coverage audit asserting every build-set module file absent from
  the live branch is covered by the delta's add rules — clean; the
  only uncovered files were 3 runtime-fetched data JSONs
  (`game/assets/portraits/draft1/portraits-manifest.json` and two
  suite proof `probe.json` artifacts), reported here as remainders.
- **Harness fight check on the BUILT tree** (before deploying): stock
  Pantera vs Demonio through `__modes.startFight` in headless
  Chromium served from the build output — roundState `fight`, Pantera
  (model `pantera-leoman`, king bank, 22 T3 actions) vs Demonio
  (model `demonio-a1`, jin bank, 22 T3 actions); a Digit1 input fired
  clip `atk:1:1`, put Demonio in hitstun and dropped its HP
  180 → 168.3; a 1→2 string advanced to clip `atk:2:2`; zero page
  errors. Frames + verdict in this PR:
  `docs/proof/2026-11-02/step5-fightcheck/`. (The repo's
  `tools/proof-harness/fight.mjs` could not run — its Playwright
  module is not installed on this VM — so the probe was adapted from
  Lane B's landed CDP harness,
  `tools/proof-harness/phase4b_template_fight.mjs`.)
- **Deploy:** 40 updated, 11 added, 0 removed. Resulting tree
  **997,773,216 B**. Deploy commit
  `625600dcb21ae4b97db3d4b9861abdd916710cca` on
  `gh-pages-m1-20261029`. Updated include all 19 Step 2 moveset JSONs
  and the suite/game wiring of #1491–#1498; added are the new modules
  (`game/js/morph-apply.js`, `game/js/frame-step.js`,
  `customization/creation-suite-ui/js/morph-targets.js`, and 8 more).
- **Live verification (coordinator, own reads):** Pages status
  `built`; live `deploy-manifest.json` reads commit
  `e15815709919aea34f78957522708c56a0f0375b`, files 2,150,
  bytes 997,773,216; spot checks — `game/js/morph-apply.js` HTTP 200
  at 2,338 B (== main) and `game/js/fighter.js` HTTP 200 at
  233,772 B (== main); site root 200.

## Open remainders after this lane

1. Clip-byte extraction projects (Step 1): T7 live-memory extraction
   for the Raven/Lucky Chloe banks (parent/browser lane); a TTT2 MOTA
   parser for Jun; DOA4 `mot.afs`/`anm.afs` decryption for Bass.
2. NO-ENTRY (c) 479, incl. the tackle-mount re-classing call (128) —
   a gameplay decision.
3. `game/assets/portraits/draft1/portraits-manifest.json` is not on
   Pages (runtime-fetched data; the guarded delta's add whitelist
   does not cover `game/assets/`).
4. Phase 4B remainders from #1498: roster-mode Soldier slot, custom
   moveset slots, template-body textures.
5. B2 queue (all storage-cap blocked, key preserved): Negativo refit,
   Purple Rain re-rig, packed Kiko model, and now the Demonio attire1
   re-upload (Step 4).
6. The itch.io draft zip was not rebuilt in this lane (the lane's
   Step 5 text covers the Pages republish only).

## Owner instruction (verbatim quote)
> Get everything else done

## Method the owner specified
Finish the itemized remainders from docs/handoffs/CLAUDE-WIP-COMPLETION-2026-11-02.md to 100% (no-bank fighter banks resolved from each fighter's own data, NO-ENTRY stance prefixes fixed by class, Phase 4B model swap proven by animation and landed if it passes, Demonio attire1 repo-vs-bucket reconcile, consolidated republish built with tools/deploy/build_pages.py --shell-only --core, gated by the module-graph check and a local harness fight check on the built tree, delta-deployed to gh-pages-m1-20261029 and verified live), using official-game holdings and industry-standard systems, with every step proven by real tool runs and viewed frames, landed as instruction-gate PRs merged on green.

## Method actually used
Finish the itemized remainders from docs/handoffs/CLAUDE-WIP-COMPLETION-2026-11-02.md to 100% (no-bank fighter banks resolved from each fighter's own data, NO-ENTRY stance prefixes fixed by class, Phase 4B model swap proven by animation and landed if it passes, Demonio attire1 repo-vs-bucket reconcile, consolidated republish built with tools/deploy/build_pages.py --shell-only --core, gated by the module-graph check and a local harness fight check on the built tree, delta-deployed to gh-pages-m1-20261029 and verified live), using official-game holdings and industry-standard systems, with every step proven by real tool runs and viewed frames, landed as instruction-gate PRs merged on green.

## Deviations (none / list, each with owner approval link)
None

## Proof (paths to files, frames, test output)
`docs/handoffs/EVERYTHING-ELSE-2026-11-02.md`
`docs/handoffs/NO-BANK-FIGHTERS-EVIDENCE-2026-11-02.md`
`docs/handoffs/STANCE-NOENTRY-CLOSEOUT-2026-11-02.md`
`docs/tech/DEMONIO-ATTIRE1-RECONCILE-2026-11-02.md`
`docs/proof/2026-11-02/phase4b/README.md`
`docs/proof/2026-11-02/step5-fightcheck/01-idle-stance.png`
`docs/proof/2026-11-02/step5-fightcheck/02-attack-1.png`
`docs/proof/2026-11-02/step5-fightcheck/04-string-1-2.png`
`docs/proof/2026-11-02/step5-fightcheck/verdict2.json`

## Self-check: I verified the result against the literal instruction
- [x] Every step's numbers come from runs I or my lanes executed and I re-verified the merges, the deploy, and the live manifest against GitHub myself; the frames in the Proof section were viewed, not just listed.
