import struct, json, numpy as np
def load(path):
    d=open(path,'rb').read(); ln=struct.unpack('<I', d[12:16])[0]
    g=json.loads(d[20:20+ln]); off=20+ln; bln=struct.unpack('<I', d[off:off+4])[0]
    return g, d[off+8:off+8+bln]
def node_m(n):
    if n.get('matrix'): return np.array(n['matrix'],dtype=float).reshape(4,4).T
    m=np.eye(4); s=n.get('scale',[1,1,1]); m=np.diag([s[0],s[1],s[2],1.0])@m
    if n.get('rotation'):
        x,y,z,w=n['rotation']
        r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1]],dtype=float)
        m=r@m
    t=n.get('translation',[0,0,0]); T=np.eye(4); T[:3,3]=t; return T@m
def worlds(g):
    w={}
    def visit(i,pm):
        m=pm@node_m(g['nodes'][i]); w[i]=m
        for c in g['nodes'][i].get('children',[]): visit(c,m)
    for s in g['scenes']:
        for r in s['nodes']: visit(r,np.eye(4))
    return w
def acc_data(g,blob,ai):
    a=g['accessors'][ai]; bv=g['bufferViews'][a['bufferView']]
    off=(bv.get('byteOffset',0))+(a.get('byteOffset',0))
    ncomp={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt={5126:np.float32,5125:np.uint32,5123:np.uint16,5121:np.uint8,5122:np.int16,5120:np.int8}[a['componentType']]
    stride=bv.get('byteStride'); isz=np.dtype(dt).itemsize
    if stride and stride!=ncomp*isz:
        raw=np.frombuffer(blob,dtype=np.uint8,count=a['count']*stride,offset=off).reshape(a['count'],stride)
        return raw[:,:ncomp*isz].copy().view(dt).reshape(a['count'],ncomp)
    return np.frombuffer(blob,dtype=dt,count=a['count']*ncomp,offset=off).reshape(a['count'],ncomp).copy()
