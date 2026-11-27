# HANDOFF — Western Heart

**Last updated: 2026-11-23 (America/New_York).**
**Repo:** `mhvnsnt/western-heart` (PUBLIC), default branch `main`, main tip 32ec401 (#1773, 2026-11-23).
**Purpose of this file:** any agent that picks up work here reads this FIRST, then the linked docs. It states what we've done, where we're at, and what we're working toward — so the owner can say "go to this repo, pick up the work" and you just know. Update this file in the same PR whenever the state changes (add, don't delete).

## OWNER FOCUS (Nov 27 2026): models, animations, promo clips from extracted game data

**Set by the owner (mhvnsnt), 2026-11-27 10:12 AM America/Chicago. This is the MAIN FOCUS until he changes it.**

In his words (summary): even though Bannon and Western Heart are not being sold yet, the work that matters most now is **perfecting the character MODELS and ANIMATIONS** of those games using the **already extracted / decrypted / decoded commercial game files and code**, and then producing **in-game video clips, image stills, and marketing / advertising / promotional videos** that show them working correctly.

- **Bannon:** WWE 2K26 actual game files first (models, rigs, anims, moves), plus every other wrestling game we have data for (2K19/2K22/2K23/2K25, Wrestling Empire, WMXIX, KoC2, ...).
- **Western Heart:** Tekken 7 / Tekken 3, DOA, VF5, SF and every other game feeding the roster — each fighter matches his source character move-for-move (input → animation, side by side), plus his own canon extras.
- **Private-project rule:** the commercial data is the BASE. These are private projects, not sold yet; build on top of the extracted data freely. Nothing from them is sold until it has been customized into the owner's own work.
- **Pull-in-first:** never hand-build what the extracted data or an existing tool/kit already provides. Pull it in whole.
- **Proof:** no "looks right" claim without rendered stills/clips that were actually looked at (media-proof-standard: bytes exist, content is real, before/after for edits).

### Who owns what
| Lane | Owner | Notes |
|---|---|---|
| Western Heart models / animations / promo clips | **MoneyManBusch (Grok Bot)** | Pantera first (King T7 parity), then 2-3 strongest fighters. The separate Pantera attire-wiring lane keeps running; do not collide with it. |
| Bannon model / animation / promo push — **coordination** | **MoneyManBusch (Grok Bot)** | Picks the hero wrestlers, sets the 2K26-correctness bar, captures clips. |
| Bannon engine lane | **Claude** (unchanged) | Do NOT overwrite Claude's engine work. Coordinate through this HANDOFF / the lane docs, small add-only PRs. |
| Everything else (menus, story, arcade, sweeps, other repos) | **Muse and the other agents** | Keep going on your lanes; this focus does not pause you. |

### Deliverable order
1. Hero characters fully correct from extracted data (rig, weights, textures, real anims, signature moves, entrances).
2. In-game stills + clips captured from the live build (headless capture / in-engine camera paths, existing promo/entrance kits — no hand-made lookalikes).
3. First promo deliverable: a ~30 s in-game trailer per game, internal/private until the owner says otherwise. Nothing gets posted publicly without his explicit OK.

## 1. What this repo is

WESTERN HEART — the chimera-built fighting game. Tekken 7 base + Tekken 3 legacy + Eastern Mind soul + wrestling systems. The main chat's home repo and the biggest build: a Roster-100 fighting game with real movesets decoded from real game files, custom characters, portrait-first screens (that is how he plays), and a live build he playtests from his phone.

