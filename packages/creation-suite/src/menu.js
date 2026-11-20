// Shared Creation Suite menu tree (data only; each game renders it with its
// own UI kit). Flow (owner spec 2026-10-14):
//   Main menu -> <per-game suite name> -> [Character Creation/Edit | Moveset]
//   -> character list -> pick a character -> that character's sub-menu.
// Layout is a 50/50 blend: WWE 2K Creation Suite (deep part slots, layered
// attire, Create-a-Moveset categories/slots) + Tekken Customization (fast
// per-character list, preset slots, item category tabs, live preview).
export const GAME_LABELS = {
  'western-heart':           { suite: 'Create a Fighter',  moveset: 'Move List Forge' },
  'Bannon':                  { suite: 'Create a Wrestler', moveset: 'Create a Moveset' },
  'AshLanev2':               { suite: 'Create a Brawler',  moveset: 'Fight Style Editor' },
  'brutalfistgrokversionten':{ suite: 'Create a Fighter',  moveset: 'Moveset Editor' },
};

export const CHARACTER_SUBMENU = [
  { id: 'presets',  label: 'Presets / Saved Looks', from: 'tekken' },     // Tekken preset slots
  { id: 'body',     label: 'Body', tabs: ['Body Type', 'Frame', 'Mass', 'Physics (jiggle)'], from: 'wwe' },
  { id: 'head',     label: 'Head & Face', tabs: ['Face', 'Hair', 'Facial Hair', 'Eyes'], from: 'wwe' },
  { id: 'attire',   label: 'Attire', tabs: ['Face (masks)', 'Head', 'Upper', 'Lower', 'Hands', 'Feet', 'Accessories'], layers: true, from: 'wwe' },
  { id: 'paint',    label: 'Paint & Tattoos', from: 'wwe' },
  { id: 'alt',      label: 'Alternate Attires', from: 'both' },
  { id: 'moveset',  label: 'Moveset', from: 'wwe' },
  { id: 'profile',  label: 'Profile & Style', from: 'wwe' },
  { id: 'entrance', label: 'Entrance / Intro & Win Pose', from: 'both' },
];

export const MOVESET_SCREENS = [
  { id: 'library', label: 'Move Library', note: 'every move from every teardown, filter by game/type/position' },
  { id: 'categories', label: 'Categories', note: 'WWE Create-a-Moveset categories; uncapped (Bannon moveset_schema.json: 25 categories / 439 slots)' },
  { id: 'slot', label: 'Slot Edit', note: 'assign move + AI priority/repetition/timing' },
  { id: 'command', label: 'Command List', note: 'Tekken-style input strings, frame data from the move-table interpreter' },
  { id: 'preview', label: 'Preview / Try it', note: 'plays the move on the selected character' },
];

export function suiteMenu(game) {
  const L = GAME_LABELS[game] || { suite: 'Creation Suite', moveset: 'Moveset' };
  return {
    id: 'creation_suite', label: L.suite,
    children: [
      { id: 'character', label: 'Character Creation / Edit', next: 'characterList', then: CHARACTER_SUBMENU },
      { id: 'moveset', label: L.moveset, next: 'characterList', then: MOVESET_SCREENS },
    ],
  };
}
