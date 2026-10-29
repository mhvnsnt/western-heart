/* model-key-guard.test.mjs — Regression guard for the model-key defect class.
 *
 * THE BUG THIS GUARDS (owner order 2026-10-21, audit: docs/MODEL-KEY-AUDIT-2026-10-21.md):
 * a fighter who HAS their own model wired in the repo loads ANOTHER character's
 * model because a key in the resolution chain points at the wrong character.
 * Found in the wild: DIABLO's roster `model:` pointed at 'steve-fox' (fixed in
 * PR #412), then a full audit found 13 more (phantom, skull, sakura, kinpo,
 * waterfall, kingtyrant, burger, awapop, purplerain, nightwolf, cyborgx,
 * negativo, thor).
 *
 * THE CHAIN (verified in code):
 *   player / character-select path: game/js/attires.js selectedAttireModel()
 *     = ATTIRE_VARIANTS[fighter.model] || ATTIRE_VARIANTS[fighter.id], first
 *       entry by default; fighters with no entry fall back to fighter.model.
 *   enemy / prefetch / transform-formKey path: the RAW roster `model:` field
 *     (game/js/main.js, game/js/select-screen.js, game/js/fighter.js).
 *   the resolved key then loads MODEL_URLS[key] in game/js/assets.js, after
 *     the (currently empty) ATTIRE_CUSTOMIZATIONS override layer is applied.
 * A fighter is correct only when BOTH paths land on their own model (or on a
 * base the canon docs declare for them — the Nine Souls' vessel bases and
 * Zui's steve-fox, per game/assets/models/MODEL-STATUS.md).
 *
 * The OWNERSHIP table below mirrors the audit doc (source of truth:
 * docs/MODEL-INVENTORY.md, game/assets/models/MODEL-STATUS.md,
 * roster/TRIPO-REGISTRY.md). When a fighter's own model is wired or their
 * declared base changes, update the audit doc and this table together.
 *
 * Run: node --test game/tests/model-key-guard.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, mkdtempSync, cpSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

/* fighter id -> { own: [MODEL_URLS keys that are this fighter's own wired
 * models], base: declared canon base key, pending: own file not yet in repo } */
