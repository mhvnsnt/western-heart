import struct
p='/home/hatch/workspace/doa4-bass/default_pe.bin'
d=open(p,'rb').read(0x4000)
peoff=struct.unpack('<I', d[0x3c:0x40])[0]
print('pe hdr at', hex(peoff), d[peoff:peoff+4])
nsec=struct.unpack('<H', d[peoff+6:peoff+8])[0]
optsz=struct.unpack('<H', d[peoff+20:peoff+22])[0]
imgbase=struct.unpack('<I', d[peoff+24+28:peoff+24+32])[0]
entry=struct.unpack('<I', d[peoff+24+16:peoff+24+20])[0]
print(f'nsec={nsec} optsz={optsz} imagebase={imgbase:#x} entry_rva={entry:#x}')
soff=peoff+24+optsz
for i in range(nsec):
    s=d[soff+i*40:soff+i*40+40]
    name=s[:8].split(b'\0')[0].decode()
    vsz,va,rsz,roff=struct.unpack('>IIII', s[8:24]) if False else struct.unpack('<IIII', s[8:24])
    print(f'{name:8s} VA={va:#010x} VSZ={vsz:#x} RAW={roff:#x} RSZ={rsz:#x}')
print('filesize', 23068672)
