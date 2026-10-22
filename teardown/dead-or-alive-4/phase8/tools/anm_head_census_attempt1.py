import struct, collections, json
d=open('/home/hatch/workspace/_doa4p2-scratch/p7/data/anm.afs','rb').read()
print('size',len(d),hex(len(d)))
HEAD_END=0x6B000
head=d[:HEAD_END]
# 16B records census
n=HEAD_END//16
fields=[collections.Counter() for _ in range(4)]
first_bytes=collections.Counter()
for i in range(n):
    r=head[i*16:(i+1)*16]
    for f in range(4):
        fields[f][struct.unpack_from('>I',r,f*4)[0]]+=1
    first_bytes[r[0]]+=1
for f in range(4):
    print(f'field+{f*4}: distinct={len(fields[f])} top5={fields[f].most_common(5)}')
# +8 field full enumeration
c8=fields[2]
print('PLUS8 distinct count:',len(c8))
print('PLUS8 all (hex:count):')
print(' '.join(f'{v:08x}:{c}' for v,c in sorted(c8.items())))
# u16 views
for off in (0,2,4,6,8,10,12,14):
    c=collections.Counter()
    for i in range(n):
        c[struct.unpack_from('>H',head,i*16+off)[0]]+=1
    print(f'u16@{off}: distinct={len(c)} top3={[(hex(k),v) for k,v in c.most_common(3)]}')
