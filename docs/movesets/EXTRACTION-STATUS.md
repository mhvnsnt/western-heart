# Moveset Extraction Status — Lane F (round 2)

**Owner order:** "Research and wire: TTT2 movesets/inputs, T6 movesets/inputs,
DOA movesets (Bass = Vain Abel), Urban Reign movesets. 38 fighters still ride
T3 proxies — replace proxies with real per-game data as extraction lands."

## Landed this round

- **DOA → Vain Abel (Bass Armstrong): REAL DATA.** `game/assets/movesets/vainabel.json`
  rebuilt from `teardown/dead-or-alive-4/movesets/bass-armstrong/BASS-MOVELIST.md`
  (triangulated DOA2/DOA5/DOA6, in-repo via PR #218). 42 moves with real Bass
  names/inputs/damage, mapped to Tekken inputs per the federation rule
  (DOA P→1/2, K→3/4, T→1+3/2+4, numpad→Tekken dirs, 236→qcf etc.).
  Damage: DOA2 base ×0.625 (DOA2 160HP → WH 100HP). Palm Jab 12f startup is
  DOA5-verified; other startups = Bass archetype (official DOA stats:
  Speed 1/5, Power 5/5, Throw 5/5). DOA2 throw damage not in source — WH
  grappler convention used, noted per move. `proxy: false`.
  **Proxies remaining: 38 → 37.**

## Schema v2 (moveset-editor contract, for Lane H)

- `docs/movesets/MOVESET-SCHEMA.md` — the agreed field contract.
- Every move in all 45 files now carries `anim_ref` (preview-animation clip
  reference: `t3:king:row:44`, `doa:bass:palm-jab`, ...), `input_slots`
  (Tekken slots the move can occupy, canonical first), `move_class`
  (strike/throw/string/special). Top-level `schema_version: 2`.
- Additive only — no v1 field renamed/removed (527 moves augmented, 0 modified).
- Lane H's branch (r2/creation-suite) has no editor code yet — this doc + the
  fields ARE the proposal; editor should read the JSONs directly per this contract.

## Per-game extraction status

| Game | Status | Blocker / next step |
|---|---|---|
| **TTT2** (Tekken Tag Tournament 2) | Format researched, not extracted | Release `ttt2-7z-v1` verified (16×500MB). Needs 13GB download + STFS extract + model/moveset pull. **Blocked: disk at 73%, ceiling 75%.** Sequenced after disk frees. Teardown docs (ROSTER 59, STAGES 29) in `teardown/tekken-tag-tournament-2/`. TTT2 movelists share T3's bank lineage — the T3 decode template (`teardown/tekken3/movesets/`) applies once banks are out. |
| **T6 PSP** (Tekken 6) | Not extracted | `teardown/tekken6` ~30%: videos + structure done, EBOOT decrypted, **DATA401 models still encrypted — decrypt6 lane owns decrypt. Coordinating, not duplicating.** Moveset pull starts when decrypt lands. |
| **DOA** (Dead or Alive) | **Bass LANDED** (see above) | Binary moveset decode from DOA4 teardown not yet done (50 chrthree meshes decoded; motion banks untouched). The movelist triangulation is the real per-game data for now. Other DOA fighters: no WH fighter maps to them 1:1 — future. |
| **Urban Reign** | Not extracted | Teardown ~95% (509 files, audio out). **PPKs need binary RE** — no moveset semantics yet. Blocked on RE lane. |

## Honest gaps

- 37 fighters still on T3 proxies (list: every `proxy: true` in `game/assets/movesets/`).
  Proxy replacement is gated on the extractions above — no fake "real" data.
- 18 pre-existing throw-recovery quirks from round 1 (`recovery < startup` on some
  1+3/2+4 entries — T3 bank throw rows). Untouched: rebalancing round-1 frame
  data is out of scope for this lane.
- `anim_ref` values for T3 rows point at decoded bank rows; the editor's live
  preview still needs the animation-clip player wired to those rows (Lane H).
- TTT2/T6/UR movesets: format understood, bytes not yet in hand — this doc will
  be updated as each extraction lands.
