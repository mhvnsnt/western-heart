/* ============================================================
   WESTERN HEART — Input Manager
   Unifies touch (virtual joystick + action buttons) and keyboard
   into one command state consumed by the player Fighter.

   Exposed state:
     axisX  : -1..1 horizontal move
     up     : bool (jump intent — set after 200ms hold, Tekken tap/hold rule)
     down   : bool (crouch intent — set after 200ms hold)
     held   : { block }                  // continuous
     pressed: queue of one-shot actions  // 1/2/3/4 (Tekken limbs),
                                         // 1+3/2+4/1+2/3+4/1+4/2+3 chords,
                                         // ss-up/ss-down (sidestep),
                                         // surge/dodge/transform (WH),
                                         // vskill (V-System: KeyV / V button)

   TEKKEN INPUTS: 1/2/3/4 = left punch / right punch / left kick / right kick
   (LP/RP/LK/RK touch buttons). Any two limbs within 140ms = chord
   (1+3 / 2+4 throws, 1+2 / 3+4 specials, 1+4 / 2+3 command inputs).
   Motions (qcf, f,F) tracked via direction history in the fighter's
   TekkenBuffer (see movesets.js).
   SIDESTEP (Tekken 7 semantics): TAP u/d (<200ms) = sidestep into the
   background/foreground; HOLD u/d (>=200ms) = jump/crouch. The game waits
   out the tap window before committing to jump/crouch — exactly like Tekken.
   COMMAND GRAB (legacy): press P+K together (touch) or J+K together / U (keyboard).
   ============================================================ */

import { stickToDir } from './combat-core.js';
export class InputManager {
  constructor() {
    this.axisX = 0;
    this.up = false;
    this.down = false;
    this.held = { block: false };
    this._lastT = { '1': 0, '2': 0, '3': 0, '4': 0 };
    this._queue = [];
    this._keys = {};
    this._joyActive = false;
    this._joyId = null;
    this._joyCenter = { x: 0, y: 0 };
    this._lastPunchT = 0;
    this._lastKickT = 0;
    this.enabled = false;
  }

  init() {
    this._bindKeyboard();
    this._bindJoystick();
    this._bindButtons();
  }

  enable(on) { this.enabled = on; if (!on) this.reset(); }

  reset() {
    this.axisX = 0; this.up = false; this.down = false; this.held.block = false; this._queue.length = 0;
    this._keys = {};
    this._lastPunchT = 0; this._lastKickT = 0;
    this._lastT = { '1': 0, '2': 0, '3': 0, '4': 0 };
    clearTimeout(this._udTimer); this._udDir = null; this._udHeld = false;
    this._resetJoyKnob();
  }

  consume() { const q = this._queue.slice(); this._queue.length = 0; return q; }

  _push(action) {
    if (!this.enabled) return;
    // Worker 35: difficulty assists (input layer). translate() handles
    // throw-break assist; after() handles auto-combo / one-button special.
    if (window.WHAssists) action = window.WHAssists.translate(action, this) || action;
    this._queue.push(action);
    if (window.WHAssists) window.WHAssists.after(action, this);
  }

  /* Worker 35: button remapping. Translates the physical key through the
     player's remap table to the canonical action code the switch below
     dispatches on. Joystick is never remapped (owner-approved). */
  _remapCode(code) {
    if (!window.WHIdentity) return code;
    const I = window.WHIdentity;
    const keys = (I.getRemap && I.getRemap().keys) || {};
    const def = I.REMAP_DEFAULT_KEYS || {};
    // cur(): '' means explicitly unbound (conflict-cleared) — do NOT fall back.
    const cur = (a) => (a in keys ? keys[a] : def[a]);
    for (const action of Object.keys(def)) {
      if (cur(action) === code) return def[action];
    }
    // A default key whose action moved elsewhere is dead (true rebind, not alias).
    for (const action of Object.keys(def)) {
      if (def[action] === code && cur(action) !== code) return '__unbound__';
    }
    return code;
  }

