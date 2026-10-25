/* ============================================================
   WESTERN HEART — identity boot (worker 35)
   Classic script, runs before the module graph (main.js). Wires:
   1. colorblind palette -> <html data-cb>
   2. touch-button remap -> .act-btn dataset (joystick untouched)
   3. match-result observer -> currency + Soul Cache awards + titles
   4. player card/name/title onto the versus HUD nameplates
   5. worker-37 T8 menu: runtime card injection (SIDE GAMES / OPTIONS)
   No edits to main.js / game.js / fighter.js / mainmenu.js required.
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

    /* 5. worker-37 T8 menu integration (runtime, no file edits on their lane):
          inject worker-35 cards into their submenus when they open. */
    injectMenuCards();
  });

  /* Worker 37 owns the T8 main menu (game/js/mainmenu.js). We do NOT edit
     their files or the menu markup. Instead, when their SIDE GAMES / OPTIONS
     submenus open, we append our cards (same .mm-card grammar) linking to
     our standalone pages. Graceful no-op if their structure changes. */
  function injectMenuCards() {
    var submenu = document.getElementById('mm-submenu');
    var titleEl = document.getElementById('mm-sub-title');
    var wrap = document.getElementById('mm-cards');
    if (!submenu || !titleEl || !wrap || !window.MutationObserver) return;
    var CARDS = {
      'SIDE GAMES': [
        { wh: 'w35-sidegames', badge: 'NEW', t: '🎮 MYTHOLOGY GAMES', d: 'Festival games, spirit trials, yokai pastimes — Tekken Bowl-style, drawn from world mythologies. Two playable now.', href: 'side-games.html' },
      ],
      'OPTIONS': [
        { wh: 'w35-identity', badge: 'NEW', t: '🜏 IDENTITY HUB', d: 'Titles, player card, Soul Shards, Soul Caches — your shrine record.', href: 'identity.html' },
        { wh: 'w35-access', badge: 'NEW', t: '♿ ACCESS & ASSISTS', d: 'Button remapping, colorblind palettes, difficulty assists.', href: 'settings.html' },
      ],
    };
    var maybeInject = function () {
      if (submenu.hidden) return;
      var key = (titleEl.textContent || '').trim().toUpperCase();
      (CARDS[key] || []).forEach(function (c) {
        if (wrap.querySelector('[data-wh="' + c.wh + '"]')) return;
        var b = document.createElement('button');
        b.className = 'mm-card hot';
        b.setAttribute('data-wh', c.wh);
        b.innerHTML = '<span class="mm-badge">' + c.badge + '</span><h3>' + c.t + '</h3><p>' + c.d + '</p>';
        b.addEventListener('click', function () { window.location.href = c.href; });
        wrap.appendChild(b);
      });
    };
    new MutationObserver(maybeInject).observe(submenu, { attributes: true, attributeFilter: ['hidden'] });
    new MutationObserver(maybeInject).observe(wrap, { childList: true });
  }

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