Settled canon (examples, full canon lives in the repo's canon docs): Byou takes Wang Jinrei; Pond takes Master Raven's Tekken 7 kit; Zen is the Still Soul; Gyou is the Moving Soul; Saku Ra is one fighter, the bloom; Jin_soul is the Blade Soul, a whole different character from Jin Kazama. Kutz and Realizzt joined the roster; DXMMII is already in and selectable; Lili and Baek fold in as custom-character material, not roster fighters; Bake folds into Kevin, who replaces him.

## 2. Where we're at

### DONE
- **Nov 22–23 landing wave (verified on main 2026-11-23, main tip 32ec401).** Canon syncs: #1829 move-editor + roster-clarification orders (eb6be66) · #1846 Kutz Chordz one-guy correction + Ren Truth mouth (fd055e8) · #1847 Ren is not Demonio; Tou green model stays (bad2b83) · #1848 moveset-library design (416e3e3) · #1849 Deadlift Alley-Oop owner ruling (72fead43) — the Deadlift section is in `docs/canon-archive/CANON-MASTER.md` line 1939. **After the tip moved mid-refresh, also landed and verified: #1834 Ren functional Truth-style mouth — 3D teeth, tongue, uvula, jaw (4cefd4a, 2026-11-23T16:23Z) · #1840 Replace Ren portrait with the real Rin bitmap, D_SUMIE b036 (648b3e4, 16:24Z) · #1775 YANM keyframe decode + YOBJ v2 bind pose, W4 lane (26e52c1, 16:24Z) · #1777 WMXIX dynamic follow-up — 99 specials (98/99), motion names, calibrated durations, HHH textures (23414cb, 16:25Z — main tip).** Note: #1834 and #1840 were listed as UNSTABLE-held in the 15:44Z queue run — they have since MERGED; the held list below is corrected. **Follow-up 2026-11-23 ~16:35Z: #1836 Kevin default model baek → kevin-tripo (615591f) and #1839 finger-rig C3 hand-pose driver (ce89189) also MERGED — they were in the "BLOCKED, held" range below, now landed. W6 wave: #1770 KoC2 teardown — King of Colosseum 2 full extraction, 49,214 files (fb6fb16) · #1772 WMXIX CAW meshes, 1,141 OBJs + extraction tools (b954833) · #1773 WMXIX textures, 9,410 PNGs + face contact sheets (32ec401 — main tip).** Moveset/teardown wave: #1822 Kevin full canon moveset (8d42064) · #1823 canon-moveset character inventory (02e047f) · #1824 T7 receiver fix logged as the permanent fix (d3f8642) · #1825 canon fix: Zen's own Tripo body, Gyou's conditional Paul, RIN Steve-body retire (75efc0d) · #1826 SCVI complete moveset teardown (4a39733) · #1827 VF5 complete teardown (f7eed39) · #1832 SFIV (25) + SFxT (55) movesets wired (6afccc4) · #1845 USFIV v6: AE parse 244/244 — 44 fighters, 3,853 moves (4011ca6). Fixes: #1828 github.io shell unblocked (925dd75) · #1841 pr-status-board retry fix (985cd6e) · #1843 Batch2 clean slice: Dragunov slice.json + 4 anim gap docs (5d26b8b) · #1844 Scimitar pose-safe re-encode (b2a52a7). #1833 was this HANDOFF.md landing (2df3867). **#911 select-card audit MERGED 2026-11-22 (6f1726a)** — no longer open. Queue: **37 open PRs** as of 2026-11-23 ~16:35Z (42 at ~16:30Z; #1836/#1839/#1770/#1772/#1773 landed after it, plus this handoff refresh #1850 itself).
- **Big fix P1B merged — 9 files, verified byte-for-byte, live build updated.**
- **Canon sync #1830 merged (2026-11-22, b050892).** Bake folds into Kevin, who replaces him.
- **DOA6 animation bank #1831 merged (2026-11-22, 9f65d26).** DOA6 GTAV06 .ifp animation bank (`tools/anim/doa6-ifp-multi.py`).
- **Pantera Tekken 7 clips: 185 of 643 pulled** (458 rows left for a follow-up lane).
- **Baek's missing hit found in the real files and wired in** — his jab works in test; the file now counts 12 working moves against the old baseline of 10 (one test still red, being confirmed from the test log).
- **Move-library fix done, all 14 checks green** — merge held until the page can be re-read clean; never merged blind.
- **Mocap viewer fix in** (was shipping broken — nothing rendered, one wrong line reading a number from the wrong place); live page check still pending. Not handed back until it is seen playing in a real browser.
- **Releases (2026-11-22):** `doa6-gtainside-ifp-20261122`, `vf5-dural-xps-v1`.

### IN PROGRESS
- **Moveset audit + scramble fix (owner order 2026-11-20, running).** Audit found 102 of 645 files scrambled, 94 of them Tekken 7, with zero Tekken 7 motion files ever checked against a solved decode. The fix: check whether all 102 follow the same pattern and use already-unscrambled material to unscramble the rest. No fixes landed yet.
- **Pantera throw regression (owner report 2026-11-19, still open).** Bent backwards, back to the opponent, knees bending backwards. The victim now actually gets thrown on camera in the new build, but the real paired throw still never plays: the throw connects at 1.45 meters while the file caps at 1.27. The fix that trusts the grab changes throw selection for every fighter — HIS CALL (see §6). The Tekken 7 pair itself is now disputed (clips may be only the 40-frame grab, throw in throw data) — the hunt runs, Tekken 3 stays the default. The crew proved him right that the thrower's throw lives in the mislabeled victim files; receivers are pulled, the decode sampler works, shoulder/arm mapping still needs fixing.
- **Demonio fix (amended):** human form is the Tripo model he uploaded, not the old Tekken 3 Jin; default is the unwinged demon, winged Devil only on transform with a full meter; all 80 Devil moves kept in the Devil form, but only 60 of 80 inputs actually play a Devil move and 20 inputs have no move wired yet. The 18 displaced-key Tekken 7 Devil records and the transformation GLB inventory are still open.
- **Move-editor orders (2026-11-20, standing):** every move gets its real animation; hover preview works like WWE 2K26 pulled from the actual commercial source; VF and DOA move lists are custom-fighter starting points in the game's own inputs; renaming/copying a saved move list never overwrites the original.
- **Live-build sync (standing):** every push must update the live build, the testable build, and the deployable build — ALL of them, automatically (workflow on every push to main). Live = github.io shell + western-heart.pages.dev.

### BLOCKED
- **Pantera paired throw — owner's call (see §6).** Not a lane decision.
- **Roster-100 Wave 2 portrait freshness gate** fails CI on placeholder cards and false manifest claims — cards must be real, manifests must be true.

## 3. What we're working toward

**The goal:** assembled, playable slices built in player-progression order, short jobs finished and deployed before long jobs: T-pose fighters with a simpler, single-source moveset and no canon extras first, then the long jobs. No fighter is presented as proof before his pipeline is finished. A missing outfit never gates a fighter — skin, eyes, and hair matter most; clothing can be added later from parts.

**The bar:** every move its real animation from the real files; menus, HUDs, buttons, and fonts built from the actual Tekken and WWE front-end code, never hand-tooled lookalikes; portrait as the primary layout with the fighter preview visible alongside the menus the whole time, no panel ever covering the fighter preview; safe-area boundaries respected in both orientations.

## 4. Standing rules that apply here

- **Branch → PR → merge, always.** Never push to main directly. Add-only, zero-conflict PRs, no force pushes. A PR is not a clean merge on one green signal alone.
- **Checkpoint-and-save law:** CHECKPOINT.md first, update after every step; the repo is the save; resume, never restart.
- **No-temp-storage law:** nothing in /tmp or any wipeable location, ever. Everything goes straight into the repo or a durable folder the second it exists.
- **No-gaps / solve-it law:** a gap or block is never the end of the work — route-switch until it's done or every reasonable route is exhausted with exact errors recorded.
- **Real-source-only:** every part comes from the actual source code and files, wired up fully. No hand-tooled lookalikes, no fake panels, no cutout frame shipped as finished work when it still shows gaps, holes, or source-piece leftovers.
- **Pull-working-complete:** find the project / modding-community work that ALREADY has the material pulled apart AND put back together, working — pull it in WHOLE. No hand-tooling, no surgery-fixing every thing afterward. If no complete working source exists for a piece, report the exact piece and why — never rebuild it from scratch silently.
- **Archive.org first:** for any game acquisition, archive.org is checked first, live, with the item's actual files inspected. A stale "not there" note never counts.
- **No-hand-tooling / no-shortcuts:** the proper way, not the quick hack. If the system cannot fit a model it stops and reports.
- **Kevin rule:** resolve missing names from the fighter's own data, never by guessing. Never call a fighter's model missing without checking the GLBs he uploaded by URL first — Cuts has transformations he uploaded; Realist's model comes from Ash Lane, possibly Western Heart. Never invent a base character.
- **Canon is his, checked before writing:** a rule exists only in his exact words. When his words conflict with recorded canon, check canon first, flag the mismatch in the moment, never propagate a slip. (Exception: Tekken base names in mappings are transitional scaffolding being converted gradually to his canon.)
- **Live-build sync law:** every push updates live + testable + deployable, automatically.
- **Sign-in standing approval:** Google/Gmail (fmmg.mars@gmail.com) and GitHub (mhvnsnt) are blanket-approved forever. Never ask him to do sign-in steps himself.

## 5. Key files and paths

| What | Where |
|---|---|
| Canon docs (roster, souls, kits) | Canon docs in repo (see README) |
| Moveset / animation banks | `tools/anim/` (incl. `doa6-ifp-multi.py`) |
| Live build | github.io shell + western-heart.pages.dev (auto-synced on push to main) |
| Releases | `doa6-gtainside-ifp-20261122`, `vf5-dural-xps-v1` |
| Open PRs (sample — full list in repo; 37 open as of 2026-11-23 ~16:35Z) | #182 RESEARCH rig auto-fix survey (do not merge) · #377 Keemap wire-in (DO NOT MERGE — tool fails rig, evidence inside) · #706 Ashlane→DOA claimed-map lock · #713 VF5 Dural stance for Zen · #714 CORNERSTONE moveset (Yamazaki / Rock / Toguro) · #826 T7 character select rebuild · #875 / #908 face-cone skin-weight audit + fixer · #970 Batch2 moveset pull · #1820 / #1835 CLEAN but owner-held · #1842 UNSTABLE, held · #1837 / #1838 BLOCKED, held (verified OPEN 2026-11-23 ~16:35Z; #1836 and #1839 from that range have MERGED). #911 select-card audit is MERGED (6f1726a), not open. |
| Build-sync automation workdir | `~/workspace/_build-sync-automation-20261120/` |

## 6. Open decisions needing the owner

- **Pantera throw-range fix:** the fix that trusts the grab changes throw selection for every fighter. Trade-off: paired throws play, but throw selection changes everywhere. His call — put plainly, not decided in a lane. (The T7 pair dispute — grab-only clips vs throw in throw data — rides with this.)
- **Canon questions (his call):** Zen's pronoun; whether Gyou's Paul is permanent; the canon doc's contradictory Jin Kazama section — retire or fix; whether Demonio's human form plays its own moves or keeps the base kit; whether Bloodline Ember is an outfit or a fourth form.
- **PR reviews:** #1817, #1818, #1820, #1814 (per his queue) and #1792 merge — put to him once, plainly, with the trade-off; do not decide in a lane. #1835 is also CLEAN but owner-held (per MERGE-QUEUE.md 2026-11-23).
- **VF/DOA slashed inputs + the old move-list screen:** his call, per his queue.

## 7. How to pick up

1. Read this HANDOFF.md first, then the canon docs and README in the repo.
2. Check what other agents are already doing before starting anything (never start a duplicate session).
3. Resume from the stated next step — never restart, never re-derive finished work. The scramble fix, the Pantera hunt, and the Demonio fix each have their own state — pick up from the lane's checkpoint, not from the top.
4. Land work branch → PR → merge, add-only. After a merge, read back every payload file from main before reporting it done — no sampling.
5. Update this HANDOFF.md in the same PR when the state changes. Verify with your own eyes in the live build before claiming anything done. His eyes overrule a team's gate.
