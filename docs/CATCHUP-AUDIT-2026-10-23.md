# WESTERN HEART — CATCH-UP AUDIT (2026-10-23)

Snapshot: mhvnsnt/western-heart main @ 024df77fb9d9 (2026-10-23T11:20:45Z). Every cell below was verified
against main itself: git-trees API enumeration of roster/, game/, docs/, customization/; a direct
line-by-line parse of game/js/assets.js MODEL_URLS, game/js/roster-full.js, game/js/movesets.js and
game/assets/movesets/index.json; GLB JSON-chunk parses (skins/joints) of all 198 roster+model GLBs;
and a payload hunt across all 760 PRs, 759 branches, 89 releases (718 assets), 1,178 checkpoint
files, local worktree dirs (5,403 GLBs), and the memory record. A payload counts as landed ONLY if
verified on main. Automated claim matches were hand-reviewed line by line; audit narration was
discounted wherever it masqueraded as a landing claim.

## The headline

- 68 fighter rows audited (67 roster dirs merged into canonical fighters, plus the dir-less Nine Souls;
  wizard-gang is a faction row, not a fighter).
- Canon: only 4 of 68 fighters have a canon/bio file in their roster dir (buffalo-bill, dorowani
  [voice only], gyou, zen). BUT the full character bible IS on main — root CANON.md (165,306 bytes)
  holds complete entries for 43 of the 64 fighters who lack a roster-dir file. It was
  pushed to the repo root and never split into the per-fighter files. That is the single biggest
  catch-up item: the text exists, the filing never happened.
