# Urban Reign — Phase 4 State

Branch: `ur-phase4-assignment` — base: `ur-phase3-textures` @ d36795a (PR #464 head).
Lane: TEARDOWN COMPLETION SWEEP, Phase 4: pool assignment + name bridge + polish + canonical wiring.

## Inherited state (verified — do not re-derive)

- 72 characters skinned + textured (phases 1+3); 72 textured GLBs with 733 embedded images in `teardown/urban-reign/textured-models/` (PR #464).
- `.gyu` motion cracked (56,844 tracks, 0 failures, `tools/ur_gyu.py`).
- 31/72 fighters natively animated (pmot banks: 001–005, 016, 020–022, 030–032, 041–046, 054–063, 070–072).
- 41/72 proxy — motions in shared general pools (829 general motions in packed banks `game/assets/anim/ur-general-{normal,30frame,weapon}/` + `ur-native-index.json`), unassigned.
- motdat `.info` cracked (689 records) AND `.bin` bridge format cracked (`[u32 N][N×u32 monotonic offset table][records]`) with count parity on all 3 held pairs (P1 35/35, P44 1/1, P55 3/3) — `.bin` record k = payload for `.info` name k; missing link is records → `.gyu` bank motion indices.
- Sources: ISO release `urban-reign-iso-v1`; SLUS_212.09 MD5 `0fa29bd55638f9ebe49feb494d4decd5`; Ghidra at `~/workspace/tools/ghidra/`.
- Workdir `~/workspace/ur-phase3-work/` (clone + scratch, retained).
- Engine: Godot 4.7.2 LOCKED — `teardown/` artifacts are the deliverables; game-side changes minimal.

## Jobs

- JOB 1 — POOL ASSIGNMENT VIA LOADER CODE (the 41): decompile SLUS_212.09 motion-loading path (`kg_human`/`kg_objdata` + pmot/general-bank selection logic) in Ghidra; find how the game decides which general-pool motions belong to a fighter without a pmot bank. Rule must come from code or file table — never motion-content similarity. Apply proven rule per-fighter (clips on own textured GLB skeleton + `game/assets/movesets/ur-charNNN.json` + viewed frame). If no per-character rule, land closed search + exact remaining evidence source (e.g. PCSX2 RAM capture spec).
- JOB 2 — NAME BRIDGE: match P1 `.bin` record shapes against pmot001's 56-motion bank (record sizes/structure vs bank motion headers). If shapes lock record↔motion for P1, generalize across held pairs and assign ONLY proven name↔motion pairs. If fails, land comparison data + verdict + next discriminating test.
- JOB 3 — POLISH: (a) char064 missing s16 group (1197/1260 verts); (b) 11 characters with ≥1 unproven accessory piece; (c) node-graph hunt (motion bone b → GLB node b assumption).
- JOB 4 — CANONICAL SET + WIRING RECORD: update `teardown/urban-reign/WIRING-INVENTORY.md` marking `textured-models/` as THE canonical fighter model set; refresh `game/assets/models/street-reign/` copies ONLY if byte-swap of same filenames; CANON-CONVERSION.md identities stay OWNER-pending (CHAR001..072).

## Progress log

- Phase 4 start: branch `ur-phase4-assignment` created from `ur-phase3-textures` @ d36795a + this state file + PR opened BEFORE analysis.

## Results (landed cf239b0)

- JOB 1 — CLOSED SEARCH: no per-character assignment table exists for the 41 in any shipped file (gyuindex slots all-zero for them; general_index = slot↔global-ID only; motdat P-lists exist only for pmot fighters). Native count unchanged 31/72. Runtime (PCSX2) capture spec landed. Ghidra decompile blocked in this VM (OOM kill + import failure) — recorded honestly. Report: `PHASE4-JOB1-LOADER-SEARCH.md`.
- JOB 2 — NAME BRIDGE CRACKED: .bin record format fully cracked (global ID + embedded name + frames + variable header + sampled payload). Payload root stream = bank motion's decoded root track ×1000. **27/35 P1 name↔pmot001-motion pairs proven** (max dev ≤0.06 mm), assigned into `game/assets/movesets/ur-char001.json` (27 clips annotated `motdatName`) + `motion-names/name-bridge-p1-proven.json`. 8 unproven: type-14 root-decode gap (7) + record 14 (88f, no pmot candidate). Report: `motion-names/JOB2-NAME-BRIDGE-PHASE4.md`.
- JOB 3 — gaps documented with exact next steps (no fabrication): (a) char064 1197/1260, one s16 group, decoder reject-log step named; (b) 11 accessories — proof standard + per-piece excavation named, none claimed; (c) node graph not in any shipped file searched; H-index proven for bodies (1.8e-07), suspect only for accessories; PPK 0xae00 decode test named. Report: `PHASE4-JOB3-POLISH.md`.
- JOB 4 — `WIRING-INVENTORY.md` created on this branch: `textured-models/` = THE canonical set (supersedes phase-1 untextured GLBs). street-reign refresh NOT a same-filename byte-swap (charNNN.glb vs charNNN_textured.glb + embedded-animation difference) → documented as one-step follow-up, not performed. CANON identities untouched (OWNER-pending).
