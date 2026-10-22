/* Node test: VoiceEngine placeholder behavior (no recordings yet).
   Stubs document; fetch will fail -> manifest null -> subtitle-only path. */
const els = {};
global.document = {
  getElementById: (id) => els[id] || null,
  createElement: (tag) => {
    const el = {
      tag, children: [], _cls: new Set(),
      setAttribute() {},
      appendChild(c) { el.children.push(c); return c; },
      querySelector() { return null; },
      classList: {
        add: (c) => el._cls.add(c),
        remove: (c) => el._cls.delete(c),
        contains: (c) => el._cls.has(c),
      },
      set innerHTML(v) { el.children = []; },
      get innerHTML() { return ''; },
      textContent: '',
      id: '',
    };
    return el;
  },
  head: { appendChild() {} },
  body: { appendChild(el) { els[el.id] = el; } },
};

const { voice } = await import('../js/voice.js');
let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : (fail++, console.log('FAIL:', m)); };

// unlock builds subtitle layer without throwing
voice.unlock();
ok(els['wh-voice-sub'], 'subtitle layer built on unlock');

// play() with no manifest: silent no-op, never throws
voice.play('nofighter', 'win');
await new Promise(r => setTimeout(r, 300));
ok(true, 'play() with no manifest does not throw');

// playLine with no manifest: shows subtitle, waits, resolves
const t0 = Date.now();
await voice.playLine('dorowani', 'intro-01', 'Konnichiwa!');
const dt = Date.now() - t0;
ok(dt >= 1500, `playLine placeholder waits for subtitle read (${dt}ms)`);
const sub = els['wh-voice-sub'];
const lineText = sub.children.map(c => c.textContent).join(' ');
ok(lineText.toLowerCase().includes('konnichiwa'), `subtitle shows line text (got: "${lineText}")`);

// manifest path: inject a fake manifest, clip with no file -> placeholder
voice.manifests.set('dorowani', {
  fighter: 'dorowani',
  clips: [{ id: 'intro-01', trigger: 'intro', file: '', text: 'Konnichiwa!', status: 'placeholder' }],
});
await voice.playLine('dorowani', 'intro-01');
ok(true, 'playLine with placeholder clip resolves');

// debugBleeps default off (never synth fake voice for the user)
ok(voice.debugBleeps === false, 'debugBleeps defaults OFF');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
