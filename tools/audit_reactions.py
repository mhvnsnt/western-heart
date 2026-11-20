#!/usr/bin/env python3
"""WH hit-reaction coverage audit (2026-10-31, owner I-lane 'reactions').

One reproducible run behind docs/WH-100-GAP-INVENTORY-2026-10-30.md's
reactions section. Replicates the engine's own rules from main:
- bankIdFor(charId, movesetId), game/js/fighter.js (armor-king override,
  FIGHTER_BANK overrides incl. zen -> null, then moveset index
  anim_bank || t3_source -> SOURCE_TO_BANK, then MOVESET_MAP fallback).
- SOURCE_TO_BANK + T3_BANKS, game/js/t3anims.js.
- _pickReaction (fighter.js): row = banks[attackerDir].rows[move.t3_row]
  else common_rows[move.t3_row]; no row -> no pick (generic 'hit' clip).
- selectReactionSlot (game/js/t3-reaction-select.js), IN ITS OWN ORDER:
  class 1/3 never react (class 2 grounded-only); reaction value 0 or
  (v & 0xf000) -> no pick (0x1nnn acts only through a throw).
- Playback: picked slot must sit in reactions.banks[defender|attacker]
  .slots and be baked in that bank's reactions.pack.json (reactions.json
  per-bank 'coverage': wanted/baked/missing).
Classifier cross-verified against the shipped selectReactionSlot under
node: 24/24 sampled moves agree (see verify cases in the audit notes).

Population: game/assets/movesets/*.json files carrying a `moves` dict
(129 files, 56,527 moves). Excluded with cause: index.json,
ur-native-index.json, t3_input_tables.json (tables/indexes) and 31
ur-charNNN.json (schema-2 Urban Reign native banks; no `moves`/t3_row
shape, unreferenced by fighter.js/characters.js).
"""
import json, glob, os, collections, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
R = json.load(open(f'{ROOT}/game/assets/anim/t3/reactions.json'))
RECORDS, COMMON, BANKS, COV = R['records'], R['common_rows'], R['banks'], R['coverage']
IDX = json.load(open(f'{ROOT}/game/assets/movesets/index.json'))['fighters']

T3_BANKS = {'king':'king_on_pantera_leoman','jin':'jin','xiaoyu':'xiaoyu','bryan':'bryan',
 'gunjack':'gunjack','yoshimitsu':'yoshimitsu','paul':'paul','lei':'lei','nina':'nina',
 'hwoarang':'hwoarang','eddy':'eddy','julia':'julia','anna':'anna',
 'bosconovitch':'bosconovitch','heihachi_ownrig':'heihachi','armorking':'armorking',
 'law':'law','heihachi':'heihachi_on_jin','ogre':'ogre','kuma':'kuma','gon':'gon',
 'forestlaw':'forestlaw_on_law'}
SOURCE_TO_BANK = {'king':'king','demonio':'jin','jin':'jin','bryan':'bryan','xiaoyu':'xiaoyu',
 'yoshimitsu':'yoshimitsu','gunjack':'gunjack','deviljin':'jin','paul':'paul',
 'lei':'lei','nina':'nina','hwoarang':'hwoarang','eddy':'eddy','julia':'julia',
 'anna':'anna','bosconovitch':'bosconovitch','heihachi':'heihachi',
 'armorking':'armorking','armor-king':'armorking','ogre':'ogre','kuma':'kuma',
 'panda':'kuma','gon':'gon','law':'law','forestlaw':'forestlaw','dural':'dural'}
FIGHTER_BANK = {'awapop':'nina','torch':'anna','kingtyrant':'eddy','kai':'eddy','tou':'paul',
 'gyou':'hwoarang','zen':None,'rave':'lei','yukihyo':'armorking','nightwolf':'julia',
 'chatur':'ogre','dorowani':'gon','menajerii':'kuma','gashadokuro':'kuma',
 'aotsuki':'kuma','silvertongue':'xiaoyu','docfrank':'bosconovitch','tobi':'hwoarang',
 'buffalo-bill':'law'}
MOVESET_MAP = {'rin':'demonio','byou':'demonio','tou':'heihachi','sha':'xiaoyu','kai':'demonio',
 'jin_soul':'yoshimitsu','retsu':'bryan','zen':'heihachi','gyou':'demonio',
 'pantera':'king','demonio':'demonio','phantom':'yoshimitsu','diablo':'heihachi',
 'skull':'bryan','samura1':'gunjack','sakura':'xiaoyu','zui':'demonio',
 'kinpo':'demonio','waterfall':'demonio','kingtyrant':'xiaoyu','burger':'bryan',
 'awapop':'demonio','scimitar':'demonio','purplerain':'demonio','nightwolf':'xiaoyu',
 'dio':'heihachi','cyborgx':'gunjack','michiko':'demonio','star':'xiaoyu',
 'torch':'demonio','bruno':'bryan','negativo':'bryan','thor':'bryan',
 'yukihyo':'king','slice':'bryan','docfrank':'gunjack',
 'demonio-bloodline-ember':'demonio','doc-frank-machine-shop':'gunjack',
 'baek-master-white':'bryan','mariposa-monarch':'xiaoyu','dxmmii-patchwork':'demonio',
 'cainelias':'king','zangief':'king','blanka':'bryan','vega':'xiaoyu','iori':'heihachi',
 'charger':'bryan','charger-attire2':'bryan','armor-king':'king',
 'kronos':'king','kronos-attire2':'king','demonio-human':'demonio',
 'doc-frank-wowomomo':'gunjack','doc-frank-hood':'gunjack',
 'deathfang':'heihachi','ryuji-rock':'king','koreshi':'heihachi'}
