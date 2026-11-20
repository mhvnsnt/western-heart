"""Round 7: re-extract NDPP bounding boxes from the CLEAN bulk slice.
Same validated method as round 2 (models/tools/extract_boxes.py): per
NDPP section, scan the payload for 24-f32 axis-aligned box patterns
(|v|<2, <=2 unique values per axis across the 8 corners x ~50000 =
descriptor bbox scale). Difference vs round 2: runs on the verified
clean bulk and over EVERY NDPP occurrence (1,565), not only the old
357-section chain on corrupt bytes. Output: r7_boxes.json (workdir
scratch + summary counts printed)."""
import struct, json
import numpy as np
WORK='/home/hatch/workspace/_t6r4-work'
OFF=38592*2048; SIZE=81591641
with open(f'{WORK}/bulk_decrypted_r6.bin','rb') as f:
    f.seek(OFF); data=f.read(SIZE)
def find_boxes(payload):
    fl=np.frombuffer(payload[:len(payload)//4*4], dtype='<f4')
    n=len(fl); boxes=[]
    if n<24: return boxes
    ok_mask=(np.abs(fl)<2.0) & np.isfinite(fl)
    cs=np.concatenate(([0], np.cumsum(ok_mask.astype(np.int64))))
    cand=np.nonzero((cs[24:]-cs[:-24])==24)[0]
    used_until=-1
    for i in cand:
        if i<used_until: continue
        verts=fl[i:i+24].reshape(8,3)
        ok=True
        for ax in range(3):
            u=np.unique(np.round(verts[:,ax],4))
            if len(u)>3 or len(u)<2: ok=False; break
        if ok:
            boxes.append({'word_off':int(i),'verts':verts.tolist()}); used_until=i+24
    return boxes
sections=[]; i=0; total=0
while True:
    j=data.find(b'NDPP', i)
    if j<0: break
    i=j+4
    size,flags=struct.unpack_from('<II', data, j+4)
    if not (20<=size<=2_000_000 and j+size<=len(data)): continue
    boxes=find_boxes(data[j+20:j+size])
    if boxes:
        sections.append({'rel':j,'size':size,'flags':hex(flags),'boxes':boxes})
        total+=len(boxes)
print('sections with boxes:', len(sections), 'total boxes:', total)
json.dump(sections, open(f'{WORK}/r7scratch/r7_boxes.json','w'))
print('wrote r7_boxes.json')
