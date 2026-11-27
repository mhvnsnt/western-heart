/* ============================================================
   WESTERN HEART — God Within mode (game/js/godwithin.js)
   Branch: godwithin/wiring-20261126 (owner order 2026-11-26:
   "Get it fully into the repo and wired up into God within mode
   how it should be and built with our characters and environments
   and Canon.")

   WHAT THIS IS: the God Within mode — the Devil Within / Urban
   Reign / Def Jam / Sato transmigration stack, reskinned into WH
   canon, wired onto the STORY Trial spine that already ships in
   game/js/modes.js. Pure logic, no DOM, no imports: safe to import
   in node (test/godwithin.test.mjs) and in the browser (modes.js
   imports it statically; the Dream and Banabana layers are dynamic
   imports in modes.js so a missing layer degrades, never breaks).

   THE LOOP (menu → mode → stage → fight → death → dream/voyage →
   face-pick → next life):
     1. Main menu → GOD WITHIN card (mainmenu.js, story submenu).
     2. Pick any GLB-backed roster fighter (83 of 85; byou + ryuji
        have no GLB and are never offered — see GODWITHIN_UNPLAYABLE).
     3. Seven rungs (GODWITHIN_RUNGS): five Devil Within chapters
        (Helix Palace → Central Mountain → Octagonal Shrine → Palace
        of Dreaming → Trial summit), the Trader's rung, the final
        Shrine vs the Assembled Soul.
     4. Each chapter rung fights its anchor guardians in order
        (12 anchors, 3+2+2+2+3), then the chapter boss (DW boss
        behaviour on a WH body). Win a guardian: shards + stay on
        the rung. Win the boss: claim the rung's force + advance.
     5. Death: ONE dream night (LSD dream-system, startDay()),
        then the Banabana voyage (Roly-Polys hub), then the RNF
        face-pick (assemble eyes/nose/mouth — Art score decides the
        face), then reincarnation from the FULL 83-vessel pool.
     6. Clear the final Shrine: the soul is nearly whole; the Sky
        (Planetokio layer) opens — gated until its discs land
        in-repo (see GODWITHIN_SKY + gaps).

   PROVENANCE — pulled-from-source vs WH-original, per row, is
   marked on every table below. Licence/source log (honest):
     • Devil Within 5-stage design, combat table, bosses, gems and
       economy: spec pulled whole from mhvnsnt/game-reverse-engineering
       tekken5/TEARDOWN-DEVIL-WITHIN.md + GameFAQs CJ800 v2.30a;
       stage files verified on disk (325 files / 234 MB);
       recomp pipeline verified playing headless (t5-headless
       sha256 978c782d…, 6 playtests, unknown 0). Upstream
       devilwithin-coop itself is still WIP — the pipeline run is
       the verified piece, not an upstream release.
     • Urban Reign recomp v1.4.1: thiagordsfx/urban-reign-recomp,
       GPL-3.0, snapshot on harvest/brawlers @fe4eed4.
     • Def Jam Vendetta recomp v0.7.3: jcsix694, GPL-3.0.
       Def Jam: Fight for NY recomp v1.2.0-beta: vyanhursky, MIT
       (stable v1.2.0 GA landed upstream Nov 20 — refresh owed).
       Def Jam modding tools: MIT. All on harvest/brawlers.
     • Urban Reign Redux v0.5: Jasonafex, NO licence declared;
       release urban-reign-redux-20261120, whole sha ad222bad…
       (24-part streaming-verify PASS).
     • LSD dream core: klnuno/lsd-decomp (MATCHING decomp,
       1,447/1,447 functions) as truth; TheShovel/lsd-dream-emu-ds
       JS port (no licence declared; upstream Revamped MIT).
       WH data is WH-authored. Shipped as game/js/dream-system.js.
     • Roly-Polys World Tour disc catalog: Sato slice built WH-native
       (game/js/rolypolys-hub.js + game/data/rolypolys-world.js,
       ported from the phase2 slice — WH characters only).
     • RNF mechanic: RHYTHM-N-FACE-MECHANIC.md spec. The RNF manual
       PDF is MISSING (lane-3 upload died 2026-11-20) — faces 10–12
       and the exact face triples are PROVISIONAL, flagged, never
       presented as the manual's.
     • Def Jam Icon: EXCLUDED — no decomp/recomp exists anywhere;
       owner call (gap G6). Nothing of Icon's is mapped in.
   No Sato / Def Jam / Urban Reign character or place is cloned.
   Every playable is a WH character; every world is a WH reskin.

   VERIFICATION (this lane, 2026-11-26, live):
   WH main @ d65c53a9. NO `roster/` GLB directory exists in the WH
   git tree (0 paths) — roster GLBs live on the private B2 bucket
   via the Cloudflare Worker remote base (game/js/asset-config.js,
   owner 2026-10-31 no-card route); `assets/models/*.glb` ARE
   in-tree blobs. Featured-fighter GLBs were HEAD-checked live
   against the Worker (2026-11-26) AND cross-checked against the
   R2 upload manifest (tools/deploy/r2-upload-manifest.json,
   2,242 models) and the git tree at d65c53a9:
   - R2-200 + in-manifest: demonio-a1, phantom, sakura, zen,
     pantera-leoman, skull, sam-ur-a1, diablo, demonio-winged,
     demonio-human, gyou-spirit (alt), parvati non-cdn (see below).
   - In-tree blob + jsDelivr-200 (R2 404, not in manifest — these
     load from the Pages shell / jsDelivr, not the bucket):
     tou-soul-tex (1,616,136 B), kai-soul-tex (1,834,764 B).
   - In-tree blob + in-manifest (base keys): nightwolf.glb,
     dxmmii.glb, retsu-body.glb, kiko-tanaka.glb (RAVE).
   - GYOU's roster key (gyou-attire1) 404s on R2 and is NOT in the
     manifest — his jsDelivr 200 is a STALE cache (the file is not
     in the tree at d65c53a9) and is NOT trusted. GYOU plays via
     his spirit-form alt (gyou-spirit, R2-200 + in-manifest).
   - NIGHTWOLF / DXMMII roster attire keys 404 on R2 (not in
     manifest); both play via their in-tree base keys.
   - MEGAMI's MODEL_URLS key ends '-cdn' but the file on R2 is the
     non-cdn name (roster/parvati/attires/attire1/model-rigged.glb,
     R2-200 + in-manifest) — the '-cdn' suffix looks stale; flagged
     as gap GW-19, not silently re-pointed.
   ============================================================ */

export const GODWITHIN_MODE = {
  key: 'godwithin',
  name: 'GOD WITHIN',
  origin: 'wh',
  canon: 'CANON.md §5 The Trial + §1 The Two Laws of Death',
  desc: 'The Trial, descended. Five Devil Within chapters, twelve anchor guardians, dreams between lives, voyages between deaths, and a face to be assembled. Death is not failure — it is reincarnation.',
};

/* ---------------- 12 anchors → guardian rooms ----------------
   Anchor pairs kept EXACTLY as specified (INTEGRATION-DESIGN §1.7).
   guardianId is always a roster id with a verified GLB — except
   PRAYER, whose guardian BYOU has no model: the room is guarded by
   RAVE, Byou's replacement vessel (in-tree kiko-tanaka.glb),
   flagged standIn until a BYOU GLB lands. SHA is not a fighter;
   SAKU RA is her vessel (TAJI room). JIN has no standalone id;
   PHANTOM carries his blade (NASKA room + DW4 boss body). */
