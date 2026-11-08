/* ============================================================
   WESTERN HEART — "The Heart and Mind Inside": per-character flows
   (Pantera lane, 2026-11-08 — the template every character follows)

   The shared descent (game/js/heartmind.js: HEARTMIND_STAGES,
   HEARTMIND_STORIES, genericStory) is the frame every fighter
   starts from. A per-character flow individualizes it: the
   fighter's own stage subs + tuning, their own echo pool (drawn
   from their canon relationships), their own wave composition,
   their own boss intros (in their story entry in heartmind.js),
   their own corner partner, and the decoded-file donors that
   feed their Surge Form.

   This module is dependency-free (browser + Node) so tests can
   import it directly, the way heartmind-campaign.js is. It
   imports nothing; heartmind.js imports it.

   CANON LAW (Jay, 2026-11-07 ~22:32, revised — criterion is SOURCE,
   not spelling, confirmed ~22:43):
   - "Devil" MAY appear — but ONLY in OUR own way and language
     (Jay's own characters and words, e.g. DIABLO and his title
     "The Devil Soul", "The Devil That Stays..."). NEVER the Tekken
     way (Devil Gene, Devil Jin, "Jin's devil", "Devil Within").
     Nothing in this file uses it either way.
   - "Jin" ONLY ever means the soul JIN (the Blade Soul). Nothing
     in this file uses the name for anyone else.
   - No canon name is invented here. Names marked PROPOSED are
     Jay's calls, not used in code (see HEARTMIND-JAY-CALLS.md).
   - Pantera is male (he/him); everyone else by name only.

   SOURCES (per item, in the doc):
   - Canon: CANON.md "PANTERA — The Panther Soul" (vessel of TOU,
     闘 — battle itself; Fire, Plains of Chi-U; "The hold is
     honest"); ROSTER.md §Pantera; NINE-SOULS-CANON.md (TOU row).
   - Flow shape: Urban Reign Story Mode — 100 missions, partner
     earned by beating them, partner commands, retry on fail
     (TEARDOWN-PART-C-URBAN-REIGN.md §2.1/§2.5; UR-STAGE-MISSION-
     DECODE.md §4). Redux craft: grounded idles, HD textures,
     expanded stage selection (Part C §3).
   - DW donors: dw-motion-index.json + dw_measurements.json
     (236/242 files extracted, DW-DECODE-LOG.md "What got decoded
     with real bytes"); canon names per HEARTMIND-RENAME-MAP.md §1/§4
     (PROVISIONAL until the keyframe decode lands).
   ============================================================ */

/* ---------------- Pantera's flow ----------------
   Canon: vessel of TOU (闘 — battle itself). He fights because
   fighting is what he is; the trial didn't recruit him, it
   recognized him. He believes the trial is a tournament that
   found the right fighter. He has nothing to resolve — the trial
   uses him as the standard the others are measured against.
   (CANON.md PANTERA: "Being purified of: Nothing.")

   Redux flow that fits him: Urban Reign's mission + partner
   structure, in wrestling language — a mission is a CARD (a
   night's card of opponents), the partner is his CORNER (earned
   by beating them: the one who would not stay down walks with
   you — Pantera respects only those who refuse to stay down),
   the double-team is a TAG. His descent is five cards, one
   tournament night. The mission structure + ranks are the
   standard made playable: he IS the measure. */

/* Pantera's five inner rooms. Same keys, names and arenas as the
   shared HEARTMIND_STAGES (those names are CONFIRMED canon) —
   his own subs (story text, like the beats) and his own tuning:
   the trial tests the standard harder, so his diff runs a step
   above the shared flow at every stage. */
export const PANTERA_STAGES = [
  { n: 1, key: 'threshold', name: 'THE THRESHOLD', stage: 'tong-nou',
    sub: 'The mat is here. I am here.',
    waves: 3, diff: 0.50, restore: 0.30 },
  { n: 2, key: 'masks', name: 'THE GALLERY OF MASKS', stage: 'phantom-marketplace',
    sub: 'Every face that would not stay down.',
    waves: 3, diff: 0.58, restore: 0.30 },
  { n: 3, key: 'drowning', name: 'THE DROWNING ROOM', stage: 'palace-of-dreaming',
    sub: 'Nothing buried. Only water, and a mat under it.',
    waves: 3, diff: 0.68, restore: 0.32 },
  { n: 4, key: 'furnace', name: 'THE FURNACE', stage: 'plains-of-chi-u',
    sub: 'He hunts where the sky burns.',
    waves: 3, diff: 0.78, restore: 0.32 },
  { n: 5, key: 'stillpoint', name: 'THE STILL POINT', stage: 'octagonal-shrine',
    sub: 'Yourself, unmasked. The watcher, wearing your shape.',
    waves: 0, diff: 0.90, restore: 0.35 },
];

