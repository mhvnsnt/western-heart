import struct
ELF='/home/hatch/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF'
data=open(ELF,'rb').read()
BASE=0x08803000
def v2o(v): return v-BASE
def o2v(o): return o+BASE
def words(v0,v1):
    o=v2o(v0)
    return [struct.unpack_from('<I',data,o+4*i)[0] for i in range((v1-v0)//4)]

print("=== NTPP RTTI/vtable region (template) 0x08b9c540..0x08b9c620 ===")
for i,w in enumerate(words(0x08b9c540,0x08b9c620)):
    v=0x08b9c540+4*i
    s=''
    if 0x08800000<=w<0x08c80000: s='  <- ptr?'
    print(f'{v:#010x}: {w:#010x}{s}')
print("NTPP string bytes:", data[v2o(0x08b9c5b0):v2o(0x08b9c5b0)+32])

print()
print("=== datatextureroot string context ===")
so=data.find(b'tcb_datatextureroot')
print('full string at file off',hex(so),'vaddr',hex(o2v(so)), data[so:so+32])
print("region 0x08b93fc0..0x08b94100 words:")
for i,w in enumerate(words(0x08b93fc0,0x08b94100)):
    v=0x08b93fc0+4*i
    s=''
    if 0x08800000<=w<0x08c80000: s='  <- ptr?'
    print(f'{v:#010x}: {w:#010x}{s}')
print("ascii around string:", data[so-64:so+64])

print()
print("=== REGISTRY region 0x08bcfc00..0x08bcff00 ===")
for i,w in enumerate(words(0x08bcfc00,0x08bcff00)):
    v=0x08bcfc00+4*i
    tag=''
    if w==0x08ad161c: tag='  <<<< EMITTER'
    elif 0x08ad0000<=w<0x08ae0000: tag='  <- 0x08adxxxx code ptr'
    elif 0x08800000<=w<0x09000000: tag='  <- code-range ptr'
    elif 0x08b00000<=w<0x08d00000: tag='  <- data-range ptr'
    print(f'{v:#010x}: {w:#010x}{tag}')
