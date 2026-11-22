/* creation-suite-face-textures.test.mjs — Node test for the Creation Suite
   FACE live swap (gap (a) follow-up to PR #1057).
   Run: node test/creation-suite-face-textures.test.mjs (no dependencies).
   Pins: the face-texture map covers all 146 PNGs in
   `customization/parts/no-mercy/faces/` (98 male + 20 female + 28 extras),
   every wwe-layer preset in face-presets.json resolves to exactly one
   PNG by its preset number, and every gnm-layer preset resolves to null
   (expression bake only — no texture to swap). Preset fixtures below
   mirror `customization/templates/face-presets.json` (12 presets). */
import assert from 'node:assert';
import { FACE_TEXTURES_MALE, FACE_TEXTURES_FEMALE, FACE_TEXTURES_EXTRA,
         faceTextureForPreset, faceTextureCount } from '../packages/creation-suite/src/face-texture-map.js';

const PRESETS = [
  { id: 'wwe-face-m01', layer: 'wwe', gender: 'male', no_mercy_face: 1 },
  { id: 'wwe-face-m14', layer: 'wwe', gender: 'male', no_mercy_face: 14 },
  { id: 'wwe-face-m23', layer: 'wwe', gender: 'male', no_mercy_face: 23 },
  { id: 'wwe-face-m37', layer: 'wwe', gender: 'male', no_mercy_face: 37 },
  { id: 'wwe-face-m52', layer: 'wwe', gender: 'male', no_mercy_face: 52 },
  { id: 'wwe-face-f03', layer: 'wwe', gender: 'female', no_mercy_face: 3 },
  { id: 'wwe-face-f09', layer: 'wwe', gender: 'female', no_mercy_face: 9 },
  { id: 'wwe-face-f14', layer: 'wwe', gender: 'female', no_mercy_face: 14 },
  { id: 'gnm-determined', layer: 'gnm', gnm_preset: 'determined_focused' },
  { id: 'gnm-angry', layer: 'gnm', gnm_preset: 'angry_scowling' },
  { id: 'gnm-happy', layer: 'gnm', gnm_preset: 'happy' },
  { id: 'gnm-smug', layer: 'gnm', gnm_preset: 'smug' },
];

let n = 0;
const ok = (name, cond) => { n++; assert.ok(cond, name); console.log('ok -', name); };

ok('male table: 98 files, numbered 01..98 with no gaps', FACE_TEXTURES_MALE.length === 98 &&
  FACE_TEXTURES_MALE.every((f, i) => f.startsWith(`Face_Male_${String(i + 1).padStart(2, '0')}_`) && f.endsWith('.png')));
ok('female table: 20 files, numbered 01..20 with no gaps', FACE_TEXTURES_FEMALE.length === 20 &&
  FACE_TEXTURES_FEMALE.every((f, i) => f.startsWith(`Face_Female_${String(i + 1).padStart(2, '0')}_`) && f.endsWith('.png')));
ok('extras table: 28 unnumbered files', FACE_TEXTURES_EXTRA.length === 28 &&
  FACE_TEXTURES_EXTRA.every(f => f.startsWith('Face_') && f.endsWith('.png')));
ok('total coverage: 146 PNGs, all filenames unique',
  faceTextureCount() === 146 &&
  new Set([...FACE_TEXTURES_MALE, ...FACE_TEXTURES_FEMALE, ...FACE_TEXTURES_EXTRA]).size === 146);
for (const p of PRESETS.filter(p => p.layer === 'wwe')) {
  const f = faceTextureForPreset(p);
  const want = p.gender === 'male'
    ? `Face_Male_${String(p.no_mercy_face).padStart(2, '0')}_`
    : `Face_Female_${String(p.no_mercy_face).padStart(2, '0')}_`;
  ok(`preset ${p.id} (number ${p.no_mercy_face}) resolves live`, typeof f === 'string' && f.startsWith(want) && f.endsWith('.png'));
}
for (const p of PRESETS.filter(p => p.layer === 'gnm')) {
  ok(`preset ${p.id} (gnm) has no live texture (bake only)`, faceTextureForPreset(p) === null);
}
ok('unknown preset / bad number resolves null, never crashes',
  faceTextureForPreset(null) === null &&
  faceTextureForPreset({ layer: 'wwe', gender: 'male', no_mercy_face: 99 }) === null &&
  faceTextureForPreset({ layer: 'wwe', gender: 'male', no_mercy_face: 0 }) === null &&
  faceTextureForPreset({ layer: 'wwe', gender: 'any', no_mercy_face: 1 }) === null);
console.log(`\n${n} checks passed.`);
