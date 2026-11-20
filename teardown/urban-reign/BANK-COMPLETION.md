# Urban Reign — Motion-Bank Completion (Phase 6)

The motion-bank census is now complete for the shipped data. Every entry
that could hold a `.gyu` motion bank in either AFS of the retail disc
image (ISO release `urban-reign-iso-v1`) has been enumerated, and every
bank found has been decoded with `tools/ur_gyu.py` (Phase-5 type-14 fix
included) and searched by the name bridge at the Phase-5 gate
(maxDev ≤ 0.10 mm, unique — the gate did not move).

## Totals

| | count |
|---|---|
| Motion banks in the shipped AFS set (DVD000) | **285** |
| — decoded in Phases 2–5 (31 pmot + 10 tmot + 3 general) | 44 banks / 2,353 motions |
| — decoded NEW in Phase 6 | **241 banks / 1,004 motions** |
| Total motions searchable after Phase 6 | **3,357** |
| DVD001 AFS entries header-censused | 1,173 → **0 motion banks** |
| `motion/` motdat entries (record lists, bridge inputs — not banks) | 162 |

New-bank inventory (entry → bank id, motion count, frame stats):
`motion-names/BANK-INVENTORY-PHASE6.json` (all 241 new banks; every
bank's every motion root decoded — 1,004/1,004, 0 failures).

## Census — DVD000 AFS (2,431 entries), motion-relevant classes

- `motion/` — **162 entries** = 81 motdat lists × (`.bin` + `.info`):
  `test/` 78 (39 lists: Gnrl + P×27 + T×11), `test30/` 78 (same 39),
  `wptest/` 6 (Gnrl, P44, P55). These are RECORD LISTS in the cracked
  motdat format (the bridge's input), not `.gyu` banks — there is nothing
  in them for `ur_gyu.py` to decode. The bridge's held set is the
  `test/` P-lists (27 fighters, 886 records; Phases 4–5).
- `tec/motion/` — 44 entries: `gyuindex.bin` + `gyuindex_ppk.bin` (bank
  INDEX tables, read in Phase 4 — not banks); 3 `general.gyu` banks
  (normal / 30frame / weapon — decoded Phase 2); 3 `general_index`
  tables (not banks); `gyu_debug.gyu` (1-motion, 21-bone bank — decoded
  NEW in Phase 6); `demo/demo_motionNNN.g` ×35 (21-bone cutscene banks —
  decoded NEW in Phase 6).
- `tec/demo/` — 273 entries, ALL fetched and decode-tested in Phase 6:
  203 are single-motion `.gyu` banks (FMDL facial ×94 + yarare ×63 —
  14 bones; `anim_obj` ×32 — 2 bones; `effect` ×14 — 2 bones; AFS
  duplicate-name variants fetched by raw offset so every directory entry
  is represented) — decoded NEW. The remaining 70 are NOT motion banks:
  `data/camera_dataNNN.bin` ×35 (demo camera data; `.gyu` Bank parse
  fails on the header) and `data/demo_dataNNN.dam` ×35 (demo damage
  tables; Bank parse fails likewise).
- `afs/safe/ppk/` motion-bearing PPKs: pmot ×31 + tmot ×10 (banks,
  decoded Phase 2); `demo_data` ×35 (containers embedding byte-identical
  copies of the standalone `demo_motion` banks — verified byte-identical
  on 3/3 samples: 003 @99200, 021 @76800, 200 @15488 — not new banks);
  **`main.ppk` — TWO DISTINCT EMBEDDED BANKS NEW in Phase 6**
  (`main_bank1` @209024: 331 motions, 21 bones; `main_bank2` @1647872:
  326 motions, 21 bones), found by a validated embedded-bank scan
  (header prefilter + motion-0 root decode) and cut out as bank files;
  `main_in.ppk` (embeds byte-identical copies of `general_normal`
  @0x80 and `general_30frame` @1533056 — verified byte-identical, plus a
  non-bank tail carrying a `tec/motion_verification/` path string — not
  new banks); `mainx.ppk` (128-byte PPK header shell, zero payload
  bytes — no bank); `select.ppk` and `weapon.ppk` (validated scan:
  0 banks in each).
- char ×72 / mission ×100 / stage ×7 PPKs (model / mission / stage
  containers): sample-verified with the same validated scan —
  `char001.ppk`, `mission001.ppk`, `stage003.ppk` each contain **0**
  embedded `.gyu` banks; their fncc payloads are the Phase 1–3 model /
  mission / stage formats, not motion banks.

## Census — DVD001 AFS (1,173 unnamed entries)

DVD001 was never content-searchable by name (entries are `file_NNNNN.bin`).
Phase 6 located the AFS in the ISO (ISO9660 directory: DVD001.AFS at LBA
881429 → ISO byte 1,805,166,592; the same method reproduces DVD000's
known base 3,063,840,768 exactly) and fetched the first 128 bytes of
**every** entry (clustered range fetches; full census:
`motion-names/DVD001-HEADER-CENSUS.json`). Result:

- 1,132 entries — **CRI ADX audio** (header signature `8000` + copyright
  offset, encoding 0x03, sample rate at +8; `(c)CRI` copyright string
  verified in-entry). A stream format, not a container.
- 39 entries — **PSS** (MPEG program stream, `00 00 01 BA` — cutscene
  movies, 0.76 GB). A stream format, not a container.
- 2 entries — empty (size 0).
- **0 entries** with a `.gyu` bank header, **0** PPK containers.

DVD001 holds no motion bank, at any entry start or (both its formats
being non-container streams) embedded. The Phase-5 open thread — "source
bank outside the searched set" — is therefore NOT hiding in DVD001.

## Re-run outcome (Job 2, details in `motion-names/PHASE6-NAME-BRIDGE-ADDENDUM.md`)

- New own-bank proofs: **0** (no Phase-6 bank is any fighter's own pmot
  bank — the pmot set is closed at 31 by the AFS + `gyuindex.bin`).
  `motdatName` annotations unchanged at **484**; cross-checked this
  phase: annotations in `game/assets/movesets/ur-char*.json` = 484 =
  own-bank proven total.
- New cross-bank proofs: **18 records** proven in `main_bank1` /
  `main_bank2` (Phase 5 had searched those banks only for the P1 five);
  17 of them were already cross-proven elsewhere — 1 record,
  char032 rec18 `cbco_spd_chuka`, is **identified for the first time**
  (→ main_bank1 m115, maxDev 0.0343 mm). Cross-bank total: 306 → **307**.
- The 5 P1 records (6 `cbco_screw_r`, 10 `moco_d_jumpk_f`,
  11 `moco_d_jumpk_y1`, 12 `moco_d_jumpk_y2`, 14 `moco_doubleairk_f`):
  **they do not close.** No hit in any of the 241 new banks (best
  new-bank deviations 205.0–4,342.7 mm). With the searched set now =
  every motion bank in the shipped AFS set, the Phase-5 verdict is
  definitive for shipped data: their source bank is not in the shipped
  AFS set at all (the motdat test tool's working banks / an unshipped
  variant bank) — not a decode gap, and not findable in DVD001 either.
  Only a runtime (PCSX2) capture could source them. The same holds for
  their P2/P3 clone-list counterparts.

## Definitive unproven remainder (402 records, by reason class)

| reason class | records |
|---|---|
| Identity proven in ANOTHER bank (cross-bank evidence recorded, never annotated — per-character isolation) | 307 |
| No bank in the AFS: no identity in any of the 285 shipped banks (incl. the 5 P1 records ×3 clone lists = 15) | 92 |
| Borderline over gate: own-bank near-candidate exists but exceeds the 0.10 mm gate (char042 rec50 0.1361, char055 rec34 0.1253, char057 rec32 0.1020 mm; next candidates ≥1443 mm; no Phase-6 bank even shares their frame counts — gate does not move) | 3 |
| **Total unproven own-bank** | **402** |

Fighter-level remainder (no records to bridge): char005 / char070 /
char071 / char072 have pmot banks but NO P-list anywhere in the 162
`motion/` entries — nothing held, nothing to bridge. The 41 proxy
fighters have neither a pmot bank nor a P-list (Phase-4 closed search)
and remain PCSX2-capture-gated; Phase 6 did not touch them.

Canon identities stay OWNER-pending.
