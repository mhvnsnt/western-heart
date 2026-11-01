// Creation suite phase 1 (2026-11-01). Node, no browser. Run: node --test test/creation-suite-templates.test.mjs
// Owner: "make sure in the Creation suite when you're creating a fighter that it's not mixable soldier as the default
// template make sure it's like a WWE style default template with all their options ... nothing's empty stubs";
// "smart to my screen in my safety boundaries ... no matter the orientation". Plan: customization/CREATION-SUITE-ORDER-2026-11-01.md.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (rel) => readFileSync(join(ROOT, rel), 'utf8');
const TRACKED = new Set(execFileSync('git', ['ls-files', '--', 'customization', 'packages'], { cwd: ROOT, maxBuffer: 1 << 28 }).toString().split('\n'));
const shipped = (rel) => TRACKED.has(rel) || existsSync(join(ROOT, rel));

function glbJson(rel) {
  const b = readFileSync(join(ROOT, rel));
  assert.equal(b.toString('latin1', 0, 4), 'glTF', rel + ' is a GLB');
  const len = b.readUInt32LE(12);
  return JSON.parse(b.toString('utf8', 20, 20 + len));
}

const TEMPLATES = JSON.parse(src('customization/templates/body-templates.json')).templates;

test('CREATE offers the WWE-style base bodies: 3 divisions, every mesh shipped', () => {
  assert.ok(TEMPLATES.length >= 9);
  const divs = new Set(TEMPLATES.map((t) => t.division));
  for (const d of ['Heavyweight', 'Cruiserweight', "Women's"]) assert.ok(divs.has(d), 'division ' + d);
  for (const t of TEMPLATES) {
    assert.ok(t.base_mesh && shipped(t.base_mesh), `${t.id}: base_mesh ${t.base_mesh} is in the repo`);
    assert.ok(t.name && t.desc, `${t.id}: name + description for the select card`);
  }
});

test('the default new fighter is a template body, never the stock Soldier model', () => {
  const s = src('customization/creation-suite-ui/js/suite.js');
  assert.match(s, /template:DEFAULT_TEMPLATE_ID, baseGlb:templateGlb\(DEFAULT_TEMPLATE_ID\)/, 'blankFighter() starts on a template');
  assert.match(s, /const BLANK_GLB = templateGlb\(DEFAULT_TEMPLATE_ID\);/);
  const def = /const DEFAULT_TEMPLATE_ID = '([^']+)'/.exec(s)[1];
  assert.ok(TEMPLATES.some((t) => t.id === def), `default template ${def} exists`);
  assert.ok(!/baseGlb:'customization\/create-fighter\/assets\/Soldier\.glb'/.test(s), 'Soldier is not the default base');
  assert.match(s, /function migrateLegacy\(\)/, 'saved fighters on the Soldier base move to the default template');
  assert.match(s, /if\(firstVisit && F\.mode==='blank'\) openTemplateSelect\(\);/, 'first visit opens the base-body select');
  assert.match(s, /cb\.onclick=\(\)=>\{ closeModal\(\); openTemplateSelect\(\); \}/, 'CREATE A FIGHTER goes through the base-body select');
});

test('no real wrestlers or source-game fighters on screen (names law)', () => {
  const s = src('customization/creation-suite-ui/js/suite.js');
  const list = /const BODY_TYPES = \[([\s\S]*?)\];/.exec(s)[1];
  for (const bad of ['Austin', 'HBK', 'Rikishi', 'Rock\'', 'King Frame', 'Ganryu', 'Chyna']) assert.ok(!list.includes(bad), `body type list has no "${bad}"`);
  const html = src('customization/creation-suite-ui/index.html');
  assert.ok(!/UI-EXTRACTION-LOG|No drag-and-drop|verbatim/i.test(html), 'no developer notes in the page');
  assert.ok(!/src-note'\)\.textContent='Menus:/.test(s), 'no developer footer');
});

