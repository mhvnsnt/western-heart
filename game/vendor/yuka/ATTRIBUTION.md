# Attribution — Yuka.js

Vendored from the official repository. **Unmodified build.**

- **Project:** Yuka — JavaScript library for game AI
  (https://github.com/Mugen87/yuka)
- **Author:** Mugen87 (https://github.com/Mugen87)
- **License:** MIT — see `LICENSE` in this directory
  (Copyright © 2023 Yuka authors)
- **Build vendored:** official ES-module build `build/yuka.module.js`
  from `master` @ `10591304811222d6856020d5de129b39ef43b58d`
  (committed 2023-01-16), blob SHA
  `4a4cc6e779b9b4e9fc14b8f2de34fefcae6f729c`
- **Used for:** the combat AI brain — `game/js/ai/combat-state.js`
  (hierarchical combat state machine), `game/js/ai/grapple-chains.js`
  (grapple chain state machine). Yuka's `State` / `StateMachine`
  classes drive the CPU fighter's decisions; the game code only
  executes the resulting intents through its own `try*` calls.

No changes were made to the vendored build. To update: replace
`yuka.module.js` with the new official build and record the new
commit SHA + blob SHA here.