export const GODWITHIN_ANCHORS = [
  { anchor: 'PYRAMSTP', chapter: 1, hostStageId: 'helix-palace', guardianId: 'tou',     guardian: 'TOU',     note: 'The climb through the machine halls.' },
  { anchor: 'TAJI',     chapter: 1, hostStageId: 'helix-palace', guardianId: 'sakura',  guardian: 'SAKU RA', note: 'SHA’s vessel — the tomb-room, the lab’s dead heart.' },
  { anchor: 'STPAUL',   chapter: 1, hostStageId: 'helix-palace', guardianId: 'skull',   guardian: 'SKULL',   note: 'Judgement hall for the lab’s experiments.' },
  { anchor: 'PYRAMID',  chapter: 2, hostStageId: 'octagonal-shrine', guardianId: 'retsu', guardian: 'RETSU', note: 'The dead king entombed beneath the mountain.' },
  { anchor: 'SHRINE',   chapter: 2, hostStageId: 'octagonal-shrine', guardianId: 'zen',   guardian: 'ZEN',   note: 'Stillness at the mountain’s heart.' },
  { anchor: 'GODDESS',  chapter: 3, hostStageId: 'octagonal-shrine', guardianId: 'sakura', guardian: 'SAKU RA', note: 'The idol over the ruins.' },
  { anchor: 'PRAYER',   chapter: 3, hostStageId: 'octagonal-shrine', guardianId: 'rave',  guardian: 'RAVE',  note: 'STAND-IN: BYOU has no GLB — RAVE guards the prayer room as Byou’s replacement vessel until a BYOU model lands.', standIn: 'byou' },
  { anchor: 'NASKA',    chapter: 4, hostStageId: 'palace-of-dreaming', guardianId: 'phantom', guardian: 'PHANTOM', note: 'The lines are only read from above — the dream-ship reads them.' },
  { anchor: 'TENG',     chapter: 4, hostStageId: 'palace-of-dreaming', guardianId: 'gyou', guardian: 'GYOU', note: 'Tengu mountain — the sky heights.' },
  { anchor: 'DEVIL',    chapter: 5, hostStageId: 'tong-nou', guardianId: 'demonio', guardian: 'DEMONIO', note: 'The Demon Soul — the devil is the final gate.' },
  { anchor: 'BIGHEAD',  chapter: 5, hostStageId: 'tong-nou', guardianId: 'diablo',  guardian: 'DIABLO',  note: 'The stone head that watches the final arena.' },
  { anchor: 'PYRAMSUN', chapter: 5, hostStageId: 'tong-nou', guardianId: 'pantera', guardian: 'PANTERA', note: 'The panther in the sun — the final arena under the sun.' },
];

/* ---------------- 5 Devil Within chapters → WH stages ----------------
   DW stage dirs are the on-disk truth (verify/extracted/tk5data2/area/):
   lab_A, lab_B, egy_A, blu_A, blu_B. DW bosses are RESKINNED, never
   cloned: the boss FIGHT is the anchor guardian's fight (WH character,
   WH moveset); the DW boss's BEHAVIOUR is the pulled-from-source part.
   dwDir 'lab_A' has no boss.txt on disk (boss1 lives in chr/) and
   'blu_A' has none at all — boss identities below follow the DW design
   spec / GameFAQs, not the file list alone (Lane C gaps G1–G2). */
export const GODWITHIN_CHAPTERS = [
  {
    n: 1, dwStage: 'lab_A', dwName: 'G Corporation Lab (Medicern)',
    whStageId: 'helix-palace', whStage: 'HELIX PALACE', element: 'Metal',
    dwContent: 'G Corp soldiers, JACK units; boss Modified Gun Jack (ranged projectile keeper, grabs up close).',
    boss: { id: 'samura1', name: 'SAM-UR-A1', dwBoss: 'Modified Gun Jack', behaviour: 'Ranged projectile keeper; grabs up close. JACK units → Helix Palace automaton mobs (WH-original shells on the JACK AI). G Corp soldiers → Palace guards.', provenance: 'pulled-behaviour / WH-original-body' },
    anchors: ['PYRAMSTP', 'TAJI', 'STPAUL'],
  },
  {
    n: 2, dwStage: 'lab_B', dwName: 'Deeper Lab',
    whStageId: 'octagonal-shrine', whStage: 'CENTRAL MOUNTAIN', element: 'Earth',
    dwContent: 'JACK-5, super-soldiers; boss Clone-Heihachi ×1 then ×3 simultaneously (real Heihachi moveset, clones coordinate).',
    boss: { id: 'gyou', name: 'GYOU ×3', dwBoss: 'Clone-Heihachi ×3', behaviour: 'Three GYOU — the Moving Soul, tripled. The coordination AI is the pull; the tripled body is WH-original. Child-bedroom room → a Mountain shrine room.', provenance: 'pulled-behaviour / WH-original-body' },
    anchors: ['PYRAMID', 'SHRINE'],
  },
  {
    n: 3, dwStage: 'egy_A', dwName: 'Ancient Ruins beneath the lab',
    whStageId: 'octagonal-shrine', whStage: 'OCTAGONAL SHRINE', element: 'Earth',
    dwContent: 'Ogre’s mutants; boss True Ogre (no snake arm; fire breath, flight, teleportation, T3/TTT attacks).',
    boss: { id: 'diablo', name: 'DIABLO', dwBoss: 'True Ogre', behaviour: 'Fire breath + flight + teleport kept as the boss kit, WH-original body. Mutants → shrine-corrupted mobs.', provenance: 'pulled-behaviour / WH-original-body' },
    anchors: ['GODDESS', 'PRAYER'],
  },
  {
    n: 4, dwStage: 'blu_A', dwName: 'Mystical location / alien ship',
    whStageId: 'palace-of-dreaming', whStage: 'PALACE OF DREAMING', element: 'Water',
    dwContent: 'Alien monsters (punch/kick fighters); boss Soul Sphere (floating energy ball, contact damage, spawns monsters, stays airborne, repositions).',
    boss: { id: 'phantom', name: 'PHANTOM', dwBoss: 'Soul Sphere', behaviour: 'The Ghost Blade as the floating sphere-host; spawn-and-reposition kit kept, WH-original body. Alien monsters → dream-aliens (Planetokio Collect-Virus possessed forms).', provenance: 'pulled-behaviour / WH-original-body' },
    anchors: ['NASKA', 'TENG'],
  },
  {
    n: 5, dwStage: 'blu_B', dwName: 'Final arena (same mystical zone)',
    whStageId: 'tong-nou', whStage: 'THE TRIAL / FINAL SHRINE', element: 'Void',
    dwContent: 'Boss: True Ogre → transforms to Monstrous Ogre (whirlwinds, stomps, sweeps; BOTH forms share ONE health bar).',
    boss: { id: 'demonio', name: 'DEMONIO', dwBoss: 'True → Monstrous Ogre', behaviour: 'Unwinged demon form → winged Devil form on full meter; the shared-health-bar transform is the pull — matches WH canon (default unwinged demon, winged Devil only on transform with a full meter). Final guardian sequence: PANTERA → DIABLO → DEMONIO.', provenance: 'pulled-behaviour / WH-original-body' },
    anchors: ['DEVIL', 'BIGHEAD', 'PYRAMSUN'],
  },
];

