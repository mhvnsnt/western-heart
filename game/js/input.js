/* ============================================================
   WESTERN HEART — Input Manager
   Unifies touch (virtual joystick + action buttons) and keyboard
   into one command state consumed by the player Fighter.

   Exposed state:
     axisX  : -1..1 horizontal move
     up     : bool (jump intent)
     down   : bool (crouch intent — enables d/df/db motions)
     held   : { block }                  // continuous
     pressed: queue of one-shot actions  // 1/2/3/4 (Tekken), 1+3/2+4 throws,
                                         // punch/kick/grab/surge/dodge (legacy)

   TEKKEN INPUTS: 1/2/3/4 keys = left punch / right punch / left kick / right kick.
   1+3 or 2+4 together (140ms chord) = throw. Motions (qcf, f,F) tracked via
   direction history in the fighter's TekkenBuffer (see movesets.js).
   COMMAND GRAB (legacy): press P+K together (touch) or J+K together / U (keyboard).
   ============================================================ */

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
    this._resetJoyKnob();
  }

  consume() { const q = this._queue.slice(); this._queue.length = 0; return q; }

  _push(action) { if (this.enabled) this._queue.push(action); }

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

  /* Tekken chords: 1+3 / 2+4 => throw, 1+2 / 3+4 => special chord.
     Same 140ms window as the legacy P+K grab. */
  _tekken(btn) {
    const now = performance.now();
    const chords = { '1': ['3', '1+3'], '3': ['1', '1+3'], '2': ['4', '2+4'], '4': ['2', '2+4'],
                     '1x': ['2', '1+2'], '2x': ['1', '1+2'] };
    // primary: 1+3 / 2+4 throws; secondary: 1+2 / 3+4 (chain-throw specials)
    const pairs = btn === '1' ? [['3', '1+3'], ['2', '1+2']]
                : btn === '2' ? [['4', '2+4'], ['1', '1+2']]
                : btn === '3' ? [['1', '1+3'], ['4', '3+4']]
                : [['2', '2+4'], ['3', '3+4']];
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

  /* ---------------- Keyboard ---------------- */
  _bindKeyboard() {
    window.addEventListener('keydown', (e) => {
      if (this._keys[e.code]) return; // ignore auto-repeat
      this._keys[e.code] = true;
      if (!this.enabled) return;
      switch (e.code) {
        case 'KeyA': case 'ArrowLeft': this.axisX = -1; break;
        case 'KeyD': case 'ArrowRight': this.axisX = 1; break;
        case 'KeyW': case 'ArrowUp': this.up = true; break;
        case 'KeyJ': this._strike('punch'); break;
        case 'KeyK': this._strike('kick'); break;
        case 'KeyU': this._push('grab'); break;
        case 'KeyL': this._push('surge'); break;
        case 'Digit1': this._tekken('1'); break;
        case 'Digit2': this._tekken('2'); break;
        case 'Digit3': this._tekken('3'); break;
        case 'Digit4': this._tekken('4'); break;
        case 'KeyS': case 'ArrowDown': this.down = true; break;
        case 'Space': this.held.block = true; e.preventDefault(); break;
        case 'ShiftLeft': case 'ShiftRight': this._push('dodge'); break;
      }
    });
    window.addEventListener('keyup', (e) => {
      this._keys[e.code] = false;
      switch (e.code) {
        case 'KeyA': case 'ArrowLeft': if (this.axisX < 0) this.axisX = this._keys['KeyD'] ? 1 : 0; break;
        case 'KeyD': case 'ArrowRight': if (this.axisX > 0) this.axisX = this._keys['KeyA'] ? -1 : 0; break;
        case 'KeyW': case 'ArrowUp': this.up = false; break;
        case 'KeyS': case 'ArrowDown': this.down = false; break;
        case 'Space': this.held.block = false; break;
      }
    });
  }

  /* ---------------- Virtual joystick ---------------- */
  _bindJoystick() {
    const base = document.getElementById('joystick');
    const knob = document.getElementById('joystick-knob');
    if (!base) return;
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
      this.axisX = Math.abs(nx) > 0.25 ? Math.max(-1, Math.min(1, nx)) : 0;
      this.up = (Math.sin(ang) * clamped) / maxR < -0.55; // pushed up
      this.down = (Math.sin(ang) * clamped) / maxR > 0.55; // pushed down (crouch)
    };
    const end = () => {
      this._joyActive = false; this._joyId = null;
      this.axisX = 0; this.up = false; this.down = false;
      this._resetJoyKnob();
    };
    this._resetJoyKnob = () => { if (knob) knob.style.transform = 'translate(0,0)'; };

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