/* Pantera's wave tables. Same shape as brawler.js WAVE_TABLES
   (zones of { waves: [[{t, n}...]] } or { boss }). Brute-heavy:
   his descent is holds, not gunfire — the power archetype
   (DW init_obj mon_power1/2, 1-frame 78-bone spawn poses) is the
   donor for the brutes. Gunners appear only at the Furnace, where
   the trial escalates and throws everything at the standard.
   Bosses are the shared kinds (warden / masks / ogre / sphere /
   shadow) — their names are CONFIRMED and do not change. */
export const PANTERA_WAVE_TABLES = {
  threshold: [
    { waves: [[{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }], [{ t: 'echo', n: 3 }]] },
    { waves: [[{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }], [{ t: 'echo', n: 2 }, { t: 'brute', n: 1 }]] },
    { boss: 'warden' },
  ],
  masks: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }]] },
    { waves: [[{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }], [{ t: 'echo', n: 3 }]] },
    { boss: 'masks' },
  ],
  drowning: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }]] },
    { waves: [[{ t: 'echo', n: 4 }], [{ t: 'brute', n: 2 }]] },
    { boss: 'ogre' },
  ],
  furnace: [
    { waves: [[{ t: 'gunner', n: 1 }, { t: 'echo', n: 2 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 3 }]] },
    { waves: [[{ t: 'echo', n: 4 }], [{ t: 'brute', n: 2 }, { t: 'gunner', n: 1 }]] },
    { boss: 'sphere' },
  ],
  stillpoint: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 1 }]] },
    { boss: 'shadow' },
  ],
};

/* Pantera's echo pool: the fighters his canon names.
   - DEMONIO: the only soul who meets him head-on, every time.
     Mutual respect, no warmth. (CANON.md PANTERA Relationships)
   - DIABLO: he dismisses as a pretender. (CANON.md PANTERA)
   - SAM-UR-A1: curious about him — a thing that cannot feel the
     hold. (CANON.md PANTERA)
   The Masks boss wears these faces too (the brawler draws boss
   echoes from the same cast). */
export const PANTERA_ECHO_IDS = ['demonio', 'diablo', 'samura1'];

/* Corner partner (Urban Reign partner rule, adapted): the partner
   is earned by beating them. Demonio's echo keeps rising in the
   waves and would not stay down — after the Masks, the real
   Demonio walks to Pantera's corner. No warmth, just the work.
   (UR: manual p.34 / HG101 — "to gain an AI companion, you must
   first defeat them"; Part C §2.5.) */
export const PANTERA_PARTNER_AFTER = 'masks';
export const PANTERA_PARTNER_ID = 'demonio';

/* Decoded-file donors for Pantera's descent. All numbers measured
   (dw_measurements.json); canon names per HEARTMIND-RENAME-MAP.md
   §1/§4. PROVISIONAL until the gym keyframe stream is decoded —
   the HM_TEARDOWN seam still waits on that decode, so these are
   donor records, not wired animation. Nothing here is a claim
   about motion the bytes have not shown.
   - Surge Form throws: the ikdv throw clips are the grappler's
     donors for Pantera's Surge Form ("PANTHER'S WRATH",
     roster-full.js). b_nage pair is the sparse subtype (34
     values/frame vs 420) — a retarget must handle it separately
     (DW-DECODE-LOG.md §4).
   - Surge Form transform: djin newhane 00–03 ("Soul Surge Bloom",
     PROVISIONAL). Trigger: dwup00 (60f). Beam: dwhadoh00 (45f) —
     its name is PROPOSED "Soul Beam" (Jay call #6), NOT used here.
   - Warden kit: kmb1, 39 clips, 3,186 frames (53.1 s at 60 fps).
   - Brute archetype: mon_power1/2 — 1-frame 78-bone spawn poses,
     archetype donor only (the WH brute is a roster fighter with
     power x1.3, not a decoded motion).
   - Boss bodies (bone counts measured): boss1 78, boss2 78,
     boss3 111, boss5 111. boss4 does not exist — the sphere needs
     no body, and that absence IS the design (map §4).
   - Stage map objects: moj_stg00/01/02/04 are geometry (NUDP
     models counted), NOT text (log §5 correction). Which one feeds
     which inner room waits on the NUDP/MIF parse — UNMEASURED.
   - Music: lab (stage 1), Egyptian (stage 3), blue + final-boss
     (stage 5). Stages 2 and 4 have no DW theme — UNMEASURED. */
