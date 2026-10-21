import struct
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
d=open(D+'anm.afs','rb').read()
def plaus(seg, endian):
    n=len(seg)//4; ok=0
    fmt=endian+'f'; ut=endian+'I'
    for i in range(n):
        f=struct.unpack(fmt, seg[i*4:i*4+4])[0]
        if f==f and abs(f)<=2.0 and f!=0.0: ok+=1
    return ok/n
def swap16(b):
    ba=bytearray(b)
    ba[0::2], ba[1::2] = b[1::2], b[0::2]
    return bytes(ba)
def swap32(b):
    ba=bytearray(len(b))
    for i in range(0, len(b)-3, 4):
        ba[i:i+4]=b[i:i+4][::-1]
    return bytes(ba)
regions={'head[0:0x68000]': d[:0x68000], 'trans[0x68000:0x6c000]': d[0x68000:0x6c000], 'float[0x70000:0x170000]': d[0x70000:0x170000], 'mid[0x1a0000:0x1b0000]': d[0x1a0000:0x1b0000], 'tail[0x2a1000:0x2af000]': d[0x2a1000:0x2af000]}
for rn, seg in regions.items():
    seg=seg[:len(seg)//4*4]
    print(f"{rn}: BE={plaus(seg,'>'):.3f} LE={plaus(seg,'<'):.3f} swap16+BE={plaus(swap16(seg),'>'):.3f} swap16+LE={plaus(swap16(seg),'<'):.3f} swap32+BE={plaus(swap32(seg),'>'):.3f}")
