/* ============================================================
   WESTERN HEART — identity boot (worker 35)
   Classic script, runs before the module graph (main.js). Wires:
   1. colorblind palette -> <html data-cb>
   2. touch-button remap -> .act-btn dataset (joystick untouched)
   3. match-result observer -> currency + Soul Cache awards + titles
   4. player card/name/title onto the versus HUD nameplates
   No edits to main.js / game.js / fighter.js required.
   ============================================================ */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    if (!window.WHIdentity) return;
    var I = window.WHIdentity;

    /* 1. colorblind palette */
    if (window.WHColorblind) window.WHColorblind.apply();
    else document.documentElement.setAttribute('data-cb', I.getColorblind());

    /* 2. touch-button remap (face buttons + specials; joystick NEVER touched) */
    try {
      var touch = I.getRemap().touch || {};
      var labels = I.TOUCH_LABELS;
      document.querySelectorAll('.act-btn').forEach(function (btn) {
        var slot = btn.getAttribute('data-touch-slot') || btn.dataset.btn;
        btn.setAttribute('data-touch-slot', slot);
        var mapped = touch[slot] || slot;
        btn.dataset.btn = mapped;
        btn.textContent = labels[mapped] || mapped.toUpperCase();
      });
    } catch (e) { /* HUD-less page */ }

    /* 3. match-result observer: award shards + caches, check titles */
    var resultScreen = document.getElementById('screen-result');
    if (resultScreen && window.MutationObserver) {
      var awarded = false;
      new MutationObserver(function () {
        var active = resultScreen.classList.contains('active');
        if (active && !awarded) {
          awarded = true;
          awardForResult();
        } else if (!active) { awarded = false; }
      }).observe(resultScreen, { attributes: true, attributeFilter: ['class'] });
    }

    /* 4. paint the player's card onto P1's HUD nameplate when a fight starts */
    var hud = document.getElementById('hud');
    if (hud && window.MutationObserver) {
      new MutationObserver(function () {
        if (!hud.classList.contains('active')) return;
        var p = I.get(), t = I.titleById(p.title);
        var nameEl = document.getElementById('p1-name');
        if (nameEl && !nameEl.dataset.whCard) {
          nameEl.dataset.whCard = '1';
          nameEl.innerHTML = '';
          var nm = document.createElement('span'); nm.textContent = p.name; nameEl.appendChild(nm);
          var tt = document.createElement('small'); tt.className = 'wh-hud-title'; tt.textContent = ' · ' + t.name; nameEl.appendChild(tt);
        }
      }).observe(hud, { attributes: true, attributeFilter: ['class'] });
    }
  });

  function awardForResult() {
    var I = window.WHIdentity;
    var title = (document.getElementById('result-title') || {}).textContent || '';
    var sub = (document.getElementById('result-sub') || {}).textContent || '';
    var won = title.indexOf('WIN') !== -1;
    var perfect = /perfect/i.test(sub);
    var great = /great/i.test(sub);
    var surgeWin = /surge/i.test(sub);
    var res = I.awardMatch({ won: won, perfect: perfect, great: great, surgeWin: surgeWin });
    toast('+' + res.shards + ' ' + I.CURRENCY_NAME +
      (res.drops.length ? ' · +' + res.drops.length + ' Soul Cache' + (res.drops.length > 1 ? 's' : '') : ''));
  }

  function toast(msg) {
    var t = document.createElement('div');
    t.className = 'wh-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
    setTimeout(function () { t.classList.remove('show'); setTimeout(function () { t.remove(); }, 400); }, 2600);
  }
})();
