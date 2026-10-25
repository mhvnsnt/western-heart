# Tekken 6 (PSP) — hand/arm rigging + posing reference

Status: **no T6-native skeleton extract exists yet** in the repo.

What was checked:
- teardown/tekken6/decrypted/: EBOOT.DECRYPTED.ELF + README only (decrypt work).
- teardown/tekken6/models/: NDPP bounding-volume docs only.
- Release tekken6-psp-v1: PSP ISO (unextracted for skeleton).
- Release tekken6-recon-20261016: recon work backup.

Best available source: tekken6-era-hand-arm.json (this directory) — the full
147-bone Tekken 6-era skeleton with complete hand/finger layout, extracted from
the Tekken Revolution beast-king SFM port (same engine family as T6 PSP):

- Arm chain: arm {side} shoulder 1 -> shoulder 2 -> elbow -> wrist
  (+ elbow adj / shoulder 2 adj / shoulder 1 adj 1-2 / back adjustment bones)
- Fingers: "arm {side} finger {1..5}{a|b|c}" — 5 digits, 2-3 segments each
- Fist/open/grip = authored animation poses on the finger chains (no procedural system)
- Bind-pose positions (meters) included in the JSON for retarget scaling

Open work: extract a T6-PSP-native skeleton to confirm 1:1 with the TR instance.