  /* P+K chord => command grab. Tracks the most recent strike press;
     if the other one lands within 140ms, the pair becomes a grab. */
  _strike(kind) {
    const now = performance.now();
    if (kind === 'punch') {
      if (now - this._lastKickT < 140) { this._lastKickT = 0; this._push('grab'); return; }
      this._lastPunchT = now;
    } else {
      if (now - this._lastPunchT < 140) { this._lastPunchT = 0; this._push('grab'); return; }
      this._lastKickT = now;
    }
    this._push(kind);
  }

  /* Tekken chords: any two limbs within 140ms.
     1+3 / 2+4 = throws; 1+2 / 3+4 = specials; 1+4 / 2+3 = command inputs.
     Throw pairs keep priority (most deliberate), then specials, then commands. */
  /* Vertical intent right now, including a u/d still inside its 200ms tap window: a limb
     pressed with the stick at d/f is d/f+1 in Tekken, not a sidestep followed by 1. */
  vertNow() {
    if (this.up) return 'up';
    if (this.down) return 'down';
    return this._udDir || null;
  }

  /* 8-way octant stick (tekken-command-interpreter lane): the octant direction
     feeds the command buffer (stickDir) so f+1 / d/f+2 / qcf resolve cleanly.
     MOVEMENT (axisX, up/down) keeps the original independent thresholds:
     x 0.25 deadzone, y 0.55 tap-vs-hold zones. Driving movement from the
     octant classified any push >22.5° below horizontal as down, so a natural
     thumb drift while walking kept crouching the fighter (owner playtest
     bug 2026-10-23: stick "keeps going down"). x right-positive, yUp
     up-positive (screen-agnostic). */
  _stick8(x, yUp) {
    const d = stickToDir(x, yUp, 1, 0.38);
    this.stickDir = d;
    // Movement: analog x with 0.25 deadzone (pre-8-way behavior).
    this.axisX = Math.abs(x) > 0.25 ? Math.max(-1, Math.min(1, x)) : 0;
    // Movement: vertical via Tekken tap-vs-hold zones (0.55 threshold),
    // not the octant — a mostly-horizontal push must not crouch.
    this._udStick(-yUp);
  }

  _tekken(btn) {
    const now = performance.now();
    if (this._udDir && !this._udHeld) this._udUsed = true; // the tap fed this attack's direction
    const pairs = btn === '1' ? [['3', '1+3'], ['2', '1+2'], ['4', '1+4']]
                : btn === '2' ? [['4', '2+4'], ['1', '1+2'], ['3', '2+3']]
                : btn === '3' ? [['1', '1+3'], ['4', '3+4'], ['2', '2+3']]
                : [['2', '2+4'], ['3', '3+4'], ['1', '1+4']];
    for (const [pair, name] of pairs) {
      if (now - this._lastT[pair] < 140) {
        this._lastT[pair] = 0; this._lastT[btn] = 0;
        this._push(name);
        return;
      }
    }
    this._lastT[btn] = now;
    this._push(btn);
  }

  /* ---- Sidestep tap-vs-hold (Tekken 7 semantics) ----
     Joystick/keyboard u/d press starts a 200ms timer. Release before it
     fires = sidestep ('ss-up'/'ss-down'); holding past it = jump/crouch
     (up/down set true, cleared on release). */
  _udPress(dir) {
    // dir: 'up' | 'down'
    if (this._udDir) return; // already tracking
    this._udDir = dir;
    this._udT = performance.now();
    this._udTimer = setTimeout(() => {
      if (!this._udDir) return;
      if (this._udDir === 'up') this.up = true;
      else this.down = true;
      this._udHeld = true;
    }, 200);
  }
  /* Touch stick vertical zone (owner t116u fix). Legacy kept 'down' latched when the stick
     re-centred after a HELD crouch (only taps were released), so every neutral 3/4 came out
     as d+3/d+4/FC; and d->u without lifting was ignored. V2: leaving the zone always releases,
     switching u<->d releases then presses. localStorage wh_input_resolver='legacy' = old path. */
  _udStick(ny) {
    let legacy = false;
    try { legacy = localStorage.getItem('wh_input_resolver') === 'legacy'; } catch (e) {}
    const want = ny < -0.55 ? 'up' : ny > 0.55 ? 'down' : null;
    if (legacy) {
      if (want) this._udPress(want);
      else if (this._udDir && !this._udHeld) this._udRelease();
      return;
    }
    if (want && this._udDir === want) return;
    if (this._udDir) this._udRelease();
    if (want) this._udPress(want);
  }
  _udRelease() {
    if (!this._udDir) return;
    const dir = this._udDir;
    const held = performance.now() - this._udT >= 200;
    clearTimeout(this._udTimer);
    this._udDir = null; this._udHeld = false;
    const used = this._udUsed; this._udUsed = false;
    if (this.up || this.down) { this.up = false; this.down = false; }
    else if (!held && !used) this._push(dir === 'up' ? 'ss-up' : 'ss-down');
  }

