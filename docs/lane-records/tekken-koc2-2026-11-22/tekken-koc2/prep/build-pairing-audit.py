#!/usr/bin/env python3
"""Build the Tekken per-clip pairing audit from the Bannon repo manifest.

Input: /tmp/tekken-manifest.json — assets/moves/ik/tekken/manifest.json,
fetched read-only via the GitHub connector from mhvnsnt/Bannon main
(2026-11-22/23). No clip is re-decoded; no field is invented.

Per-clip facts come ONLY from the manifest (file list + named sets) and
from the three IK files sampled read-only this lane (T3_KING_R127,
T7_KING_mokg_tkr_DVD, T5DW_PANTERA_ikdv_36_nage_y), which all show the
same shape the manifest/README state for ALL 383: clip_refs.receiver
null, reaction null, positioning.attacker_receiver null,
root_horizontal_travel_m null, bannon_library_move null, coverage
partial. Per-clip move_class is NOT in the manifest (only totals), so
it is NOT asserted per clip — only the named throw_clips set (18) is.

Verdicts:
  NOT_A_MOVE   — non-wrestling beam clips (5); nothing to pair.
  ADAPTATION   — MADE clips (3); not decoded motion, wire only labelled.
  BLOCKED_TRUNCATED — ends before its registry first active frame (14);
    no contact keyframe; needs source-pack re-bake.
  BLOCKED_NO_RECEIVER — everything else; solo-only, needs a receiver
    (AKI P1/P2 pair, WMXIX once identified, or authored reaction) plus
    root x/z restore from the western-heart source pack root track.
"""
import json

MANIFEST = '/tmp/tekken-manifest.json'
OUT = '/home/hatch/workspace/bannon-all-moves-all-games-show/tekken-koc2/pairing-audit.json'

m = json.load(open(MANIFEST))
files = m['files']                      # 383 filenames, manifest order
throw = set(m['throw_clips'])           # 18
contact = set(m['contact_beyond_clip'])  # 14
spike = set(m['spike_exception_clips'])  # 5
nonw = set(m['non_wrestling_motion_clips'])  # 5
made = set(m['made_clips'])             # 3

def source_of(name):
    if name.startswith('T3_'):
        return 'tekken3'
    if name.startswith('T7_'):
        return 'tekken7'
    if name.startswith('T5DW_'):
        return 'tekken5_dw'
    if name.startswith('MADE_'):
        return 'western_heart_made'
    return 'UNKNOWN'

rows = []
for fn in files:
    cid = fn[:-5]  # strip .json
    src = source_of(cid)
    is_throw_clip = cid in throw
    is_contact = cid in contact
    is_spike = cid in spike
    is_nonw = cid in nonw
    is_made = cid in made
    if is_nonw:
        verdict = 'NOT_A_MOVE'
        basis = 'Manifest non_wrestling_motion_clips: beam effect, not a wrestling move.'
    elif is_made:
        verdict = 'ADAPTATION'
        basis = 'MADE clip: adaptation of decoded T3 King motion, NOT decoded motion (tools/tekken/README.md). Wire only labelled as adaptation.'
    elif is_contact:
        verdict = 'BLOCKED_TRUNCATED'
        basis = 'Manifest contact_beyond_clip: clip ends before registry first active frame; no contact keyframe. Full motion lives in the western-heart source pack row; needs re-bake.'
    else:
        verdict = 'BLOCKED_NO_RECEIVER'
        basis = 'Solo-only attacker motion. No receiver clip exists in the batch or registry; root x/z dropped by converter v1 (lives in WH source pack root track).'
    pair_lead = None
    if src == 'tekken7':
        pair_lead = ('King .tkmvst only: receiver move 554 found for both King throws in '
                     'T7_King.tkmvst (2,787 moves). Needs artifact download before '
                     '2027-02-19 + re-extract --compression none + tkmvst_to_wh conversion. '
                     'Not attached to a specific clip id here — the .tkmvst move list is not in hand.')
    rows.append({
        'clip_id': cid,
        'source': src,
        'is_throw_clip': is_throw_clip,
        'truncated_before_contact': is_contact,
        'spike_exception': is_spike,
        'non_wrestling': is_nonw,
        'made_adaptation': is_made,
        'receiver': None,
        'reaction': None,
        'root_horizontal_travel_m': None,
        'bannon_library_move': None,
        'coverage': 'partial',
        'pairing_verdict': verdict,
        'pairing_basis': basis,
        'pair_lead': pair_lead,
    })

