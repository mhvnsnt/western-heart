
## 2026-11-10 14:55 CST — T7 graph heading trace (PR #1737, no code change)
Move-entry yaw rules decoded (flip on extradata bit15; turn -u_0x56 gated by u_0x98 bit27 and 0x3C00 != 0x1C00). Per-frame yaw = base + undecoded term T (writer untraced) → facing after first source move stays unknown (fail closed). Continuous neutral→jab→string→return→dash→run→return NOT achieved; not merged, not deployed; Pages not retried. Proof: `docs/proof/2026-11-10/t7-heading/README.md`.
