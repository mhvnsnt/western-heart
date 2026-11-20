# Attribution — lite-rollback-webrtc

- **What:** `RTCPeerConnection` + `RTCDataChannel` transport for lite-rollback. Browser-to-browser, no server in the data path. API: `createHost`, `createJoiner`, `connectPeer`, `wrapDataChannel`.
- **Source:** https://github.com/peshovurtoleta/lite-rollback-webrtc
- **Author:** Zahary Shinikchiev
- **Version vendored:** 1.1.0 (HEAD 2026-10-16)
- **License:** MIT (LICENSE vendored alongside)
- **Why it beats what we had:** we had no WebRTC transport. This plugs straight into the vendored `lite-rollback` session (`send`/`onMessage`/`close` contract, verified by `assertTransport`) and ships a Pong demo we used as the reference for `game/netplay/demo/`.
- **What was vendored:** `src/index.js`, `src/index.d.ts`, `LICENSE`. Upstream examples/tests not vendored.
- **Signaling note:** the package deliberately ships no signaling — our demo uses manual SDP copy/paste (zero server), and `game/netplay/signaling/server.js` is a minimal WebSocket room server for real use.