const OWNERSHIP = {
  "awapop": {
    "own": [
      "awa-pop",
      "awa-pop-attire2"
    ]
  },
  "baek-master-white": {
    "own": [
      "kevin-tripo",
      "baek",
      "baek-master-white"
    ]
  }, // wire-up 2026-10-22: Kevin A1 Tripo wired + ladder Slot 1
  "bruno": {
    "own": [
      "bruno",
      "bruno-attire1",
      "bruno-attire2"
    ]
  }, // wave 1 2026-10-23: his two on-main source attires wired into his ladder
  "burger": {
    "own": [
      "burger",
      "burger-attire2",
      "burger-attire3",
      "burger-attire4",
      "burger-attire5",
      "burger-attire6",
      "burger-attire7"
    ]
  },
  "byou": {
    "pending": true
  },
  "charger": {
    "own": [
      "charger",
      "blanka"
    ]
  }, // wave 1 2026-10-23: Blanka model ladders behind Charger (obsolete-originals rule)
  "charger-attire2": {
    "own": [
      "charger-attire2"
    ]
  },
  "buffalo-bill": {
    "own": [
      "buffalo-bill"
    ]
  }, // wave 1 2026-10-23: select entry + base key landed (Attire 3 'Ashes' model)
  "cainelias": {
    "own": [
      "cain-elias",
      "cain-elias-attire2"
    ]
  }, // wave 1 2026-10-23: select entry landed; model keys were already wired
  "chordz": {
    "own": [
      "chordz"
    ]
  }, // wave 1 2026-10-23: select entry + model key landed
  "cyborgx": {
    "own": [
      "cape-jones",
      "cape-jones-attire1",
      "cyborg-x"
    ]
  },
  "deathfang": {
    "own": [
      "deathfang",
      "deathfang-werewolf",
      "iori"
    ]
  }, // wave 1 2026-10-23: Iori model ladders behind Deathfang (obsolete-originals rule)
  "demonio": {
    "own": [
      "demonio",
      "demonio-a1",
      "demonio-winged",
      "demonio-human",
      "demonio-bloodline-ember",
      "demonio-body"
    ]
  },
  "demonio-bloodline-ember": {
    "own": [
      "demonio-bloodline-ember"
    ]
  },
  "demonio-human": {
    "own": [
      "demonio-human"
    ]
  },
  "demonio-winged": {
    "own": [
      "demonio-winged"
    ]
  },
  "diablo": {
    "own": [
      "diablo",
      "diablo-attire1"
    ]
  },
  "dio": {
    "own": [
      "dio",
      "dio-attire1"
    ]
  }, // wave 1 2026-10-23: Jade God source wired into his ladder
  "doc-frank-frankenstein": {
    "own": [
      "doc-frank-frankenstein"
    ]
  },
  "doc-frank-hood": {
    "own": [
      "doc-frank-hood"
    ]
  },
  "doc-frank-machine-shop": {
    "own": [
      "doc-frank-machine-shop"
    ]
  },
  "doc-frank-wowomomo": {
    "own": [
      "doc-frank-wowomomo"
    ]
  },
  "docfrank": {
    "own": [
      "doc-frank",
      "doc-frank-a1",
      "doc-frank-big",
      "doc-frank-wowomomo",
      "doc-frank-wowomomo-big",
      "doc-frank-hood",
      "doc-frank-hood-big",
      "doc-frank-frankenstein",
      "doc-frank-frankenstein-big",
      "doc-frank-machine-shop"
    ]
  },
  "dxmmii-patchwork": {
    "own": [
      "dxmmii-tripo",
      "dxmmii-patchwork",
      "dxmmii-a2"
    ]
  }, // table was stale vs the re-keyed ladder (Tripo default Slot 1); fixed 2026-10-22
  "gyou": {
    "pending": true
  },
  "jin_soul": {
    "base": "steve-fox"
  },
  "kai": {
    "pending": true
  },
  "kingtyrant": {
    "own": [
      "king-tyrant",
      "king-tyrant-attire1",
      "king-tyrant-attire2",
      "king-tyrant-attire3",
      "king-tyrant-attire4",
      "king-tyrant_alt1"
    ]
  }, // wire-up 2026-10-22: Tripo attires 1-4 wired + ladder
  "kinpo": {
    "own": [
      "kinpo",
      "kinpo-attire2",
      "kinpo-t8",
      "kinpo_alt1"
    ]
  }, // wire-up 2026-10-22: Attire 2 Goth Sport added to her ladder
  "koreshi": {
    "own": [
      "koreshi",
      "koreshi-attire1",
      "vega"
    ]
  }, // wave 1 2026-10-23: Tripo source wired + Vega model ladders behind Koreshi
  "kronos": {
    "own": [
      "kronos",
      "kronos-attire2",
      "kronos-attire3",
      "zangief",
      "zangief-attire1"
    ]
  }, // wave 1 2026-10-23: Zangief models ladder behind Kronos (obsolete-originals rule)
  "kronos-attire2": {
    "own": [
      "kronos-attire2"
    ]
  },
  "mariposa-monarch": {
    "own": [
      "mariposa-butterfly-default",
      "mariposa",
      "mariposa-monarch",
      "zafina-golden-pharaoh",
      "zafina"
    ]
  }, // table was stale vs the deduped ladder (Slot 1 Butterfly Default); fixed 2026-10-22
  "michiko": {
    "own": [
      "michiko-attire1",
      "michiko-attire2",
      "michiko"
    ]
  }, // wire-up 2026-10-22: Tripo Attires 1-2 (auto-rigged) wired + ladder
  "negativo": {
    "own": [
      "n3g4tiv0",
      "negativo-attire1",
      "negativo-attire2"
    ]
  }, // wave 1 2026-10-23: his two on-main source attires wired into his ladder
  "nightwolf": {
    "own": [
      "nightwolf",
      "nightwolf-attire1"
    ]
  }, // wire-up 2026-10-22: Tripo Attire 1 wired + ladder
  "pantera": {
    "own": [
      "pantera",
      "pantera-leoman",
      "pantera_alt1",
      "pantera-body"
    ]
  },
  "phantom": {
    "own": [
      "phantom",
      "phantom-t8",
      "jin-bloodline-ember"
    ]
  }, // wire-up 2026-10-22: Jin Kazama Bloodline Ember added to Phantom's ladder
  "purplerain": {
    "own": [
      "purple-rain",
      "purple-rain-main"
    ]
  },
  "retsu": {
    "pending": true
  },
  "rin": {
    "pending": true
  },
  "ryuji": {
    "own": [
      "ryuji-rock"
    ]
  },
  "ryuji-rock": {
    "own": [
      "ryuji-rock"
    ]
  }, // model landed 2026-10-22 (owner Tripo); byte-identical copy at the key's path 2026-10-23 (wave 1) — no longer pending
  "sakura": {
    "own": [
      "saku-ra",
      "saku-ra-main",
      "saku-ra_alt1"
    ]
  },
  "samura1": {
    "own": [
      "sam-ur-a1",
      "sam-ur-a1-body"
    ]
  },
  "scimitar": {
    "own": [
      "scimitar"
    ]
  },
  "sha": {
    "pending": true
  },
  "skull": {
    "own": [
      "skull",
      "skull-tripo",
      "skull-base"
    ]
  }, // wave 1 2026-10-23: Tripo A1 + Bryan base wired into his ladder (ATTIRE-SLOTS.md)
  "slice": {
    "own": [
      "slice",
      "slice-attire1",
      "slice-attire2"
    ]
  },
  "star": {
    "own": [
      "star",
      "star-attire1",
      "star-attire2",
      "star-attire3",
      "star-attire5"
    ]
  }, // wire-up 2026-10-22: Tripo attires 1-3+5 wired + ladder
  "thor": {
    "own": [
      "thor",
      "thor-attire2"
    ]
  },
  "torch": {
    "own": [
      "torch",
      "torch-tripo-a1",
      "torch-tripo-a2"
    ]
  }, // table was stale vs the torch ladder (A1 Valkyrie of Flame default); fixed 2026-10-22
  "vainabel": {
    "own": [
      "vainabel",
      "vainabel-attire1",
      "vainabel-attire2",
      "vainabel-attire3",
      "vainabel-attire4"
    ]
  }, // wave 1 2026-10-23: select entry + base key landed (base = Attire 2; A1 Tripo not on disk)
  "tou": {
    "pending": true
  },
  "waterfall": {
    "own": [
      "waterfall",
      "waterfall-attire1"
    ]
  }, // wave 1 2026-10-23: Tripo source wired into her ladder
  "yukihyo": {
    "own": [
      "yukihyo",
      "yukihyo-attire1",
      "yukihyo-attire2",
      "yukihyo-attire3",
      "armor-king",
      "armor-king-attire1"
    ]
  }, // wave 1 2026-10-23: his source attires wired + Armor King models ladder behind him
  "zen": {
    "own": [
      "zen",
      "zen-attire1",
      "zen-body"
    ]
  }, // +zen-body (ladder Attire 2)
  "zui": {
    "own": [
      "zui-attire1",
      "zui-attire2"
    ],
    "base": "steve-fox"
  }
};

