import struct, zlib, json, sys, os, random
WORK="/home/hatch/workspace/_t6r4-work"
sys.path.insert(0, f"{WORK}/wh/teardown/tekken6/tools")
man=json.load(open(f"{WORK}/recon/x/tekken6/work/decrypt3/manifest.json"))
new=open(f"{WORK}/bulk_decrypted_r6.bin","rb").read()
old=open(f"{WORK}/recon/x/tekken6/work/decrypt3/bulk_decrypted.bin","rb").read()
print("sizes", len(new), len(old), flush=True)
nb=len(new)//1024
diff_blocks=odd_diff=even_diff=0
for i in range(nb):
    s=i*1024
    if new[s:s+1024]!=old[s:s+1024]:
        diff_blocks+=1
        if i%2==1: odd_diff+=1
        else: even_diff+=1
print(f"blocks total={nb} differing={diff_blocks} ({diff_blocks/nb:.1%}) odd={odd_diff} even={even_diff}", flush=True)
gz=[f for f in man['files'] if f['magic'].startswith('GZIP')]
npass=0
for idx,f in enumerate(gz):
    off=f['start_rel']*2048
    d=new[off:off+f['size']]
    if f['magic']=='GZIP+prefix16': d=d[16:]
    w=struct.unpack('<5I', d[:20])
    out=zlib.decompress(d[20:20+w[4]])
    ok=len(out)==w[3] and zlib.adler32(out)==struct.unpack('>I', d[20+w[4]-4:20+w[4]])[0]
    npass+=ok
print(f"TOP76 FROM R6 BULK FILE: {npass}/76", flush=True)
from bulk_decrypt import decrypt_bulk_bytes, BULK0
iso=open(f"{WORK}/iso/tekken6-psp.iso","rb")
random.seed(6)
s_end=os.path.getsize(f"{WORK}/iso/tekken6-psp.iso")//2048
okc=0; trials=40
for _ in range(trials):
    s=random.randrange(BULK0, s_end)
    iso.seek(s*2048); raw=iso.read(2048)
    dec=decrypt_bulk_bytes(raw, (s-BULK0)*2048)
    if dec==new[(s-BULK0)*2048:(s-BULK0)*2048+2048]: okc+=1
print(f"FRESH SPOT CHECK: {okc}/{trials}", flush=True)
OFF=38592*2048; SIZE=81591641
print("NDPP entry87 slice old=", old[OFF:OFF+SIZE].count(b'NDPP'), "new=", new[OFF:OFF+SIZE].count(b'NDPP'), flush=True)
print("GMO whole bulk old=", old.count(b'GMO\x00'), "new=", new.count(b'GMO\x00'), "MOTA new=", new.count(b'MOTA'), flush=True)
d0=open(f"{WORK}/decoded76/idx00_entry454.bin","rb").read()
print("idx0 NDPP count", d0.count(b'NDPP'), flush=True)
json.dump({"diff_blocks":diff_blocks,"total_blocks":nb,"odd_diff":odd_diff,"even_diff":even_diff,"top76_from_bulk":npass,"spot":okc}, open(f"{WORK}/r6scratch/r6_bulk_verify.json","w"), indent=1)
print("DONE", flush=True)
