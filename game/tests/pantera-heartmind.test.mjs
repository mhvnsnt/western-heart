/* Pantera's HeartMind — his own story and flow, the template every
   character follows (2026-11-08, branch pantera-heartmind).
   - Imports the dependency-free flows module directly (same pattern
     as heartmind-campaign.test.mjs).
   - Text-checks the heartmind.js / brawler.js seams, because the
     controller and brawler run in the browser and cannot be
     imported in Node.
   - Canon-law check (revised Law 1, 2026-11-07 ~22:32; criterion
     is SOURCE not spelling, confirmed ~22:43): "Devil" may appear
     ONLY in our own way, never the Tekken way (Devil Gene, Devil
     Jin, "Jin's devil", "Devil Within"); "Jin" only ever the soul
     JIN. Pantera's story uses neither word at all — the test
     asserts that strictest form for HIS text. The chapter title
     "The Devil That Stays..." is Jay's, unassigned — it is NOT
     in Pantera's story. */
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  PANTERA_FLOW,
  getHeartmindFlow,
  FIGHTER_SOUL,
} from '../js/heartmind-flows.js';

const heartmindSrc = readFileSync(new URL('../js/heartmind.js', import.meta.url), 'utf8');
const brawlerSrc = readFileSync(new URL('../js/brawler.js', import.meta.url), 'utf8');
const rosterSrc = readFileSync(new URL('../js/roster-full.js', import.meta.url), 'utf8');

const SHARED_STAGE_KEYS = ['threshold', 'masks', 'drowning', 'furnace', 'stillpoint'];

/* Extract one object-literal entry from a source text by brace
   counting, starting at the first `{` after `marker`. Pantera's
   entry holds no braces inside its strings, so a plain counter
   is exact here; the assertions below confirm the slice shape. */
function extractEntry(src, marker) {
  const start = src.indexOf(marker);
  assert.ok(start >= 0, `marker not found: ${marker}`);
  const open = src.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') {
      depth--;
      if (depth === 0) return src.slice(open, i + 1);
    }
  }
  throw new Error(`unbalanced braces after ${marker}`);
}

describe('Pantera flow (heartmind-flows.js)', () => {
  it('resolves by fighter id, and only Pantera is individualized', () => {
    assert.equal(getHeartmindFlow('pantera'), PANTERA_FLOW);
    assert.equal(getHeartmindFlow('demonio'), null);
    assert.equal(getHeartmindFlow('nobody'), null);
    assert.equal(PANTERA_FLOW.fighterId, 'pantera');
    assert.equal(PANTERA_FLOW.soul, 'tou');
    assert.equal(FIGHTER_SOUL.pantera, 'tou');
  });

  it('uses the same five inner rooms, in order, with his own subs', () => {
    const keys = PANTERA_FLOW.stages.map((s) => s.key);
    assert.deepEqual(keys, SHARED_STAGE_KEYS);
    for (const s of PANTERA_FLOW.stages) {
      assert.ok(s.name && s.sub, `${s.key} needs a name and a sub`);
      assert.ok(s.diff > 0 && s.diff <= 1, `${s.key} diff in (0, 1]`);
      assert.ok(s.restore >= 0.3 && s.restore <= 0.35, `${s.key} restore in range`);
    }
    assert.equal(PANTERA_FLOW.stages[0].sub, 'The mat is here. I am here.');
    assert.equal(PANTERA_FLOW.stages[4].sub, 'Yourself, unmasked. The watcher, wearing your shape.');
  });

  it('wave tables cover every stage and use only known enemy kinds', () => {
    assert.deepEqual(Object.keys(PANTERA_FLOW.waveTables).sort(), [...SHARED_STAGE_KEYS].sort());
    const kinds = new Set(['brute', 'echo', 'gunner']);
    for (const [key, zones] of Object.entries(PANTERA_FLOW.waveTables)) {
      assert.ok(zones.length >= 2, `${key} needs waves + boss`);
      const last = zones[zones.length - 1];
      assert.ok(last.boss, `${key} ends with a boss zone`);
      for (const z of zones) {
        if (!z.waves) continue;
        for (const wave of z.waves) {
          for (const spec of wave) {
            assert.ok(kinds.has(spec.t), `${key}: unknown kind ${spec.t}`);
            assert.ok(spec.n >= 1, `${key}: wave count >= 1`);
          }
        }
      }
    }
    // Brute-heavy: gunners only at the Furnace, where the trial escalates.
    const gunnerStages = Object.entries(PANTERA_FLOW.waveTables)
      .filter(([, zones]) => JSON.stringify(zones).includes('"gunner"'))
      .map(([k]) => k);
    assert.deepEqual(gunnerStages, ['furnace']);
  });

  it('echo pool is his canon relationships, all real roster ids', () => {
    assert.deepEqual(PANTERA_FLOW.echoIds, ['demonio', 'diablo', 'samura1']);
    for (const id of PANTERA_FLOW.echoIds) {
      assert.ok(rosterSrc.includes(`id: '${id}'`), `${id} is not a roster id`);
    }
  });

  it('corner partner is Demonio, earned after the Masks', () => {
    assert.equal(PANTERA_FLOW.partnerAfter, 'masks');
    assert.equal(PANTERA_FLOW.partnerId, 'demonio');
  });

  it('DW donors use the index real filenames, with measured frames', () => {
    const { dwDonors } = PANTERA_FLOW;
    for (const t of dwDonors.surgeThrows) {
      assert.match(t.file, /^gym_ikdv_.*_nage_[fy]\.dat$/, `bad throw filename ${t.file}`);
      assert.ok(t.frames > 0 && t.bones === 35, `${t.file} needs measured frames/bones`);
    }
    assert.equal(dwDonors.surgeThrows.length, 6);
    assert.equal(dwDonors.surgeTransform.length, 4);
    assert.equal(dwDonors.surgeTrigger.file, 'gym_dwup00.dat');
    assert.equal(dwDonors.surgeBeam.file, 'gym_dwhadoh00.dat');
    assert.equal(dwDonors.wardenKit.group, 'kmb1');
    assert.equal(dwDonors.wardenKit.files, 39);
    // The sphere needs no body — boss4 does not exist, by design.
    assert.equal(dwDonors.bossBodies.sphere, null);
    assert.ok(dwDonors.bossBodies.warden && dwDonors.bossBodies.shadow);
    // Stage map objects are geometry; per-room mapping is UNMEASURED.
    assert.equal(dwDonors.stageMaps.length, 4);
    assert.ok(!dwDonors.stageMaps.some((m) => m.file === 'moj_stg03.dat'));
  });

  it('flow data carries no Devil Within-way wording', () => {
    const data = JSON.stringify(PANTERA_FLOW);
    assert.doesNotMatch(data, /devil/i, 'no Devil in Pantera flow data');
    assert.doesNotMatch(data, /\bjin\b/i, 'no Jin in Pantera flow data');
    assert.doesNotMatch(data, /\bking\b|\bpaul\b|\bheihachi\b|\bbryan\b|\bgun jack\b/i,
      'no source-character names in Pantera flow data');
  });
});