export const PANTERA_DW_DONORS = {
  surgeThrows: [
    { file: 'gym_ikdv_36_nage_f.dat', frames: 120, bones: 35, canon: 'Surge Kit — throw, variant 36' },
    { file: 'gym_ikdv_36_nage_y.dat', frames: 126, bones: 35, canon: 'Surge Kit — throw, variant 36' },
    { file: 'gym_ikdv_b_nage_f.dat', frames: 170, bones: 35, sparse: true, canon: 'Surge Kit — throw, variant b' },
    { file: 'gym_ikdv_b_nage_y.dat', frames: 170, bones: 35, sparse: true, canon: 'Surge Kit — throw, variant b' },
    { file: 'gym_ikdv_ppp_nage_f.dat', frames: 92, bones: 35, canon: 'Surge Kit — throw, ppp variant' },
    { file: 'gym_ikdv_ppp_nage_y.dat', frames: 92, bones: 35, canon: 'Surge Kit — throw, ppp variant' },
  ],
  surgeTransform: [
    { file: 'gym_djin_newhane00.dat', frames: 1, bones: 12, canon: 'Soul Surge Bloom — variant 00' },
    { file: 'gym_djin_newhane01.dat', frames: 13, bones: 12, canon: 'Soul Surge Bloom — variant 01' },
    { file: 'gym_djin_newhane02.dat', frames: 13, bones: 12, canon: 'Soul Surge Bloom — variant 02' },
    { file: 'gym_djin_newhane03.dat', frames: 25, bones: 12, canon: 'Soul Surge Bloom — variant 03' },
  ],
  surgeTrigger: { file: 'gym_dwup00.dat', frames: 60, bones: 27, canon: 'Surge Kit — power-up' },
  surgeBeam: { file: 'gym_dwhadoh00.dat', frames: 45, bones: 27, note: 'name PROPOSED (Jay call #6), not used' },
  wardenKit: { group: 'kmb1', files: 39, frames: 3186, seconds: 53.1 },
  bruteArchetype: [
    { file: 'gym_init_obj_mon_power1.dat', frames: 1, bones: 78 },
    { file: 'gym_init_obj_mon_power2.dat', frames: 1, bones: 78 },
  ],
  bossBodies: {
    warden: { file: 'gym_init_obj_boss1.dat', bones: 78 },
    masks: { file: 'gym_init_obj_boss2.dat', bones: 78 },
    ogre: { file: 'gym_init_obj_boss3.dat', bones: 111 },
    sphere: null, // boss4 does not exist — the sphere needs no body
    shadow: { file: 'gym_init_obj_boss5.dat', bones: 111 },
  },
  stageMaps: [
    { file: 'moj_stg00.dat', nudpModels: 29, room: 'UNMEASURED — NUDP parse pending' },
    { file: 'moj_stg01.dat', nudpModels: 18, room: 'UNMEASURED — NUDP parse pending' },
    { file: 'moj_stg02.dat', nudpModels: 20, room: 'UNMEASURED — NUDP parse pending' },
    { file: 'moj_stg04.dat', nudpModels: 3, room: 'UNMEASURED — NUDP parse pending' },
  ],
  music: {
    threshold: 'snd_bg_lab',
    masks: null, // UNMEASURED — no DW theme for stage 2
    drowning: 'snd_bg_egy',
    furnace: null, // UNMEASURED — no DW theme for stage 4
    stillpoint: 'snd_bg_blu + snd_boss_last',
  },
};

/* The full Pantera flow — the template. The next character gets
   the same shape: their own stages (same keys), their own echo
   pool from their canon relationships, their own wave tables,
   their own partner rule, their own DW donors. */
export const PANTERA_FLOW = {
  fighterId: 'pantera',
  soul: 'tou', // 闘 — battle itself (NINE-SOULS-CANON.md TOU row)
  stages: PANTERA_STAGES,
  waveTables: PANTERA_WAVE_TABLES,
  echoIds: PANTERA_ECHO_IDS,
  partnerAfter: PANTERA_PARTNER_AFTER,
  partnerId: PANTERA_PARTNER_ID,
  dwDonors: PANTERA_DW_DONORS,
};

/* Per-character flow table, keyed by fighter id. One entry per
   individualized fighter; everyone else runs the shared flow. */
export const HEARTMIND_CHARACTER_FLOWS = {
  pantera: PANTERA_FLOW,
};

/* Vessel → soul map (template). Only Pantera is mapped here —
   each following fighter's lane adds its own vessel's soul
   (canon: NINE-SOULS-CANON.md vessel table). The map lets a
   vessel without its own story fall back to its soul's nineStory
   instead of the generic frame. */
export const FIGHTER_SOUL = {
  pantera: 'tou',
};

/* Flow for a fighter, or null for the shared flow. */
export function getHeartmindFlow(fighterId) {
  return HEARTMIND_CHARACTER_FLOWS[fighterId] || null;
}
