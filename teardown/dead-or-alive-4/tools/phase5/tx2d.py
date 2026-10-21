import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
xp=g['xpr2_offset']
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
recs=[]; pos=xp
while pos < len(d)-16:
    m=d[pos:pos+4]
    if m in (b'XPR2',b'USER',b'TX2D',b'VBUF',b'IBUF'):
        f1,f2,f3=struct.unpack('>3I', d[pos+4:pos+16]); recs.append((m.decode(),f1,f2)); pos+=16
    elif m==b'\x00\x00\x00\x00': pos+=16
    else: break
tx=[r for r in recs if r[0]=='TX2D']
print('TX2D records:', len(tx))
for i,(m,f1,f2) in enumerate(tx[:14]):
    desc=struct.unpack('>10I', d[xp+f1:xp+f1+40])
    print(f'TX2D#{i} f1={f1:#x} f2={f2} desc={[hex(x) for x in desc]}')
