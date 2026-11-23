# KoC2 download link — WORKLOG

Task: serve the KoC2 English ISO over HTTP from the Oracle VM so Mars can download it to his phone and play it in a PS2 emulator app (AetherSX2/NetherSX2). Mars asked for the link 2026-11-20 ~14:24.

State at start (verified by parent via SSH ~14:25):
- M2 English ISO: /home/ubuntu/koc2-english/King of Colosseum II (English).iso, 4,593,778,688 bytes, SHA-256 e3febfb1… (complete)
- Hybrid ISO: /home/ubuntu/koc2-english/King of Colosseum II (Hybrid JP-EN).iso, 1,071,808,512 bytes vs 4.6GB real — INCOMPLETE, copy owned by disk-relief lane (0af8798d). Do NOT re-copy; report state only.
- VM disk: 13G free. nginx config NOT in /etc/nginx/sites-enabled/ — locate it first.

Rules: SSH only via the HTTP CONNECT tunnel + explicit key; never touch port 443 (ttyd); never touch the TeraBox nginx token path (/tb-46d45aabd70ca6b9c8b808a9/); back up any nginx config before editing; no file copies of the 4.6GB ISO (alias only); no repo pushes.

## 2026-11-20 ~14:26-14:29 EST — DONE, link live + verified

- Found the nginx config: /etc/nginx/sites-available/arcade (port 80, symlinked from sites-enabled/). Backed up to /etc/nginx/sites-available/arcade.bak-koc2link BEFORE editing. TeraBox token path untouched; port 443 untouched.
- Added two exact-file locations to the port-80 server block (alias, NO file copy):
  - location = /koc2/King-of-Colosseum-II-English.iso -> "/home/ubuntu/koc2-english/King of Colosseum II (English).iso"
  - location = /koc2/ps2-bios.zip -> /home/ubuntu/koc2-english/ps2_bios_official.zip (BIOS included: AetherSX2/NetherSX2 cannot run without one)
- Permissions so www-data can serve from /home/ubuntu (matches AGENTS.md a+rX pattern): chmod o+x /home/ubuntu; chmod o+rx /home/ubuntu/koc2-english; chmod o+r on the ISO + BIOS zip.
- Reload race noted: first curls at 19:26:49 returned 404 (old workers still shutting down; new workers started 19:26:48). Retried a minute later — 200. No config error.
- Verification (all on the VM + externally):
  - HEAD: 200, Content-Length 4593778688 (exact), application/octet-stream, ETag "6b0038db-111cf8000", Accept-Ranges: bytes.
  - Range 0-1MB: HTTP 206, SHA-256 f46ec23f... matches file head.
  - Range @2GB 1MB: HTTP 206, SHA-256 30e14955... matches file.
  - Range tail 1MB: HTTP 206, SHA-256 33954cf4... matches file.
  - BIOS range 64KB: HTTP 206, SHA-256 cf75fbfe... matches file. BIOS HEAD: 200, Content-Length 13380830.
  - Full ISO SHA-256: e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc (matches known e3febfb1...).
  - External check from this sandbox: 200 + 206, same ETag.
  - Arcade root still 200 after reload.
- Hybrid ISO state (read-only, NOT touched): still 1,071,808,512 bytes (epoch timestamp) at all three checks (~14:25, ~14:27, ~14:29) — copy not visibly progressing; owned by disk-relief lane 0af8798d. When it completes + hash-verifies (SHA-256 45193305...), add a matching exact location and report that URL as a follow-up.

## URLs
- ISO: http://132.145.194.139/koc2/King-of-Colosseum-II-English.iso (4,593,778,688 bytes, SHA-256 e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc)
- BIOS: http://132.145.194.139/koc2/ps2-bios.zip (13,380,830 bytes)
