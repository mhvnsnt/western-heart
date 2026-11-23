# KoC2 phone black screen (0 fps) — diagnosis + fix

**Date:** 2026-11-21 ~09:22–11:10 EST · **Lane:** fd940514 (KoC2 diagnosis)
**Player:** `arcade/play-ps2.html` on branch `muse/wrestling-arcade` (Bannon)
**Deployed:** `/var/www/arcade/play-ps2.html` on the Oracle VM (md5 `efd5f160…`)
**Commit:** `8a5416239dacb5350b8c10d7702c0d5f27bcac3a` (verified on GitHub — remote
file md5 matches the deployed file). Parent head was `e8ba2804` (unchanged
during the work; base file md5 `f48bfb41` confirmed identical before pushing).

## What Mars saw (09:19 EST, Motorola Edge 2025, Chrome)

Same tunnel link that boots to the title at ~34 fps in the VM Puppeteer
harness. On his phone: page loads, pad renders, status says "Running — tap the
pad to play", but the canvas stays black and the badge shows **0 fps · 0%**.
Screenshot: `~/workspace/user/files/1000185813_17_e4b7.png`.

## Root cause — honest statement

**The phone failure did NOT reproduce in mobile emulation, so the exact
phone-side cause is NOT proven.** What IS proven is that the old player could
not tell anyone where it stopped:

1. `state = 'running'` and "Running — tap the pad to play" were set the
   instant `bootDiscImage()` returned — they never proved a single frame was
   drawn. A stuck emulator and a healthy one looked identical on screen.
2. **Disc fetches had no timeout and no retry.** A plain `fetch()` never times
   out: on a flaky/slow phone connection, one stalled 2 MB window fetch hangs
   the emulator forever — black screen, 0 fps, no error, no feedback. This is
   the failure mode that matches Mars's symptom exactly, and the only one
   that is network-dependent. (The manifest fetch had already succeeded, so
   state reached "running"; the first big window fetch is the first thing
   that can stall.)
3. **No WebGL handling at all.** No `webglcontextlost` listener anywhere
   (Play.js has zero), no record of whether the emulator's GL init even got a
   context. On a phone GPU, context creation failure or context loss = silent
   permanent black screen. Note: Play!'s GL calls already generate errors
   under SwiftShader ("WebGL: too many errors…" warning in every harness run),
   so a stricter mobile (Adreno) driver failing where SwiftShader soldiers on
   is a live possibility we cannot test from here.
4. The emulator's own errors (`printErr`) went only to the console, and the
   debug log was hidden unless `?debug=1` — Mars's screenshot could not show
   any of it.

**Ruled out by the reproduction runs** (mobile emulation + real tap boot,
Motorola Edge 2025 viewport/UA/touch, default autoplay policy, live tunnel
URL): mobile viewport/UA/touch, tap-initiated boot, autoplay policy, the SAB
gate, WASM load/compile, manifest + piece fetches (from a fast network),
pthread worker spawn, GL context creation under SwiftShader, rAF liveness.
Both arms (mobile + desktop control) booted in ~2 s and ran 20–38 fps.

Also worth knowing: **a 0 fps badge alone does not prove failure** — healthy
runs show `0 fps · 0%` transiently (first reading, and whenever a 1 s window
happens to catch 0 frames). The black screen + his report of "nothing
happening" is the real symptom. And the game is legitimately black for the
first ~10–25 s while it loads (prompt appears ~t=25–30 s; title/FMV ~90 s
after the prompt is dismissed), so a screenshot taken too early looks the
same as a stuck boot — the new stage indicator fixes that ambiguity.

## What changed (play-ps2.html, 25,751 → 35,619 bytes)

1. **On-screen diagnostics box, always visible** (grey box under the status
   line, refreshed twice a second): boot stage + seconds in stage, total
   frames, WASM state, SAB/isolated, GL context state, rAF tick count, disc
   reads/MB, retry count, pending-read age, last error. A screenshot of this
   box is now the debugger.
2. **GL watch:** a `getContext` wrapper installed before boot records exactly
   what the emulator's GL init requested and whether it got a context
   (`webgl2 ✓` / `webgl2 ✗ FAILED` / `not-requested`) — without creating a
   context itself.
3. **Disc fetch timeout + retry:** every piece/manifest fetch gets a 30 s
   timeout (AbortController) and 3 attempts with 1 s backoff (manifest 15 s).
   Retries are counted on screen. A read that fails after retries still
   zero-fills (emulator never hangs forever) but the error is now visible.
4. **`webglcontextlost` / `webglcontextrestored` handlers:** on loss, show
   the error + a Retry (reload) button instead of a silent black screen.
5. **Watchdogs:** no-frames warning (running 20 s with 0 frames — message
   distinguishes "still waiting on the disc" from "drew nothing at all") and
   slow-boot warning (90 s without reaching running), both with a Retry
   button. A black screen is never the only feedback again.