  /* ---------------- Keyboard ---------------- */
  _bindKeyboard() {
    window.addEventListener('keydown', (e) => {
      if (this._keys[e.code]) return; // ignore auto-repeat
      this._keys[e.code] = true;
      if (!this.enabled) return;
      // Worker 35: remap physical key -> canonical action code first.
      switch (this._remapCode(e.code)) {
        case 'KeyA': case 'ArrowLeft': this.axisX = -1; break;
        case 'KeyD': case 'ArrowRight': this.axisX = 1; break;
        case 'KeyW': case 'ArrowUp': this._udPress('up'); break;
        case 'KeyS': case 'ArrowDown': this._udPress('down'); break;
        case 'KeyJ': this._strike('punch'); break;
        case 'KeyK': this._strike('kick'); break;
        case 'KeyU': this._push('grab'); break;
        case 'KeyL': this._push('surge'); break;
        case 'Digit1': this._tekken('1'); break;
        case 'Digit2': this._tekken('2'); break;
        case 'Digit3': this._tekken('3'); break;
        case 'Digit4': this._tekken('4'); break;
        case 'Space': this.held.block = true; e.preventDefault(); break;
        case 'ShiftLeft': case 'ShiftRight': this._push('dodge'); break;
        case 'KeyV': this._push('vskill'); break; // V-System (owner 2026-10-22)
      }
    });
    window.addEventListener('keyup', (e) => {
      this._keys[e.code] = false;
      // Worker 35: translate through the remap so held keys release correctly.
      switch (this._remapCode(e.code)) {
        case 'KeyA': case 'ArrowLeft': if (this.axisX < 0) this.axisX = this._keys[this._physicalCode('right')] ? 1 : 0; break;
        case 'KeyD': case 'ArrowRight': if (this.axisX > 0) this.axisX = this._keys[this._physicalCode('left')] ? -1 : 0; break;
        case 'KeyW': case 'ArrowUp': case 'KeyS': case 'ArrowDown': this._udRelease(); break;
        case 'Space': this.held.block = false; break;
      }
    });
  }

  /* Worker 35: physical key currently bound to an action (for held-key checks). */
  _physicalCode(action) {
    if (!window.WHIdentity) return action;
    const I = window.WHIdentity;
    const keys = (I.getRemap && I.getRemap().keys) || {};
    const def = I.REMAP_DEFAULT_KEYS || {};
    const cur = (action in keys) ? keys[action] : def[action];
    return cur || '';
  }

  /* ---------------- Virtual joystick ----------------
     Primary path: nipplejs (MIT, vendored in game/vendor/nipplejs/) drives the
     left-thumb stick. Its directional vector feeds the SAME state the legacy
     binding fed — axisX (0.25 deadzone) and _udStick (Tekken tap-vs-hold) — so
     fighter behavior is unchanged. Multi-touch is safe: nipplejs only binds
     inside #joystick; the .act-btn buttons are separate DOM elements with
     their own touchstart handlers, so stick + buttons work simultaneously.
     Fallback: if the vendored build failed to load, the previous hand-rolled
     binding runs unchanged. */
  _bindJoystick() {
    const base = document.getElementById('joystick');
    const knob = document.getElementById('joystick-knob');
    if (!base) return;
    this._resetJoyKnob = () => { if (knob) knob.style.transform = 'translate(0,0)'; };

    if (window.nipplejs) {
      // nipplejs draws its own base + knob UI inside the zone; retire the legacy knob.
      if (knob) knob.style.display = 'none';
      const manager = window.nipplejs.create({
        zone: base,
        mode: 'static',                          // fixed stick, bottom-left (fighting-game standard)
        position: { top: '50%', left: '50%' },    // centered in the #joystick zone
        color: 'white',
        size: 120,                               // 130px zone with a small margin
        threshold: 0.1,
        fadeTime: 150,
        restOpacity: 0.85,
      });
      // nipplejs vector: x is right-positive, y is UP-positive (negated screen y).
      // _udStick takes screen-style ny (down-positive; up zone is ny < -0.55).
      manager.on('move', (evt, data) => {
        const nx = Math.max(-1, Math.min(1, data.vector.x || 0));
        this._stick8(nx, (data.vector.y || 0));
      });
      manager.on('end', () => {
        this.axisX = 0;
        this._udRelease(); // resolve any pending tap/hold
      });
      this._joyManager = manager;
      return;
    }
    this._bindJoystickLegacy(base, knob);
  }

