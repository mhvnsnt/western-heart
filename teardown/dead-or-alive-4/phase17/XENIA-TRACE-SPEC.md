# DOA4 Phase 17 — Xenia trace spec (dynamic closure for G4 items 1 + 2)

Purpose: ONE capture session that closes both remaining G4
items dynamically, the way the other games' captures are
spec'd. Static state going in: .mot record grammar PROVEN
(44 sub-blocks + 44-entry descriptor of absolute offsets);
the per-item length rule is stateful and every word-aligned
functional class tested is falsified (see
`phase17/MOT-STATEFUL.md`); the 0x9C arena, its bases and its
pointer globals are pinned (see `phase17/W21-TRACE-2.md`).
Binary: `default.xex` retail sha256
`56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f`,
true VA base 0x82000000. Fighter: ZACK (per-character
isolation; zack's data touches zack's skeleton only).

## Session setup
- Xenia (canary or master with the debugger/log build),
  DOA4 retail ISO (whole-ISO sha256
  `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa`,
  release `doa4-iso-v1`).
- Boot to the main menu, then start a VERSUS match: P1 = Zack,
  P2 = any (the capture is about P1's motion load + playback).
- Enable a full instruction trace log OR set the breakpoints
  below before confirming the character select.

## Capture 1 — the .mot record expansion (ITEM 1)
Target record: zack.mot's DEFAULT record (descriptor at file
offset 22,936 in `zack.mot`, release `doa4-mot-20261022`) is
loaded for every Zack appearance; any real clip record is a
bonus. What to dump, in order:
1. **W1 (watchpoint, write) on the .mot registry record for
   zack.mot**: the registry is 196 records × 0x6C at VA
   0x82C69A70; zack.mot's record is the one whose +0x18 name
   pointer reads `D:\bin\zack.mot` (find it in the dump of the
   table at match load; the table is static in the PE's .data —
   file offset 0xC4BC70 in `default_pe.bin`). Log every code
   address that READS that record's fields during the match
   load; the reader that follows the name to the AFS open is
   the proven loader (0x82391AFC area) — the reader AFTER the
   file is in memory is the expansion consumer. Record its VA.
2. **The loaded zack.mot buffer**: when the open helper
   0x8238ED10 is called with the zack.mot name (registry path
   above; also entry id for mot.afs files), dump the
   destination buffer pointer it returns/produces and the full
   buffer (2,097,528 B). Verify byte-identity against the
   release copy of `zack.mot` (sha256 in
   `phase15/mot-entries-manifest.json`).
3. **W2 (watchpoint, write) on the FIRST runtime byte the
   consumer writes while expanding the default record**: set
   after step 2 by watching the region the consumer's writes
   land in — practically: hardware watchpoints on the two
   record-pointer globals 0x83099E04 / 0x83099BA8 (writes) from
   character-select confirm until the first frame of the
   fight; log the writing VA + the pointer value written.
   That VA is the playback/repoint step named in
   W21-TRACE-2 §2.
4. **The expanded runtime buffer for one zack motion**: when
   Zack performs his first command move (any P1 attack),
   dump (a) 64 KB starting at the pointer value logged in
   step 3, (b) the 0x9C arena window 0x83020188..0x83021188,
   (c) the instruction trace (or at minimum the call stack +
   register state) at the W2 hit. From (a)+(c): the
   consumer's per-item loop is read directly off the executed
   path — item boundaries in the file record (record-layer
   offsets are known exactly) vs values in the expanded
   buffer give the length rule empirically, per item, with
   the loop's state variables visible in registers.

## Capture 2 — the w21 file-side writer (ITEM 2)
Same session, earlier moment (character select / match load):
5. **W3 (watchpoint, write) on the 0x9C arena token slots**:
   watch 0x83020188 (record 0, +0x00) and 0x8302018C.. — set
   the watch BEFORE confirming Zack. The first writer whose
   stored u16s are NOT the FUN_824000B0 clear pattern and NOT
   the initializer's per-index fields is the expansion writer
   (or its immediate caller). Log: writer VA, call stack, and
   r-source registers; dump 4 KB around the source pointer
   register's value (expected: inside the loaded zack.bin
   buffer — verify the w21 table bytes `zack.bin` offsets from
   release `doa4-anime-definition-20261022` appear at
   source − 0x54 or source − w21_offset).
6. Dump the full loaded `zack.bin` buffer (137 KB) and its
   base address, so file offsets can be tied to runtime
   addresses for the offline expander test (validator bands
   [0x15,0x1C]/[0x1D,0x24]/[0x25,0x2C] + 0x34-record ids).

## Deliverables from the capture (one session)
- consumer VA + executed per-item loop (item 1 CLOSED by
  direct observation; the rule is then re-implemented offline
  and must tile >=99% of zack + m_zack sub-blocks — the
  standing proof gate — before any clip is assembled).
- writer VA + source buffer base (item 2 CLOSED when the
  offline expander reproduces the dumped 0x9C records for
  zack under the W21-TRACE-2 §5 validation).
- All dumps as files + a session log with VA register state
  at each watchpoint hit.