// --- Load the real chain modules (sandbox copy: same pattern as
// --- customization/tools/test_game_hook.mjs; the two modules are pure ESM).
const sandbox = mkdtempSync(join(tmpdir(), 'wh-model-key-guard-'));
cpSync(join(ROOT, 'game/js/roster-full.js'), join(sandbox, 'roster-full.js'));
cpSync(join(ROOT, 'game/js/attires.js'), join(sandbox, 'attires.js'));
cpSync(join(ROOT, 'game/js/material-status.js'), join(sandbox, 'material-status.js')); // material gate data
writeFileSync(join(sandbox, 'package.json'), '{"type":"module"}');
const { FULL_ROSTER } = await import(pathToFileURL(join(sandbox, 'roster-full.js')).href);
const { selectedAttireModel } = await import(pathToFileURL(join(sandbox, 'attires.js')).href);
// Material gate (tools/assets/material_gate.mjs): quarantined models are never offered,
// so a fighter's player path skips them; a fighter with none left is not selectable.
const { MATERIAL_STATUS } = await import(pathToFileURL(join(sandbox, 'material-status.js')).href);
const QUARANTINED = new Set(Object.keys(MATERIAL_STATUS.quarantine || {}));

// --- MODEL_URLS parsed from the real assets.js source (authored table of
// --- plain string literals), with the ATTIRE_CUSTOMIZATIONS override layer
// --- from the real generated registry applied on top, exactly as assets.js
// --- applies it at runtime.
function parseExportedObject(file, name) {
  const src = readFileSync(file, 'utf8');
  const start = src.indexOf(`export const ${name} = {`);
  assert.notEqual(start, -1, `${name} not found in ${file}`);
  const end = src.indexOf('\n};', start);
  const block = src.slice(start + `export const ${name} = `.length, end + 2).replace(/\/\/[^\n]*/g, '');
  return Function('return (' + block + ')')();
}
const MODEL_URLS = parseExportedObject(join(ROOT, 'game/js/assets.js'), 'MODEL_URLS');
const OVERRIDES = parseExportedObject(join(ROOT, 'game/js/attire-customizations.js'), 'ATTIRE_CUSTOMIZATIONS');
for (const [k, u] of Object.entries(OVERRIDES || {})) if (u) MODEL_URLS[k] = u;

