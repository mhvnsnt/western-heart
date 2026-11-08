#!/usr/bin/env python3
"""apply_dw_wiring.py — apply the Devil Within retarget wiring to the game.
Patches game/js/t3anims.js (the DW_MOVES / ensureDwMoves / dwMoveClip /
dwMoveRetarget mirror of the T7 moves) and game/js/fighter.js (the dw: hooks:
Surge Form trigger, DW beam, Surge Form throw override).
Reproducible and idempotent: fails loudly on a missing anchor, skips edits
that are already applied. Run from the repo root:
  python3 tools/anim/apply_dw_wiring.py
Anchors are exact strings from the dw-decode head (af46251); the script
refuses to run if any anchor is absent.
"""
import argparse
import os
import re
import sys

def _default_root():
    # The script lives at <repo>/tools/anim/apply_dw_wiring.py when landed.
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(here) == 'anim' and os.path.basename(os.path.dirname(here)) == 'tools':
        return os.path.dirname(os.path.dirname(here))
    return os.path.abspath(os.path.join(here, '..', '..'))

ROOT = os.environ.get('DW_WIRING_ROOT') or _default_root()
T3 = os.path.join(ROOT, 'game/js/t3anims.js')
FG = os.path.join(ROOT, 'game/js/fighter.js')

DW_T3ANIMS = '''
/* ============================================================
   DEVIL WITHIN MOVES (DW) — retargeted DW motion curves.
   Mirrors the T7 moves (T7_MOVES / ensureT7Moves / t7MoveClip /
   t7MoveRetarget) but loads the wh-dw-moves/1 packs baked by
   tools/anim/dw_curve_bake.py from the decoded DW curves
   (teardown/tekken5/dw-motion-curves.json). The DW bank has NO
   stance clip (the DW clips start moving immediately), so dwMoveClip
   does NOT gate on a captured rest pose — the rig is analyzed on
   first retarget, the same analyzeRig the T3 banks use.
   The DW clips are the Surge Kit donor (gym_ikdv_*) and the Soul
   Surge Bloom donor (gym_dwup00 / gym_dwhadoh00) — donor data only,
   never presented as a source character. active_frames is null for
   every DW move: the decode carries no hit timing, so the game times
   DW moves on the moveset's own S/A/R (honest nulls).
   ============================================================ */
export const DW_MOVES = {
  pantera: { dir: 'assets/anim/dw/', pack: 'moves.pantera.pack.json' },
};

const _dwmoves = {}; // fighterId -> { skelId, clips: { name: clip }, moves: { moveKey: { clip, active, dw_source } } }
const _dwmovesLoading = {};

export function ensureDwMoves(fid, THREE) {
  const spec = DW_MOVES[fid];
  if (!spec) return Promise.resolve(null);
  if (_dwmoves[fid]) return Promise.resolve(_dwmoves[fid]);
  if (_dwmovesLoading[fid]) return _dwmovesLoading[fid];
  _dwmovesLoading[fid] = (async () => {
    try {
      const pack = await fetchT7Json(spec.dir + spec.pack);
      const skelId = 'dw:' + spec.dir;
      if (!_t3skelCache[skelId]) _t3skelCache[skelId] = await fetchT7Json(spec.dir + (pack.skeleton || 'skeleton.json'));
      const clips = {};
      for (const [cname, cdata] of Object.entries(pack.clips || {})) {
        if (cdata.anim_set && cdata.anim_set !== 'FIGHT') continue;
        const clip = jsonToClip(`dw_${fid}_${cname}`, cdata, THREE);
        if (!clip) continue;
        clip.userData.dw = cdata.dw_source;
        clips[cname] = clip;
      }
      const moves = {}, byInput = {};
      for (const [key, m] of Object.entries(pack.moves || {})) {
        if (!clips[m.clip]) continue;
        moves[key] = { clip: m.clip, active: null, dw_source: m.dw_source };
        const ni = t7NormInput(m.input);
        if (ni && !byInput[ni]) byInput[ni] = key;
      }
      _dwmoves[fid] = { skelId, clips, moves, byInput };
      console.log(`[WH-DW] ${fid}: ${Object.keys(clips).length} DW move clips (${spec.dir}${spec.pack})`);
      return _dwmoves[fid];
    } catch (e) {
      console.warn(`[WH-DW] ${fid}: DW move clips unavailable, moves keep their current clips:`, e.message || e);
      return null;
    }
  })();
  return _dwmovesLoading[fid];
}

export function dwMoveClip(fid, moveKey, model, input) {
  const rec = _dwmoves[fid];
  if (!rec) return null;
  const key = rec.moves[moveKey] ? moveKey : (input && rec.byInput ? rec.byInput[t7NormInput(input)] : null);
  const mv = key ? rec.moves[key] : null;
  if (!mv || !rec.clips[mv.clip]) return null;
  // No stance gate: the DW bank has no stance clip, so there is no captured
  // rest pose to require — the rig is analyzed on first retarget.
  return { name: 'dw:' + key, clip: rec.clips[mv.clip], skelId: rec.skelId, active: null, dw_source: mv.dw_source, anim: mv.clip };
}

export function dwMoveRetarget(fid, moveKey, model, THREE, instanceKey) {
  const rec = _dwmoves[fid];
  if (!rec) return null;
  const mv = rec.moves[moveKey];
  if (!mv || !rec.clips[mv.clip]) return null;
  const name = 'dw:' + moveKey;
  return retargetT3Clips({ [name]: rec.clips[mv.clip] }, rec.skelId, model, THREE, instanceKey, [name]);
}
'''

