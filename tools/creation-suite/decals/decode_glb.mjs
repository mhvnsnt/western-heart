#!/usr/bin/env node
/* decode_glb.mjs — strip EXT_meshopt_compression from GLBs so Blender 4.x can import them.
   Usage: node tools/creation-suite/decals/decode_glb.mjs OUT_DIR in1.glb [in2.glb ...]
   Blender 4.3's glTF importer stops with "Extension EXT_meshopt_compression is not available";
   the template bodies are gltfpack -cc output. The decoded copies are scratch (not committed). */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { basename, join } from 'node:path';
import { decodeGlbToPlain } from './glb-skin.mjs';
const [out, ...ins] = process.argv.slice(2);
if (!out || !ins.length) { console.error('usage: decode_glb.mjs OUT_DIR in.glb...'); process.exit(2); }
mkdirSync(out, { recursive: true });
for (const f of ins) {
  const buf = await decodeGlbToPlain(readFileSync(f));
  writeFileSync(join(out, basename(f)), buf);
  console.log(`decoded ${f} -> ${join(out, basename(f))} (${buf.length} B)`);
}
