/* ============================================================
   WESTERN HEART — Cutscene player
   Fullscreen HTML5 video overlay for Eastern Mind source footage
   (teardown/eastern-mind/.../video/*.mp4, real Osamu Sato animation).
   Skippable by click/tap or Escape. Returns a promise that resolves
   when the video ends or is skipped. Engine code calls playCutscene()
   — never embeds <video> markup itself.
   ============================================================ */

let _overlay = null;
let _video = null;
let _done = null;

function _cleanup() {
  if (_video) {
    try { _video.pause(); } catch (e) {}
    _video.removeAttribute('src');
    _video.load();
    _video = null;
  }
  if (_overlay) {
    _overlay.remove();
    _overlay = null;
  }
  document.removeEventListener('keydown', _onKey, true);
}

function _finish() {
  const cb = _done;
  _cleanup();
  _done = null;
  if (cb) cb();
}

function _onKey(e) {
  if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
    e.stopPropagation();
    _finish();
  }
}

/* src: path to the mp4, relative to game/index.html (e.g.
   '../teardown/eastern-mind/prologue-ending/video/LOGO.mp4').
   opts: { skippable=true, label } — label shows as a kicker line. */
export function playCutscene(src, opts = {}) {
  const { skippable = true, label = '' } = opts;
  stopCutscene();
  return new Promise((resolve) => {
    _done = resolve;
    _overlay = document.createElement('div');
    _overlay.id = 'wh-cutscene';
    _overlay.setAttribute('style',
      'position:fixed;inset:0;background:#000;z-index:9999;' +
      'display:flex;align-items:center;justify-content:center;flex-direction:column;');
    _video = document.createElement('video');
    _video.setAttribute('style', 'max-width:100vw;max-height:100vh;object-fit:contain;');
    _video.setAttribute('playsinline', '');
    _video.src = src;
    const finish = () => _finish();
    _video.addEventListener('ended', finish);
    _video.addEventListener('error', finish);
    _overlay.appendChild(_video);
    if (label) {
      const k = document.createElement('div');
      k.textContent = label;
      k.setAttribute('style',
        'position:absolute;top:18px;left:0;right:0;text-align:center;' +
        'color:#FFD76A;letter-spacing:0.35em;font-size:13px;opacity:0.85;' +
        'font-family:serif;pointer-events:none;');
      _overlay.appendChild(k);
    }
    if (skippable) {
      const hint = document.createElement('div');
      hint.textContent = 'TAP / ESC — SKIP';
      hint.setAttribute('style',
        'position:absolute;bottom:22px;left:0;right:0;text-align:center;' +
        'color:#8a8a9a;letter-spacing:0.3em;font-size:11px;opacity:0.7;pointer-events:none;');
      _overlay.appendChild(hint);
      _overlay.addEventListener('click', finish);
      document.addEventListener('keydown', _onKey, true);
    }
    document.body.appendChild(_overlay);
    const p = _video.play();
    if (p && p.catch) p.catch(finish);
  });
}

export function stopCutscene() {
  if (_overlay) _finish();
}

/* Eastern Mind cutscene registry — the game's own footage, placed. */
export const EM_CUTSCENES = {
  // Story-mode title sting: the real Eastern Mind logo animation.
  'story.intro': '../teardown/eastern-mind/prologue-ending/video/LOGO.mp4',
  // Reincarnation: death → transmigration flash (3.8s).
  'reincarn.flash': '../teardown/eastern-mind/prologue-ending/video/ANIM01.mp4',
  // Palace of Dreaming stage entry: one of the land's own room films.
  'stage.dreaming.intro': '../teardown/eastern-mind/stage-3-palace-of-dreaming/video/W_RMEYE.mp4',
};
