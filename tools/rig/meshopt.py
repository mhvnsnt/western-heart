"""Fallback `meshopt` module for tools/rig-repair/_common.py when the native
Python binding is unavailable: decodes EXT_meshopt_compression bufferViews via
node + the vendored game/vendor/addons/libs/meshopt_decoder.js (MIT)."""
import os, subprocess, json
_DEC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                    'game', 'vendor', 'addons', 'libs', 'meshopt_decoder.js'))
_JS = """
import { MeshoptDecoder as M } from %s;
const a = JSON.parse(process.argv[1]);
const chunks = []; for await (const c of process.stdin) chunks.push(c);
const src = new Uint8Array(Buffer.concat(chunks));
await M.ready;
const t = new Uint8Array(a.count * a.stride);
M.decodeGltfBuffer(t, a.count, a.stride, src, a.mode, a.filter || 'NONE');
process.stdout.write(Buffer.from(t));
"""


class _Out(bytes):
    def tobytes(self):
        return bytes(self)


def decode_gltf_buffer(comp, count, stride, mode, filt=None):
    js = _JS % json.dumps('file://' + _DEC)
    r = subprocess.run(['node', '--input-type=module', '-e', js,
                        json.dumps({'count': count, 'stride': stride, 'mode': mode, 'filter': filt})],
                       input=bytes(comp), capture_output=True, check=True)
    return _Out(r.stdout)