/* ---------------- The 7 rungs ----------------
   God Within runs the Trial ladder (STORY_STAGES in modes.js, reused
   verbatim for rung order, forces and difficulty): rungs 1–5 are the
   five DW chapters in DW order, rung 6 is the Trader, rung 7 is the
   final Shrine vs the Assembled Soul. Forces follow the TRIAL rung
   (wood → fire → earth → metal → water) — the chapter's element is
   its home, not its reward. pool is the rung's STORY_STAGES pool,
   used for the Trader toll fight and as fallback foes. */
export const GODWITHIN_RUNGS = [
  { rung: 1, chapter: 1, title: 'CHAPTER 1 — HELIX PALACE', sub: 'The machine palace. The lab IS a Metal-land facility.', forceKey: 'wood', diff: 0.55, pool: ['pantera', 'demonio', 'skull', 'zui', 'sakura', 'michiko'] },
  { rung: 2, chapter: 2, title: 'CHAPTER 2 — CENTRAL MOUNTAIN', sub: 'The lab is built on the mountain’s root.', forceKey: 'fire', diff: 0.62, pool: ['tou', 'retsu', 'bruno', 'thor', 'kingtyrant', 'slice'] },
  { rung: 3, chapter: 3, title: 'CHAPTER 3 — OCTAGONAL SHRINE', sub: 'The ruins ARE the shrine’s undercroft.', forceKey: 'earth', diff: 0.68, pool: ['zen', 'demonio', 'yukihyo', 'docfrank', 'purplerain'] },
  { rung: 4, chapter: 4, title: 'CHAPTER 4 — PALACE OF DREAMING', sub: 'The “alien ship” is a dream-vessel on the Threshold’s Sea.', forceKey: 'metal', diff: 0.74, pool: ['samura1', 'cyborgx', 'burger', 'scimitar', 'negativo'] },
  { rung: 5, chapter: 5, title: 'CHAPTER 5 — THE FINAL SHRINE', sub: 'The Trial ladder’s top; the final gate before the Octagonal Shrine Par-fang.', forceKey: 'water', diff: 0.80, pool: ['phantom', 'dio', 'nightwolf', 'star', 'awapop', 'kinpo'] },
  { rung: 6, chapter: null, title: 'THE TRADER — PHANTOM MARKETPLACE', sub: 'The Trader buys and sells elemental forces. All transactions are final.', forceKey: null, diff: 0.85, trader: true, pool: ['scimitar', 'burger', 'awapop', 'slice'] },
  { rung: 7, chapter: null, title: 'FINAL — THE SHRINE', sub: 'The Assembled Soul waits. It is you, assembled.', forceKey: null, diff: 0.95, boss: true, pool: [] },
];

export function godwithinChapterForRung(rungIndex) {
  const rung = GODWITHIN_RUNGS[rungIndex];
  if (!rung || !rung.chapter) return null;
  return GODWITHIN_CHAPTERS[rung.chapter - 1] || null;
}

export function godwithinAnchorsForChapter(chapterN) {
  return GODWITHIN_ANCHORS.filter((a) => a.chapter === chapterN);
}

/* ---------------- Combat layer ----------------
   DW base kit: the WH fight engine already carries these inputs —
   the kit is the mode's contract, not a second engine. The brawler
   (game/js/brawler.js, "Heart and Mind Within") stays the free-roam
   companion: God Within fights are Trial fights with the DW kit,
   surge and shard rules applied; the brawler is offered from the
   God Within clear screen as "DESCEND" (same soul, free-roam). */