  /* Legacy hand-rolled touch binding — fallback when nipplejs is unavailable
     (vendor script blocked or failed to load). Behavior identical to before. */
  _bindJoystickLegacy(base, knob) {
    const maxR = 46;

    const start = (id, x, y) => {
      const r = base.getBoundingClientRect();
      this._joyCenter = { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      this._joyActive = true; this._joyId = id;
      move(x, y);
    };
    const move = (x, y) => {
      if (!this._joyActive) return;
      let dx = x - this._joyCenter.x;
      let dy = y - this._joyCenter.y;
      const dist = Math.hypot(dx, dy);
      const clamped = Math.min(dist, maxR);
      const ang = Math.atan2(dy, dx);
      const kx = Math.cos(ang) * clamped;
      const ky = Math.sin(ang) * clamped;
      knob.style.transform = `translate(${kx}px, ${ky}px)`;
      const nx = (Math.cos(ang) * clamped) / maxR;
      // Tekken tap-vs-hold: tap u/d = sidestep, hold = jump/crouch.
      const ny = (Math.sin(ang) * clamped) / maxR;
      this._stick8(nx, -ny);
    };
    const end = () => {
      this._joyActive = false; this._joyId = null;
      this.axisX = 0;
      this._udRelease(); // resolve any pending tap/hold
      this._resetJoyKnob();
    };

    base.addEventListener('touchstart', (e) => {
      const t = e.changedTouches[0]; start(t.identifier, t.clientX, t.clientY); e.preventDefault();
    }, { passive: false });
    base.addEventListener('touchmove', (e) => {
      for (const t of e.changedTouches) if (t.identifier === this._joyId) move(t.clientX, t.clientY);
      e.preventDefault();
    }, { passive: false });
    const tEnd = (e) => {
      for (const t of e.changedTouches) if (t.identifier === this._joyId) end();
    };
    base.addEventListener('touchend', tEnd);
    base.addEventListener('touchcancel', tEnd);
    // Mouse fallback for joystick (desktop testing)
    base.addEventListener('mousedown', (e) => { start('mouse', e.clientX, e.clientY); });
    window.addEventListener('mousemove', (e) => { if (this._joyId === 'mouse') move(e.clientX, e.clientY); });
    window.addEventListener('mouseup', () => { if (this._joyId === 'mouse') end(); });
  }

  /* ---------------- Action buttons ---------------- */
  _bindButtons() {
    document.querySelectorAll('.act-btn').forEach((btn) => {
      const action = btn.dataset.btn;
      const press = (e) => {
        e.preventDefault();
        if (action === 'block') this.held.block = true;
        else if (action === 'punch' || action === 'kick') this._strike(action);
        else if (/^[1234]$/.test(action)) this._tekken(action); // LP/RP/LK/RK limbs
        // TRANSFORM touch button: tap = transform up; tap while crouching
        // (joystick held down) = rare transform-down. No keyboard input.
        else if (action === 'transform') this._push(this.down ? 'transform-down' : 'transform');
        else this._push(action);
      };
      const release = (e) => {
        e.preventDefault();
        if (action === 'block') this.held.block = false;
      };
      btn.addEventListener('touchstart', press, { passive: false });
      btn.addEventListener('touchend', release, { passive: false });
      btn.addEventListener('touchcancel', release, { passive: false });
      btn.addEventListener('mousedown', press);
      btn.addEventListener('mouseup', release);
      btn.addEventListener('mouseleave', release);
    });
  }
  _resetJoyKnob() {}
}
