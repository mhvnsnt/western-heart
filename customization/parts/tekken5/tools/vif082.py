"""Tekken 5 NUDP VIF globalFlags 0x82 packet decoder (gap-closure W7d).

The 16 models inside the 9 ctype-5 containers of TK5DATA1.BIN are the only
DATA1 models whose VIF packets carry globalFlags 0x82; ModelMagic's
VIFerator assumes the 0x91/0x93 section layout and desyncs on every one
(W7b survey S4: 0 of 97 submeshes converted). This module decodes the 0x82
form. Layout, proven byte-exact on all 238 VIF blobs of the 16 models
(every blob consumed to exactly its size field, every section count equal
to the packet's own vertCount, every face index in range):

  u16 size, u16 globalFlags = 0x0082
  STCYCL 0x01000105
  UNPACK S-32 num=1            -> vertCount (u32 data word)
  STMASK 0x20000000, mask = 0x00000080
  UNPACK V3-32 addr=1 num=N    -> positions (12N bytes, f32 x3)
  UNPACK V4-8  addr=3 num=N    -> vertex colors RGBA (4N bytes, PS2 alpha
                                  scale 0..128; NOT bone indices - values
                                  are color-like, alpha in PS2 range)
  UNPACK V2-32 addr=4 num=N    -> UVs (8N bytes, f32 x2)
  STCYCL 0x01000500
  STMASK 0x20000000, mask = 0xFFFFFF7F
  tristrip marker words (top byte 0x70) until 0-padding, 16B alignment
  terminators (final blob of the chain may omit them):
    STCYCL 0x01000101, STMASK, mask 0, FLUSHA 0x14000000

Differences vs the 0x91/0x93 forms: NO normals section (addr 2), NO
weights (addr 0xCC), NO bone-index section (addr 0xCD); a V4-8 color
section at addr 3 is always present. The two STMASK masks are the
byte-reversed complements of the 0x91 form's masks. Tristrip markers
decode exactly as ModelMagic's VIFerator (divisor 5 - the STCYCL CL=5
VU stride is shared by all three forms), so faces come from
VIFerator.get_faces() unchanged. Normals must be computed from faces;
there is no skinning data in these packets (submesh bone palettes are
all-0xFF).

NUDP container parsing is ModelMagic's (model_nudp.NUDP), reused as-is.
"""
import struct, sys, os

_MM = '/home/hatch/workspace/tk5-lanes/research/dl2/Tekken5_Tools/ModelMagic'
if os.path.isdir(_MM) and _MM not in sys.path:
    sys.path.insert(0, _MM)
from model_nudp import NUDP          # noqa: E402  (community tooling, evaluation use)
from vifMaker import VIFerator, TriStrip  # noqa: E402
from fileRW import FRead             # noqa: E402


def decode_blob(data):
    """Decode one 0x82 VIF blob (starts with u16 size). Strict: any
    deviation from the proven layout raises. Returns a dict with
    n/pos/col/uv/strips/faces."""
    size, flags = struct.unpack_from('<HH', data, 0)
    assert flags == 0x82, f'flags {flags:#x}'
    assert size <= len(data), 'blob size overruns buffer'
    p = 4

    def u32():
        nonlocal p
        v = struct.unpack_from('<I', data, p)[0]
        p += 4
        return v

    assert u32() == 0x01000105, 'STCYCL'
    assert u32() == 0x60018000, 'vertCount UNPACK S-32'
    n = u32()
    assert u32() == 0x20000000, 'STMASK'
    assert u32() == 0x00000080, 'mask1'

    def unpack_hdr(cmd_expect):
        nonlocal p
        _imm, num, cmd = struct.unpack_from('<HBB', data, p)
        assert cmd == cmd_expect, f'cmd {cmd:#x} != {cmd_expect:#x} @{p}'
        assert num == n, f'num {num} != vertCount {n} @{p}'
        p += 4

    unpack_hdr(0x78)  # V3-32 positions @ VU addr 1
    pos = [struct.unpack_from('<3f', data, p + i * 12) for i in range(n)]
    p += 12 * n
    unpack_hdr(0x6E)  # V4-8 colors @ VU addr 3
    col = [tuple(data[p + i * 4:p + i * 4 + 4]) for i in range(n)]
    p += 4 * n
    unpack_hdr(0x64)  # V2-32 UVs @ VU addr 4
    uv = [struct.unpack_from('<2f', data, p + i * 8) for i in range(n)]
    p += 8 * n
    assert u32() == 0x01000500, 'STCYCL2'
    assert u32() == 0x20000000, 'STMASK2'
    assert u32() == 0xFFFFFF7F, 'mask2'
    strips = []
    while p + 4 <= size:
        w = struct.unpack_from('<I', data, p)[0]
        if w == 0x01000101:  # terminator block: STCYCL, STMASK, mask 0, FLUSHA
            assert struct.unpack_from('<I', data, p + 4)[0] == 0x20000000
            assert struct.unpack_from('<I', data, p + 8)[0] == 0
            assert struct.unpack_from('<I', data, p + 12)[0] == 0x14000000
            p += 16
            break
        if w == 0:
            p += 4
            continue
        assert (w >> 24) == 0x70, f'marker word {w:#010x} @{p}'
        strips.append(TriStrip(w))
        p += 4
    assert p == size, f'consumed {p} != blob size {size}'
    vf = VIFerator()
    vf.verts = [type('V', (), {'pos': q})() for q in pos]
    vf.triStrips = strips
    faces = vf.get_faces()
    return {'n': n, 'pos': pos, 'col': col, 'uv': uv,
            'strips': strips, 'faces': faces, 'size': size}


def decode_model(path):
    """Parse a .nudp file (ModelMagic structure reader) and decode every
    VIF blob of every submesh with the 0x82 decoder."""
    nud = NUDP()
    nud.read(FRead(open(path, 'rb')))
    out = []
    for gi, g in enumerate(nud.MeshGroups):
        for si, sm in enumerate(g.subMeshs):
            for bi, blob in enumerate(sm.vifDMA):
                r = decode_blob(bytes(blob.data))
                r.update({'group': gi, 'sub': si, 'blob': bi,
                          'tex': sm.material.textureIndex,
                          'bone_node': g.boneNodeID,
                          'palette': list(sm.bonePalette)})
                out.append(r)
    return nud, out
