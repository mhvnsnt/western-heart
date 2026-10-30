# Tekken 6 PSP — Teardown ROUND 5: un-driven modes + RAM-dump diff

Date: 2026-10-21. Lane: round 5, attempt 2 (attempt-1 lane died to a daemon
restart ~5 min in, landed nothing; redone under the owner's standing
AUTO-RECOVERY approval, 2026-10-14). Same branch as round 4
(`teardown/tekken6-round4-ppsspp-trace`, PR #446); this file is the round-5
successor to ROUND4-STATUS.md and is kept current after every step.

Entry state (from ROUND4-STATUS.md F1–F7, not re-tested): score **20/76**
byte-exact; loader feeds raw container bytes (F1–F3); header/flag split
DEAD (F4); bit-reversed extras DEAD (F5); standalone dictionaries DEAD +
output length dictionary-invariant (F6); PPSSPP trace controlled-negative
across boot/title/menus/arcade-stage-load (F7). The F6 triad any solution
must explain together: (a) failing streams consume input bits exactly to
end-of-stream, (b) decoded length falls SHORT of stated output size,
(c) early matches reference up to ~20 KB BEFORE output start.

## Round-5 plan (round 4's ranked steps, unchanged)

1. Drive the un-driven modes under the same breakpoints: CUSTOMIZATION +
   GALLERY (the COM set idx58–75 is plausibly customization/model data).
   Control discipline: the hot-PC control must fire in-session before any
   zero-hit result is read.
2. RAM-dump diff (breakpoint-independent): full 32 MB RAM dumps during an
   active fight AND a customization/gallery screen; search for failing
   containers' raw bytes + decoded GMO/COM plaintext signatures; diff any
   found plaintext vs `bulk_decrypted.bin` / the Python decoder's output.
3. Overlay check on the same dumps: executable code outside the EBOOT VA
   span (a DATA401-loaded overlay carrying its own decoder).
4. Only if context is captured: implement in `tekken6_gzip.py`, re-run all
   76, QuickBMS .bms, COM/GMO batch, WIRING-INVENTORY.md update.
5. If modes + RAM are also controlled-negative: land that + the
   completeness implication in PR #446 (a proven boundary is a deliverable).
   The chained-decode (continuation-fragment) offline test runs ONLY if
   RAM/static evidence points there (hypothesis discipline).

## Progress

- [x] Signatures built (`round5-evidence/r5_sigbuild.py` →
  `r5_signatures.json`): per-container raw/body 64 B prefixes + decoder
  output head/mid. Tolerant (zero-window history) decode reproduces the
  F6 numbers exactly (idx0 partial = 104,054 of 105,472) and the strict
  adler oracle still scores **20/76** — signature set validated against
  round-4 ground truth before any RAM was read.
- [x] PPSSPP session launched (driver `round5-evidence/r5_driver.py`:
  breakpoints on loader 0x89d27a0 / wrapper 0x8b559c8 / inflate
  0x8b55bf0 / return 0x89d27ec + in-session control). Control PC sampled
  live this session: **0x8ac6c74** — the same hot PC as F7's control.
- [x] Step 1: modes driven under breakpoints — attract/title in
  attempts 5/5b (36 captured loads, F9/F12); CUSTOMIZATION + GALLERY
  superseded by the root-cause proof (see F13 note).
- [x] Step 2: RAM dump (attract fight) + diff — root cause found (F12).
- [x] Step 3: overlay check on the dumps — scan ran; no separate
  decoder (F13 note).
- [x] Verdict + PR #446 update — SOLVED, 76/76 (F13 + VERDICT).

## Attempt 3 (2026-10-21, AUTO-RECOVERY redo of attempt 2)

Attempt 2 died to a daemon restart mid-session. Its local record was
recovered intact in `_t6r4-work/`: `trace_r5.jsonl` (13 records, now
archived as `round5-evidence/trace_r5_attempt2.jsonl`), `ppsspp_r5.log`,
`r5_shots/boot1.png` (2.9 KB — blank), `dumps_r5/` empty. What it
proves: the session launched, PC sampling found the F7 hot PC
**0x8ac6c74** again (29/40 samples), all five breakpoints were added,
and at the single `status` probe (~7 min after READY) loader/wrapper/
inflate/ret hits were all 0 — but **control_hits was also 0**, so by
F7 discipline that zero is NOT readable: attempt 2 never validated
its control in-session before dying, and no mode was driven (only
`status` + `shot boot1` commands were ever issued).

### F8. Attempt-2 driver defect found by inspection (explains control=0)

`r5_driver.py` classified every breakpoint hit by parsing the PC out
of `cpu.getAllRegs` (category scan, index 32). Every round-4 trace
that used that parse recorded `pc: null` on all hits
(`round4-evidence/trace_r5.jsonl`) — the parse never worked in this
PPSSPP build, so `r5_driver.py` could never count a control hit nor
classify a loader hit, and its RAM-dump pause (wait for a recognised
control hit) could never trigger. The working PC source is the
stepping event itself (`ev['pc']`, proven in `ws_control.py`, F7's
control) with `cpu.status` as fallback.

Attempt-3 driver `round5-evidence/r5c_driver.py` fixes this and the
dump path: hit PC from the event / `cpu.status`; RAM dumps pause via
`game.pause` / `game.resume` (both present in the v1.20.4 debugger
API) and read memory while paused; raw `getAllRegs` replies are
logged verbatim on the first loader/wrapper hits so register capture
is evidence, not assumption. Tooling committed BEFORE the session
launches (capture→commit discipline).

- [ ] Step 1 (attempt 3): drive CUSTOMIZATION + GALLERY under the
  fixed breakpoints, control validated in-session first.
- [ ] Step 2 (attempt 3): RAM dumps (fight + customization/gallery).
- [ ] Step 3 (attempt 3): overlay check on the dumps.
- [ ] Verdict + PR #446 update.

## Attempt 5 (2026-10-21, AUTO-RECOVERY redo; attempts 1–4 + first attempt-5 spawn lost to daemon restarts/infra abort)

- attempt 5 session live, control hits=47 (control PC 0x8ac6c74, PPSSPP v1.20.4, game ULES01376 TEKKEN 6 booted; breakpoints armed on loader 0x89d27a0 / wrapper 0x8b559c8 / inflate 0x8b55bf0 / ret 0x89d27ec; loader/wrapper/inflate/ret hits all 0 at the READY+status probe — control validated in-session BEFORE any mode is driven, per F7 discipline).

## Findings

(appended as they land — emulator/RAM ground truth only)

### F9. THE LOADER FIRES IN-GAME — title→attract-VS load runs the full chain repeatedly (attempt 5, 2026-10-21)

Attempt-5 session (trace archived: `round5-evidence/trace_r5c_attempt5.jsonl`,
screenshot `round5-evidence/a5_vs_loading.png`): control 0x8ac6c74
validated in-session (334 hits). Boot → autosave dialog → Bandai Namco
splash → intro movie → title. Pressing CROSS at the title started an
attract/VS load ("VS / NOW LOADING" screen), and the FULL chain fired
repeatedly: **19 complete loader→wrapper→inflate→ret cycles in ~9
minutes** (seq 0–18 `load_done`, seq 19 in flight when a daemon restart
killed PPSSPP + driver). This overturns the round-4 F7 framing: the
chain is not dead code and not save-data-only — it decodes asset
containers during ordinary fight loading. Round 4's controlled
negative covered boot/title/menus/arcade-stage-load only; the attract
load path was never driven with a working driver (attempt-2/round-4
PC parse was broken, F8).

Register ground truth (from the two `regs_raw` records — the reply
shape is `registerNames` + `uintValues`; see F10): seq-0 loader hit:
a0=0x09FFF3F0 (=sp, struct on stack), a1=0x0853C3A0, a2=a3=0x7960
(31,072), ra=0x089D9D84, pc=0x089D27A0. Seq-0 wrapper hit:
a0=0x0853C3A0 (dest = loader's a1), a1=0x7960 (cap), a2=0x097F0014
(src), a3=0, ra=0x089D27EC (the loader's wrapper-return check — the
ret breakpoint address), pc=0x08B559C8. PPSSPP's own symbol for the
inflate breakpoint 0x8B55BF0 is `openseason_data_decode`.

### F10. r5c_driver register-parse defect #2 (fixed in attempt 5b driver)

`regs_probe` looked for category keys `values`/`registers` + `names`;
this PPSSPP build returns `registerNames` + `uintValues`, so every
parsed register came back null (gpr={} on all hits) and the
container/dest dump-on-ret path never triggered. The evidence survived
only in the two verbatim `regs_raw` records. Attempt-5b driver parses
`registerNames`/`uintValues`.

### F11. Control breakpoint throttles emulation ~35× — validate, then drop it

With the hot-PC control armed, the session advanced ~2M PPSSPP ticks/s
(each hit = pause + WS roundtrip + resume); boot→title took ~35 min.
After removing ONLY the control via the side channel
(`bp_side.py remove 0x8ac6c74`; loader/wrapper/inflate/ret stayed
armed), throughput rose to ~70M ticks/s and title→attract-load took
~2 min. Discipline going forward: validate the control in-session,
record its count, remove it for driving, re-arm briefly at each
checkpoint for a fresh beside-the-negative count.

### F12. ROOT CAUSE FOUND — our sector-cipher decryption corrupts every ODD 1024-byte block (attempt 5b, 2026-10-21)

Attempt-5b session (fixed driver): title → cross → attract load fired
**36 complete loader→wrapper→inflate→ret cycles**, every captured
container + dest dumped (`dumps_r5/loadN_container.bin` /
`loadN_dest.bin`); attract fight ran to GAME OVER (Eddy). Per-load
captures prove the game's chain is PLAIN ZLIB semantics: e.g. seq-0
container (GZIP header w=[magic,1,1,106768,40308], body starts
`78 da`) — `zlib.decompress(body)` == game dest byte-exact, all
106,768 B. Captured containers are mostly NESTED containers inside
bundle files (bulk offsets unaligned), not the manifest's top-level 76.

RAM dump `ram_attract.bin` (32 MB, sha256
257e290e2c7de42ababe1e1b4eb301175b7376137cdfa6da76ceb8ce21d6a42f;
taken live — `game.pause` is an unknown event in this build — 510/683
chunks read, rest zero-filled) contains a top-level FAILING container:
**idx74 (entry 733) resident at VA 0x9616950** with the game's own
decrypted bytes. Three facts, each independently decisive:

1. The RAM copy's body decompresses with PLAIN zlib to the FULL
   stated 607,144 B; adler32 = 0x3841ee39 == the stream trailer.
2. RAM vs our `bulk_decrypted.bin` copy of idx74: byte-identical for
   the first 1,024 B, then a strict alternating block map over the
   whole 93,191 B: `=X=X=X=…` — every EVEN 1024-B block identical,
   every ODD 1024-B block different (45,871 divergent bytes total).
3. Therefore the "custom gzip / missing encode context" does not
   exist. The 56 failures are an artifact of OUR decrypt3 sector
   cipher: it decrypts odd 1024-B blocks wrongly. The 20 passes are
   exactly the containers whose streams end before the first odd
   block matters (outputs 336–1,088 B). The F6 triad follows: strict
   decoders (ours + the game's wrapper under Unicorn, fed OUR bytes)
   die on the first bad distance in block 1; tolerant decoding limps
   to a short output; "pre-history references" are distances into
   garbage-decoded block-1 output. Round 4's Unicorn result is
   explained — it was fed corrupted bytes and faithfully failed.

FIX PATH: repair the sector cipher's odd-block handling in the
decrypt3 pipeline (check k1/k2 alternation per 1024-B half-sector —
manifest records k1/k2 per file), re-decrypt DATA401.BIN, re-run all
76 (goal 76/76 adler-exact), then QuickBMS .bms (G5) + COM/GMO batch.

### F13. FIX VERIFIED — per-1024 cipher calls give 76/76 adler-exact (attempt 5b, 2026-10-21)

Keystream experiment against the idx74 RAM truth: the true keystream
for a sector's second 1024-B half equals a FRESH `cipher_block` call
with `length=1024, t0 = sector_base + 1024` (candidate C; the driver's
own continuation/spill/second-sector candidates all failed). The game
decrypts in 1024-B units; `full_bulk_decrypt.py`'s per-2048 call was
the whole bug. Verified end-to-end three ways:

1. idx74 re-decrypted per-1024 == the game's RAM copy byte-for-byte
   (full 93,200 B) and zlib-decodes to adler-exact 607,144 B.
2. `tools/decode_all76.py` (new, self-contained: ISO → per-1024
   decrypt → header parse → plain zlib → length+adler oracle):
   **76/76 adler-exact**, no regressions (the 20 former passes still
   pass). Full inventory (sizes, sha256, classification) in
   `round5-evidence/r5_inventory_summary.json`; decoded outputs stay
   in the lane workdir (`decoded76/`), out of the repo.
3. The UNMODIFIED round-2 `tekken6_gzip.py` decoder also scores
   byte-exact on correctly decrypted idx0/idx40/idx74 — its
   "length-composition defect" was an artifact of corrupted input,
   as were the Unicorn wrapper failures (fed our corrupted bytes)
   and the entire custom-gzip premise.

Deliverables landed with F13: `tools/bulk_decrypt.py` (corrected
streaming bulk decryptor), `tools/decode_all76.py` (batch + oracle),
`tools/tekken6.bms` (QuickBMS container extractor for the decrypted
bulk — authored, not executed: no QuickBMS binary on this VM),
`tekken6_gzip.py` resolution banner, `WIRING-INVENTORY.md` updated.

COM/GMO batch (brief step 7): all 76 decoded + verified. The 18 COM
files (idx58–75) each hold ONE COM container: plaintext head
`00 00 00 01 "COM\0" 00 00 00 00 <count u32>` with count 7–16
(176 total across the set) — the per-character mesh inventory (G4)
starts from these decoded files; a literal `GMO\0` magic scan over
all 76 plaintexts finds 0 (inner assets use a different framing —
counted honestly, not rounded to the old "40 meshes" estimate).

Overlay check (brief step 6): the ram_search overlay scan of
`ram_attract.bin` ran (results in the lane's `r5_ram_attract.json`);
no separate decoder was needed or found — the decode question is
closed by F12/F13, and no finding depends on the overlay scan. The
scan's raw output is retained in the workdir for the record.

CUSTOMIZATION/GALLERY (brief steps 2/5): NOT driven — superseded.
The mode hunt existed to find the encode context; the context turned
out to be our own decryption bug, proven by the attract-mode loads +
RAM diff + offline 76/76. Driving the remaining modes would add no
evidence to a closed question. Stated plainly per the
no-false-completion rule: per-mode coverage is attract/title only.

### Attempt-5 session timeline / open steps

- [x] Session live + first commit pushed BEFORE driving (30a8095).
- [x] Title reached; attract-VS load fired the chain 19× (attempt 5)
  and 36× (attempt 5b, all captured with registers + container/dest
  dumps).
- [x] RAM dump during the attract fight load (attempt 5b:
  `ram_attract.bin`, 32 MB, sha256 in F12) + signature search +
  idx74 RAM-vs-bulk diff → root cause (F12).
- [x] Per-container capture with the fixed regs parser (5b): game
  dest == plain zlib byte-exact (F12).
- [x] Verdict: context FOUND (it was our cipher driver's call
  granularity) — implemented + 76/76 + .bms + COM batch + inventory
  (F13).
- [ ] CUSTOMIZATION + GALLERY driven — not done; superseded by the
  root-cause proof (see F13 note). No longer load-bearing.
- [ ] Follow-ups for later lanes (not blockers to this verdict):
  regenerate the full bulk with `tools/bulk_decrypt.py` (the round-3
  `bulk_decrypted.bin` is corrupt in odd blocks — anything derived
  from it in rounds 2–4 needs re-derivation); re-scan the NDPP
  archive's 2,546 embedded containers on the corrected bulk; COM
  per-character inventory (G4) + GMO→GLB batch (G3) from the decoded
  COM files; execute `tekken6.bms` once a QuickBMS binary is present.

## VERDICT (round 5): SOLVED — 76/76

The missing "encode context" never existed. Tekken 6 PSP DATA401
containers are standard zlib under a 20-byte GZIP header, protected
by a sector cipher that must be called once per 1024-byte block.
Score: **76/76 adler-exact** (from 20/76), zero regressions, proven
against the game's own decoder in a live emulator and against RAM
ground truth. Gates: G1 (decode) MET, G2 (emulator proof) MET,
G5 (QuickBMS .bms) authored, G3/G4 unblocked (decoded COM files +
inventory landed; conversion itself is the next lane's work).
