# Motion/Move-Data Identification Status (T6 Lane A, 2026-10-21)

Target: locate move/motion data (offsets, sizes, magic-bytes/structural
evidence) in the 2,169-entry DATA401 manifest so moves can be pulled for the
canon characters (owner order 2026-10-21 ~13:02 CDT).

## What was tried this run
1. **DINF manifest header** (decrypted, verified — see DINF-MANIFEST-NOTES.md):
   120 bytes, fields = magic/version/sector-size/entry-count/byte-total/names/
   build-path. **No per-entry table, no motion info.** Entry offsets/sizes
   live only in DATA401.IDX.
2. **DATA401.IDX** (LBA 230240, 26,028 B = 2169 × 12 B exactly, encrypted):
   decrypt unresolved — goes through imported `openPac` (invisible
   statically); keyset-A attempt (K1=0xE11CF772/K2=0xA0DC9EB4) yielded no
   structure (2026-10-14). Without the IDX, no entry has a known offset/size.
3. **Bulk magic scan**: impossible statically — bulk sectors are uniformly
   encrypted (entropy ~7.91; see BULK-SPOTTEST-2026-10-21.md). No GMO/TIM2/
   motion magic recoverable from ciphertext.
4. **EBOOT string evidence** (`decrypted/EBOOT.DECRYPTED.ELF`, banked 4.1 MB):
   - No motion file-extension strings (no `.mot`/`.anm`/`.skl`/`.mbd`).
   - `link_ANIMEFF_*` / `PrmANIMEFF_*` / `ANIMEFF_*` — animation *effect* hooks
     (stage/scene effects), not character motion data.
   - `tcb_kkPlayerSkeleton` — C++ type name confirming a skeleton-driven
     player animation system exists (`tk::` engine namespace).
   - Pack interface strings: `openPac`, `ktRead`, `%s/DATA401.IDX`,
     `disc0:/sce_lbn0x%x_size0x%llx` — entries are addressed by index/LBN,
     not by filename with a motion extension.

## Verdict
**Motion/move-data offsets are NOT identifiable from static evidence yet.**
The identification chain is blocked at exactly one link: the IDX decrypt
(2169 × 12-byte entries). Everything downstream — entry boundaries, then
magic/structure scans for motion data inside entries — waits on that.

## What unblocks it (no re-hunt by lane A — sweep owns this)
- The teardown-sweep lane's decrypt6 encode-context crack (56 failing DATA401
  containers, live-PPSSPP work in `_t6r4-work`, checkpoint
  `teardown-sweep-tekken6-psp.json`): once containers decode, entry payloads
  become scannable for motion structures.
- Or the IDX `openPac` decrypt (imported PRX — needs live trace or deeper RE).

## Already-decodable containers (step 4 — landed)
- `DINF_400.BIN` → `decrypted/DINF_400.DECRYPTED.BIN` (120 B, sha256
  `e79c563320b1edd9b4c5ae26d36e40c2f99d9064cf7046cf37cb957e3aba0b1c`):
  the only fully decoded DATA401 container. Reproducer banked
  (`tools/dinf_decrypt_verify.py`).
- Sector 230256 (sole CRC-passing sector): decrypts to random bytes with its
  extracted keys — NOT decodable via the sector path; documented, not forced.
- Everything else in the bulk: still cipher. No container was "decoded" by
  guessing — evidence only.

## Handoff for the next attempt / sweep
When the sweep's containers decode: (1) decrypt IDX if possible, else use
container order as entry proxy; (2) magic-scan payloads for GMO (`GMO\0`),
TIM2, and motion structures; (3) cross-reference entry sizes against the
384,051,200-byte manifest total. Lane A's banked tooling (sector_cipher.py,
dinf_decrypt_verify.py, bulk_spottest.py) is the static-side foundation.
