/* ============================================================
   WESTERN HEART — Movesets (LANE 3: moveset wiring)
   Per-fighter Tekken movelists built from REAL T3 teardown data
   (teardown/tekken3/movesets/moveset_{king,jin,bryan,heihachi,
   xiaoyu,yoshimitsu,gunjack}.json — decoded motion banks).

   Tekken input language: 1=left punch, 2=right punch,
   3=left kick, 4=right kick. Throws: 1+3, 2+4. Strings: 1,2.
   Specials: motion inputs (qcf+2, f,F+1 ...).

   Data files: game/assets/movesets/{fighter_id}.json (45 fighters).
   Every move carries t3_source/t3_row/t3_command provenance.
   Fighters whose Tekken base has no T3 bank use the closest
   archetype proxy — marked "proxy": true with an honest note.
   (T7/TTT2 per-character banks are gapfill lane's extraction work).

   SCHEMA v2 (moveset-editor contract, docs/movesets/MOVESET-SCHEMA.md):
   each move also carries:
     anim_ref    — preview-animation clip ref for the editor's live preview
                   ("t3:king:row:44", "doa:bass:palm-jab", ...)
     input_slots — Tekken input slots the move can occupy in the editor
                   (canonical first; strings also list component inputs)
     move_class  — "strike" | "throw" | "string" | "special" (editor filters)
   Top level: schema_version: 2, plus per-game provenance fields and the
   honest "proxy" flag. v2 is additive — no v1 field was renamed/removed.
   ============================================================ */

// All fighter ids with a wired moveset file (36 playable + 9 staged for lane 2)
export const MOVESET_IDS = [
  'pantera', 'demonio', 'phantom', 'diablo', 'skull', 'samura1', 'sakura',
  'rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu', 'zen', 'gyou',
  'zui', 'kinpo', 'waterfall', 'kingtyrant', 'burger', 'awapop', 'scimitar',
  'purplerain', 'nightwolf', 'dio', 'cyborgx', 'michiko', 'star', 'torch',
  'bruno', 'negativo', 'thor', 'yukihyo', 'slice', 'docfrank',
  'sunra', 'dxmmii', 'realizzt', 'rave', 'kutz', 'chordz', 'vainabel',
  'lili', 'baek',
  // DOA/VF federation (owner 2026-10-19): converted movelists, Tekken-notation
  'doa-kasumi', 'doa-bass', 'doa-hayabusa',
  'vf-akira', 'vf-sarah', 'vf-kage',
  // Reskin wave (2026-10-19): first custom attires as selectable fighters.
  'demonio-bloodline-ember', 'doc-frank-machine-shop', 'baek-master-white',
  'mariposa-monarch', 'dxmmii-patchwork',
  // Wave 2 (2026-10-19): Demonio winged devil form.
  'demonio-winged',
  // Sketchfab intake (owner 2026-10-19): working names, WH names pending.
  'zangief', 'blanka', 'vega', 'iori', 'armor-king',
  // Custom fighters (owner 2026-10-19): KRONOS — Zangief base + Golem (Urban Reign) mix.
  'kronos',
  // Ryuji Yamazaki x The Rock hybrid (owner 2026-10-19): 22 moves, King-proxy
  // throws incl. ROCK BOTTOM (frame data from T3 King chain row 281). Model
  // pending the owner's Tripo link — roster-full.js entry lands with model.glb.
  'ryuji-rock',
  // Intake wave 2 (owner 2026-10-19): remaining four intake movesets.
  'hugo', 'raiden', 'marduk', 'bob',
  // SF authentic translations (owner 2026-10-19, Akuma-in-T7 pattern:
  // SF motions kept, Tekken frame/throw logic). Builder: teardown/street-fighter-3d-games/tools/build_sf_movesets.py
  'sf-zangief', 'sf-blanka', 'sf-vega', 'sf-ryu', 'sf-ken', 'sf-chunli',
  'sf-guile', 'sf-mbison', 'sf-sagat', 'sf-dhalsim', 'sf-cammy',
];

const _movesets = {};
// Browser global mirror (fighter.js reads window.WH_MOVESETS); guarded for Node tests.
const _g = (typeof window !== 'undefined') ? window : (typeof globalThis !== 'undefined' ? globalThis : {});