export const GODWITHIN_COMBAT = {
  dwBaseKit: {
    source: 'TEARDOWN-DEVIL-WITHIN.md §1.3 input table (pulled-from-source)',
    inputs: ['Punch', 'Kick', 'Block', 'Jump', 'Throw', 'punch-punch-kick string', 'launcher', 'uppercut', 'L1 5-hit combo', 'jump kicks', 'forward roll', 'back flip'],
    note: 'Every playable WH character gets this kit, skinned to their own moveset.',
  },
  surge: {
    source: 'Devil Gauge → L1+Triangle Devil Jin transform (pulled); WH Soul Surge (CANON.md §4)',
    rule: 'Gauge fills as you fight / take damage. Full gauge = transform. DEMONIO: unwinged → winged Devil. Every other playable: 10-second Soul Surge.',
  },
  shards: {
    source: 'DW blue gems (health) / red gems (Devil Gauge) (pulled)',
    rule: 'Blue Soul Shards heal; red Soul Shards charge Surge. Same pickups, WH economy — one wallet (WHIdentity) shared across God Within, Dream, Banabana and the Trader.',
  },
  pointsRank: {
    source: 'DW points per kill / combo / clear; Rank S conditions (pulled)',
    rule: 'Points → Soul Shards; Rank S (50-hit combo, fast clear, minimal damage, no hits in boss fight, max KOs) → shard multiplier.',
  },
  camera: {
    source: 'DW third-person follow (pulled)',
    rule: 'Auto-frames player + nearest enemies, pulls back in arenas. WH-original implementation.',
  },
  blockingDoor: {
    source: 'Redux 0.5 known issue — "the first door doesn’t block you while enemies are still alive" (pulled bug report as spec)',
    rule: 'WH RULE (WH-original fix): the door DOES block until the room is cleared. The Redux bug is the anti-spec and the regression test.',
  },
  urbanReign: [
    { system: 'Street brawling — multi-enemy crowd fights, 100 missions, 9 mission archetypes', whForm: 'God Within street-brawl mode: crowd fights at Phantom Marketplace (market brawls) and Plains of Chi-U (street pits). Missions become WH Trial side-missions; the 9 archetypes become WH mission types (WH-original naming, pulled structure).', status: 'data' },
    { system: 'Up to 8 players / CoopTool / multiplayer', whForm: 'God Within co-op up to 8 in arena brawls. DW campaign co-op follows the devilwithin-coop 2-player split-screen pattern ONLY if that source verifies — currently UNVERIFIED (gap G4): DW chapters ship single-player until then.', status: 'data-gated' },
    { system: 'Redux Tekken guests (Jin, Kazuya, King, Nina, Yoshimitsu, Reina, Bob, …)', whForm: 'NOT carried as guests. Guest slots become WH roster slots: Yoshimitsu’s slot → JIN and PHANTOM; Jin’s slot → RIN. No Tekken character appears.', status: 'data' },
    { system: 'Redux grounded idles / skeleton repairs / moveset + sound fixes', whForm: 'Applied to WH models as rig fixes (grounded idles = feet planted, arms at sides — the Cape Jones idle law, same discipline). The fix list is pulled, the application is WH-original.', status: 'data' },
    { system: 'Redux HD texture packs', whForm: 'WH texture pass: Eastern Mind bitmap palettes (“Colour Is Law”, CANON §8) on WH models. HD packs are reference only, never shipped as Tekken textures.', status: 'data' },
    { system: 'Redux story stages opened to multiplayer', whForm: 'DW chapters + UR mission stages open to WH multiplayer (arena + co-op).', status: 'data' },
    { system: 'Redux Mod Manager pack system (1.18 GB manager, pack-based mods)', whForm: 'WH Mod Pack system (WH-original): packs = WH stage packs / fighter packs / texture packs, managed in the WH hub. The Manager’s pack structure is the pulled template; the packs are WH content.', status: 'data' },
    { system: 'Redux Editor (54 MB creator editor)', whForm: 'WH Stage/Fighter Editor (WH-original): place fighters, stages, movesets, WH-native. The Redux Editor is the reference implementation.', status: 'data' },
    { system: 'UR stage PPKs (7 stage PPKs, ~100 mission PPKs, DVD000.AFS 2,431 files)', whForm: 'WH stage library: the 5 DW chapters + Marketplace + Plains pits + Palace stages; mission PPK structure → WH mission definitions.', status: 'data' },
    { system: 'Redux DW stage-1 door bug', whForm: 'See blockingDoor above — the bug is the regression test.', status: 'data' },
  ],
  defJam: [
    { system: 'Vendetta grapple system (AKI wrestling engine: grapple → hold/throw chain, limb targeting)', whForm: 'WH grapple layer: grapple opens a throw/hold chain on any WH fighter; the chain is the pulled mechanic, the holds are each fighter’s own moveset.', feeds: ['tou', 'pantera', 'retsu'], status: 'data' },
    { system: 'Vendetta crowd interaction (crowd as weapon / ring-out pressure, up to 4 players)', whForm: 'WH crowd layer: Marketplace / Plains crowds react, shove, and can be used — the crowd is a stage hazard, not a fighter.', feeds: ['all street-brawl playables'], status: 'data' },
    { system: 'FFNY 5 fighting styles — Streetfighting, Kickboxing, Martial Arts, Submission, Wrestling (pick 3 per fighter)', whForm: 'WH 5 style schools (WH-original names, pulled structure): each WH fighter holds styles from their canon base.', feeds: ['tou', 'retsu', 'phantom', 'gyou', 'rave', 'kai', 'zen', 'sakura', 'rin'], status: 'data' },
    { system: 'FFNY weapons (environmental weapons in venues)', whForm: 'WH stage weapons: Marketplace stalls / Plains debris / Palace props become pick-up weapons. Weapon set is WH-original — no Def Jam branded weapons.', feeds: ['tou', 'retsu', 'pantera'], status: 'data' },
    { system: 'FFNY Create-a-Fighter (142 fighters, 7,948 CAW files, fitting room in modding tools)', whForm: 'WH custom-character system: the CAW STRUCTURE (parts, fitting room) is the pull; every part is a WH part. No Def Jam character is creatable. (WH converted Def Jam parts catalog 1,201 entries NOT re-verified — gap G5.)', feeds: ['all playables'], status: 'data-gated' },
    { system: 'FFNY venues (48 venues, VENUE.XML)', whForm: 'WH venue set: the 48-venue STRUCTURE (crowd density, weapon spawns, ring shape) maps onto WH stages — Marketplace, Plains pits, Helix rooms, Palace of Dreaming. No Def Jam venue is reproduced.', feeds: ['stage team'], status: 'data' },
    { system: 'Vendetta mod kit + Blender plugin / FFNY modding tools', whForm: 'WH modding path: the tooling pattern (Blender plugin + fitting room) is the template for WH’s own fighter/stage tooling.', feeds: ['build lane'], status: 'data' },
    { system: 'Def Jam Icon', whForm: 'EXCLUDED — no decomp/recomp/fan port/modding tool exists anywhere (searched 2026-11-20). Only route: RPCS3 + own disc. OWNER CALL (gap G6) — not mapped in.', feeds: [], status: 'excluded-owner-call' },
  ],
  /* FFNY pick-3 structure is the pull; school names/moves are WH canon. */
  styleSchools: {
    tou: ['Streetfighting', 'Kickboxing'],
    retsu: ['Kickboxing', 'Martial Arts'],
    phantom: ['Martial Arts', 'Submission'],
    gyou: ['Martial Arts', 'Streetfighting'],
    rave: ['Submission', 'Martial Arts'],
    kai: ['Wrestling', 'Streetfighting'],
    zen: ['Submission', 'Martial Arts'],
    sakura: ['Martial Arts', 'Submission'],
    rin: ['Streetfighting', 'Martial Arts'],
  },
};

/* ---------------- RNF face-pick ----------------
   Spec: RHYTHM-N-FACE-MECHANIC.md §2.3 — Art ≥ 40 unlocks a face
   as a reincarnation option; Art 50 = TRUE face (mission briefing
   + shard bonus); Art 30 = wearable copy, no briefing; below 30 =
   not offered. The face-pick IS the RNF ritual: at every death the
   player assembles eyes / nose / mouth from the EM_FACE pieces and
   the assembly is scored against the vessel's TRUE face.
   TRUE-FACE TRIPLES: WH-authored index triples (eyes/nose/mouth
   into EM_FACE) — the RNF manual PDF that would confirm the
   intended faces is MISSING (gap G7), so the triples are flagged
   provisional and the mechanic (thresholds + scoring) is the
   spec-faithful part. Faces 10–12 are proposals only, NOT offered. */
export const GODWITHIN_RNF = {
  thresholds: { trueFace: 50, offered: 40, copy: 30 },
  faces: [
    { n: 1, vessel: 'rin',     name: 'RIN — the Protagonist',   trueFace: [0, 0, 0] },
    { n: 2, vessel: 'tou',     name: 'TOU — the Fighting Soul', trueFace: [1, 0, 1] },
    { n: 3, vessel: 'phantom', name: 'JIN — the Blade Soul',    trueFace: [2, 1, 0] },
    { n: 4, vessel: 'sakura',  name: 'SHA — the Sand Soul',     trueFace: [0, 1, 2] },
    { n: 5, vessel: 'gyou',    name: 'GYOU — the Moving Soul',  trueFace: [1, 2, 1] },
    { n: 6, vessel: 'zen',     name: 'ZEN — the Still Soul',    trueFace: [2, 0, 2] },
    { n: 7, vessel: 'rave',    name: 'BYOU — the Sick Soul',    trueFace: [0, 2, 0], note: 'Face 7 belongs to BYOU; RAVE wears it until a BYOU GLB lands.' },
    { n: 8, vessel: 'retsu',   name: 'RETSU — the Violent Soul', trueFace: [1, 1, 1] },
    { n: 9, vessel: 'kai',     name: 'KAI — the Sea Soul',      trueFace: [2, 2, 2] },
  ],
  provisionalFaces: [
    { n: 10, vessel: 'diablo', name: 'DIABLO — the intruder', note: 'Proposal only. Gated on deaths ≥ 3 AND the RNF manual PDF landing.' },
    { n: 11, vessel: 'assembled-soul', name: 'ASSEMBLED SOUL', note: 'Proposal only — composite of all nine styles; NOT a playable until the owner calls it.' },
    { n: 12, vessel: 'trader', name: 'THE TRADER’S MASK', note: 'Proposal only. The Trader is not a roster fighter.' },
  ],
  triplesProvisional: true,
  routeFinals: [
    { route: 'Water', stage: '#036', hostStageId: 'palace-of-dreaming', dancer: 'sakura' },
    { route: 'Steel', stage: '#036', hostStageId: 'helix-palace', dancer: 'pantera' },
    { route: 'Universe', stage: '#036', hostStageId: 'octagonal-shrine', dancer: 'diablo' },
    { route: 'Voice', stage: '#036', hostStageId: 'phantom-marketplace', dancer: 'skull' },
  ],
};