PROVEN = ('true-map branch-graph', 'true-map exact', 'class-verified remap')
MID = ('true-map class+limb', 'true-map class-only', 'true-map input+class',
       'same-notation', 'dash-branch', 'standing jab row')
GUESS = ('nearest limb/class/startup',)

def bank_id_for(cid, info):
    if cid == 'armor-king': return 'armorking'
    if cid in FIGHTER_BANK: return FIGHTER_BANK[cid]
    src = (info.get('anim_bank') or info.get('t3_source')) if info else None
    if not src: src = MOVESET_MAP.get(cid)
    if not src: return None
    return SOURCE_TO_BANK.get(src)

def js_key(v):
    if isinstance(v, list): return ','.join(js_key(x) for x in v)
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, float) and v == int(v): return str(int(v))
    return str(v)

def classify_row(row):
    """selectReactionSlot order. Returns class label for a found row."""
    react, cls = row[0], row[2]
    if cls in (1, 3): return 'class_never'
    if react == 0: return 'no_reaction_value'
    if react & 0xF000: return 'throw_range_value'
    if react >= len(RECORDS) or RECORDS[react] is None: return 'dangling_reaction'
    if cls == 2: return 'pick_grounded_only'
    return 'pick'

all_slots = set()
for b in BANKS.values(): all_slots.update(b['slots'].keys())

per_file, named = {}, collections.defaultdict(list)
TOT, DSTOT = collections.Counter(), collections.Counter()
for fp in sorted(glob.glob(f'{ROOT}/game/assets/movesets/*.json')):
    ms = json.load(open(fp))
    if not isinstance(ms.get('moves'), dict): continue
    stem = os.path.basename(fp)[:-5]; cid = ms.get('fighter') or stem
    info = IDX.get(cid) or IDX.get(stem) or {'anim_bank': ms.get('anim_bank'), 't3_source': ms.get('t3_source')}
    bank = bank_id_for(cid, info); bdir = T3_BANKS.get(bank) if bank else None
    brows = BANKS[bdir]['rows'] if bdir in BANKS else {}
    own_slots = BANKS[bdir]['slots'] if bdir in BANKS else {}
    c, dc = collections.Counter(), collections.Counter()
    for key, mv in ms['moves'].items():
        if not isinstance(mv, dict): continue
        c['moves'] += 1
        dmg = mv.get('damage'); damaging = isinstance(dmg, (int, float)) and dmg > 0
        thr = mv.get('move_class') == 'throw' or bool(mv.get('isGrab')) or \
            (isinstance(mv.get('t3_condition'), (int, float)) and 2 <= mv['t3_condition'] <= 0x17)
        if thr: c['throws'] += 1
        if not damaging: c['no_damage'] += 1
        t = mv.get('t3_row')
        cls = None; mism = False
        if t is None:
            cls = 'no_t3_row'
            if damaging and not thr:
                at3 = mv.get('anim_t3')
                if isinstance(at3, dict) and at3.get('row') is not None:
                    adir = T3_BANKS.get(SOURCE_TO_BANK.get(at3.get('bank')) or '')
                    if adir and adir == bdir:
                        r2 = brows.get(str(at3['row']))
                        if r2 and classify_row(r2) in ('pick', 'pick_grounded_only'):
                            g = str(at3.get('match', '')).split('(')[0].strip()
                            tier = 'proven' if g in PROVEN else ('mid' if g in MID else ('guess' if g in GUESS else 'other'))
                            dc[f'fillable_{tier}'] += 1
                        else: dc['animrow_not_pickable'] += 1
                    else: dc['animrow_other_bank'] += 1
        else:
            if isinstance(t, list) and len(t) > 1:
                c['multirow_list'] += 1
                last = t[-1]
                r_last = brows.get(str(last)) or COMMON.get(str(last))
                named['multirow'].append({'file': stem, 'move': key, 't3_row': t,
                    'last_row_pickable': bool(r_last) and classify_row(r_last) in ('pick', 'pick_grounded_only')})
            row = brows.get(js_key(t)) or COMMON.get(js_key(t))
            if row is None:
                cls = 'row_miss'
                if len(named[f'rowmiss::{stem}']) < 3: named[f'rowmiss::{stem}'].append({'move': key, 't3_row': t})
            else:
                cls = classify_row(row)
                if cls in ('pick', 'pick_grounded_only'):
                    src = mv.get('t3_source') or ms.get('t3_source')
                    sb = SOURCE_TO_BANK.get(src) if src else bank
                    sdir = T3_BANKS.get(sb) if sb else None
                    if sdir and bdir and sdir != bdir: c['pick_src_mismatch'] += 1; mism = True
                    rec = RECORDS[row[0]]
                    if ('0x%x' % rec[0]) not in own_slots and ('0x%x' % rec[0]) not in all_slots: c['slot_nowhere'] += 1
        c[cls] += 1
        if damaging and not thr:
            dc['dmg_strikes'] += 1; dc[cls] += 1
            if mism: dc['pick_src_mismatch'] += 1
    per_file[stem] = {'bank': bank, 'dir': bdir, **dict(c), 'ds': dict(dc)}
    TOT.update(c); DSTOT.update(dc)

out = {'population_files': len(per_file), 'totals': dict(TOT), 'dmg_strike_totals': dict(DSTOT),
       'per_file': per_file, 'named': dict(named),
       'bank_coverage': {d: {'wanted': v['wanted'], 'baked': v['baked'], 'missing': v['missing']} for d, v in COV.items()},
       'records': len(RECORDS), 'common_rows': len(COMMON)}
if '--out' in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)
print('files', len(per_file)); print('TOTALS', dict(TOT)); print('DMG-STRIKE', dict(DSTOT))
