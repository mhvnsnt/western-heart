#!/usr/bin/env python3
"""Round 11 Job 4: B3 assignment via bulk (DATA401 slice) index order.
Anchors = full-character-pattern containers in the r7 census (bulk order).
Tests the contiguity hypothesis and scores segment plausibility.
Emits r11_b3_assignment.json with per-container confidence labels."""
import json, os, collections

CEN = json.load(open('/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round7-evidence/r7_census.json'))
cs = CEN['containers']

def classify(c):
    slots = {s['slot']: s for s in c.get('slots', [])}
    if c['kind'] == 'B-texture': return 'B-texture'
    if c['kind'] == 'dir-other': return 'dir-other'
    magics = {s['slot']: s['magic'] for s in c.get('slots', [])}
    sizes = {s['slot']: s['size'] for s in c.get('slots', [])}
    has_bone = any(m == 'BONE' for m in magics.values())
    has_ndpp = any(m == 'NDPP' for m in magics.values())
    full = (magics.get(1) == 'BONE' and magics.get(0) == 'NDPP' and magics.get(10) == 'NDPP'
            and magics.get(12) == 'BONE' and sizes.get(12) == 1664)
    if full: return 'full-char'
    if sizes.get(0) == 624 and sizes.get(9, 0) > 10000: return 'stage-pattern'
    if has_bone: return 'boned-part'
    if has_ndpp: return 'rigid-part'
    return 'A-other'

for c in cs: c['class'] = classify(c)
counts = collections.Counter(c['class'] for c in cs)
print('slice class counts:', dict(counts))

anchors = [i for i, c in enumerate(cs) if c['class'] == 'full-char']
print('full-char anchors:', len(anchors), 'at n =', anchors)

# segments: from each anchor (inclusive) to next anchor (exclusive)
segs = []
for k, a in enumerate(anchors):
    b = anchors[k + 1] if k + 1 < len(anchors) else len(cs)
    seg = cs[a:b]
    segs.append((a, b, collections.Counter(c['class'] for c in seg), sum(c['len'] for c in seg)))
for k, (a, b, cnt, total) in enumerate(segs):
    print(f'seg{k:2d} anchor n={a:4d} len={b-a:4d} pkgs bytes={total:9d} mix={dict(cnt)}')
pre = cs[:anchors[0]] if anchors else []
print('pre-first-anchor containers:', len(pre), collections.Counter(c['class'] for c in pre))
post_classes = collections.Counter()
# stage-pattern clustering: positions of stage-pattern containers relative to segments
stage_pos = [i for i, c in enumerate(cs) if c['class'] == 'stage-pattern']
def seg_of(i):
    for k, a in enumerate(anchors):
        if a <= i and (k + 1 == len(anchors) or i < anchors[k + 1]): return k
    return -1
print('stage-pattern containers by segment:', collections.Counter(seg_of(i) for i in stage_pos))
# A/B interleave check: container right after each anchor
after = collections.Counter(cs[a + 1]['class'] for a in anchors if a + 1 < len(cs))
print('class of container immediately after each anchor:', dict(after))
# segment length stats
lens = [b - a for a, b, _, _ in segs]
print('segment lengths: min', min(lens), 'max', max(lens), 'mean', sum(lens) / len(lens))
boned = [dict(cnt).get('boned-part', 0) for _, _, cnt, _ in segs]
print('boned-part per segment: min', min(boned), 'max', max(boned), 'mean', sum(boned) / len(boned))

# Assignment JSON: every A-model slice container gets a label.
# anchor-proven: the 28 full-char anchors themselves + a B-texture IMMEDIATELY
# following an A container of the same segment start? Keep conservative:
# proven = full-char anchors only (structure-proven, character identity unnamed).
# inferred = boned-part / rigid-part / B-texture / A-other / dir-other inside a
# segment (assigned segment index = preceding anchor). stage-pattern and
# pre-first-anchor = unassigned.
out = {'source': 'round7-evidence/r7_census.json (5,470 containers, entry-87 slice, bulk order)',
       'method': 'anchors = full-character-pattern containers in bulk order; contiguity hypothesis scored in JOB4-B3-ASSIGNMENT.md',
       'anchors': [{'n': a, 'rel': cs[a]['rel'], 'sha256': cs[a]['sha256'], 'len': cs[a]['len']} for a in anchors],
       'assignments': []}
lab_counts = collections.Counter()
for i, c in enumerate(cs):
    if c['class'] == 'full-char':
        lab, seg = 'anchor-proven', seg_of(i)
    elif i < anchors[0] or c['class'] == 'stage-pattern':
        lab, seg = 'unassigned', None
    else:
        lab, seg = 'contiguity-inferred', seg_of(i)
    lab_counts[lab] += 1
    out['assignments'].append({'n': i, 'rel': c['rel'], 'sha256': c['sha256'], 'len': c['len'],
                               'kind': c['kind'], 'class': c['class'], 'confidence': lab,
                               'segment': seg})
out['label_counts'] = dict(lab_counts)
out['segment_stats'] = [{'segment': k, 'anchor_n': a, 'containers': b - a, 'bytes': t,
                         'mix': dict(cnt)} for k, (a, b, cnt, t) in enumerate(segs)]
json.dump(out, open('/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round11-evidence/r11_b3_assignment.json', 'w'), indent=1)
print('label counts:', dict(lab_counts))
