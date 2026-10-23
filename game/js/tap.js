/* ============================================================
   WESTERN HEART — tap recognizer (mobile-first input)
   Owner law (2026-10-23): this is a MOBILE game — SCREEN TAPS, not
   button clicks. Every interactive control uses touchstart/touchend
   tap recognition, never bare click, never hover.
   onTap(el, handler):
   - touchstart records the touch point; touchend fires the handler
     ONLY when the finger barely moved (< 14px) and lifted quickly
     (< 600ms) — a scroll/swipe/pinch inside a scrolling strip never
     misfires as a tap (the select grids scroll; this is the critical
     disambiguation).
   - the emulated click is suppressed via preventDefault, so the tap
     fires EXACTLY once on Android/Chrome and iOS/Safari.
   - the click listener stays as the mouse / keyboard / assistive-tech
     fallback (desktop parity) — it never double-fires with touch
     because the emulated click is killed above.
   Elements wired through onTap are marked dataset.tapHandled so the
   document-level tap forwarder in main.js skips them.
   ============================================================ */

const TAP_MAX_MOVE_PX = 14;
const TAP_MAX_MS = 600;

export function onTap(el, handler) {
  if (!el || el.dataset.tapHandled) return;
  el.dataset.tapHandled = '1';
  let sx = 0, sy = 0, st = 0, live = false;
  el.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) { live = false; return; }
    const t = e.touches[0];
    sx = t.clientX; sy = t.clientY; st = Date.now(); live = true;
  }, { passive: true });
  el.addEventListener('touchend', (e) => {
    if (!live) return;
    live = false;
    const t = e.changedTouches[0];
    if (!t) return;
    const moved = Math.hypot(t.clientX - sx, t.clientY - sy);
    if (moved > TAP_MAX_MOVE_PX || Date.now() - st > TAP_MAX_MS) return; // a scroll, not a tap
    e.preventDefault(); // kill the emulated click — exactly one fire
    handler(e);
  }, { passive: false });
  // Mouse / keyboard / assistive-tech fallback. Never double-fires with
  // the touch path: the emulated click after a real tap is suppressed.
  el.addEventListener('click', (e) => { handler(e); });
}

export function isTapHandled(el) {
  return !!(el && el.dataset.tapHandled);
}