/* Score an assembled face (picked piece indices) against a vessel's
   true face. 3 matches = Art 50 (TRUE), 2 = Art 40 (offered),
   1 = Art 30 (copy), 0 = Art 20 (not offered). Pure. */
export function rnfScoreFacePick(picked, trueFace) {
  if (!picked || !trueFace) return { art: 0, matches: 0, status: 'locked' };
  let matches = 0;
  for (let i = 0; i < 3; i++) if (picked[i] === trueFace[i]) matches++;
  const art = matches === 3 ? 50 : matches === 2 ? 40 : matches === 1 ? 30 : 20;
  return { art, matches, status: rnfFaceStatus(art) };
}

export function rnfFaceStatus(art) {
  if (art >= GODWITHIN_RNF.thresholds.trueFace) return 'true';
  if (art >= GODWITHIN_RNF.thresholds.offered) return 'offered';
  if (art >= GODWITHIN_RNF.thresholds.copy) return 'copy';
  return 'locked';
}

export function godwithinRnfFaceFor(vesselId) {
  return GODWITHIN_RNF.faces.find((f) => f.vessel === vesselId) || null;
}

/* ---------------- Planetokio sky layer ----------------
   GATED (data only): the Planetokio discs 1–3 are complete on
   release sato-planetokio-rhythm-20261120, but no Planetokio
   content is staged in the WH repo — the sky layer ships as data
   + entry points, and its islands stay locked until the discs
   land in-repo (gap G9). Nothing here claims the discs are in. */
export const GODWITHIN_SKY = {
  gated: true,
  gateReason: 'Planetokio discs 1–3 complete on release sato-planetokio-rhythm-20261120 (26+27+28 parts + CUEs + manifest) but not staged in mhvnsnt/western-heart. Sky islands unlock when the discs land in-repo.',
  entry: 'From any Banabana port once its anchor is unlocked — "Sail upward". Final entry at Central Mountain peak (Tokyo Tower = Central Mountain peak).',
  islands: GODWITHIN_ANCHORS.map((a) => ({
    anchor: a.anchor, guardianId: a.guardianId,
    possession: 'Collect Virus possession arc — cured by quest/vaccine (Puri-puri arc pattern), not by fight.',
  })),
  hubPois: ['clinic — revive after KO', 'save point', 'store', 'stamp post'],
  ending: 'Stamp count decides the ending — good ending = ascension to the Intergalactic Collect Exhibition (the cosmic ending above DW5).',
};

/* ---------------- Trader / shards economy ----------------
   One wallet (WHIdentity) shared across God Within, Dream,
   Banabana and the Trader. Forces are bought from the Trader with
   shards — NEVER won on a machine (Trial-honesty rule). Slot:
   3 of a kind pays 10×, 2 pays 2×. Completion payout is the DW
   per-character payout, owner-adjustable. */
export const GODWITHIN_ECONOMY = {
  wallet: 'WHIdentity — one shared Soul Shard wallet (God Within, Dream, Banabana, Trader).',
  payouts: {
    dreamNight: 20,       // dream.html day-end minimum (20 + 5 × nav flags; a between-lives night walks no nav, so 20)
    guardianWin: 250,     // WH-authored: one anchor room cleared
    bossWin: 1000,        // WH-authored: one chapter boss cleared
    tollWin: 100,         // WH-authored: Trader toll fight
    trueFace: 500,        // WH-authored: RNF TRUE-face shard bonus (spec: "mission briefing + shard bonus", no number given)
    completion: 100000,   // DW per-character completion payout — OWNER-ADJUSTABLE
  },
  slotPays: { three: 10, two: 2 },
  rules: [
    'Forces are bought from the Trader with shards, never won on a machine.',
    'Jackpot pays shards, never a force.',
    'Rank S → shard multiplier (see GODWITHIN_COMBAT.pointsRank).',
    'Side games (Banabana hub, Trader’s Slot, Chō-han) pay shards only — they never advance the Trial.',
  ],
};

/* ---------------- Playable characters ----------------
   Featured 17 per Lane C Table (d) — GLB URLs as authored in
   MODEL_URLS (game/js/assets.js), verified by THIS lane 2026-11-26:
   - 'r2-200': HEAD 200 live against the Worker remote base.
   - 'tree-blob': blob exists in the WH git tree (game/assets/models/).
   - 'jsdelivr-fallback': 404 on the Worker, 200 on jsDelivr
     (resolveAssetCandidates falls back there — playable, but the
     R2 miss is a gap: the file should be uploaded to the bucket).
   - 'no-glb': no model — NEVER playable, never invented.
   - 'not-rostered': no roster entry — NPC/economy host only.
   The full God Within pool is all 83 GLB-backed roster fighters
   (godwithinVesselPool); the 17 below are the FEATURED cast. */
