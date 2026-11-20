# Tekken 5 — hand/arm rigging + posing reference

Status: **no T5-native skeleton extract exists yet** in the repo or releases.

What was checked:
- Release tekken5-ctype5-glbs-v1 (8 assets): decoded VIF 0x82 geometry — nodes have
  NO names and NO skin/skeleton. Geometry only.
- Release tekken5-costume-glbs-v1 (81 assets): costume meshes — 5 unnamed nodes,
  no skins. Geometry only.
- Release tekken5-ps2-v1: acquisition marker, 0 assets.
- No teardown/tekken5/ directory exists in the repo.

Proxy used: the Tekken 6-era 147-bone skeleton (see ../tekken6/rigging-reference/
tekken6-era-hand-arm.json) — T5, T6, Tekken Revolution and TTT2 share the same
engine family and the same "arm {side} finger {1..5}{a|b|c}" naming convention
(this naming is visible in every T5/T6-era community port; the 147-bone layout
in the beast-king SFM port is the T6/Revolution instance of it).

Open work: decode a T5-native skeleton from the PS2 ISO (Internet Archive) or a
T5 model pull to confirm the T5 instance matches the T6-era convention.
