// Tekken 7 Moveset Parser
// Converts TheBigTuna JSON format → Western Heart moveset format
// Also handles TKMovesets output and other T7 data formats
// 
// Input (TheBigTuna): { notation, hit_level, damage, speed, on_block, on_hit, on_ch, notes }
// Output (WH): { notation_lp, notation_original, hit_level, damage, speed, on_block, on_hit, on_ch, notes, animation: 'UNMAPPED' }
//
// Button mapping: LP1=Tekken 1=Left Punch, RP2=Tekken 2=Right Punch, LK3=Tekken 3=Left Kick, RK4=Tekken 4=Right Kick
// User directive 2026-10-24: Use MOD damage values, ignore license gaps, pull everything that helps

const BUTTON_MAP = {
  '1': 'LP1',
  '2': 'RP2',
  '3': 'LK3',
  '4': 'RK4'
};

/**
 * Convert Tekken notation (1/2/3/4) to WH LP1/RP2/LK3/RK4 format
 * Preserves directional prefixes (f, b, d, u, d/f, etc.), stance prefixes (FC, WS, etc.),
 * and structure (commas for strings, + for chords, ~ for transitions, / for directions)
 * 
 * Examples:
 *   "1" → "LP1"
 *   "1, 2" → "LP1, RP2"
 *   "1+2" → "LP1+RP2"
 *   "d/f+1" → "d/f+LP1"
 *   "in rage d/f+1+2" → "in rage d/f+LP1+RP2"
 *   "FC d/f+2" → "FC d/f+RP2"
 *   "WS 1, 2" → "WS LP1, RP2"
 */
function convertNotation(notation) {
  if (!notation || typeof notation !== 'string') return notation;
  // Replace button numbers 1-4 when they appear as standalone button inputs
  // Regex: (?<![0-9A-Za-z])1(?![0-9]) ensures we don't match "10" or "1" inside words
  // This handles: start of string, after +, comma, space, /, ~, etc.
  // And before +, comma, space, /, ~, end, etc.
  let result = notation;
  result = result.replace(/(?<![0-9A-Za-z])1(?![0-9])/g, 'LP1');
  result = result.replace(/(?<![0-9A-Za-z])2(?![0-9])/g, 'RP2');
  result = result.replace(/(?<![0-9A-Za-z])3(?![0-9])/g, 'LK3');
  result = result.replace(/(?<![0-9A-Za-z])4(?![0-9])/g, 'RK4');
  return result;
}

/**
 * Parse a single TheBigTuna move into WH format
 */
function parseMove(move) {
  if (!move || typeof move !== 'object') return null;
  const origNotation = move.notation || '';
  const lpNotation = convertNotation(origNotation);
  return {
    notation: lpNotation,
    notation_lp: lpNotation,
    notation_original: origNotation,
    hit_level: move.hit_level || null,
    damage: move.damage !== undefined ? move.damage : null,  // MOD damage, do NOT overwrite
    speed: move.speed || null,
    on_block: move.on_block || null,
    on_hit: move.on_hit || null,
    on_ch: move.on_ch || null,
    notes: move.notes || null,
    animation: 'UNMAPPED',  // NEVER guess from frame data or T3 rows
    source: 'TheBigTuna/Tekken-7-Frame-Data'
  };
}

/**
 * Parse a full TheBigTuna character file into WH format
 * Deduplicates moves (King jab appears twice in source)
 * 
 * @param {Object} data - TheBigTuna JSON data ({ metadata, moves } or array)
 * @param {string} character - Character name (e.g., 'king')
 * @returns {Object} WH-format moveset
 */
function parseCharacter(data, character) {
  let moves = [];
  let metadata = {};
  
  if (Array.isArray(data)) {
    moves = data;
  } else if (data && typeof data === 'object') {
    moves = data.moves || data.data || [];
    metadata = data.metadata || {};
  }
  
  const seen = new Set();
  const parsed = [];
  let dupsRemoved = 0;
  
  for (const move of moves) {
    const parsedMove = parseMove(move);
    if (!parsedMove) continue;
    
    // Deduplicate by (notation_lp, hit_level, damage, speed)
    const key = `${parsedMove.notation_lp}|${parsedMove.hit_level}|${parsedMove.damage}|${parsedMove.speed}`;
    if (seen.has(key)) {
      dupsRemoved++;
      continue;
    }
    seen.add(key);
    parsed.push(parsedMove);
  }
  
  return {
    source: {
      repo: 'TheBigTuna/Tekken-7-Frame-Data',
      game: 'Tekken 7',
      character: character,
      button_map: 'LP1=Tekken 1=Left Punch, RP2=Tekken 2=Right Punch, LK3=Tekken 3=Left Kick, RK4=Tekken 4=Right Kick',
      damage_source: 'MOD (TheBigTuna) - user authorized 2026-10-24, overrides WH old values',
      license_note: 'User authorized pull regardless of license status (2026-10-24)',
      warnings: [
        'NO move names in source (notation only) - names must come from wavu.wiki / WH T7 blocks, NOT invented',
        'NO animation IDs in source - this solves movelist + frame data, NOT move->animation mapping',
        'Animation column stays UNMAPPED until live T7 extraction lands'
      ]
    },
    metadata_original: metadata,
    move_count: parsed.length,
    dups_removed: dupsRemoved,
    moves: parsed
  };
}

/**
 * Parse TKMovesets output format (if available)
 * TKMovesets JSON structure: { moves: [{ name, input, anim_name, ... }] }
 * This is a placeholder for when live extraction lands
 */
function parseTKMovesets(data, character) {
  // TKMovesets format has anim_name which IS the animation mapping
  // This is the path to real animation data (not available from frame data alone)
  let moves = [];
  if (Array.isArray(data)) {
    moves = data;
  } else if (data && typeof data === 'object') {
    moves = data.moves || [];
  }
  
  const parsed = moves.map(move => {
    const origNotation = move.input || move.notation || '';
    return {
      notation: convertNotation(origNotation),
      notation_lp: convertNotation(origNotation),
      notation_original: origNotation,
      name: move.name || null,
      animation: move.anim_name || 'UNMAPPED',  // TKMovesets HAS animation names
      animation_addr: move.anim_addr || null,
      hit_level: move.hit_level || null,
      damage: move.damage || null,
      source: 'TKMovesets (Kiloutre)'
    };
  });
  
  return {
    source: {
      repo: 'Kiloutre/TKMovesets',
      game: 'Tekken 7',
      character: character,
      note: 'Live extraction from running game - HAS animation mapping'
    },
    move_count: parsed.length,
    moves: parsed
  };
}

// Export for Node.js and browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    convertNotation,
    parseMove,
    parseCharacter,
    parseTKMovesets,
    BUTTON_MAP
  };
}
if (typeof window !== 'undefined') {
  window.MovesetParser = {
    convertNotation,
    parseMove,
    parseCharacter,
    parseTKMovesets,
    BUTTON_MAP
  };
}
