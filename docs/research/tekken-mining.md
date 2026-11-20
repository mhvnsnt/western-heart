# Tekken Mining — research notes (2026-10-16)

Lane goal: close the customization-item-data gap for the Creation Suite
(`tools/creation-suite/`, Tekken-7-architecture: 16 equipment slots, 21-field item CSV spec,
slot groups, color system, 57 character IDs from tekkenmods-docs/TKDataPatcher).
Targets: Tekken Tag Tournament 2 (Xbox 360 GOD) and Tekken 6 (PSP).

Full findings: `teardown/ttt2-customization-research.md`, `teardown/tekken6-customization-research.md`.

## What was found

**Tekken 6 PSP — item names + categories (new this lane):**
- Item NAME tables in the decrypted bulk: `[u32 rec_size][u8 item_idx][name\0][pad]`,
  per-language (EN/IT/FR/DE…), 10,495 records scanned. E.g. Sledgehammer, Japanese Sword,
  Leather Pants, Long Jin Bangs, Ki (Pink), SP Rage (Fire).
- Slot categories via NTXL string tables (120 in bulk): Hair - Back, Hair - Front (Right),
  Face - Other (+ full UI string set).
- EBOOT type system: `sbcustomize_item_t`, `tcb_CustomizePSP_Manager`,
  pack patterns `CUSTOMIZEPACK%d_%d` / `HAIRCUSTOMIZEPACK%d` / `DEFAULTPACK%d`.
- Item models = NDPP containers (known from prior lane); extraction owned by inflate lane.

**TTT2 — research complete, extraction blocked:**
- GOD layout mapped (title 4E4D0859, 52×170MB DataXXXX + STFS updates).
- Asset formats from tekkenmods-docs: `.nud`=NDXR geometry, `.nut`=NTXR textures,
  `.pack`=unknown archives (prime item-data suspect), `.mvl` movelists, BONE skeletons.
- Tool catalog evaluated (see PULL-LOG.md): zarmanager already covers GOD reading;
  360tools/XGDTool/GODSend-360/ulbox360 documented as fallbacks, not pulled.
- BLOCKED: 7z reassembly stalled at 11/26 parts (no process since 2026-10-15 20:58Z);
  surfaced per NO-DROPPED-WORK, not resumed (reassemble lane owns it).

## Pull-in log

- `pycdlib` (pip, LGPL-2.1-or-later) — pulled; used for PSP ISO9660 listing.
- zarmanager (dfdevx2, license unverified) — already in use by prior lane; no new pull.
- Details: `docs/research/PULL-LOG.md`.

## Open threads (for next lanes)

1. Locate `sbcustomize_item_t` definition array (slot/price/model-ref per item) — join key is
   the item_idx byte from the name tables.
2. Enumerate all 120 NTXL tables → complete slot-category list for the Creation Suite.
3. Resume TTT2 7z reassembly, then surgical-pull `.pack`/`.nud` files and document item layout.
4. When the inflate lane finishes the 56 GZIP files, cross-reference NDPP models with item names.

## Method notes

- Disk: all scratch in /tmp (bulk scans stream the 384MB file; nothing re-extracted).
- Read-only on other lanes' work dirs (`work/decrypt*`); no interference with the active
  inflate lane.
- No proprietary models pushed to the repo — formats/offsets documented only.
- TTT2's 5.7GB partial 7z retained per NEVER-DELETE-GAME-FILES LAW (not deleted, not "cleaned").
