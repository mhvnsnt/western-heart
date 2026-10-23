/* ============================================================
   WESTERN HEART — tap recognizer (mobile-first input)
   Owner law (2026-10-23): this is a MOBILE game — SCREEN TAPS, not
   button clicks. NO hand-tooled touch math, NO invented input
   behaviors (standing law): this module implements the researched
   proven stack — the native Pointer Events API
   (pointerdown/pointerup/pointermove with setPointerCapture) plus
   CSS touch-action: manipulation on tappables. That is the 2026
   baseline every guide recommends; no dependency, no gesture
   library (no swipe/pinch vocabulary is needed — the select grids
   scroll natively and taps are disambiguated from scrolls by the
   platform: the browser fires pointercancel when it takes over for
   a scroll, which voids the tap).
   onTap(el, handler):
   - pointerdown captures the pointer (setPointerCapture) and records
     the start point/time; pointermove past 10px voids the tap (it is
     a scroll/drag — the browser may also pre-empt with
     pointercancel); pointerup within 500ms and 10px fires the
     handler EXACTLY once.
   - the compatibility click that follows a touch/mouse pointerup is
     suppressed with a short skip window, so the handler never
     double-fires; a real click with no preceding pointer (keyboard
     Enter/Space, assistive tech) still reaches the handler — desktop
     and AT parity with zero extra code.
   - touch-action: manipulation (in select.css) removes the tap delay
     and keeps native scrolling working alongside the recognizer.
   Elements wired through onTap are marked dataset.tapHandled so the
   document-level tap forwarder in main.js skips them.
   Do NOT use Hammer.js here (maintenance-only/deprecated, per the
   researched stack). If a gesture vocabulary beyond tap is ever
   needed, the researched options are Coherent Labs Gameface Touch
   Gestures or ZingTouch — not custom math.
   ============================================================ */

const TAP_MAX_MOVE_PX = 10;   // platform-conventional tap slop
const TAP_MAX_MS = 500;       // platform-conventional tap duration
const SKIP_MS = 700;          // compatibility-click suppression window

export function onTap(el, handler) {
  if (!el || el.dataset.tapHandled) return;
  el.dataset.tapHandled = '1';
  let pid = null, sx = 0, sy = 0, st = 0, voided = false, skipClick = false;

  el.addEventListener('pointerdown', (e) => {
    if (pid !== null) return; // one active pointer per control
    pid = e.pointerId;
    sx = e.clientX; sy = e.clientY;
    st = performance.now();
    voided = false;
    try { el.setPointerCapture(e.pointerId); } catch (_) { /* older engine */ }
  });

  el.addEventListener('pointermove', (e) => {
    if (e.pointerId !== pid || voided) return;
    if (Math.hypot(e.clientX - sx, e.clientY - sy) > TAP_MAX_MOVE_PX) voided = true;
  });

  const release = (e) => { if (e.pointerId === pid) pid = null; };
  el.addEventListener('pointercancel', release);
  el.addEventListener('lostpointercapture', release);

  el.addEventListener('pointerup', (e) => {
    if (e.pointerId !== pid) return;
    pid = null;
    if (voided || performance.now() - st > TAP_MAX_MS) return; // scroll/hold, not a tap
    skipClick = true;
    setTimeout(() => { skipClick = false; }, SKIP_MS);
    handler(e);
  });

  // Mouse / keyboard / assistive-tech path. Never double-fires with the
  // pointer path: a real tap's compatibility click lands inside skipClick.
  el.addEventListener('click', (e) => {
    if (skipClick) return;
    handler(e);
  });
}

export function isTapHandled(el) {
  return !!(el && el.dataset.tapHandled);
}
