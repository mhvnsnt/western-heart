# Western Heart — TeraBox ↔ Repo Connection Manifest

**Owner directive (seq 78167):** "connect it to the western heart GitHub repo so the
repo knows the TeraBox is connected directly inside it." This file is that manifest.

## Account
- Login: Google via fmmg.mars@gmail.com (verified working 2026-10-12)
- Plan: **Premium Plus 7-day trial ($0.50) — EXPIRES 2026-10-20.** Renew 1–2 days before.
- Capacity: 5TB trial (30GB permanent + time-limited promo space; web UI does not show expiry)

## Folder map

| TeraBox folder | Contents | Repo counterpart |
|---|---|---|
| `/western-heart/teardown-source-binaries/` | WWF-No-Mercy.zip (24.7MB), WWF No Mercy (USA) (Rev-A).z64 (32MB), Animate3D.exe (224KB) | `teardown/TEARDOWN-SOURCES.md` (hashes); extracted knowledge in `teardown/wwf-no-mercy/` |
| `/western-heart/pantera/tail-rig/` | pantera_tail_frames.zip (35.5MB, 72 source frames) | `roster/pantera/tail-rig/` |
| `/western-heart/street-fighter-5/` | **PLANNED** — FitGirl SFV Champion Edition 26.7GB, chunked ~2GB uploads | `teardown/street-fighter-5/SFV-PULL-PLAN.md` |
| `/western-heart/def-jam-fight-for-ny/` | **PLANNED** — Def Jam ISO 4.47GB | `teardown/def-jam-fight-for-ny/` |
| `/western-heart/tekken7/` | **CANDIDATE** — full 47GB game was blocked on VM disk; TeraBox Premium is the landing-zone candidate | `teardown/tekken7/` |

## Rules
- Remote Upload is GONE from the TeraBox website (confirmed 2026-10-12); all uploads go through the browser file-grant path or chunked manual upload.
- Browser file-grant has a size limit — files >~1GB (WMXIX ISO 1.4GB, Tekken 3 zip 494MB, TEKKEN3.XAS 511MB, Urban Reign ISO 4.14GB) need chunked upload or another ingest path.
- Everything on TeraBox must also be traceable from the repo (this manifest + `teardown/TEARDOWN-SOURCES.md`). TeraBox is storage, never the system of record.
- Last verified: 62.1MB / 1024GB (2026-10-12). Re-verify after each upload batch.
