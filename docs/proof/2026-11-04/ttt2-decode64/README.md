# TTT2 0x64 decode — proof (2026-11-04)

- `clip977-decoded.json` — full decoded channel data for data004 table-0
  entry 977 (23 tracks x 30 frames), produced by
  `tools/ttt2_mota_decode64.py` from the algorithm in
  `docs/tech/ttt2-mota/DECODE64-SPEC.md`.
- `clip621-decoded.json` — entry 621 (23 tracks x 100 frames); the
  anatomical-signature validation in the spec was measured on this clip
  (type-6 hinge tracks move on exactly one component).
- The moving render (three.js skeleton viewer, headless Chromium) of
  entry 977 was frame-verified by the lane: coherent humanoid, feet
  planted, upper-body motion reads cleanly. Video delivered with the
  lane report (owner-facing proof folder), not stored in-repo due to
  size conventions for proof media in this folder set.