export const GODWITHIN_FEATURED = [
  { id: 'rin',     name: 'RIN',     role: 'Default playable; Trial spine; Banabana lead; RNF face 1; DW campaign lead (Jin’s slot).', modelKey: 'demonio-a1', glb: '../roster/demonio/attires/attire1/model.glb', verified: 'r2-200' },
  { id: 'tou',     name: 'TOU',     role: 'DW1 guardian (PYRAMSTP); Shooting Gallery + Bull Run host; grapple brawler.', modelKey: 'tou-body', glb: 'assets/models/tou-soul-tex.glb', verified: 'tree-blob' },
  { id: 'sakura',  name: 'SAKU RA', role: 'SHA’s vessel (TAJI) + DW3 guardian (GODDESS); RNF Green Castle dancer.', modelKey: 'saku-ra', glb: '../roster/sakura/attires/attire1/model-rerig.glb', verified: 'r2-200' },
  { id: 'kai',     name: 'KAI',     role: 'Cooking School + Whale Game host; RNF Sea dancer; Surge = tide.', modelKey: 'kai-body', glb: 'assets/models/kai-soul-tex.glb', verified: 'tree-blob' },
  { id: 'phantom', name: 'PHANTOM', role: 'JIN’s blade (folded into Phantom’s attire ladder); DW4 guardian (NASKA) + Soul Sphere boss body; Blue Game host.', modelKey: 'phantom', glb: '../roster/phantom/attires/attire1/model-rerig.glb', verified: 'r2-200' },
  { id: 'retsu',   name: 'RETSU',   role: 'DW2 guardian (PYRAMID); Cowboy Game host; Helix Destruction room.', modelKey: 'retsu-body', glb: 'assets/models/retsu-body.glb', verified: 'tree-blob' },
  { id: 'zen',     name: 'ZEN',     role: 'DW2 guardian (SHRINE); Sapporo Maze host; RNF Book dancer.', modelKey: 'zen', glb: '../roster/zen/attires/attire1/model-rigged.glb', verified: 'r2-200' },
  { id: 'gyou',    name: 'GYOU',    role: 'DW4 guardian (TENG); Sheep Farm host; DW2 tripled-boss body; RNF Quiet Rose dancer.', modelKey: 'gyou-attire1', glb: '../roster/gyou/spirit-body/model-gamerig-cdn.glb', verified: 'r2-200-alt', caveat: 'Roster key 404s on R2 (not in manifest; jsDelivr 200 is stale cache, untrusted). Plays via spirit-form alt gyou-spirit → ../roster/gyou/attires/spirit-form/model.glb (R2-200 + in-manifest).' },
  { id: 'byou',    name: 'BYOU',    role: 'DW3 guardian (PRAYER); Nabel Maze host; RNF Climb dancer.', modelKey: null, glb: null, verified: 'no-glb' },
  { id: 'pantera', name: 'PANTERA', role: 'DW5 guardian (PYRAMSUN); RNF Steel #036 dancer; paired-throw lead.', modelKey: 'pantera-leoman', glb: '../roster/pantera/attires/leomon/model.glb', verified: 'r2-200' },
  { id: 'demonio', name: 'DEMONIO', role: 'DW5 final guardian (DEVIL); transform flagship (unwinged → winged Devil on full meter).', modelKey: 'demonio-a1', glb: '../roster/demonio/attires/attire1/model.glb', verified: 'r2-200', forms: { winged: '../roster/demonio/attires/winged-devil/model-rigged.glb', human: '../roster/demonio/attires/human/model-rerig.glb', formsVerified: 'r2-200' } },
  { id: 'skull',   name: 'SKULL',   role: 'DW1 guardian (STPAUL); RNF Voice #036 dancer.', modelKey: 'skull', glb: '../roster/skull/attires/attire1/model-rerig.glb', verified: 'r2-200' },
  { id: 'samura1', name: 'SAM-UR-A1', role: 'DW1 boss reskin (Modified Gun Jack); RNF Moon Market dancer.', modelKey: 'sam-ur-a1', glb: '../roster/sam-ur-a1/attires/attire1/model-rerig.glb', verified: 'r2-200' },
  { id: 'diablo',  name: 'DIABLO',  role: 'DW3 boss reskin (True Ogre); DW5 guardian (BIGHEAD); RNF Universe #036 dancer; RNF face 10 (proposal).', modelKey: 'diablo', glb: '../roster/diablo/attires/attire1/model-rigged.glb', verified: 'r2-200' },
  { id: 'nightwolf', name: 'NIGHTWOLF', role: 'Guide of the newly dead (CANON.md Two Laws of Death); God Within death guide.', modelKey: 'nightwolf-attire1', glb: '../roster/nightwolf/attires/attire1/model-rigged.glb', verified: 'tree-blob', caveat: 'Attire1 key 404s on R2 (not in manifest). Plays via base key nightwolf → assets/models/nightwolf.glb (in-tree + in-manifest, 20,880,260 B).' },
  { id: 'dxmmii-patchwork', name: 'DXMMII', role: 'Patchwork DJ; featured playable (Mokujin base).', modelKey: 'dxmmii-tripo', glb: '../roster/dxmmii/attires/attire1/model-rigged-cdn.glb', verified: 'tree-blob', caveat: 'Tripo key 404s on R2 (not in manifest; jsDelivr 200 is stale cache, untrusted). Plays via base key dxmmii → assets/models/dxmmii.glb (in-tree + in-manifest, 389,936 B).' },
  { id: 'megami',  name: 'MEGAMI',  role: 'Featured playable.', modelKey: 'megami', glb: '../roster/parvati/attires/attire1/model-rigged-cdn.glb', verified: 'r2-200-alt', caveat: 'The -cdn filename 404s on R2. The file ON R2 is the non-cdn name roster/parvati/attires/attire1/model-rigged.glb (R2-200 + in-manifest) — MODEL_URLS -cdn suffix looks stale (gap GW-19).' },
  { id: 'trader',  name: 'TRADER',  role: 'Economy host (slot, Chō-han, force market); RNF face 12 (proposal). NOT a roster fighter — NPC only.', modelKey: null, glb: null, verified: 'not-rostered' },
];

/* NOTE on the featured list: Lane C Table (d) named 17 rows (16
   fighters + Trader) with all GLB URLs UNVERIFIED. This lane
   verified them — but two of Lane C's rows had no roster GLB to
   verify (BYOU: no GLB; TRADER: not rostered), so NIGHTWOLF,
   DXMMII and MEGAMI — owner-named headline fighters with verified
   GLBs — are carried as featured playables in their place in the
   implemented cast. The implemented featured cast is therefore 16
   playable fighters + the Trader as NPC host. The full pool below
   is the 83 GLB-backed roster fighters. */
export const GODWITHIN_PLAYABLE_FEATURED = GODWITHIN_FEATURED.filter(
  (f) => f.verified === 'r2-200' || f.verified === 'r2-200-alt' || f.verified === 'tree-blob',
);

/* Fighters that can NEVER be offered or fielded in God Within mode:
   model: null, modelPending in roster-full.js. Never invent a GLB. */
export const GODWITHIN_UNPLAYABLE = [
  { id: 'byou', reason: 'MODEL PENDING — model: null in roster-full.js, no GLB on the remote base or in-tree. PRAYER room guarded by RAVE (stand-in) until a BYOU GLB lands.' },
  { id: 'ryuji', reason: 'MODEL PENDING — model: null in roster-full.js, no GLB anywhere. No God Within content casts RYUJI.' },
];

/* Dead affinity ids in modes.js VESSEL_AFFINITY that are NOT roster
   ids and must never be offered: 'jin_soul' (folded into Phantom),
   'sha' (not a fighter — Saku Ra is the vessel). */
export const GODWITHIN_DEAD_IDS = ['jin_soul', 'sha'];

/* The God Within vessel pool: every roster id EXCEPT the model-pending
   and the dead ids. Pass the roster ids + the model-pending ids in;
   the pool is what chooseGodwithinVessels may offer. Pure. */
export function godwithinVesselPool(rosterIds, modelPendingIds) {
  const pending = new Set(modelPendingIds || []);
  const dead = new Set(GODWITHIN_DEAD_IDS);
  return (rosterIds || []).filter((id) => !pending.has(id) && !dead.has(id));
}

export function godwithinIsPlayable(rosterId, modelPendingIds) {
  if (!rosterId) return false;
  if ((modelPendingIds || []).includes(rosterId)) return false;
  if (GODWITHIN_DEAD_IDS.includes(rosterId)) return false;
  return true;
}

/* Full-roster reincarnation picks for God Within mode.
   modes.js chooseReincarnation only scores the 36 VESSEL_AFFINITY
   entries, so 49 of 85 fighters could never be offered. This picks
   from the FULL pool: vessels WITH an explicit affinity score on
   their profile; vessels WITHOUT one get the documented NEUTRAL
   fallback (all .3) — a stated default rule, not invented
   per-fighter stats. Diablo keeps his deaths ≥ 3 gate. Pure. */
export const GODWITHIN_NEUTRAL_AFFINITY = { aggro: 0.3, grapple: 0.3, defense: 0.3, trick: 0.3, surge: 0.3 };

export function chooseGodwithinVessels(profile, affinity, rosterIds, currentId, deaths) {
  const scored = [];
  for (const id of rosterIds || []) {
    if (id === currentId) continue;
    if (id === 'diablo' && (deaths || 0) < 3) continue;
    const aff = (affinity && affinity[id]) || GODWITHIN_NEUTRAL_AFFINITY;
    let s = 0;
    for (const k of ['aggro', 'grapple', 'defense', 'trick', 'surge']) {
      s += (profile[k] || 0) * (aff[k] || 0);
    }
    const j = (((id.length * 37 + (deaths || 0) * 91) % 100) / 100) * 0.05;
    scored.push({ id, s: s + j, explicit: !!(affinity && affinity[id]) });
  }
  scored.sort((a, b) => b.s - a.s);
  return scored.slice(0, 3).map((x) => x.id);
}

