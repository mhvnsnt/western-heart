# Vendored: inkjs 2.4.0 (MIT, Inkle)

File: `ink.mjs` in this directory is the inkjs 2.4.0 runtime
copied verbatim from the npm package (`inkjs/dist/ink.mjs`,
128,049 bytes), NOT a CDN load and NOT modified. License: MIT
(Inkle). Source: https://github.com/inkle/ink (inkjs is the
official JavaScript port of the Ink runtime).

Why vendored: PR #1044's `game/js/ink-loader.js` takes a
caller-passed Story constructor so the game keeps no CDN
dependency. `game/js/story-wiring.js` passes this vendored
constructor in, so compiled Ink JSON stories actually run in
game. The inkjs-compiler BOM gotcha (compiler emits a UTF-8
BOM that inkjs's JSON.parse chokes on) is handled by
`ink-loader.js`'s BOM strip, not by editing this file.

Upgrade path: replace this file with the newer inkjs dist
`ink.mjs` and update the version line above; no game code
changes are needed (the Story surface is stable).
