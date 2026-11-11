/* Vertex normals for a deformed REGION of a mesh, exactly as a full computeVertexNormals() would give them.

   Why (lag fix, owner 2026-11-11: "the game is really laggy ... when you trying to fight her"): the soft-body flesh
   sims (softbody.js, mpm-tissue.js) move a small region of a dense body mesh (Tripo models run to hundreds of
   thousands of triangles) and then called geometry.computeVertexNormals() on the WHOLE mesh, every frame on high
   quality. A moved vertex only changes the normals of the vertices that share a triangle with it, so:
     write set W = the region's vertices + every vertex that shares a triangle with one of them (one ring);
     triangle set T = every triangle that touches W.
   Each W normal is the area-weighted sum over ALL its triangles (all in T), the same formula three.js uses
   (r160 BufferGeometry.computeVertexNormals: cb = C - B, ab = A - B, n += cb x ab, then normalize), so every
   normal that can change comes out bit-for-bit the same as the full recompute. Every other normal is untouched,
   because none of its triangles moved. Cost scales with the region, not the mesh. */

/** Build once per region: { write: Int32Array of vertices whose normals are rewritten, tris: Uint32Array a,b,c
    triples, minV, maxV: index range of the write set (for a partial GPU upload) }. */
export function buildRegionNormalPlan(geometry, regionVerts) {
  const pos = geometry.attributes.position;
  const n = pos.count;
  const idx = geometry.index ? geometry.index.array : null;
  const triCount = idx ? idx.length / 3 : Math.floor(n / 3);
  const corner = (t, k) => (idx ? idx[t * 3 + k] : t * 3 + k);
  const inRegion = new Uint8Array(n);
  for (let i = 0; i < regionVerts.length; i++) inRegion[regionVerts[i]] = 1;
  // one ring around the region
  const inWrite = new Uint8Array(n);
  for (let t = 0; t < triCount; t++) {
    const a = corner(t, 0), b = corner(t, 1), c = corner(t, 2);
    if (inRegion[a] || inRegion[b] || inRegion[c]) { inWrite[a] = 1; inWrite[b] = 1; inWrite[c] = 1; }
  }
  const write = [];
  let minV = n, maxV = -1;
  for (let v = 0; v < n; v++) if (inWrite[v]) { write.push(v); if (v < minV) minV = v; if (v > maxV) maxV = v; }
  const tris = [];
  for (let t = 0; t < triCount; t++) {
    const a = corner(t, 0), b = corner(t, 1), c = corner(t, 2);
    if (inWrite[a] || inWrite[b] || inWrite[c]) tris.push(a, b, c);
  }
  return { write: Int32Array.from(write), inWrite, tris: Uint32Array.from(tris), minV, maxV };
}

/** Recompute the plan's normals in place and flag the normal attribute for upload (only its write range when the
    renderer supports partial updates). Falls back to the full recompute when the geometry has no normal attribute. */
export function updateRegionNormals(geometry, plan) {
  const nAttr = geometry.attributes.normal;
  if (!nAttr || !plan || !plan.write.length) { geometry.computeVertexNormals(); return; }
  const P = geometry.attributes.position.array, N = nAttr.array, W = plan.write, T = plan.tris, w = plan.inWrite;
  for (let i = 0; i < W.length; i++) { const o = W[i] * 3; N[o] = 0; N[o + 1] = 0; N[o + 2] = 0; }
  for (let i = 0; i < T.length; i += 3) {
    const a = T[i] * 3, b = T[i + 1] * 3, c = T[i + 2] * 3;
    // cb = C - B, ab = A - B, n = cb x ab (three.js r160 order and operands)
    const cbx = P[c] - P[b], cby = P[c + 1] - P[b + 1], cbz = P[c + 2] - P[b + 2];
    const abx = P[a] - P[b], aby = P[a + 1] - P[b + 1], abz = P[a + 2] - P[b + 2];
    const nx = cby * abz - cbz * aby, ny = cbz * abx - cbx * abz, nz = cbx * aby - cby * abx;
    if (w[T[i]]) { N[a] += nx; N[a + 1] += ny; N[a + 2] += nz; }
    if (w[T[i + 1]]) { N[b] += nx; N[b + 1] += ny; N[b + 2] += nz; }
    if (w[T[i + 2]]) { N[c] += nx; N[c + 1] += ny; N[c + 2] += nz; }
  }
  for (let i = 0; i < W.length; i++) {
    const o = W[i] * 3;
    const x = N[o], y = N[o + 1], z = N[o + 2];
    const l = Math.sqrt(x * x + y * y + z * z);
    if (l > 0) { N[o] = x / l; N[o + 1] = y / l; N[o + 2] = z / l; }
  }
  if (typeof nAttr.addUpdateRange === 'function') { // r159+: upload only the write range
    nAttr.clearUpdateRanges && nAttr.clearUpdateRanges();
    nAttr.addUpdateRange(plan.minV * 3, (plan.maxV - plan.minV + 1) * 3);
  }
  nAttr.needsUpdate = true;
}