def replace_once(src, anchor, new, label, path):
    if new.strip() in src:
        print(f'  SKIP (already applied): {label}')
        return src
    if anchor not in src:
        raise SystemExit(f'ANCHOR NOT FOUND in {path} for {label}: {anchor[:100]!r}')
    print(f'  applied: {label}')
    return src.replace(anchor, new, 1)

def main():
    # ---- t3anims.js ----
    with open(T3) as f:
        t3 = f.read()
    if 'export const DW_MOVES' not in t3:
        m = re.search(r'export function t7MoveRetarget\([^\n]*\n(?:.*\n)*?\}\n', t3)
        if not m:
            raise SystemExit('ANCHOR NOT FOUND: t7MoveRetarget in t3anims.js')
        anchor = m.group(0)
        t3 = t3.replace(anchor, anchor + DW_T3ANIMS, 1)
        with open(T3, 'w') as f:
            f.write(t3)
        print('  applied: t3anims.js DW section (after t7MoveRetarget)')
    else:
        print('  SKIP (already applied): t3anims.js DW section')

    # ---- fighter.js ----
    with open(FG) as f:
        fg = f.read()

    # (1) import the DW functions next to the T7 ones.
    old_imp = "  applyT7Stance, ensureT7Moves, t7MoveClip, t7MoveRetarget, retargetProfileFor } from './t3anims.js';"
    new_imp = "  applyT7Stance, ensureT7Moves, t7MoveClip, t7MoveRetarget, ensureDwMoves, dwMoveClip, dwMoveRetarget, retargetProfileFor } from './t3anims.js';"
    fg = replace_once(fg, old_imp, new_imp, 'fighter.js import (DW functions)', FG)

    # (2) bind: ensureDwMoves in the background next to ensureT7Moves.
    old_bind = "    try { const p = ensureT7Moves(this.char.id, THREE); if (p && p.catch) p.catch(() => {}); } catch (e) { /* optional */ }"
    new_bind = old_bind + "\n    try { const p = ensureDwMoves(this.char.id, THREE); if (p && p.catch) p.catch(() => {}); } catch (e) { /* optional */ }"
    fg = replace_once(fg, old_bind, new_bind, 'fighter.js bind (ensureDwMoves in background)', FG)

    # (3) startSurgeForm: set the trigger-pending flag.
    old_aura = "    this._auraFlash = 1.0;\n    return true;\n  }"
    new_aura = ("    this._auraFlash = 1.0;\n"
                "    // Soul Surge Bloom trigger (DW dwup00): play the DW trigger clip once when\n"
                "    // the form starts. Best-effort — if the DW pack has not loaded yet, the form\n"
                "    // still starts and the trigger plays on the next surge.\n"
                "    this._dwTriggerPending = true;\n"
                "    this._dwTriggerId = (this._dwTriggerId || 0) + 1;\n"
                "    return true;\n  }")
    fg = replace_once(fg, old_aura, new_aura, 'fighter.js startSurgeForm (trigger pending)', FG)

    # (4) _attackClipPlan: DW beam hook before the T7 branch.
    old_t7 = "    // REAL T7 MOVE (t3anims.js T7_MOVES): the row's own Tekken 7 clip, mapped exactly by"
    new_t7 = ("    // DW SURGE BEAM: the surge attack plays the DW wave clip (dwhadoh00).\n"
              "    // Keyed on attackName === 'surge' — the surge move has no moveKey, so the\n"
              "    // T7 branch below (which needs move.moveKey) never matches it. Skipped\n"
              "    // if the DW retarget failed before (in _dwskip), like the T7 skip set.\n"
              "    if (attackName === 'surge' && !(this._dwskip && this._dwskip.has('surge'))) {\n"
              "      const dw = dwMoveClip(this.char.id, 'surge', this._t3.model);\n"
              "      if (dw) return { name: dw.name, kind: 'dw', timing: null, why: 'DW surge beam (dwhadoh00)', limb: 'armR' };\n"
              "    }\n"
              + old_t7)
    fg = replace_once(fg, old_t7, new_t7, 'fighter.js _attackClipPlan (DW beam hook)', FG)

    # (5) _attackClip: dw: branch after the t7: branch.
    old_t7b = """    if (name && !this.t3actions[name] && name.startsWith('t7:')) {
      const rc = t7MoveRetarget(this.char.id, this._t3.bank, name.slice(3), this._t3.model, THREE, this._t3.modelKey);
      if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
      if (!this.t3actions[name]) {
        // Could not retarget safely: this move keeps its previous clip choice from now on.
        (this._t7skip || (this._t7skip = new Set())).add(name.slice(3));
        plan = this._attackClipPlan(move, attackName);
        name = plan ? plan.name : null;
      }
    }"""
    new_t7b = old_t7b + """
    if (name && !this.t3actions[name] && name.startsWith('dw:')) {
      const rc = dwMoveRetarget(this.char.id, name.slice(3), this._t3.model, THREE, this._t3.modelKey);
      if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
      if (!this.t3actions[name]) {
        // Could not retarget safely: this move keeps its previous clip choice from now on.
        (this._dwskip || (this._dwskip = new Set())).add(name.slice(3));
        plan = this._attackClipPlan(move, attackName);
        name = plan ? plan.name : null;
      }
    }"""
    fg = replace_once(fg, old_t7b, new_t7b, 'fighter.js _attackClip (dw: branch)', FG)

    # (6) _dwThrowAction / _dwTriggerAction helpers — inserted at class level
    # just before the _bindThrowPair method declaration (NOT inside its body).
    old_bindthrow = "  _bindThrowPair(pair, victim) {"
    helpers = """  /* Retarget the DW Surge Kit throw clip for this fighter's front throw.
     Returns the action name or null (pack not loaded yet, or not a front throw). */
  _dwThrowAction() {
    const key = this.attackName;
    if (key !== '1+3' && key !== '2+4') return null;
    const name = 'dw:' + key;
    if (this.t3actions[name]) return name;
    const rc = dwMoveRetarget(this.char.id, key, this._t3.model, THREE, this._t3.modelKey);
    if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
    return this.t3actions[name] ? name : null;
  }
  /* Retarget the DW Soul Surge Bloom trigger clip ('dw:surge-trigger') onto this
     fighter. Returns the action name or null (pack not loaded yet). */
  _dwTriggerAction() {
    const name = 'dw:surge-trigger';
    if (this.t3actions[name]) return name;
    const rc = dwMoveRetarget(this.char.id, 'surge-trigger', this._t3.model, THREE, this._t3.modelKey);
    if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
    return this.t3actions[name] ? name : null;
  }
"""
    if '_dwThrowAction' not in fg:
        fg = replace_once(fg, old_bindthrow, helpers + old_bindthrow, 'fighter.js _dwThrowAction / _dwTriggerAction helpers', FG)
    else:
        print('  SKIP (already applied): fighter.js DW helpers')

    # (7) the Surge Form throw override in _bindThrowPair.
    old_victim = "    pair.victimAction = victim._reactionAction(vBank, pair.clips.victimSlot, 'victim:' + hexSlot(pair.clips.victimSlot));"
    new_victim = old_victim + """
    // SURGE FORM THROW (DW): in Surge Form, Pantera's front throws play the DW Surge Kit
    // throw clip for the thrower only — the victim keeps the T3 reaction, the pair root
    // still follows the pack anchors, and the pack's damage time / duration still time
    // the pair. Known limit: the DW clip (2.0/2.1 s) is not the pair's duration, so the
    // thrower may finish early/late; the pair clock rules.
    if (thrower.surgeForm) {
      const dwName = thrower._dwThrowAction && thrower._dwThrowAction();
      if (dwName) pair.throwerAction = dwName;
    }"""
    fg = replace_once(fg, old_victim, new_victim, 'fighter.js _bindThrowPair (Surge Form DW throw override)', FG)

    # (8) _animate idle/walk branch: pending trigger plays once, owns the frame.
    old_idle = """        // Animated bank stance / walk cycle — the living fighting idle.
        if (t3Active) this._playT3(t3Wanted, { loop: true });
        else this._stopT3();"""
    new_idle = """        // SOUL SURGE BLOOM TRIGGER (DW dwup00): when Surge Form just started, play
        // the DW trigger clip once. It owns the frame while it runs (isRunning);
        // when it finishes, the stance loop resumes. If the DW pack has not
        // loaded yet, the flag clears and the form still started.
        if (this._dwTriggerPending) {
          const dwName = this._dwTriggerAction && this._dwTriggerAction();
          if (dwName) {
            this._dwTriggerPending = false;
            const a = this.t3actions[dwName];
            if (a && a.isRunning && a.isRunning()) break;
            if (this._playT3Once(dwName, 'dw-trigger:' + (this._dwTriggerId || 0))) break;
          } else {
            this._dwTriggerPending = false;
          }
        }
        // Animated bank stance / walk cycle — the living fighting idle.
        if (t3Active) this._playT3(t3Wanted, { loop: true });
        else this._stopT3();"""
    fg = replace_once(fg, old_idle, new_idle, 'fighter.js _animate (pending DW trigger plays once)', FG)

    with open(FG, 'w') as f:
        f.write(fg)
    print('done.')

if __name__ == '__main__':
    main()