assert len(rows) == 383, len(rows)
from collections import Counter
by_src = Counter(r['source'] for r in rows)
by_verdict = Counter(r['pairing_verdict'] for r in rows)
assert by_src == {'tekken3': 230, 'tekken7': 96, 'tekken5_dw': 54,
                  'western_heart_made': 3}, dict(by_src)
assert sum(1 for r in rows if r['is_throw_clip']) == 18
assert sum(1 for r in rows if r['truncated_before_contact']) == 14
assert sum(1 for r in rows if r['spike_exception']) == 5
assert sum(1 for r in rows if r['non_wrestling']) == 5
assert sum(1 for r in rows if r['made_adaptation']) == 3
assert all(r['receiver'] is None and r['reaction'] is None
           and r['root_horizontal_travel_m'] is None
           and r['bannon_library_move'] is None for r in rows)
# R127 is both a throw clip and truncated — the overlap the manifest implies.
r127 = [r for r in rows if r['clip_id'] == 'T3_KING_R127'][0]
assert r127['is_throw_clip'] and r127['truncated_before_contact']
assert r127['pairing_verdict'] == 'BLOCKED_TRUNCATED'

doc = {
    'generated': '2026-11-22/23',
    'lane': 'Coordinator lane 3/4 — Tekken + KoC2 moves (owner order 2026-11-22)',
    'source_manifest': 'mhvnsnt/Bannon main assets/moves/ik/tekken/manifest.json (generated 2026-11-19, lane K3), fetched read-only via GitHub connector this lane; SHA d5eca46bff5d576e0528c9aee1d2d2290207f9ac',
    'sampled_ik_files': ['T3_KING_R127 (throw, truncated)', 'T7_KING_mokg_tkr_DVD (spike exception)', 'T5DW_PANTERA_ikdv_36_nage_y'],
    'sample_shape': 'All three sampled IK files: clip_refs.receiver null, reaction null, positioning.attacker_receiver null, root_horizontal_travel_m null, bannon_library_move null, coverage partial. Manifest + README state the same for all 383.',
    'counts': {
        'total': 383,
        'by_source': dict(by_src),
        'by_pairing_verdict': dict(by_verdict),
        'throw_clips_named': 18,
        'move_class_throw_total': 27,
        'move_class_note': 'Manifest move_class totals are signature 4 / strike 136 / throw 27 / mixed 63 / none 151 / special 2. Per-clip move_class is NOT in the manifest and is NOT asserted per row here. throw_clips (18 named) != move_class throw (27): 9 throw-classified moves share clips or are classified without a named throw clip entry — do not force the two numbers to match.',
        'registry_moves_in_scope': 1002,
        'registry_moves_with_clip': 916,
        'registry_moves_without_clip': 86,
        'registry_without_clip_note': '82 tekken8 data-only (WH holds clip-MAPS only, no T8 clip data packs) + 4 western-heart originals unauthored (Pantera Claw Driver, Pantera Hunt, Yukihyo Storm Shadow Lesson, Yukihyo Whiteout).',
        'mapped_named_library_moves': 0,
    },
    'clips': rows,
}
json.dump(doc, open(OUT, 'w'), indent=1)
print('wrote', OUT)
print('by_source:', dict(by_src))
print('by_verdict:', dict(by_verdict))
print('throw clips:', sum(1 for r in rows if r['is_throw_clip']),
      '| truncated:', sum(1 for r in rows if r['truncated_before_contact']),
      '| overlap throw+truncated:', sum(1 for r in rows if r['is_throw_clip'] and r['truncated_before_contact']))
