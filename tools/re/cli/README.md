# CLI decoder stack — inventory + install (2026-10-19)

Small tools live on the VM; install recipes live here. Nothing here guesses at
formats — these are the real decoders.

## On the VM now (verified 2026-10-19)

| Tool | Version | Path | Status |
|------|---------|------|--------|
| Ghidra | 12.1.4 PUBLIC (2026-09-21, current stable) | `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC` | ✅ headless verified |
| Temurin JDK 21 | 21.0.12.1+1 | `~/workspace/tools/ghidra/jdk-21.0.12.1+1` | ✅ |
| GhidraMCP | 2.0.0 | `~/workspace/tools/ghidra-mcp/` (venv + bridge) | ✅ extension installed; HTTP smoke test pending |
| ghidra-psx-ldr | — | `Ghidra/Extensions/ghidra_psx_ldr` | ✅ (PS1 EXE loader) |
| 7z / 7za | 24.09 | `~/workspace/tools/p7zip/extracted/usr/bin/` | ✅ |
| file | system | `/usr/bin/file` | ✅ |

## Needs work (honest flags)

| Tool | Issue | Path forward |
|------|-------|--------------|
| QuickBMS | Only 32-bit binaries on hand — **segfault** on this 64-bit kernel (exit 139). GitHub source tarballs proxy-blocked from this VM. | Compile from source on a better network: `https://github.com/aluigi/quickbms` (gcc build, single C file). Then drop the 64-bit binary at `~/workspace/tools/quickbms64`. |
| binwalk | v2 is EOL/archived (CVE-2026-7179, no patches). v3.1.0 (Rust) is current but needs cargo — no Rust toolchain on this VM. | `cargo install binwalk` on a machine with Rust, or Kaggle. Marginal for game ISOs (firmware tool) — low priority. |
| vgmstream | Not installed. Needed for game audio (PS2 ADX/VAG, etc.). | Build `vgmstream-cli` from https://github.com/vgmstream/vgmstream (cmake). Medium priority. |
| xdelta3 | Not installed. | Static binary or apt on a machine with working apt. Low priority. |
| ps2dis / PS2-specific | Not installed. | Evaluate: `ps2dis` (old), Ghidra's MIPS SLEIGH covers most PS2 needs; R5900 MMI gaps are the known hole. |
| Noesis | Windows-only GUI; Python bridges exist but need a Windows host or Wine. | Documented, not installed. Low priority while Blender/gltf-transform cover mesh work. |

## Install recipes

```bash
# binwalk v3 (needs Rust)
cargo install binwalk
# vgmstream-cli (needs cmake + gcc)
git clone https://github.com/vgmstream/vgmstream && cd vgmstream && cmake -B build && cmake --build build
# QuickBMS 64-bit (needs gcc)
# from https://github.com/aluigi/quickbms source:
gcc -o quickbms quickbms.c -lm -ldl -pthread
```

## PS2 / PSP notes

- PS2 ELFs are big-endian MIPS. Ghidra auto-detects `MIPS:BE:32:default`; R5900 MMI
  (parallel) instructions show as Pcode errors — analysis continues, data hunting unaffected.
- PSP EBOOT.BIN: decrypt first (KIRK). See `teardown/tekken6/` for the worked example.
- ISO9660: `game-reverse-engineering/tools/iso9660_extract.py`.