describe('Pantera seams (heartmind.js / brawler.js)', () => {
  it('heartmind.js imports the flows module and the soul map', () => {
    assert.ok(heartmindSrc.includes("from './heartmind-flows.js'"));
    assert.ok(heartmindSrc.includes('getHeartmindFlow(fighterId)'));
    assert.ok(heartmindSrc.includes('FIGHTER_SOUL[char.id]'));
  });

  it('Pantera has his own story entry, distinct from the soul story', () => {
    const stories = heartmindSrc.slice(heartmindSrc.indexOf('HEARTMIND_STORIES'));
    const pantera = extractEntry(stories, 'pantera: {');
    assert.ok(pantera.includes('DESCENT OF THE HOLD'));
    assert.ok(pantera.includes('bossIntros'));
    assert.ok(pantera.includes('partnerBeat'));
    assert.ok(pantera.includes('SHADOW OF PANTERA'));
    assert.ok(pantera.includes('The mat is here. I am here.'));
    // The soul's nineStory('tou') still exists, keyed by soul id —
    // Pantera's own entry is what the fighter id resolves to.
    assert.ok(heartmindSrc.includes("tou: nineStory('tou')"));
  });

  it('Pantera story text uses no banned word at all', () => {
    const stories = heartmindSrc.slice(heartmindSrc.indexOf('HEARTMIND_STORIES'));
    const pantera = extractEntry(stories, 'pantera: {');
    assert.doesNotMatch(pantera, /devil/i, 'no Devil in Pantera story');
    assert.doesNotMatch(pantera, /\bjin\b/i, 'no Jin in Pantera story');
    assert.doesNotMatch(pantera, /\bking\b|\bpaul\b|\bheihachi\b|\bbryan\b|\bgun jack\b/i,
      'no source-character names in Pantera story');
    assert.doesNotMatch(pantera, /\bogre\b/i, 'no bare Ogre in Pantera story');
    assert.doesNotMatch(pantera, /The Devil That Stays/i,
      'the unassigned chapter title is NOT in Pantera\'s story');
  });

  it('controller uses the flow stages and plays boss intros + partner beat', () => {
    assert.ok(heartmindSrc.includes('const stages = flow ? flow.stages : HEARTMIND_STAGES'));
    assert.ok(heartmindSrc.includes('echoIds: flow ? flow.echoIds : null'));
    assert.ok(heartmindSrc.includes('waveTables: flow ? flow.waveTables : null'));
    assert.ok(heartmindSrc.includes('story.bossIntros[stages[stageIdx].key]'));
    assert.ok(heartmindSrc.includes('flow.partnerAfter === st.key'));
    assert.ok(heartmindSrc.includes('story.partnerBeat'));
  });

  it('brawler honors the flow echo pool and wave tables', () => {
    assert.ok(brawlerSrc.includes('this.content.echoIds'));
    assert.ok(brawlerSrc.includes('this.content.waveTables'));
    assert.ok(brawlerSrc.includes('this.content.waveTables[st.key]'));
  });
});
