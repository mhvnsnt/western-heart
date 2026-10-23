import struct, collections, math
d=open('/home/hatch/workspace/_doa4p2-scratch/p7/data/anm.afs','rb').read()
H=d[:0x6B000]; n=len(H)//16
# equality matrix within record
print('byte-position equality rate (i==j) within 16B record:')
for i in range(16):
    row=[]
    for j in range(16):
        if i==j: row.append('  .  ')
        else:
            r=sum(1 for k in range(n) if H[k*16+i]==H[k*16+j])/n
            row.append(f'{r:.2f}' if r>=0.08 else '  -  ')
    print(i, ' '.join(row))
# per-position entropy
def ent(bs):
    c=collections.Counter(bs); N=len(bs)
    return -sum(v/N*math.log2(v/N) for v in c.values())
for i in range(16):
    col=bytes(H[k*16+i] for k in range(n))
    print(f'pos{i}: ent={ent(col):.2f} top={collections.Counter(col).most_common(3)}')
# XOR consecutive records -> float plausibility
def plaus(bs):
    ok=tot=0
    for i in range(0,len(bs)-3,4):
        f=struct.unpack_from('>f',bs,i)[0]; tot+=1
        if f==f and abs(f)<=10.0 and f!=0.0: ok+=1
    return ok/tot
x=bytes(a^b for a,b in zip(H, H[16:]))
print('XOR-consecutive plaus:', round(plaus(x),3), 'raw head plaus:', round(plaus(H),3))
# SUB consecutive (byte-wise) distribution
s=bytes((a-b)&0xff for a,b in zip(H[16:],H))
print('byte-diff==0 rate:', s.count(0)/len(s))
# cross-record equality at same position (rec k vs k+1 same pos)
for i in range(16):
    r=sum(1 for k in range(n-1) if H[k*16+i]==H[(k+1)*16+i])/(n-1)
    print(f'same-pos next-rec eq pos{i}: {r:.3f}')
# global stream: byte at offset t vs t+L equality for L in 1..32 (whole head as stream)
for L in range(1,33):
    r=sum(1 for t in range(len(H)-L) if H[t]==H[t+L])/(len(H)-L)
    if r>0.03: print(f'stream lag {L}: eq {r:.3f}')
