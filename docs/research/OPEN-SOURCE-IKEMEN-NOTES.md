# Ikemen GO — reference notes for Western Heart (NOT engine code)

Source: ikemen-engine/Ikemen-GO (MIT), pulled to the workspace open-source
lane. WH keeps its Three.js engine. These are SYSTEMS to port, not code
to import.

## Systems worth porting (in priority order)
1. **Rollback + delay netcode** (nightly builds; `RollbackNetcode` flag,
   rollback UDP port, frame delay setting). WH online play should be
   designed rollback-first: deterministic fixed-timestep simulation +
   input history + resimulation. Do not bolt delay-only netcode on later.
2. **Input buffering / command system** (`.cmd` files: command definitions
   with input sequences + timing windows). WH's LP1/RP2/LK3/RK4 inputs +
   Tekken-style motion inputs (f, F + LP+RP etc.) map cleanly onto a
   command table with per-command buffer windows. The KESSHOU input
   scheme (f, F + LP+RP inside a ready window) is a command-table entry,
   not special-case code.
3. **Training mode** (pause menu extras): dummy control, AI level, dummy
   mode, guard mode, fall recovery, distance setting, button jam. WH
   training mode should ship these as a checklist, not just "dummy stands
   there". Guard mode + fall recovery are the two that most affect
   combo testing.
4. **Hit/block data model**: Ikemen/MUGEN states carry hit flags, guard
   flags, and per-state physics. WH's `hitbox.js` (frame-gated boxes) is
   the WH-native version; keep frame data (startup/active/recovery) as
   DATA on moves, not hardcoded per move.
5. **Screenpack/motif system**: menus as data (system.def + lifebars +
   select screen as configurable layout). WH's T7-sourced select screen
   should stay data-driven the same way — layout numbers in files, not
   in code — so menu iteration doesn't need code changes.
6. **Debug keys + debug mode**: frame step, hitbox display toggle,
   state display. WH needs the same three debug toggles in training mode
   (hitbox display already has its wireframe helper in `hitbox.js`).

## Explicitly NOT ported
- 2D sprite pipeline, MUGEN character format (`.air/.cns/.cmd` as a file
  format — the IDEAS port, the format doesn't), ZSS/Lua scripting
  (WH is JS; a JS move-scripting layer is the equivalent, if wanted).
- Any MUGEN community character content (licensing + canon rules).

Buttons, per standing rule: LP1 = Left Punch = Tekken 1, RP2 = Right
Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.