const urlToRepoPath = (u) => (u.startsWith('../') ? u.slice(3) : join('game', u));

test('every fighter with a wired own model resolves to their OWN model on both resolution paths', () => {
  const bad = [];
  for (const f of FULL_ROSTER) {
    const o = OWNERSHIP[f.id];
    if (!o || !o.own) continue; // no own model wired: declared-base / fallback riders are covered below
    if (f.modelPending) continue; // MODEL PENDING: no own model yet (ryuji since 6e3ba07c2 gave ryuji-rock to CORNERSTONE)
    const playerKey = selectedAttireModel(f);
    const enemyKey = f.model;
    if (playerKey === null && !o.own.some(k => !QUARANTINED.has(k))) continue; // material-gated out of select
    if (!o.own.includes(playerKey)) bad.push(`${f.id}: player/select path resolves '${playerKey}' (not their own)`);
    if (!o.own.includes(enemyKey)) bad.push(`${f.id}: enemy/raw path resolves '${enemyKey}' (not their own)`);
  }
  assert.deepEqual(bad, [], 'wrong-character model resolutions:\n' + bad.join('\n'));
});

test('declared-base riders stay on their declared base (do not "fix" the souls onto wrong files)', () => {
  const bad = [];
  for (const f of FULL_ROSTER) {
    const o = OWNERSHIP[f.id];
    if (!o || !o.base || o.own) continue;
    const playerKey = selectedAttireModel(f);
    if (playerKey !== o.base || f.model !== o.base)
      bad.push(`${f.id}: declared base '${o.base}' but resolves player='${playerKey}' roster='${f.model}'`);
  }
  assert.deepEqual(bad, [], 'declared-base drift:\n' + bad.join('\n'));
});

test('every resolved model URL points at a file that exists in the repo', () => {
  const bad = [];
  for (const f of FULL_ROSTER) {
    const o = OWNERSHIP[f.id] || {};
    if (o.pending || f.modelPending) continue; // MODEL PENDING: no own model yet (owner 2026-10-23)
    for (const [path, key] of [['player', selectedAttireModel(f)], ['enemy', f.model]]) {
      if (key === null) continue; // material-gated out of select (no usable attire)
      const url = MODEL_URLS[key];
      if (!url) { bad.push(`${f.id}: ${path} key '${key}' has no MODEL_URLS entry`); continue; }
      if (!existsSync(join(ROOT, urlToRepoPath(url)))) bad.push(`${f.id}: ${path} key '${key}' -> ${url} (file missing)`);
    }
  }
  assert.deepEqual(bad, [], 'unresolvable model targets:\n' + bad.join('\n'));
});
