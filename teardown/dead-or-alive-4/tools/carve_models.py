#!/usr/bin/env python3
"""
DOA4 Model Carver - Extract vertex buffers from "encrypted" AFS archives.

The 6 AFS files (chrone, chrtwo, chrthree, mot, stg) have plaintext data.
Resource tables contain VBUF (vertex buffer) records:
  [MAGIC:4][offset:4BE][stride:4BE][count:4BE]

Vertex format (20 bytes, big-endian):
  [0:12]  float3 position
  [12:20] float2 UV

This script extracts all unique vertex buffers and saves as GLB point clouds.
Index buffers (IBUF) format not yet decoded - meshes are point clouds for now.
"""

import struct, re, os, sys, json

def parse_vbuf_tables(data):
    """Find all VBUF records and group by containing XPR2 table."""
    # Find XPR2 table positions
    xpr2_positions = [m.start() for m in re.finditer(b'XPR2', data)]
    
    tables = []
    for xpr2_pos in xpr2_positions:
        # Parse records from xpr2_pos onwards until non-record data
        records = []
        pos = xpr2_pos
        # Limit scan to 64KB per table
        end_limit = min(xpr2_pos + 65536, len(data))
        while pos < end_limit - 16:
            magic = data[pos:pos+4]
            if magic in (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF'):
                f1 = struct.unpack('>I', data[pos+4:pos+8])[0]
                f2 = struct.unpack('>I', data[pos+8:pos+12])[0]
                f3 = struct.unpack('>I', data[pos+12:pos+16])[0]
                records.append({
                    'type': magic.decode(),
                    'table_offset': pos,
                    'f1': f1, 'f2': f2, 'f3': f3,
                })
                pos += 16
            elif magic == b'\x00\x00\x00\x00':
                pos += 16
            else:
                # Check if it's still plausible table data
                # If we've seen VBUF/IBUF, continue a bit more
                break
        tables.append({
            'xpr2_offset': xpr2_pos,
            'records': records,
        })
    return tables

def extract_vertex_buffers(data, tables):
    """Extract unique vertex buffers from VBUF records."""
    buffers = []
    seen_offsets = set()
    
    for table in tables:
        vbufs = [r for r in table['records'] if r['type'] == 'VBUF']
        # Group by f3 (count) and f2 (stride) - same buffer has same params
        # Take the smallest f1 (earliest offset) as buffer start
        from collections import defaultdict
        groups = defaultdict(list)
        for v in vbufs:
            key = (v['f2'], v['f3'])
            groups[key].append(v)
        
        for (stride, count), group in groups.items():
            # Sanity checks
            if stride not in (12, 16, 20, 24, 28, 32, 36):
                continue
            if count < 3 or count > 100000:
                continue
            # Take smallest offset
            min_offset = min(v['f1'] for v in group)
            if min_offset in seen_offsets:
                continue
            if min_offset + count * stride > len(data):
                continue
            seen_offsets.add(min_offset)
            
            # Verify it's plausible vertex data (check first few positions)
            try:
                plausible = 0
                for i in range(min(10, count)):
                    o = min_offset + i * stride
                    x, y, z = struct.unpack('>3f', data[o:o+12])
                    if -1000 < x < 1000 and -1000 < y < 1000 and -1000 < z < 1000:
                        plausible += 1
                if plausible < 8:
                    continue
            except:
                continue
            
            buffers.append({
                'offset': min_offset,
                'stride': stride,
                'count': count,
                'xpr2_table': table['xpr2_offset'],
            })
    
    return buffers

def vertices_to_glb(vertices, uvs, output_path):
    """Write vertices as GLB point cloud."""
    import struct
    
    # GLB format: JSON chunk + BIN chunk
    # Simple point cloud with POSITION and TEXCOORD_0
    
    n = len(vertices)
    # Interleave: position (3 floats) + uv (2 floats) = 20 bytes per vert
    bin_data = bytearray()
    for i in range(n):
        bin_data.extend(struct.pack('<3f', *vertices[i]))
        if uvs and i < len(uvs):
            bin_data.extend(struct.pack('<2f', *uvs[i]))
        else:
            bin_data.extend(struct.pack('<2f', 0.0, 0.0))
    
    # Pad BIN to 4-byte alignment
    while len(bin_data) % 4:
        bin_data.append(0)
    
    json_str = json.dumps({
        "asset": {"version": "2.0", "generator": "doa4-carve-models"},
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": n,
                "type": "VEC3",
                "max": [max(v[i] for v in vertices) for i in range(3)],
                "min": [min(v[i] for v in vertices) for i in range(3)],
            },
            {
                "bufferView": 1,
                "componentType": 5126,
                "count": n,
                "type": "VEC2",
            }
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": n * 12,
                "byteStride": 20,
            },
            {
                "buffer": 0,
                "byteOffset": n * 12,
                "byteLength": n * 8,
                "byteStride": 20,
            }
        ],
        "buffers": [{"byteLength": len(bin_data)}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 0, "TEXCOORD_0": 1},
                "mode": 0,  # POINTS
            }]
        }],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }, separators=(',', ':'))
    
    # Pad JSON to 4-byte alignment
    json_bytes = json_str.encode('utf-8')
    while len(json_bytes) % 4:
        json_bytes += b' '
    
    # GLB header
    glb = bytearray()
    glb.extend(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(json_bytes) + 8 + len(bin_data)))
    glb.extend(struct.pack('<II', len(json_bytes), 0x4E4F534A))  # JSON chunk
    glb.extend(json_bytes)
    glb.extend(struct.pack('<II', len(bin_data), 0x004E4942))  # BIN chunk
    glb.extend(bin_data)
    
    with open(output_path, 'wb') as f:
        f.write(glb)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('afs_file', help='Input AFS file')
    parser.add_argument('-o', '--output', default='carved_models', help='Output directory')
    args = parser.parse_args()
    
    print(f"Reading {args.afs_file}...")
    with open(args.afs_file, 'rb') as f:
        data = f.read()
    print(f"  {len(data)} bytes")
    
    print("Parsing VBUF tables...")
    tables = parse_vbuf_tables(data)
    print(f"  Found {len(tables)} XPR2 tables")
    
    print("Extracting vertex buffers...")
    buffers = extract_vertex_buffers(data, tables)
    print(f"  Found {len(buffers)} unique vertex buffers")
    
    os.makedirs(args.output, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.afs_file))[0]
    
    manifest = []
    for i, buf in enumerate(buffers):
        offset = buf['offset']
        stride = buf['stride']
        count = buf['count']
        
        vertices = []
        uvs = []
        for j in range(count):
            o = offset + j * stride
            try:
                x, y, z = struct.unpack('>3f', data[o:o+12])
                vertices.append((x, y, z))
                if stride >= 20:
                    u, v = struct.unpack('>2f', data[o+12:o+20])
                    uvs.append((u, v))
            except:
                break
        
        if len(vertices) < 3:
            continue
        
        out_name = f"{base}_model_{i:03d}_{len(vertices)}v.glb"
        out_path = os.path.join(args.output, out_name)
        vertices_to_glb(vertices, uvs, out_path)
        
        # Bbox
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        manifest.append({
            'file': out_name,
            'offset': hex(offset),
            'stride': stride,
            'verts': len(vertices),
            'bbox': {
                'min': [min(xs), min(ys), min(zs)],
                'max': [max(xs), max(ys), max(zs)],
            }
        })
        print(f"  [{i+1}/{len(buffers)}] {out_name}: {len(vertices)} verts")
    
    manifest_path = os.path.join(args.output, f"{base}_manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest: {manifest_path}")
    print(f"Total: {len(manifest)} models extracted")

if __name__ == '__main__':
    main()
