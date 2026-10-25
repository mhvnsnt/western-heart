# Vendored: JoltPhysics.js (wasm-compat)

- **Package:** `jolt-physics` 1.1.1 (npm)
- **Source tarball:** https://registry.npmjs.org/jolt-physics/-/jolt-physics-1.1.1.tgz
- **Upstream repo:** https://github.com/jrouwe/JoltPhysics.js
- **Author:** Jorrit Rouwe (Jolt Physics author)
- **License:** MIT — see `LICENSE` in this directory
  (Copyright (c) 2022-2024 Jorrit Rouwe)
- **File:** `jolt-physics.wasm-compat.js` (3.2 MB)

## Why this build

`wasm-compat` embeds the WASM binary base64-encoded inside the JS bundle,
so the game ships as plain static files on GitHub Pages with no separate
`.wasm` file to host and no `locateFile` configuration. It is the
single-threaded build — no COOP/COEP headers required (GitHub Pages does
not send them, so the multithread builds are unusable there).

## Why vendored (not CDN)

The game already vendors three.js locally (`game/vendor/three.module.js`)
and ships as static files. Jolt follows the same rule: no runtime
dependency on unpkg or any CDN. `game/js/softbody.js` dynamically imports
this file on first use (`../vendor/jolt/jolt-physics.wasm-compat.js`),
so the 3.2 MB parse cost is paid once, lazily, and only when a fighter
with a soft-body region loads.

## What the game uses

Only the **soft-body** subsystem (XPBD): `SoftBodySharedSettings`,
`SoftBodyCreationSettings`, `SoftBodyMotionProperties`, one `JoltInterface`
with a collision-free layer setup. No rigid bodies, no character
controller — those stay wherever the game already has them.

## Upgrading

1. Download the new `jolt-physics` tarball from npm.
2. Extract `package/dist/jolt-physics.wasm-compat.js` over this file.
3. Copy `package/LICENSE` over `LICENSE` if it changed.
4. Update the version number at the top of this file and in the header of
   `game/js/softbody.js` (`SoftBody.JOLT_VERSION`).
5. Re-run `node test/softbody.test.mjs` — the sim-behavior assertions
   (drift / dent / recovery / pinning) must still pass.
