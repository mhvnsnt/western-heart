import struct, collections, math, json
d=open('/home/hatch/workspace/_doa4p2-scratch/p7/data/anm.afs','rb').read()
print('size',len(d),hex(len(d)))
def ent(bs):
    c=collections.Counter(bs); n=len(bs)
    return -sum(v/n*math.log2(v/n) for v in c.values())
# region entropy scan 4KB blocks across whole file, find transitions
prev=None
for off in range(0,len(d),0x1000):
    e=ent(d[off:off+0x1000])
    tag=''
    if prev is not None and abs(e-prev)>0.7: tag=' <-- TRANSITION'
    if off<0x2000 or tag or off>=0x2A0000 and off<0x2B2000: print(f'{off:08x} ent={e:.2f}{tag}')
    prev=e
HEAD=d[:0x6B000]
# byte value histogram of head vs body sample
print('head byte0-of-16 hist top:', collections.Counter(HEAD[i] for i in range(0,len(HEAD),16)).most_common(5))
# check duplicated-byte structure: rate byte[2k]==byte[2k+1] overall in head
pairs=sum(1 for i in range(0,len(HEAD)-1,2) if HEAD[i]==HEAD[i+1]); print('head adjacent-even pair equal rate:',pairs/(len(HEAD)//2))
body=d[0x6B000:0x16B000]
pairs=sum(1 for i in range(0,len(body)-1,2) if body[i]==body[i+1]); print('body adjacent-even pair equal rate:',pairs/(len(body)//2))
# u32 at +8: decompose: hi u16 set, lo u16 set, cross counts
n=len(HEAD)//16
hi=collections.Counter(); lo=collections.Counter()
for i in range(n):
    v=struct.unpack_from('>I',HEAD,i*16+8)[0]; hi[v>>16]+=1; lo[v&0xffff]+=1
print('+8 hi u16 distinct',len(hi),sorted((hex(k),v) for k,v in hi.items()))
print('+8 lo u16 distinct',len(lo),sorted((hex(k),v) for k,v in lo.items()))
# phase7 said 68 distinct +8 values — check subranges: first 0x10000? per 64KB block distinct counts
for b in range(0,0x6B000,0x10000):
    c=set()
    for i in range(b//16,min((b+0x10000)//16,n)): c.add(struct.unpack_from('>I',HEAD,i*16+8)[0])
    print(f'block {b:06x}: +8 distinct={len(c)}')
# Are records maybe 8B not 16B? distinct u32 at each 4B slot of 8B records
for slot in range(2):
    c=collections.Counter(struct.unpack_from('>I',HEAD,i*8+slot*4)[0] for i in range(len(HEAD)//8))
    print(f'8B-record slot{slot}: distinct={len(c)} top={c.most_common(3)}')
# check +12 field: bytes 12,13 and 14,15 relation
r1213=sum(1 for i in range(n) if HEAD[i*16+12]==HEAD[i*16+13]); r1415=sum(1 for i in range(n) if HEAD[i*16+14]==HEAD[i*16+15])
print('b12==b13',r1213/n,'b14==b15',r1415/n)
# interpret +12 as 2x duplicated bytes -> de-duplicated 2 bytes per record? print samples
for i in range(6): print('rec',i,HEAD[i*16:(i+1)*16].hex(' '))
# autocorrelation: does head repeat with period? compare block at 0 vs search
import hashlib
blocks={}
dups=0
for off in range(0,0x6B000,16):
    h=hashlib.md5(HEAD[off:off+16]).digest()
    if h in blocks: dups+=1
    blocks[h]=off
print('dup 16B blocks in head:',dups,'unique:',len(blocks))
# chunk at 0x2A1000 census
chunk=d[0x2A1000:0x2AF000]
print('chunk 0x2A1000 len',hex(len(chunk)),'ent',round(ent(chunk),2))
c8=collections.Counter(struct.unpack_from('>I',chunk,i*16+8)[0] for i in range(len(chunk)//16))
print('chunk +8 distinct:',len(c8),'top:',c8.most_common(3))
# 0x2B0000 8-float groups: print a few, check smoothness
for base in (0x2B0000,0x2B1000,0x100000):
    vals=struct.unpack_from('>8f',d,base); print(hex(base),[round(v,4) for v in vals])
# zero regions map
z=[]
run=None
for off in range(0,len(d),0x800):
    if d[off:off+0x800]==b'\0'*0x800:
        if run is None: run=off
    else:
        if run is not None: z.append((hex(run),hex(off))); run=None
if run is not None: z.append((hex(run),hex(len(d))))
print('zero runs >=0x800:',z[:20])