/* ---------------- Run state machine ----------------
   One God Within run: the Trial ladder (modes.js `story` state,
   reused verbatim) + this overlay. clearedGuardians / clearedBosses
   persist across deaths — death costs the vessel, never the rooms. */
export function createGodwithinRun(vesselId) {
  return {
    vesselId,
    lives: 9, // Sato's nine lives; the Trial is nine souls, nine lives
    deaths: 0,
    shards: 0,
    clearedGuardians: [], // anchor ids
    clearedBosses: [],    // chapter numbers
    faces: [],            // { vessel, art, status } from RNF face-picks
    dreams: [],           // { day, stage, shards } — one per death
    voyages: [],          // { area, scene, item } — Banabana legs sailed
    facePick: null,       // { eyes, nose, mouth } indices, this death
    startedAt: Date.now(),
  };
}

/* Next foe for a rung: guardians in anchor order, then the chapter
   boss, then null (rung complete). Trader rung → toll foe (pool
   draw, kind 'toll'). Final rung → Assembled Soul (kind 'final').
   Pure — the caller draws the toll foe from the rung pool. */
export function godwithinNextFoe(run, rungIndex) {
  const rung = GODWITHIN_RUNGS[rungIndex];
  if (!rung) return null;
  if (rung.boss) return { kind: 'final', id: 'assembled-soul', name: 'ASSEMBLED SOUL' };
  if (rung.trader) return { kind: 'toll', pool: rung.pool };
  const chapter = GODWITHIN_CHAPTERS[rung.chapter - 1];
  const anchors = godwithinAnchorsForChapter(rung.chapter);
  for (const a of anchors) {
    if (!run.clearedGuardians.includes(a.anchor)) {
      return { kind: 'guardian', anchor: a.anchor, id: a.guardianId, name: a.guardian, chapter: rung.chapter };
    }
  }
  if (!run.clearedBosses.includes(rung.chapter)) {
    return { kind: 'boss', id: chapter.boss.id, name: chapter.boss.name, dwBoss: chapter.boss.dwBoss, chapter: rung.chapter };
  }
  return null;
}

export function godwithinRungProgress(run, rungIndex) {
  const rung = GODWITHIN_RUNGS[rungIndex];
  if (!rung) return { guardiansCleared: 0, guardiansTotal: 0, bossCleared: false, complete: true };
  if (rung.trader || rung.boss) return { guardiansCleared: 0, guardiansTotal: 0, bossCleared: false, complete: false };
  const anchors = godwithinAnchorsForChapter(rung.chapter);
  const cleared = anchors.filter((a) => run.clearedGuardians.includes(a.anchor)).length;
  const bossCleared = run.clearedBosses.includes(rung.chapter);
  return {
    guardiansCleared: cleared, guardiansTotal: anchors.length,
    bossCleared, complete: cleared === anchors.length && bossCleared,
  };
}

/* Apply a win to the run. Returns { advanced, shards, complete }.
   Guardian win: mark the room, pay guardian shards, stay on the
   rung. Boss win: mark the boss, pay boss shards, claim the rung's
   force (caller adds it to story.forces), advance the rung.
   Toll win: pay toll shards, advance. Final win: run complete. */
export function godwithinMarkWin(run, rungIndex, foe) {
  if (!foe) return { advanced: false, shards: 0, complete: false };
  if (foe.kind === 'guardian') {
    if (!run.clearedGuardians.includes(foe.anchor)) run.clearedGuardians.push(foe.anchor);
    const shards = GODWITHIN_ECONOMY.payouts.guardianWin;
    run.shards += shards;
    return { advanced: false, shards, complete: false };
  }
  if (foe.kind === 'boss') {
    if (!run.clearedBosses.includes(foe.chapter)) run.clearedBosses.push(foe.chapter);
    const shards = GODWITHIN_ECONOMY.payouts.bossWin;
    run.shards += shards;
    return { advanced: true, shards, complete: false, forceKey: GODWITHIN_RUNGS[rungIndex].forceKey };
  }
  if (foe.kind === 'toll') {
    const shards = GODWITHIN_ECONOMY.payouts.tollWin;
    run.shards += shards;
    return { advanced: true, shards, complete: false };
  }
  if (foe.kind === 'final') {
    run.shards += GODWITHIN_ECONOMY.payouts.completion;
    return { advanced: true, shards: GODWITHIN_ECONOMY.payouts.completion, complete: true };
  }
  return { advanced: false, shards: 0, complete: false };
}

/* Record one between-lives beat. Pure arithmetic on the run. */
export function godwithinRecordDream(run, dream) {
  run.dreams.push(dream);
  run.shards += dream.shards || 0;
  return run.dreams.length;
}

export function godwithinRecordVoyage(run, leg) {
  run.voyages.push(leg);
  run.shards += leg.shards || 0;
  return run.voyages.length;
}

export function godwithinRecordFace(run, face) {
  run.faces.push(face);
  return run.faces.length;
}

/* ---------------- The flow, as data ---------------- */
export const GODWITHIN_FLOW = [
  { step: 1, name: 'MENU', where: 'Main menu → story submenu → GOD WITHIN card', detail: 'mode-godwithin → ModeController.startMode("godwithin").' },
  { step: 2, name: 'SELECT', where: 'Character select', detail: 'Any GLB-backed roster fighter (83 of 85). byou + ryuji never offered (no GLB).' },
  { step: 3, name: 'RUNG', where: 'Rung intro (chapter + guardian progress + force reward)', detail: 'Seven rungs: five DW chapters, the Trader, the final Shrine.' },
  { step: 4, name: 'FIGHT', where: 'Trial fight, DW base kit + Soul Surge + shard pickups', detail: 'Foe = next undefeated guardian, then the chapter boss (DW behaviour, WH body).' },
  { step: 5, name: 'DEATH', where: 'Loss → deaths++ → between-lives', detail: 'NOT straight to reincarnation: dream first, then voyage, then face-pick.' },
  { step: 6, name: 'DREAM', where: 'One LSD dream night (dream-system.js startDay())', detail: 'Day-end minimum 20 shards (dream.html rule). Special day → vignette.' },
  { step: 7, name: 'VOYAGE', where: 'Banabana hub (rolypolys-hub.js) — sail between lives', detail: 'Area → region → scene; one item per scene; winnings pay shards to the shared wallet.' },
  { step: 8, name: 'FACE-PICK', where: 'RNF ritual on the reincarnation screen', detail: 'Assemble eyes/nose/mouth; Art ≥ 40 offers the face, 50 = TRUE face + briefing + shard bonus, 30 = wearable copy.' },
  { step: 9, name: 'REINCARNATE', where: 'Vessel cards from the FULL 83-fighter pool', detail: 'chooseGodwithinVessels — explicit affinities score; the rest get the documented neutral fallback. Diablo gated at 3+ deaths.' },
  { step: 10, name: 'NEXT LIFE', where: 'Same rung, new vessel, forces carried over', detail: 'Cleared guardians/bosses persist across deaths. Death costs the vessel, never the rooms.' },
  { step: 11, name: 'SHRINE', where: 'Final rung — the Assembled Soul', detail: 'Win: 100,000-shard completion payout (owner-adjustable), ending, and the Sky opens (gated — see GODWITHIN_SKY).' },
];