/** Load all per-fighter moveset JSONs. Merges into the global WH_MOVESETS (richer than the legacy T3 aggregate). */
export async function loadFighterMovesets() {
  try {
    const data = await Promise.all(
      MOVESET_IDS.map(id =>
        fetch(`assets/movesets/${id}.json`).then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status} for ${id}`);
          return r.json();
        })
      )
    );
    _g.WH_MOVESETS = _g.WH_MOVESETS || {};
    MOVESET_IDS.forEach((id, i) => {
      _movesets[id] = data[i];
      _g.WH_MOVESETS[id] = data[i]; // full per-fighter moveset wins over aggregate
    });
    console.log(`[WH] Per-fighter movesets wired: ${MOVESET_IDS.length} fighters`);
  } catch (e) {
    console.warn('[WH] Could not load per-fighter movesets:', e);
  }
}

/** Synchronous accessor (null until loadFighterMovesets resolves). Test hook: registerMoveset(). */
export function getFighterMoveset(fighterId) {
  return _movesets[fighterId] || _g.WH_MOVESETS?.[fighterId] || null;
}

/** Register a moveset object directly (used by the Node test harness). */
export function registerMoveset(fighterId, data) {
  _movesets[fighterId] = data;
}

/** Exact notation lookup: '1', '2', '1+3', 'f+1', '1,2', 'qcf+2' ... */
export function getMove(fighterId, notation) {
  const ms = getFighterMoveset(fighterId);
  if (!ms || !ms.moves) return null;
  return ms.moves[notation] || null;
}

/** Split a special's input into {dirs:[...], button:'2'}.
 *  'qcf+2' -> {dirs:['d','d/f','f'], button:'2'}.
 *  'b,n,f+1+2' -> {dirs:['b','f'], button:'1+2'} (chain-throw chords). */
const MOTION_DIRS = {
  qcf: ['d', 'd/f', 'f'], qcb: ['d', 'd/b', 'b'],
  hcf: ['b', 'd/b', 'd', 'd/f', 'f'], hcb: ['f', 'd/f', 'd', 'd/b', 'b'],
};
export function parseSpecialInput(input) {
  // Trailing '+1/+2/...' runs are the button chord; the rest is the motion.
  const parts = input.split('+');
  const btnParts = [];
  while (parts.length && /^[1234]$/.test(parts[parts.length - 1])) btnParts.unshift(parts.pop());
  const motion = parts.join('+');
  const button = btnParts.join('+') || null;
  let dirs;
  if (MOTION_DIRS[motion]) {
    dirs = MOTION_DIRS[motion];
  } else {
    dirs = motion.split(',').map(s => s.trim()).filter(s => s && s !== 'n' && s !== 'any');
    dirs = dirs.flatMap(d => (d === 'f,F' ? ['f', 'f'] : d === 'b,B' ? ['b', 'b'] : [d]));
  }
  return { dirs, button };
}

/* ------------------------------------------------------------
   TekkenBuffer — per-fighter input history for strings, motion
   specials and directional attacks. Lives on the Fighter.
   ------------------------------------------------------------ */
export class TekkenBuffer {
  constructor(fighterId) {
    this.fighterId = fighterId;
    this.dirEvents = [];   // [{dir, t}] facing-relative: f,b,u,d,d/f,d/b,u/f,u/b
    this.lastDir = 'n';
    this.lastMove = null;  // notation of last executed attack
    this.lastMoveT = 0;
  }

  /** Feed the current facing-relative direction (call when it changes). */
  noteDirection(dir) {
    if (dir === this.lastDir) return;
    this.lastDir = dir;
    if (dir === 'n') return;
    const now = performance.now();
    this.dirEvents.push({ dir, t: now });
    if (this.dirEvents.length > 24) this.dirEvents.shift();
  }

  /** Recent direction events within ms. */
  _recentDirs(ms = 600) {
    const now = performance.now();
    while (this.dirEvents.length && now - this.dirEvents[0].t > ms) this.dirEvents.shift();
    return this.dirEvents.map(e => e.dir);
  }

  /** Does the recent direction history contain `seq` in order? */
  _matchMotion(seq, ms = 650) {
    const hist = this._recentDirs(ms);
    let i = 0;
    for (const d of hist) {
      if (d === seq[i]) { i++; if (i >= seq.length) return true; }
    }
    return false;
  }

  /**
   * Resolve a button press ('1'..'4') to a Tekken notation for this fighter.
   * Priority: motion special > string continuation > directional > raw button.
   * Returns the notation string, or null if the fighter has no such move.
   */
  pressButton(btn) {
    const ms = getFighterMoveset(this.fighterId);
    if (!ms || !ms.moves) return btn; // no data — raw passthrough
    const moves = ms.moves;

    // 1) Motion specials (qcf+2, f,F+1, ...)
    for (const sp of ms.specials || []) {
      const { dirs, button } = parseSpecialInput(sp.input);
      if (button !== btn) continue;
      if (dirs.length && this._matchMotion(dirs) && moves[sp.input]) {
        this._recordMove(sp.input);
        return sp.input;
      }
    }

    // 2) String continuation: last move '1' + press '2' -> '1,2' (800ms window)
    if (this.lastMove && performance.now() - this.lastMoveT < 800) {
      const cont = `${this.lastMove},${btn}`;
      if (moves[cont]) {
        this._recordMove(cont);
        return cont;
      }
    }

    // 3) Directional attack: current dir + button (f+1, d/f+2, ...)
    const dir = this.lastDir;
    if (dir && dir !== 'n') {
      const dnot = `${dir}+${btn}`;
      if (moves[dnot]) {
        this._recordMove(dnot);
        return dnot;
      }
    }

    // 4) Raw button
    if (moves[btn]) {
      this._recordMove(btn);
      return btn;
    }
    return null;
  }

  _recordMove(notation) {
    this.lastMove = notation;
    this.lastMoveT = performance.now();
  }

  /** Throws / explicit notations bypass the buffer. */
  recordExplicit(notation) {
    this._recordMove(notation);
  }

  /**
   * Resolve a button CHORD ('1+2', '3+4', '1+3', '2+4') to a Tekken notation.
   * Motion specials whose chord matches fire when their motion is in the
   * direction history (King's chain throws). Plain throw chords ('1+3','2+4')
   * resolve to themselves. Returns the notation or null.
   */
  pressChord(chord) {
    const ms = getFighterMoveset(this.fighterId);
    if (!ms || !ms.moves) return chord;
    const moves = ms.moves;
    for (const sp of ms.specials || []) {
      const { dirs, button } = parseSpecialInput(sp.input);
      if (button !== chord) continue;
      if (dirs.length && this._matchMotion(dirs) && moves[sp.input]) {
        this._recordMove(sp.input);
        return sp.input;
      }
    }
    // plain throw chord with no motion attached
    if ((chord === '1+3' || chord === '2+4') && moves[chord]) {
      this._recordMove(chord);
      return chord;
    }
    return null;
  }
}
