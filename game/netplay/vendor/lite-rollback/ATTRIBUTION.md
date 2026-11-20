# Attribution — lite-rollback

- **What:** Zero-GC binary ring buffer + GGPO-shaped rollback `Session` for browser-native deterministic netcode. Single-file ESM, zero dependencies, zero allocations after construction.
- **Source:** https://github.com/peshovurtoleta/lite-rollback
- **Author:** Zahary Shinikchiev
- **Version vendored:** 1.2.1 (HEAD 2026-10-16)
- **License:** MIT (LICENSE vendored alongside)
- **Why it beats what we had:** we had nothing — no rollback core for the web Three.js build. This is the exact piece: input prediction, snapshot ring, rollback + re-simulate, confirmed-frame watermark, per-frame checksums for desync detection, input-delay lead to cut rollback frequency. Explicitly benchmarks a Tekken-style fighter (~4 KB state, 7–15 frame depth) as "fine".
- **What was vendored:** `src/index.js`, `src/index.d.ts`, `README.md`, `llms.txt`, `LICENSE`. Tests/bench/demo upstream were not vendored (upstream CI covers them); our own proof lives in `game/netplay/mirror.mjs`.
- **Update path:** single file — drop in a new `src/index.js` from upstream releases.
