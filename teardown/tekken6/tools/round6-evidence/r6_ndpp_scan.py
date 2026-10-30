import struct, zlib, json, collections
WORK="/home/hatch/workspace/_t6r4-work"
OFF=38592*2048; SIZE=81591641
def scan(path, label):
    with open(path,'rb') as f:
        f.seek(OFF); data=f.read(SIZE)
    idxs=[]; i=0
    while True:
        j=data.find(b'GZIP', i)
        if j<0: break
        idxs.append(j); i=j+4
    stats=collections.Counter(); decoded_magics=collections.Counter(); total_out=0; examples=[]
    for j in idxs:
        if j+20>len(data): stats['truncated_header']+=1; continue
        w=struct.unpack('<5I', data[j:j+20])
        if not (w[1]==1 and w[2]==1 and 0<w[4]<=len(data)-j-20 and 0<w[3]<50_000_000):
            stats['bad_header_fields']+=1; continue
        stats['header_ok']+=1
        body=data[j+20:j+20+w[4]]
        if body[:2]!=b'\x78\xda':
            stats['bad_zlib_magic']+=1; continue
        try:
            out=zlib.decompress(body)
        except Exception:
            stats['zlib_fail']+=1; continue
        if len(out)!=w[3]:
            stats['len_mismatch']+=1; continue
        if zlib.adler32(out)!=struct.unpack('>I', body[-4:])[0]:
            stats['adler_mismatch']+=1; continue
        stats['adler_exact']+=1; total_out+=len(out)
        decoded_magics[out[:4]]+=1
        if len(examples)<8: examples.append((j,w[3],out[:16].hex()))
    print(label, "magic", len(idxs), dict(stats), "total_out", total_out, flush=True)
    print(label, "decoded first4:", {k.decode('latin1'):v for k,v in decoded_magics.most_common(20)}, flush=True)
    print(label, "examples", examples, flush=True)
    return {"label":label,"magic_count":len(idxs),"stats":dict(stats),"total_out":total_out,
            "decoded_first4":{k.hex():v for k,v in decoded_magics.items()},"examples":examples}
res=[]
res.append(scan(f"{WORK}/recon/x/tekken6/work/decrypt3/bulk_decrypted.bin","OLD-CORRUPT"))
res.append(scan(f"{WORK}/bulk_decrypted_r6.bin","NEW-CLEAN-R6"))
json.dump(res, open(f"{WORK}/r6scratch/r6_ndpp_scan.json","w"), indent=1)
print("DONE")
