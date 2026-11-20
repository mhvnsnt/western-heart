# Tekken Tag Tournament 2 — hand/arm rigging + posing reference

Status: **no TTT2-native skeleton extract exists yet** in the repo.

What was checked:
- teardown/tekken-tag-tournament-2/extracted-small/: MD5-named files are
  encrypted Xbox "LIVE" containers — not parseable without decryption.
- Release ttt2-7z-v1: full-game split 7z (27 assets) — not pulled for this task (size).
- tekkenmods-docs/files/en/Tekken_Tag_Tournament_2/: modding how-tos only, no skeleton data.

Best available source: tekken6-era-hand-arm.json — the full 147-bone Tekken 6-era
skeleton (TTT2 is the same engine family; the "arm {side} finger {1..5}{a|b|c}"
convention carries over):

- Arm chain: arm {side} shoulder 1 -> shoulder 2 -> elbow -> wrist
- Fingers: 5 digits, 2-3 segments each, full bind positions in the JSON
- Fist/open/grip = authored animation poses on the finger chains

Open work: decrypt the extracted-small LIVE containers or pull one TTT2-native
model to confirm the TTT2 instance.
