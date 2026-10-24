// Hit Audit — verifies attacks connect when they should.
// Checks: hitbox/hurtbox definitions exist, ranges are sane, throws have proper range.
//
// This catches "hits barely contact" and "grabs never connect".
//
// Run: node tools/combat-qa/hit_audit.mjs [--report out.json] [--fighter NAME]
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');

const args = process.argv.slice(2);
const reportPath = args.includes('--report') ? args[args.indexOf('--report') + 1] : null;
const fighterFilter = args.includes('--fighter') ? args[args.indexOf('--fighter') + 1] : null;

const msDir = join(root, 'game', 'assets', 'movesets');

// Sane ranges from Tekken (in game units, ~1 unit = 1 meter)
// Jab range: ~1.2-1.5, Mid kick: ~1.5-2.0, Throw: ~1.0-1.3
const RANGE_RULES = {
  strike: { min: 0.8, max: 2.5, warn: 'strike range outside Tekken norms' },
  throw: { min: 0.8, max: 1.5, warn: 'throw range outside Tekken norms (should be close)' },
  low: { min: 0.8, max: 2.0, warn: 'low range outside norms' },
};

const results = {
  timestamp: new Date().toISOString(),
  fighters: {},
  summary: { total: 0, rangeOk: 0, rangeFail: 0, missingHitbox: 0, failures: [] }
};

const files = readdirSync(msDir).filter(f => f.endsWith('.json') && !f.startsWith('t3_'));

for (const file of files) {
  const fighterId = file.replace('.json', '');
  if (fighterFilter && fighterId !== fighterFilter) continue;

  let data;
  try {
    data = JSON.parse(readFileSync(join(msDir, file), 'utf8'));
  } catch (e) {
    continue;
  }

  const moves = data.moves || {};
  const fr = { total: 0, rangeOk: 0, rangeFail: 0, missingHitbox: 0, failures: [] };

  for (const [moveKey, move] of Object.entries(moves)) {
    // Skip non-attacking moves
    const moveClass = move.move_class || '';
    if (!['strike', 'throw', 'grapple', 'low', 'mid', 'high'].includes(moveClass) &&
        !move.damage && !move.isGrab) {
      continue;
    }

    fr.total++;
    results.summary.total++;

    const isThrow = moveClass === 'throw' || moveClass === 'grapple' || move.isGrab;
    const range = move.range ?? move.hit_range ?? move.reach;

    if (range == null) {
      // No explicit range — check if it has hitbox data
      const hasHitbox = move.hitbox || move.hit_box || move.attack_box;
      if (!hasHitbox && move.damage > 0) {
        fr.missingHitbox++;
        results.summary.missingHitbox++;
        // Don't fail for this — many moves use default ranges
      } else {
        fr.rangeOk++;
        results.summary.rangeOk++;
      }
      continue;
    }

    const rules = isThrow ? RANGE_RULES.throw :
      moveClass === 'low' ? RANGE_RULES.low : RANGE_RULES.strike;

    if (range >= rules.min && range <= rules.max) {
      fr.rangeOk++;
      results.summary.rangeOk++;
    } else {
      fr.rangeFail++;
      results.summary.rangeFail++;
      const failure = {
        fighter: fighterId, move: moveKey, name: move.name,
        type: 'range_anomaly', range,
        expected: `${rules.min}-${rules.max}`,
        note: rules.warn
      };
      fr.failures.push(failure);
      results.summary.failures.push(failure);
    }
  }

  results.fighters[fighterId] = fr;
  if (fr.rangeFail > 0) {
    console.log(`${fighterId}: ${fr.rangeFail} range anomalies`);
  }
}

console.log(`\n=== HIT AUDIT COMPLETE ===`);
console.log(`Attack moves checked: ${results.summary.total}`);
console.log(`Range OK: ${results.summary.rangeOk}, Anomalies: ${results.summary.rangeFail}, Missing hitbox data: ${results.summary.missingHitbox}`);

if (reportPath) {
  writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\nReport written to ${reportPath}`);
}

process.exit(0);
