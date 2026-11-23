#!/usr/bin/env python3
"""Tekken + KoC2 seam-gate check (headless, no browser, no match run).

Applies the same gates the in-page __match driver enforces in
~/workspace/bannon-all-clips-working-show/match-run.py (launch-spot +
target-state + verified-clip checks; a clip that is undecoded,
wrong-spot, or not-in-hand is REFUSED, never played) plus the
library-mapping gate, to every Tekken clip in pairing-audit.json and
to KoC2 as a whole. The renderer in match.html plays 2K26 quaternion
clips only: position-pose JSON (Tekken IK / VPW2) is refused by the
same gate as the VPW2 Frog Splash probe in match-run.py, because no
position->rig IK retarget build exists.

Gates per Tekken clip:
  G1 decoded_and_in_hand — clip JSON exists in Bannon repo
       assets/moves/clips/ (yes for all 383 per manifest provenance).
  G2 receiver_present — paired receiver clip exists (no for all 383).
  G3 root_travel_present — root x/z travel in the clip (no for all 383;
       converter v1 drops it; lives in the WH source pack root track).
  G4 library_mapped — mapped to a named Bannon library move (no for all).
  G5 contact_keyframe_present — clip covers its registry first active
       frame. Known-fail: the 14 truncated clips + the 54 DW clips (no
       active frames by design, per manifest note). The other 315 are
       UNASSESSED per-clip here (needs per-file active_frames reads);
       they are NOT passed, they are unassessed — and G2/G3/G4 already
       fail every clip regardless, so the overall result does not depend
       on G5.
  G6 renderer_can_play — 2K26 quat clip the match renderer accepts
       (no for all 383: position-pose JSON, no retarget build).

KoC2 gates: G1 fails outright — 0 decoded motion, 16,660 MVS files
uncracked. No per-move gates are meaningful until Route A lands.

Output: gate-check.json. Exit 0 always (a refusal is a finding, not
a script error); the JSON carries the verdicts.
"""
import json

AUDIT = '/home/hatch/workspace/bannon-all-moves-all-games-show/tekken-koc2/pairing-audit.json'
OUT = '/home/hatch/workspace/bannon-all-moves-all-games-show/tekken-koc2/gate-check.json'

audit = json.load(open(AUDIT))
rows = audit['clips']
assert len(rows) == 383

DW_N = 54  # manifest: 54 DW clips have no active frames by design
results = []
for r in rows:
    g1 = True   # clip JSON in repo per manifest provenance
    g2 = r['receiver'] is not None
    g3 = r['root_horizontal_travel_m'] is not None
    g4 = r['bannon_library_move'] is not None
    if r['truncated_before_contact']:
        g5 = False
        g5_note = 'known-fail: truncated before first active frame'
    elif r['source'] == 'tekken5_dw':
        g5 = False
        g5_note = 'known-fail: DW clips have no active frames by design'
    else:
        g5 = None
        g5_note = 'unassessed per-clip (needs per-file active_frames read); not a pass'
    g6 = False  # position-pose JSON; renderer plays 2K26 quat clips only
    failures = []
    if not g2:
        failures.append('G2 receiver_present')
    if not g3:
        failures.append('G3 root_travel_present')
    if not g4:
        failures.append('G4 library_mapped')
    if g5 is False:
        failures.append('G5 contact_keyframe_present')
    if not g6:
        failures.append('G6 renderer_can_play')
    results.append({
        'clip_id': r['clip_id'], 'source': r['source'],
        'gates': {'G1_decoded_in_hand': g1, 'G2_receiver': g2,
                  'G3_root_travel': g3, 'G4_library_mapped': g4,
                  'G5_contact_keyframe': g5, 'G6_renderer_can_play': g6},
        'g5_note': g5_note,
        'playable_in_real_match': False,
        'gate_failures': failures,
    })

n_g5_known_fail = sum(1 for x in results if x['gates']['G5_contact_keyframe'] is False)
n_g5_unassessed = sum(1 for x in results if x['gates']['G5_contact_keyframe'] is None)
by_src = {}
for x in results:
    by_src.setdefault(x['source'], {'total': 0, 'playable': 0})
    by_src[x['source']]['total'] += 1
    by_src[x['source']]['playable'] += 1 if x['playable_in_real_match'] else 0

doc = {
    'generated': '2026-11-22/23',
    'lane': 'Coordinator lane 3/4 — Tekken + KoC2 moves (owner order 2026-11-22)',
    'method': 'Headless gate evaluation from pairing-audit.json (manifest-grounded). No browser, no match run: match-run.py needs Playwright/Chromium (subagent cannot run a live browser) and the gates refuse every Tekken/KoC2 clip before any frame renders, so a browser run would refuse 383/383 + KoC2 without producing a frame.',
    'gates': {
        'G1_decoded_in_hand': 'clip JSON exists in Bannon repo assets/moves/clips/',
        'G2_receiver': 'paired receiver clip exists',
        'G3_root_travel': 'root x/z travel present in the clip',
        'G4_library_mapped': 'mapped to a named Bannon library move',
        'G5_contact_keyframe': 'clip covers its registry first active frame',
        'G6_renderer_can_play': 'match renderer accepts the clip format (2K26 quat clips only today)',
    },
    'tekken': {
        'total': 383,
        'playable_in_real_match': 0,
        'by_source': by_src,
        'g5_known_fail': n_g5_known_fail,
        'g5_unassessed': n_g5_unassessed,
        'universal_failures': ['G2 receiver_present (383/383)', 'G3 root_travel_present (383/383)',
                               'G4 library_mapped (383/383)', 'G6 renderer_can_play (383/383)'],
    },
    'koc2': {
        'decoded_clips': 0,
        'mvs_files': 16660,
        'playable_in_real_match': 0,
        'gate_failures': ['G1 decoded_in_hand (0 decoded motion exists)'],
    },
    'match_proof': {
        'moves_played': 0,
        'stills': 0,
        'mp4_videos': 0,
        'rigs_ready': 'Finn / Big Cass / Elias / Enzo port zips present in workspace (EnzoAndCassPorts.zip 1.1 GB, EliasPorts.zip 167 MB, FinnBalorEntrancePort.zip 83 MB) but unopened here — ports are 2K26 .clips banks, not Tekken/KoC2 clips, and no Tekken/KoC2 clip passes the gates to play on them.',
        'note': 'No stills or MP4s were produced in this lane because producing them would require playing a clip that fails the gates — i.e. inventing a match. stills/ and video/ hold NOT-PROOF-YET notes instead. The first real Tekken/KoC2 match proof is owed after: (1) King artifact rescue + --compression none re-extract, (2) pairing + root restore, (3) a position-pose -> rig retarget build for the match renderer, (4) a VM/browser bout run.',
    },
    'results': results,
}
json.dump(doc, open(OUT, 'w'), indent=1)
print('wrote', OUT)
print('Tekken playable:', 0, '/ 383')
print('G5 known-fail:', n_g5_known_fail, '| G5 unassessed:', n_g5_unassessed)
print('KoC2 playable: 0 / 16660 MVS (0 decoded)')
