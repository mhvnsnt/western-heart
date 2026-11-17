import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs'; import path from 'path';
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const root = process.argv[2]; let n = 0, bad = 0;
for (const it of fs.readdirSync(root).filter((d) => fs.statSync(path.join(root, d)).isDirectory()))
  for (const f of fs.readdirSync(path.join(root, it)).filter((f) => f.endsWith('.glb'))) {
    const d = await io.read(path.join(root, it, f)); n++;
    const node = d.getRoot().listNodes().find((x) => x.getMesh()); const e = node.getMesh().getExtras();
    const p = node.getMesh().listPrimitives()[0];
    const ok = node.getSkin() && p.getAttribute('JOINTS_0') && p.listTargets().length > 0 && e.wh_hide && e.license === 'CC0-1.0';
    if (!ok) { bad++; console.log('BAD', it, f); }
  }
console.log('checked', n, 'bad', bad);
