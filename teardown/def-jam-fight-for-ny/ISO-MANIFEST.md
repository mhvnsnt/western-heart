# Def Jam: Fight for NY — ISO Manifest

**Game:** Def Jam: Fight for NY (EA Chicago, 2004)
**Platform:** PlayStation 2 (USA, SLUS_210.04)
**Source:** Internet Archive `slus-210.04.-def-jam-fight-for-ny`

## ISO Details

| Field | Value |
|---|---|
| **Filename** | `SLUS_210.04.Def Jam - Fight for NY.iso` |
| **Expected size** | 4,694,573,056 bytes (4.47 GB) |
| **SHA256** | _TBD after download completes_ |
| **Status** | Download in progress (see below) |

## Download Status (2026-10-16)

The full ISO is being pulled from archive.org. As of 2026-10-16:
- Partial on disk: 1,480,790,016 bytes (~31.5%)
- Download parked by disk-space law (resume gate: disk <75%)
- Resume command (when disk allows):
  ```bash
  cd ~/workspace/terabox-staging/def-jam
  curl -L -C - --retry 5 --retry-delay 15 --retry-all-errors \
    -o "SLUS_210.04.Def Jam - Fight for NY.iso" \
    "https://archive.org/download/slus-210.04.-def-jam-fight-for-ny/SLUS_210.04.Def%20Jam%20-%20Fight%20for%20NY.iso"
  ```

## Storage Plan

Once the download completes and verifies (exact byte size 4,694,573,056):
1. **GitHub Release** on `mhvnsnt/western-heart` (split into parts if needed)
2. **Dedicated repo** `mhvnsnt/def-jam-fight-for-ny` (owner to create — GitHub App cannot create repos)
3. **TeraBox** `/western-heart/defjam/` (browser lane)

Per the ONE-STORE RULE: once 100% verified on GitHub OR TeraBox, the local copy may be cleared.

## What's Already Here

The surgical extraction (~450MB of game data pulled via HTTP Range requests, no full download needed)
is in `surgical/`:
- `xml/` — FIGHTER.XML (142 fighters), CHARS.XML, VENUE.XML (48 venues), GAMEDATA/GCONFIG/GAMECORE.XML, AKI_CFG.XML, COMBS.XML, ENTITY.XML, TAUNT.XML
- `motion/` — Animation system data (CAMERA.XML, MAIN_ALL.DAT)
- `chars/v2ip_extracted/` — Extracted character models (V2IP_*.o, *.ssh)

Extraction tools are in `tools/` (eabig_extract.py, iso_tree.py, assemble.py, bigf_extract.py, resilient_fetch).

See TEARDOWN.md for the full disc layout and ANIMATION-FINDINGS.md for the grappling/animation system analysis.