- MODEL_URLS (game/js/assets.js) holds 149 keys on current main; exactly ONE target file is missing:
  ryuji-rock -> roster/ryuji-rock/attires/attire1/model.glb (CornerStone's Tripo sits archived at
  roster/ryuji-rock/attires/attire1/source/cornerstone-a1.glb, 18,872,720B, PR #724). An older count of
  '107 keys, 21 dirs with no key' is superseded — a 2026-10-22 wire-up pass landed most missing keys;
  the no-key set on current main is 14 fighters.
- 145 verified gaps total. Payload classes: ON-MAIN-WRONG-PATH 69, DOES-NOT-EXIST 64, LOCAL-ONLY 11, ON-BRANCH 1.
- The dominant pattern is not missing work. It is work that was pulled, archived, or written and then
  never wired: Tripo source GLBs sitting in attires/attire1/source/ with no MODEL_URLS key (chordz,
  kuma/Gashadokuro, panda/Aotsuki, scimitar — all unrigged statics), a moveset file on main that the
  loader lists never picked up (buffalo-bill), a fighter with model+moveset+loader all present but
  no roster entry (cain-elias), and 6 wired models that parse with 0 skins (baek A1 attire, blanka,
  cain-elias A1, dorowani A1, silvertongue A1, slice A1).
- Genuinely absent (DOES-NOT-EXIST): the SmutBase intake six have no models, movesets, or canon
  anywhere (intake was blocked; their dirs hold placeholders only); Jin (Eastern Mind) has no base
  model (owner Tripo still owed) and no moveset file; 12 fighters have no moveset file at all.

## Per-fighter table

| Fighter | Canon file | MODEL_URLS key | Wired model file | Roster/select entry | Moveset file | Loader-listed | Rigged (wired model) | Attires wired |
|---|---|---|---|---|---|---|---|---|
| armor-king | — | YES | YES | YES | YES | YES | rigged | — |
| awa-pop | — | YES | YES | YES | YES | YES | rigged | YES |
| baek | — | YES | YES | YES | YES | YES | rigged | YES |
| blanka | — | YES | YES | — | YES | YES | **UNRIGGED** | — |
| bonus | — | — | — | — | — | — | — | — |
| bruno | — | YES | YES | YES | YES | YES | rigged | — |
| buffalo-bill | YES | — | — | — | YES | — | no wired model (disk: UNRIGGED) | — |
| burger | — | YES | YES | YES | YES | YES | rigged | YES |
| byou | — | YES | YES | YES | YES | YES | rigged | — |
| cain-elias | — | YES | YES | — | YES | YES | **UNRIGGED** | YES |
| charger | — | YES | YES | YES | YES | YES | rigged | YES |
| chordz | — | — | — | — | YES | YES | no wired model (disk: UNRIGGED) | — |
| Cape Jones / Cyborg X | — | YES | YES | YES | YES | YES | rigged | — |
| deathfang | — | YES | YES | YES | YES | YES | rigged | YES |
| demonio | — | YES | YES | YES | YES | YES | rigged | YES |
| diablo | — | YES | YES | YES | YES | YES | rigged | YES |
| dio | — | YES | YES | YES | YES | YES | rigged | — |
| doc-frank | — | YES | YES | YES | YES | YES | rigged | YES |
| dorowani | YES | YES | YES | YES | YES | YES | **UNRIGGED** | — |
| dxmmii | — | YES | YES | YES | YES | YES | **UNRIGGED** | YES |
| gyou | YES | YES | YES | YES | YES | YES | rigged | YES |
| iori | — | YES | YES | YES | YES | YES | rigged | — |
| Jin (Eastern Mind) | — | — | — | — | — | — | no wired model (disk: rigged) | YES |
| kai | — | YES | YES | YES | YES | YES | rigged | YES |
| Kiko Tanaka / Rave | — | YES | YES | YES | YES | YES | rigged | — |
| king-tyrant | — | YES | YES | YES | YES | YES | rigged | YES |
| kinpo | — | YES | YES | YES | YES | YES | rigged | YES |
| koreshi | — | YES | YES | YES | YES | YES | rigged | — |
| kronos | — | YES | YES | YES | YES | YES | rigged | YES |
| Gashadokuro (Kuma) | — | — | — | — | — | — | no wired model (disk: UNRIGGED) | — |
| lili | — | YES | YES | — | YES | YES | rigged | — |
| mariposa | — | YES | YES | YES | YES | YES | rigged | YES |
| michiko | — | YES | YES | YES | YES | YES | rigged | YES |
| Ryusan (Mina Ashido) | — | — | — | — | — | — | — | — |
| Tobi (Mirko) | — | — | — | — | — | — | — | — |
| negativo | — | YES | YES | YES | YES | YES | rigged | — |
| nightwolf | — | YES | YES | YES | YES | YES | rigged | YES |
| Aotsuki (Panda) | — | — | — | — | — | — | no wired model (disk: UNRIGGED) | — |
| pantera | — | YES | YES | YES | YES | YES | rigged | YES |
| Megami (Parvati) | — | — | — | — | — | — | — | — |
| phantom | — | YES | YES | YES | YES | YES | rigged | YES |
| purple-rain | — | YES | YES | YES | YES | YES | rigged | YES |
| Chatur (Rahkasa) | — | — | — | — | — | — | — | — |
| retsu | — | YES | YES | YES | YES | YES | rigged | YES |
| rin | — | YES | YES | YES | YES | YES | rigged | YES |
| CornerStone (Ryuji Rock) | — | YES | YES | YES | YES | YES | rigged | — |
| Saku-ra | — | YES | YES | YES | YES | YES | rigged | YES |
| SAM-UR-A1 | — | YES | YES | YES | YES | YES | rigged | YES |
| scimitar | — | YES | YES | YES | YES | YES | rigged | — |
| sha | — | YES | YES | YES | YES | YES | rigged | YES |
| silvertongue | — | YES | YES | — | — | — | **UNRIGGED** | YES |
| skull | — | YES | YES | YES | YES | YES | rigged | — |
| slice | — | YES | YES | YES | YES | YES | **UNRIGGED** | YES |
| star | — | YES | YES | YES | YES | YES | rigged | YES |
| thor | — | YES | YES | YES | YES | YES | rigged | YES |
| torch | — | YES | YES | YES | YES | YES | ? | YES |
| tou | — | YES | YES | YES | YES | YES | rigged | YES |
| Pond (Tsuyu) | — | — | — | — | — | — | — | — |
| vainabel | — | — | — | — | YES | YES | no wired model (disk: UNRIGGED) | YES |
| vega | — | YES | YES | YES | YES | YES | rigged | — |
| Menajerii (Vixen) | — | — | — | — | — | — | — | — |
| waterfall | — | YES | YES | YES | YES | YES | rigged | — |
| Wizard Gang (faction) | — | — | — | — | — | — | — | — |
| yukihyo | — | YES | YES | YES | YES | YES | rigged | — |
| zafina | — | YES | YES | — | — | — | rigged | YES |
| zangief | — | YES | YES | YES | YES | YES | rigged | — |
| zen | YES | YES | YES | YES | YES | YES | rigged | YES |
| zui | — | YES | YES | YES | YES | YES | rigged | YES |

## Gap register (every gap + where the filled work actually sits)

| Fighter | Gap | Payload class | Location / evidence |
|---|---|---|---|
| armor-king | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:734 but never written into the repo |
| armor-king | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/armor-king/attires/ with no MODEL_URLS variant keys, first: roster/armor-king/attires/attire1/model-rigged.glb |
| awa-pop | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 AWA POP — The Bubble Soul — never split into roster/awa-pop/CANON.md |
| baek | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 KEVIN — The Master Soul — never split into roster/baek/CANON.md |
| baek | rig | DOES-NOT-EXIST | kevin-tripo attire target roster/baek/attires/attire1/model.glb is unrigged (0 skins); base model game/assets/models/baek.glb and master-white attire are rigged |
| blanka | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:926 but never written into the repo |
| blanka | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| blanka | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/blanka/attires/ with no MODEL_URLS variant keys, first: roster/blanka/attires/attire1/model.glb |
| blanka | rig | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| bonus | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| bonus | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| bonus | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| bonus | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| bonus | canon | DOES-NOT-EXIST | no canon for a fighter named Bonus recorded anywhere (memory 'bonus' lines concern the bonus-characters category) |
| bruno | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/bruno/attires/ with no MODEL_URLS variant keys, first: roster/bruno/attires/attire1/source/bruno-a1.glb |
| bruno | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 BRUNO — The Heartbreak Soul — never split into roster/bruno/CANON.md |
| buffalo-bill | model-unwired | ON-MAIN-WRONG-PATH | roster/buffalo-bill/attires/attire3/model.glb |
| buffalo-bill | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| buffalo-bill | moveset-not-loader-listed | ON-MAIN-WRONG-PATH | moveset file game/assets/movesets/buffalo-bill.json on main but id absent from MOVESET_IDS (game/js/movesets.js) and index.json |
| buffalo-bill | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/buffalo-bill/attires/ with no MODEL_URLS variant keys, first: roster/buffalo-bill/attires/attire3/model.glb |
| burger | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 BURGER — The Hunger Soul — never split into roster/burger/CANON.md |
| byou | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| byou | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/byou/CANON.md |
| cain-elias | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| cain-elias | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 CAIN ELIAS — The Deadman (Bonus) — never split into roster/cain-elias/CANON.md |
| cain-elias | rig | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| charger | canon | LOCAL-ONLY | ~/workspace/_bios-harvest-work (bios harvest lane in flight, batch 1) |
| chordz | canon | LOCAL-ONLY | owner canon recorded in 2026-10-15.md:519 but never written into the repo |
| chordz | model-unwired | ON-MAIN-WRONG-PATH | roster/chordz/attires/attire1/source/chordz-a1.glb |
| chordz | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| chordz | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/chordz/attires/ with no MODEL_URLS variant keys, first: roster/chordz/attires/attire1/source/chordz-a1.glb |
| Cape Jones / Cyborg X | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Cape Jones / Cyborg X | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 CYBORG X — The Trapped Soul — never split into roster/cyborg-x/CANON.md |
| deathfang | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 DEATHFANG — The Chained Soul (Bonus) — never split into roster/deathfang/CANON.md |
| demonio | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 DEMONIO — The Demon Soul — never split into roster/demonio/CANON.md |
| diablo | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 DIABLO — The Devil Soul — never split into roster/diablo/CANON.md |
| dio | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/dio/attires/ with no MODEL_URLS variant keys, first: roster/dio/attires/attire1/source/dio-a1-jade-god.glb |
| dio | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 DIO — The Demon That Is — never split into roster/dio/CANON.md |
| doc-frank | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 DOC FRANK — The Builder Soul — never split into roster/doc-frank/CANON.md |
| dorowani | rig | DOES-NOT-EXIST | wired model roster/dorowani/attires/attire1/source/dorowani-a1-crimson-cheeks.glb has 0 skins; no rigged version located |
| dxmmii | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 DXMMII — The Rebuilt Soul — never split into roster/dxmmii/CANON.md |
| dxmmii | rig | DOES-NOT-EXIST | wired A1 roster/dxmmii/attires/attire1/model.glb has 0 skins and no rigged A1 version located (his patchwork attire dxmmii-patchwork-rigged.glb is rigged and wired, but it is a different model) |
| iori | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:866 but never written into the repo |
| iori | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/iori/attires/ with no MODEL_URLS variant keys, first: roster/iori/attires/attire1/model.glb |
| Jin (Eastern Mind) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Jin (Eastern Mind) | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 JIN KAZAMA — The Bloodline Soul — never split into roster/jin/CANON.md |
| Jin (Eastern Mind) | model | DOES-NOT-EXIST | no base model — owner's Tripo pull still owed; one rigged reskin-attire GLB on main (roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb, 25,657,736B) |
| Jin (Eastern Mind) | moveset | DOES-NOT-EXIST | no jin moveset file; branch rename/jin-moveset-to-demonio-20261019 folded Jin's moveset into Demonio by canon design |
| kai | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/kai/CANON.md |
| Kiko Tanaka / Rave | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Kiko Tanaka / Rave | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 KIKO TANAKA — The Painted Soul — never split into roster/kiko-tanaka/CANON.md |
| king-tyrant | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §3 KING TYRANT — The Showman Soul — never split into roster/king-tyrant/CANON.md |
| kinpo | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §3 KINPO — The Buttercup Soul — never split into roster/kinpo/CANON.md |
| koreshi | canon | LOCAL-ONLY | ~/workspace/_bios-harvest-work (bios harvest lane in flight, batch 1) |
| koreshi | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/koreshi/attires/ with no MODEL_URLS variant keys, first: roster/koreshi/attires/attire1/model-rigged.glb |
| kronos | canon | LOCAL-ONLY | ~/workspace/_bios-harvest-work (bios harvest lane in flight, batch 1) |
| Gashadokuro (Kuma) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Gashadokuro (Kuma) | model-unwired | ON-MAIN-WRONG-PATH | roster/kuma/attires/attire1/source/kuma-a1.glb |
| Gashadokuro (Kuma) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Gashadokuro (Kuma) | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/kuma/attires/ with no MODEL_URLS variant keys, first: roster/kuma/attires/attire1/source/kuma-a1.glb |
| Gashadokuro (Kuma) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| lili | canon | ON-BRANCH | canon/rename-mariposa-silvertongue-20261018 |
| lili | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| lili | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/lili/attires/ with no MODEL_URLS variant keys, first: roster/lili/attires/noir-gala/lili-noir-gala.glb |
| mariposa | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 MARIPOSA — The Sealed Soul — never split into roster/mariposa/CANON.md |
| michiko | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 MICHIKO — The Outlaw Soul — never split into roster/michiko/CANON.md |
| Ryusan (Mina Ashido) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Ryusan (Mina Ashido) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Ryusan (Mina Ashido) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Ryusan (Mina Ashido) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Ryusan (Mina Ashido) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Tobi (Mirko) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Tobi (Mirko) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Tobi (Mirko) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Tobi (Mirko) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Tobi (Mirko) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| negativo | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/negativo/attires/ with no MODEL_URLS variant keys, first: roster/negativo/attires/attire1/source/negativo-a1.glb |
| negativo | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 N3GΔTIV0 — The Hunter — never split into roster/negativo/CANON.md |
| nightwolf | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 NIGHTWOLF — The Guide Soul — never split into roster/nightwolf/CANON.md |
| Aotsuki (Panda) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Aotsuki (Panda) | model-unwired | ON-MAIN-WRONG-PATH | roster/panda/attires/attire1/source/aotsuki-a1.glb |
| Aotsuki (Panda) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Aotsuki (Panda) | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/panda/attires/ with no MODEL_URLS variant keys, first: roster/panda/attires/attire1/source/aotsuki-a1.glb |
| Aotsuki (Panda) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| pantera | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 PANTERA — The Panther Soul — never split into roster/pantera/CANON.md |
| Megami (Parvati) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Megami (Parvati) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Megami (Parvati) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Megami (Parvati) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Megami (Parvati) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| phantom | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 PHANTOM — The Ghost Blade Soul — never split into roster/phantom/CANON.md |
| purple-rain | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 PURPLE RAIN — The Performer Soul — never split into roster/purple-rain/CANON.md |
| Chatur (Rahkasa) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Chatur (Rahkasa) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Chatur (Rahkasa) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Chatur (Rahkasa) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Chatur (Rahkasa) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| retsu | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/retsu/CANON.md |
| rin | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/rin/CANON.md |
| CornerStone (Ryuji Rock) | model-key-broken | ON-MAIN-WRONG-PATH | key 'ryuji-rock' -> roster/ryuji-rock/attires/attire1/model.glb missing; payload at roster/ryuji-rock/attires/attire1/source/cornerstone-a1.glb |
| CornerStone (Ryuji Rock) | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/ryuji-rock/attires/ with no MODEL_URLS variant keys, first: roster/ryuji-rock/attires/attire1/source/cornerstone-a1.glb |
| CornerStone (Ryuji Rock) | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 CORNERSTONE — The Obnoxious One (Bonus) — never split into roster/ryuji-rock/CANON.md |
| Saku-ra | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 SAKU RA — The Idol Soul — never split into roster/saku-ra/CANON.md |
| SAM-UR-A1 | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 SAM-UR-A1 — The Mech Soul — never split into roster/sam-ur-a1/CANON.md |
| scimitar | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/scimitar/attires/ with no MODEL_URLS variant keys, first: roster/scimitar/attires/attire1/source/scimitar-a1.glb |
| scimitar | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 SCIMITAR — The Vizier Soul — never split into roster/scimitar/CANON.md |
| sha | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/sha/CANON.md |
| silvertongue | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| silvertongue | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 SILVERTONGUE — The Heiress Soul — never split into roster/silvertongue/CANON.md |
| silvertongue | rig | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| silvertongue | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| skull | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/skull/attires/ with no MODEL_URLS variant keys, first: roster/skull/attires/attire1/model-rigged.glb |
| skull | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §2 SKULL — The Punisher Soul — never split into roster/skull/CANON.md |
| slice | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 SLICE — The Maniacal Agent (Bonus) — never split into roster/slice/CANON.md |
| slice | rig | DOES-NOT-EXIST | wired A1 roster/slice/attires/attire1/model.glb (the owner Tripo) has 0 skins and no rigged version of that model exists on main; his A2 is a different (Dragunov) model |
| star | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 STAR — The Current Soul — never split into roster/star/CANON.md |
| thor | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 THOR — The Thunder God (Bonus) — never split into roster/thor/CANON.md |
| torch | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §6 TORCH — The Flame Soul — never split into roster/torch/CANON.md |
| tou | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §4 THE NINE SOULS (named in the collective Nine Souls section) — never split into roster/tou/CANON.md |
| Pond (Tsuyu) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Pond (Tsuyu) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Pond (Tsuyu) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Pond (Tsuyu) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Pond (Tsuyu) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| vainabel | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:766 but never written into the repo |
| vainabel | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| vainabel | model | ON-MAIN-WRONG-PATH | attire models on main (roster/vainabel/attires/attire2/3/4/model.glb, wired only as variant keys vainabel-attire2/3/4) and A4 archived on release vain-abel-a4-tripo-20261021; no base 'vainabel' key and no roster entry |
| vega | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:926 but never written into the repo |
| vega | attires-unwired | ON-MAIN-WRONG-PATH | 1 attire GLB(s) on disk under roster/vega/attires/ with no MODEL_URLS variant keys, first: roster/vega/attires/attire1/model.glb |
| Menajerii (Vixen) | canon | DOES-NOT-EXIST | no canon recorded in repo, branches, PRs, releases, or memory |
| Menajerii (Vixen) | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| Menajerii (Vixen) | attires | DOES-NOT-EXIST | no attire models or variant keys exist |
| Menajerii (Vixen) | model | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| Menajerii (Vixen) | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| waterfall | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/waterfall/attires/ with no MODEL_URLS variant keys, first: roster/waterfall/attires/attire1/model-rigged.glb |
| waterfall | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §3 WATERFALL — The Weeping Soul — never split into roster/waterfall/CANON.md |
| Wizard Gang (faction) | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:44 but never written into the repo |
| yukihyo | attires-unwired | ON-MAIN-WRONG-PATH | 3 attire GLB(s) on disk under roster/yukihyo/attires/ with no MODEL_URLS variant keys, first: roster/yukihyo/attires/attire1/source/yukihyo-a1.glb |
| yukihyo | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 YUKIHYŌ — The Snow Leopard (Bonus) — never split into roster/yukihyo/CANON.md |
| zafina | roster-entry | DOES-NOT-EXIST | no FULL_ROSTER entry in game/js/roster-full.js (wiring never written) |
| zafina | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §7 MARIPOSA — The Sealed Soul (name law: Zafina = Mariposa) — never split into roster/zafina/CANON.md |
| zafina | moveset | DOES-NOT-EXIST | no payload on main, branches, releases, or local worktrees (earlier automated claim match was audit narration, source line read and discounted) |
| zangief | canon | LOCAL-ONLY | owner canon recorded in MEMORY.md:926 but never written into the repo |
| zangief | attires-unwired | ON-MAIN-WRONG-PATH | 2 attire GLB(s) on disk under roster/zangief/attires/ with no MODEL_URLS variant keys, first: roster/zangief/attires/attire1/model-rigged.glb |
| zui | canon | ON-MAIN-WRONG-PATH | full canon entry on main in root CANON.md ('The Character Bible', 165,306 bytes), §3 ZUI — The Drunken Soul — never split into roster/zui/CANON.md |

## Counts

Gaps by type: canon 64, attires-unwired 19, roster-entry 18, moveset 12, attires 10, model 9, rig 7, model-unwired 4, moveset-not-loader-listed 1, model-key-broken 1

Gap payloads by class: ON-MAIN-WRONG-PATH 69, DOES-NOT-EXIST 64, LOCAL-ONLY 11, ON-BRANCH 1

## CLAIM-ONLY-UNVERIFIED (claimed landed, not on main at claim time, not locatable)

- zen — historical-claim: A Zen completion report claimed PRs #470/#471 + merge 0f8a04a6 landed Zen's forms. Verified false in this audit: PR #470 is a DOA4 teardown PR (OPEN) and PR #471 is a playability-fixes PR — neither is a Zen landing, and Zen's real landings are #460 (models), #627 (rig docs), #743 (rigged GLBs). The claimed payload did not exist at claim time; it has since been landed for real.
  Source: memory/2026-10-22.md (fabrication note) + prs.json titles/states verified 2026-10-23

Note: every other automated candidate for this category was traced to audit narration, gap
inventories, or merge logs about other work, and was discounted after reading the source lines.
No other fabricated landing claims were found in this pass.

## Prioritized landing order (for follow-up landing waves — NOT landed by this audit)

1. Filing + wiring fixes (payloads already on main, zero new assets):
   - Split root CANON.md into roster/<fighter>/CANON.md for the 44 covered fighters.
   - Point the ryuji-rock key at its archived source (copy source/cornerstone-a1.glb to the wired path).
   - Add MODEL_URLS keys for chordz, kuma (Gashadokuro), panda (Aotsuki), scimitar from their on-main source GLBs; add a base key + roster entry for buffalo-bill and vainabel.
   - Add buffalo-bill to the moveset loader lists (his file is already on main).
   - Add FULL_ROSTER entries for the wired-but-unselectable (cain-elias first — model, moveset file, and loader listing already exist; then blanka, lili, zafina, silvertongue as their pieces complete).
2. Rigs: rig the 6 unrigged wired models and the archived Tripo statics (cornerstone, chordz, kuma,
   panda, scimitar, yukihyo sources — every source GLB parsed is an unrigged static) at the shared layer.
3. Movesets: new files for the 12 fighters with none (jin, kuma, panda, silvertongue, zafina, bonus,
   and the intake six once models exist).
4. Canon remainder: land the bios-harvest batch (in flight) for fighters whose canon is recorded in
   memory but not in root CANON.md (charger, koreshi, kronos, wizard-gang); the DOES-NOT-EXIST canon
   set (intake six, bonus, kuma, panda) needs the owner's word — nothing exists to land.
5. Roster entries for intake/new fighters as 1-3 complete for each.

## Method notes

- MODEL_URLS parsed line-by-line from game/js/assets.js lines 20-375 (block comments and commented-out
  keys excluded); values resolve against game/ (the page root). 149 keys; 148 targets exist; 1 missing.
- Rig = GLB JSON chunk contains skins with joints (range-request parse, no full downloads). All 198
  GLBs under roster/ + every wired game/assets/models target were parsed: 56 of 62 wired primaries are
  rigged; the archived Tripo source GLBs are uniformly unrigged statics.
- Moveset loader-listed = fighter id (any spelling variant) in MOVESET_IDS (game/js/movesets.js) or
  index.json fighters. FULL_ROSTER `moveset:` fields name Tekken banks (provenance), not loader keys —
  an early pass that tested bank ids against the loader lists produced false gaps and was corrected.
- Canonical merges: sakura dir = Saku-ra's model home; purplerain = Purple Rain; jin-eastern-mind = Jin
  (Eastern Mind); rave = Kiko Tanaka's roster id; zafina's canon lives under Mariposa (name law).
- This audit landed NOTHING. It only maps. Landing waves are dispatched separately.