test('skin tone is real (not an empty stub) and the fighter is framed inside the safe UI area', () => {
  const v = src('customization/creation-suite-ui/js/viewer3d.js');
  assert.ok(!/setSkinTone\(hex\)\{ \/\* parametric preview: tint exposed materials \*\/ \}/.test(v), 'setSkinTone is implemented');
  assert.match(v, /setSkinTone\(hex\)\{[\s\S]{0,1600}m\.color\.copy\(c\)/);
  assert.match(v, /setViewOffset\(w, h, w\/2 - cx, h\/2 - cy, w, h\)/, 'projection follows the free screen area');
  assert.match(v, /relaxPose\(\)/, 'a template stands relaxed, not in its T-pose');
  const s = src('customization/creation-suite-ui/js/suite.js');
  assert.match(s, /if\(F\.mode==='blank'\) viewer\.setSkinTone\(F\.body\.skin_tone\);/);
  assert.match(s, /viewer\.setInsets\(/);
  const html = src('customization/creation-suite-ui/index.html');
  assert.match(html, /viewport-fit=cover/, 'page extends under the notch so the CSS safe-area insets apply');
  const css = src('customization/creation-suite-ui/css/suite-t7.css');
  for (const e of ['top', 'bottom', 'left', 'right']) assert.match(css, new RegExp(`env\\(safe-area-inset-${e}`), 'safe-area ' + e);
  assert.match(css, /\(orientation:portrait\)/, 'portrait layout: fighter on top, menus in a bottom sheet');
});

test('MB-Lab template skeletons resolve to the names the body sliders and part sockets use', async () => {
  await import('../tools/anim/node_game_env.mjs');
  const { boneByName, BONE_ALIASES } = await import('../packages/creation-suite/src/body.js');
  for (const t of TEMPLATES) {
    const g = glbJson(t.base_mesh);
    const bones = g.skins[0].joints.map((i) => ({ name: g.nodes[i].name }));
    const sk = { bones };
    for (const n of ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
      'RightArm', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'RightUpLeg']) {
      assert.ok(boneByName(sk, n), `${t.id}: ${n} resolves (aliases ${(BONE_ALIASES[n] || []).join('/')})`);
    }
  }
  // Mixamo rigs are unchanged: exact / mixamorig: names still win
  const mix = { bones: [{ name: 'mixamorig:Hips' }, { name: 'mixamorig:Spine2' }] };
  assert.equal(boneByName(mix, 'Hips').name, 'mixamorig:Hips');
  assert.equal(boneByName(mix, 'Chest').name, 'mixamorig:Spine2');
  const v = src('customization/creation-suite-ui/js/viewer3d.js');
  assert.match(v, /const MBLAB_ALIASES = \{/, 'the viewer maps MB-Lab bones for sockets / framing too');
});

test('EDIT lists WH fighters by their WH names, never the source model folder names', () => {
  const ra = JSON.parse(src('customization/creation-suite-ui/data/roster-attires.json'));
  const SOURCE = ['Armor King', 'Blanka', 'Iori', 'Jin', 'Lili', 'Vega', 'Zafina', 'Zangief', 'Kuma', 'Panda', 'Sakura'];
  for (const f of ra.fighters) {
    assert.ok(f.display_name, `${f.fighter}: has a display name`);
    for (const bad of SOURCE) assert.ok(!new RegExp(`^${bad}$`, 'i').test(f.display_name), `${f.fighter}: shown as "${f.display_name}"`);
  }
  const by = Object.fromEntries(ra.fighters.map((f) => [f.fighter, f]));
  assert.equal(by['armor-king'].display_name, 'YUKIHYŌ');
  assert.equal(by.blanka.display_name, 'CHARGER');
  assert.equal(by.negativo.attires[0].glb, 'roster/negativo/attires/attire1/source/negativo-a1-refit.glb', 'the attire the game loads (the refit), not the old rig');
  const s = src('customization/creation-suite-ui/js/suite.js');
  assert.match(s, /function rosterName\(f\)/);
  assert.ok(!/\$\{esc\(f\.fighter_name\)\}/.test(s), 'roster cards never print the folder name');
});