/* ---------------- Exact gaps (carried + new) ----------------
   Nothing here is papered over. A gap is work to solve, not a
   reason to ship a substitute. */
export const GODWITHIN_GAPS = [
  { id: 'GW-1', gap: 'byou has no GLB (model: null, modelPending). PRAYER guardian room uses RAVE as stand-in; BYOU unplayable until a BYOU GLB lands on the remote base.', blocks: 'BYOU playable + PRAYER true guardian' },
  { id: 'GW-2', gap: 'ryuji has no GLB (model: null, modelPending). No God Within content casts RYUJI.', blocks: 'RYUJI playable' },
  { id: 'GW-3', gap: 'EM_FACE art missing from the repo: ../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/* — 0 teardown/ paths on WH main. The reincarnation face images 404 in the shipped game (silent degrade via img.onerror). Either stage the bitmaps into the repo or re-point EM_FACE at in-repo art.', blocks: 'Face-pick art on the shipped reincarnation screen' },
  { id: 'GW-4', gap: 'RNF manual PDF missing (lane-3 upload died 2026-11-20 on scans RAR part-004). RNF true-face triples are WH-authored provisional; faces 10–12 (DIABLO / ASSEMBLED SOUL / TRADER’S MASK) are proposals, not offered.', blocks: 'RNF faces as the manual intended them' },
  { id: 'GW-5', gap: 'Def Jam Icon — no decomp/recomp anywhere; RPCS3 + own disc only. Owner call: include via RPCS3 route / extracted assets / nothing. NOT mapped in.', blocks: 'Any Icon content', ownerCall: true },
  { id: 'GW-6', gap: 'Planetokio discs 1–3 complete on release sato-planetokio-rhythm-20261120 but not staged in WH. Sky layer ships as data + entry points only; islands stay locked.', blocks: 'Planetokio sky layer as playable content' },
  { id: 'GW-7', gap: 'GYOU roster GLB (gyou-attire1, model-gamerig-cdn.glb) 404s on the R2 remote base and is NOT in the R2 upload manifest; its jsDelivr 200 is stale cache (file not in the tree) and is NOT trusted. GYOU plays via his spirit-form alt (gyou-spirit, R2-200 + in-manifest). Upload the gamerig file to the bucket or re-point the key.', blocks: 'GYOU on his roster key' },
  { id: 'GW-7b', gap: 'NIGHTWOLF attire1 + DXMMII tripo roster keys 404 on R2 (not in manifest). Both play via their in-tree base keys (nightwolf.glb, dxmmii.glb). The attire1/tripo files should be uploaded to the bucket or the keys re-pointed.', blocks: 'NIGHTWOLF / DXMMII on their roster attire keys' },
  { id: 'GW-8', gap: 'Roster GLBs are NOT in the WH git tree — they live in the private B2 bucket (remote base). The game loads God Within mode from the repo, but its fighter bytes come from the bucket. A repo-only deploy (no bucket) cannot field the ../roster/... fighters.', blocks: 'Repo-only self-containment of fighter bytes' },
  { id: 'GW-9', gap: 'Redux 24-part shape vs single-asset re-upload — OWNER CALL (manifest flags it; integrity proven, shape undecided).', blocks: 'How Redux is consumed', ownerCall: true },
  { id: 'GW-10', gap: 'FFNY recomp in-hand is the v1.2.0-beta line; stable v1.2.0 GA landed upstream Nov 20, 2026. Refresh owed.', blocks: 'FFNY at GA' },
  { id: 'GW-11', gap: 'Vendetta 782-vs-783 blob gap (Nov 20 audit) — re-verify with check_trees.py before building on the Vendetta recomp.', blocks: 'Building on Vendetta recomp' },
  { id: 'GW-12', gap: 'DW 2-player co-op (devilwithin-coop headline feature) unverified — Phase 2 proved single-player headless only. DW chapters ship single-player until co-op verifies.', blocks: 'God Within co-op in DW chapters' },
  { id: 'GW-13', gap: 'WH converted Def Jam parts catalog (1,201 GLB entries, teardown/customization/parts-converted/defjam/CATALOG.json) NOT re-verified.', blocks: 'Custom-character parts claim' },
  { id: 'GW-14', gap: '5 shell minigames + 2 mazes: rules live inside .DXR files, not recoverable from the catalog. Shells only until a ScummVM boot test or DXR decompile recovers them.', blocks: 'Those 7 games becoming playable' },
  { id: 'GW-15', gap: 'Sparse ISO + TK5DATA2/TK5DATA3 disc part_00 files gone from disk (existed Nov 23). Extracted DW data survives; ISO rebuild needs the disc parts re-fetched.', blocks: 'Rebuilding the DW sparse ISO' },
  { id: 'GW-16', gap: 'Sato scans RAR parts 004–010 + manual PDF + scan PNGs + art book + OST never landed on release sato-planetokio-rhythm-20261120. No worker running to finish them.', blocks: 'RNF manual + scans + OST' },
  { id: 'GW-17', gap: 'TRADER is not a roster fighter (no trader/mokujin roster id). Economy host + NPC only; a playable Trader needs a roster entry + GLB + owner call.', blocks: 'Playable Trader' },
  { id: 'GW-18', gap: 'KUTZ + REALIZZT are not rostered (owner addendum 2026-11-20 says both join; no entries, no GLBs on main). Not playable in God Within until rostered.', blocks: 'KUTZ / REALIZZT playable' },
  { id: 'GW-19', gap: 'MEGAMI MODEL_URLS key ends "-cdn" (roster/parvati/attires/attire1/model-rigged-cdn.glb) but the file on R2 — and in the upload manifest — is the non-cdn name (model-rigged.glb, R2-200). The "-cdn" suffix looks stale. Fix = verify which filename is canon, then correct the key or upload the -cdn file. NOT silently re-pointed here.', blocks: 'MEGAMI on her roster key' },
  { id: 'GW-20', gap: 'TOU + KAI soul-tex GLBs are in-tree blobs but NOT in the R2 upload manifest (R2 404 both). They load from the Pages shell / jsDelivr, not the bucket. Add them to the manifest/upload or confirm they are bundled.', blocks: 'TOU / KAI on the primary asset base' },
  { id: 'GW-21', gap: 'STORY stage intro is a dead end on main (found by the godwithin-e2e, C9 run 45865036342): _storyStageIntro (modes.js:846) calls show("stage"), which shows CHOOSE YOUR ARENA (#screen-stage); its CONFIRM is a no-op without a versus pendingFight, and the intro text + ENTER button live on the hidden #screen-stage-intro panel that nothing ever shows (show("stageIntro") has zero callers on main). The Trial cannot reach its first fight through the UI. God Within had the identical line (_godwithinStageIntro, modes.js:936) — fixed on this branch to show("stageIntro"). STORY itself is left untouched here for the owner call; the one-word fix is the same.', blocks: 'STORY mode reaching its first fight', ownerCall: true },
];