6. **Boot progress:** spinner + live stage text on the button and status line
   (loading-emulator → reading-disc-list → starting-vm → booting-disc →
   running); honest note that first boot can take up to a minute on a phone.
7. **Error surfacing:** emulator stderr (`printErr`), page errors, and
   unhandled rejections now land in the diagnostics, not just the console.
8. **Inline favicon** (`data:,`) to silence the 404 that polluted the console.
9. `window.__ps2test` contract preserved (state/fps/errors/discReads/
   discBytes) — Phase 5 / tunnel harnesses keep working; new fields added
   (stage, framesTotal, wasmState, glState, pendingReadSince/Desc, lastError,
   rafTicks, glLost, retries).

## Verification (mobile emulation, live tunnel URL)

Harness: `~/workspace/koc2-disk-decision/mobile-repro.js` (repro, 2 arms ×
120 s) and `verify-fixed.js` (75 s + input test) and `verify-title.js`
(180 s title check). Puppeteer-core 23 + cached Chrome 157 on the VM
(`/dev/shm/mobile-repro`; `/home/ubuntu/ps2test` was cleared by the VM sweep
lane, so puppeteer-core was npm-installed fresh).

- **Repro (old player):** mobile arm ran 20–37 fps, memcard prompt rendered
  at t=30 s — failure did NOT reproduce. Desktop control same.
- **Fixed player, 75 s run — all 7 checks pass:** diag visible pre-boot;
  GL `webgl2 ✓`; 1,526 frames by t=80 s; fps positive (11–38); no warn
  banner on a healthy boot; input (Up + Circle) dismissed the memcard prompt;
  last error empty; zero page errors / failed requests.
- **Fixed player, 180 s title run:** prompt dismissed at t=30 s; attract FMV
  / title sequence rendering by t=120 s (Colosseum) and t=180 s (wrestler +
  flames); 3,882 frames; 45 disc reads / 90 MB; GL `webgl2 ✓` throughout;
  no errors.
- Screenshots (eyes-on checked): `mobile-repro-evidence/` —
  `A-mobile-tap-t30.png` (repro, prompt), `fixed-mobile-t10/t30/t45/t75.png`
  (diag box rendering, prompt at t=30), `fixed-title-t120/t180.png` (FMV).

## What Mars should see / tap on the retest

Same link (tunnel still live, same hostname):
`https://powerseller-success-requesting-evanescence.trycloudflare.com/play-ps2.html?game=koc2`

1. Tap **▶ Play**. The button now shows the stage as it goes
   (Loading emulator… → Reading disc… → Starting PS2… → Booting disc…).
2. The grey diagnostics box under the screen updates live. Give it **up to a
   minute** — the first picture (Japanese memcard prompt) takes ~25–30 s
   even on a fast connection, and the screen is legitimately black before
   that. If the box says `Frames: 0` and `Pending read: window @… (30s+)`,
   the disc stream is stalled — wait for the retry, or tap Retry.
3. At the memcard prompt: **D-pad Up, then ○ (Circle)** to dismiss it
   (or tap ✕/○ on the pad) — then the title/FMV loads (~60–90 s more).
4. **If it still shows a black screen: screenshot the page including the grey
   box.** The box now says exactly where it stopped (stage, GL state,
   pending read age, last error) — that screenshot is what we need to fix
   the next layer. If a red warning appears, tap its **Retry** button.

## NOT claimed

Phone success is **not** claimed — only Mars's phone proves it. The fix
removes the silent-stall failure modes and makes the next test diagnostic;
if his phone still shows black, the diagnostics box will say whether it is
the disc stream (pending read), the graphics (GL state), or something else.

## Notes for later lanes

- `/home/ubuntu/ps2test` is GONE (VM sweep lane cleared it ~2026-11-21
  14:30 UTC). Puppeteer now lives as puppeteer-core in
  `/dev/shm/mobile-repro/node_modules` with Chrome 157 at
  `~/.cache/puppeteer/chrome/linux-157.0.8103.78/chrome-linux64/chrome`.
- VM load was 14+ during the afternoon (many lanes); Chrome launch needed
  `timeout: 180000` in the harness. Load had dropped to ~2 by 15:49 UTC.
- The commit went through the GitHub connector (`push-files`), NOT git CLI:
  a fresh sparse clone hit an execution-risk flag on the clone result, so
  the clone was removed and the push was done via the connector with the
  base verified first (branch file md5 `f48bfb41` = the edit base). Sync
  record: `~/workspace/ps2-player-push.muse-github-snapshot-sync.json`.
- Snapshot-push source dir: `~/workspace/ps2-player-push/` (holds
  `arcade/play-ps2.html`); manifest
  `~/workspace/ps2-player-push-paths.txt`.
