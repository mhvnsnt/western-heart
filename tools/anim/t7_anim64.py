#!/usr/bin/env python3
"""T7 0x64 (compressed) animation decoder.
Port of TKMovesets2 Utils/Animations_T_x64.cpp ParseAnimation0x64 (Kiloutre, GPL-3.0),
itself a decompilation of Tekken 7's own routine. Reads big- or little-endian anims.
Output per frame: bone_count x 3 floats (short bones = euler radians, float bones = translation)."""
import struct
MULT = 0.000095873802  # pi/32769
def s16(v): v &= 0xFFFF; return v-0x10000 if v & 0x8000 else v
def is_short(d): return 4 <= d <= 7

class BS:
    __slots__=('d','p','rem','sat')
    def __init__(s,d,p,rem): s.d=d; s.p=p; s.rem=rem; s.sat=2
    def get(s,a):
        sat=s.sat; rem=s.rem
        if sat < a:
            it=((a-sat-1)>>3)+1; sat+=8*it
            for _ in range(it):
                rem=(s.d[s.p] | (rem<<8)) & 0xFFFFFFFF; s.p+=1
        v7=sat-a; s.sat=v7
        s.rem=rem & ~(0xFFFFFFFF<<v7) & 0xFFFFFFFF
        return s16(rem>>v7)

TABLE={1:(2,1),2:(2,-4),3:(4,5),4:(4,-20),5:(6,21),6:(6,-84),7:(8,85),8:(8,-340),
       9:(10,341),10:(10,-1364),11:(12,1365),12:(12,-5460),13:(16,0)}
END=-268435456
class St: __slots__=('a2a','x1','x2')
def nextv(bs,st):
    if st.a2a:
        st.a2a-=1
        if st.x1==0: return 0
        if st.x1==99: return END
        return st.x2+bs.get(st.x1)
    c=bs.get(4)&0xF
    if c==0: st.x1=0; st.x2=0; return 0
    if c in TABLE:
        st.x1,st.x2=TABLE[c]; return st.x2+bs.get(st.x1)
    if c==14:
        st.a2a=(bs.get(4)-1)&0xFFFF
        if st.x1==0: return 0
        if st.x1==99: return END
        return st.x2+bs.get(st.x1)
    st.x1=99; st.x2=0; return END  # 15

class Anim64:
    def __init__(self, data, off=0):
        self.d=data; self.o=off
        self.le = data[off]!=0
        e='<' if self.le else '>'; self.e=e
        typ,nb=struct.unpack_from(e+'HH',data,off)
        if typ!=0x64: raise ValueError('not 0x64 anim: %x'%typ)
        self.nb=nb
        self.desc=struct.unpack_from(e+'%dH'%nb,data,off+4)
        pb=off+4+2*nb; self.pb=pb
        self.length=struct.unpack_from(e+'H',data,pb)[0]
        self.shift=data[pb+2]&0x7F; self.fshift=data[pb+3]
        nf=struct.unpack_from(e+'H',data,pb+4)[0]
        self.foffs=struct.unpack_from(e+'%df'%nf,data,pb+6)
        p=pb+6+4*nf; self.base=[]; self.b81=[]
        for d in self.desc:
            if is_short(d):
                v=struct.unpack_from(e+'3h',data,p); p+=6
                self.base.append([x*MULT for x in v]); self.b81.append([x>>self.shift for x in v])
            else:
                v=struct.unpack_from(e+'3f',data,p); p+=12
                self.base.append(list(v)); self.b81.append([0,0,0])
        self.kf=p
    def frame(self,frame):
        """frame is 1-based like the game."""
        if frame<1: frame=1
        if frame>self.length: frame=self.length
        out=[list(b) for b in self.base]
        bf=frame-1
        nk=(self.length+14)>>4
        if (bf>>4)>=nk: bf=nk*16-1  # table holds (len+14)>>4 keyframes
        if bf==0: return out
        sub=bf&0xF; k=bf>>4
        ko=struct.unpack_from(self.e+'I',self.d,self.kf+4*k)[0]
        cur=self.kf+ko; st=St(); st.a2a=0; st.x1=0; st.x2=0
        fi=0
        for j,d in enumerate(self.desc):
            for i in range(3):
                b=self.d[cur]; nxt=b>>2
                bs=BS(self.d,cur+1,b&3); st.a2a=0
                v=s16(self.b81[j][i]+nextv(bs,st))
                if sub:
                    tot=0
                    for _ in range(sub):
                        r=nextv(bs,st)
                        if r==END: break
                        tot+=r; v=s16(v+tot)
                if is_short(d): out[j][i]=(v<<self.shift)*MULT
                else: out[j][i]=(v<<self.fshift)*self.foffs[fi]+self.base[j][i]
                cur+=nxt
            if not is_short(d): fi+=1
        return out
    def frames(self): return [self.frame(f) for f in range(1,self.length+1)]

def mota_anims(data, off=0):
    if data[off:off+4]!=b'MOTA': raise ValueError('no MOTA')
    e='>' if data[off+5]==1 else '<'
    n=struct.unpack_from(e+'I',data,off+12)[0]
    return [struct.unpack_from(e+'I',data,off+0x14+4*i)[0] for i in range(n)]

def validate(path, out=None):
    """Decode every 0x64 clip in a MOTA-bearing file (e.g. <code>rotsm.arc, mota_N.bin).
    Reports clip count, frames, decode errors and frame-to-frame continuity (mod 2pi)."""
    import re, math, json
    d = open(path, 'rb').read()
    rep = {'file': path, 'mota_blocks': 0, 'anim64': 0, 'animC8': 0, 'frames': 0,
           'errors': 0, 'max_step_rad_p99': None}
    steps = []
    for m in re.finditer(b'MOTA', d):
        M = m.start()
        try: offs = sorted(set(mota_anims(d, M)))
        except Exception: continue
        rep['mota_blocks'] += 1
        for o in offs:
            if M + o + 2 > len(d): continue
            t = d[M+o+1] if d[M+o] == 0 else d[M+o]
            if t == 0xC8: rep['animC8'] += 1; continue
            if t != 0x64: continue
            try:
                a = Anim64(d, M+o); fr = a.frames()
            except Exception:
                rep['errors'] += 1; continue
            rep['anim64'] += 1; rep['frames'] += len(fr)
            w = 0
            for i in range(1, len(fr)):
                for j, dsc in enumerate(a.desc):
                    if not is_short(dsc): continue
                    for k in range(3):
                        x = abs(fr[i][j][k]-fr[i-1][j][k]); w = max(w, min(x, abs(x-2*math.pi)))
            steps.append(w)
    if steps:
        steps.sort(); rep['max_step_rad_p99'] = round(steps[int(len(steps)*0.99)-1], 3)
        rep['max_step_rad_median'] = round(steps[len(steps)//2], 3)
    s = json.dumps(rep, indent=1)
    if out: open(out, 'w').write(s + '\n')
    return rep

if __name__ == '__main__':
    import sys, json
    if len(sys.argv) < 2:
        print('usage: t7_anim64.py <file-with-MOTA> [report.json]'); sys.exit(2)
    r = validate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(r)); sys.exit(1 if r['errors'] else 0)
