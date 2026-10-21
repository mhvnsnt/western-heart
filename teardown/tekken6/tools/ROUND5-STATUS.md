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
- [ ] Step 1: drive CUSTOMIZATION + GALLERY under breakpoints.
- [ ] Step 2: RAM dumps (fight + customization/gallery) + diff.
- [ ] Step 3: overlay check on the dumps.
- [ ] Verdict + PR #446 update.

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
