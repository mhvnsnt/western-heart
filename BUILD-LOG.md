
## 2026-11-10 14:55 CST — T7 graph heading trace (PR #1737, no code change)
Move-entry yaw rules decoded (flip on extradata bit15; turn -u_0x56 gated by u_0x98 bit27 and 0x3C00 != 0x1C00). Per-frame yaw = base + undecoded term T (writer untraced) → facing after first source move stays unknown (fail closed). Continuous neutral→jab→string→return→dash→run→return NOT achieved; not merged, not deployed; Pages not retried. Proof: `docs/proof/2026-11-10/t7-heading/README.md`.

## 2026-11-27 CST — Pantera: all six attires rigged, wired and checked in poselab
A5/A6 were static and lying on their side; they are now rigged from the A3 parts (rig_multipart_from_donor.py). A4 had exploding arms from a stale skin and is reweighted from A3. A3's weights were re-smoothed against the T7 King poses the fight actually plays (game_pose_seam_smooth.py, layer coupling), which removes the shin shards and trouser tears. A2 was packed to 18.7 MB so Cloudflare Pages hosts it. Originals are kept beside the new files. Limits: A3-A6 trouser stretch is still p99.9 up to 19, feet joints carry no weight, and the tail is rigid. Proof: `docs/proof/2026-11-27/pantera-attires/README.md`.
