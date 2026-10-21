# UR Phase 2 STATE
workdir: ~/workspace/ur-phase2-work/ (STATE + scratch)
clone: ~/workspace/ur-phase2-wh/ branch ur-phase2-motion (stacked on ur-sweep1-wiring / PR #434)
strategy: follow-on stacked PR, base = ur-sweep1-wiring
## Format status
- .gyu bank layout: PROVEN (header+cumulative motion table+track tables; 0 nonmono motions all banks)
- Types 8+12: DECODED, all 16,613 tracks across 4 general banks decode w/o failure
- Types 13+14: implemented (set-2 byte-pair s16 cumsum; 13 scale 1/16383, 14 float pairs) - validation running
- pmotNNN.ppk = fncc+gyu per-character banks (36 chars); pmot001 = 56 motions / 21 bones
- motdat .info name lists held (Gnrl 294 names, P1 35) - bank assignment TBD
- Bone mapping hypothesis: motion bone i = node id i = name-pool order (MUNE1..TSUMASAKI_L = nodes 0..20)
## Jobs
1 gyu: decoder landed; next = 13/14 validation, Blender char001 proof, batch convert, game wiring
2 texture: not started (PPK tail analysis next)
3 polish: not started
