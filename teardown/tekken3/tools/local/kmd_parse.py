#!/usr/bin/env python3
"""Parse Tekken 3 3DMK models based on n0madic/tekken3remake documentation.
Extracts vertices and faces for rendering. Skips skinning/imports for simplicity.
All offsets in file are relative to file start.
"""
import struct, json

def parse_kmd(data):
    """Parse a 3DMK record. Returns dict with rows containing verts/faces."""
    if data[8:12] != b'3DMK':
        raise ValueError("Not a 3DMK file")
    row_count, scale = struct.unpack_from('<2I', data, 0)
    assert row_count == 27, f"Expected 27 rows, got {row_count}"
    
    rows = []
    for i in range(27):
        ro = 0x10 + i * 56
        w = struct.unpack_from('<14I', data, ro)
        verts_off = w[0]
        variants_off = w[1]
        normals_off = w[2]
        faces_off = w[3]
        texmap_off = w[4]
        jx, jy, jz = struct.unpack_from('<3i', data, ro + 0x14)
        parent = struct.unpack_from('<i', data, ro + 0x20)[0]
        active = w[12]  # +0x30
        
        row = {
            'index': i, 'active': active, 'parent': parent,
            'joint': (jx, jy, jz),
            'verts': [], 'faces': [],
        }
        
        # Parse vertex block
        if verts_off and active:
            try:
                v = parse_vertex_block(data, verts_off)
                row['verts'] = v
            except Exception as e:
                pass
        
        # Parse face block
        if faces_off and active:
            try:
                # Find end: use next non-zero block or texmap as boundary
                # For simplicity, parse each face group
                f = parse_face_block(data, faces_off)
                row['faces'] = f
            except Exception as e:
                pass
        
        rows.append(row)
    
    return {'scale': scale, 'rows': rows}

def parse_vertex_block(data, off):
    """Parse vertex block, return list of (x,y,z)."""
    pos = off
    lead = struct.unpack_from('<I', data, pos)[0]; pos += 4
    # import lists
    for _ in range(2):
        cnt = struct.unpack_from('<I', data, pos)[0]; pos += 4
        pos += ((cnt + 3) // 4) * 4  # packed 4 per word, word-aligned
    count = struct.unpack_from('<I', data, pos)[0]; pos += 4
    verts = []
    for _ in range(count):
        x, y, z, pad = struct.unpack_from('<4h', data, pos)
        pos += 8
        verts.append((x, y, z))
    return verts

def parse_face_block(data, off):
    """Parse face block, return list of (v0, v1, v2[, v3])."""
    faces = []
    pos = off
    # 4 groups: ft3, ft4, gt3, gt4
    # ft3: 8 bytes/rec, 3 verts; ft4: 8 bytes/rec, 4 verts
    # gt3: 8 bytes/rec, 3 verts; gt4: 12 bytes/rec, 4 verts
    rec_sizes = [8, 8, 8, 12]
    n_verts = [3, 4, 3, 4]
    for gi in range(4):
        if pos + 4 > len(data):
            break
        count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        # Sanity: count shouldn't be absurd
        if count > 10000:
            break
        for _ in range(count):
            if pos + rec_sizes[gi] > len(data):
                break
            v0 = struct.unpack_from('<I', data, pos)[0]
            # Vertex slots are byte offsets (slot*4): bits 2-8 -> v0, 9-15 -> v1, 16-22 -> v2
            # For quads: bits 25-31 -> v3
            # Convert byte offset to vertex index: (bits >> 2) & 0x7F... actually slot = offset/4
            # The doc says "byte offsets (slot×4)" so slot = value/4
            # bits 2-8 give (offset >> 2) & 0x7F = slot & 0x7F (since offset = slot*4)
            i0 = (v0 >> 2) & 0x7F
            i1 = (v0 >> 9) & 0x7F
            i2 = (v0 >> 16) & 0x7F
            if n_verts[gi] == 3:
                faces.append((i0, i1, i2))
            else:
                i3 = (v0 >> 25) & 0x7F
                # Quad as two triangles
                faces.append((i0, i1, i2))
                faces.append((i0, i2, i3))
            pos += rec_sizes[gi]
    return faces

def kmd_to_obj(data, filepath):
    """Convert 3DMK to OBJ with parts positioned by joint offsets (no animation)."""
    kmd = parse_kmd(data)
    # Build part hierarchy: compute world offset for each row
    # parent field indexes draw parts, not rows. Use PART_ROW mapping in reverse.
    # For simplicity: accumulate joint offsets along parent chain using row parent.
    # Note: doc says parent indexes parts, but let's try using it as row index first.
    
    # Actually, let's just place each part at its joint offset relative to parent
    # We'll do a simple traversal
    world_offsets = {}
    
    def get_world(i, visited=None):
        if i in world_offsets:
            return world_offsets[i]
        if visited is None:
            visited = set()
        if i in visited or i < 0 or i >= 27:
            return (0, 0, 0)
        visited.add(i)
        row = kmd['rows'][i]
        jx, jy, jz = row['joint']
        parent = row['parent']
        if parent < 0:
            world_offsets[i] = (jx, jy, jz)
        else:
            # Parent is a part index; map part->row via PART_ROW
            PART_ROW = (0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24)
            if 0 <= parent < len(PART_ROW):
                prow = PART_ROW[parent]
                px, py, pz = get_world(prow, visited)
                world_offsets[i] = (px + jx, py + jy, pz + jz)
            else:
                world_offsets[i] = (jx, jy, jz)
        return world_offsets[i]
    
    with open(filepath, 'w') as f:
        f.write("# Tekken 3 3DMK export\n")
        v_offset = 1
        for row in kmd['rows']:
            if not row['active'] or not row['verts']:
                continue
            wx, wy, wz = get_world(row['index'])
            f.write(f"\ng part_{row['index']}\n")
            for (x, y, z) in row['verts']:
                # Note: doc says game stores (x, y, -z). We'll output as-is for now.
                f.write(f"v {x + wx} {y + wy} {z + wz}\n")
            for face in row['faces']:
                # Validate indices
                nv = len(row['verts'])
                if all(0 <= idx < nv for idx in face):
                    idxs = ' '.join(str(idx + v_offset) for idx in face)
                    f.write(f"f {idxs}\n")
            v_offset += len(row['verts'])
    return kmd

if __name__ == '__main__':
    import sys
    data = open(sys.argv[1], 'rb').read()
    kmd_to_obj(data, sys.argv[2])
    print(f"Exported to {sys.argv[2]}")
