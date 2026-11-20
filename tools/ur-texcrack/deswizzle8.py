import re
# Extract tables from recomp source
src = open('urban-reign-recomp/runtime/ps2xRuntime/src/lib/gs/ps2_gs_memory.cpp').read()
m = re.search(r'BlockTableP8\s*\{\{(.*?)\}\};', src, re.S)
BLOCK8 = [int(x) for x in re.findall(r'\d+', m.group(1))]
m = re.search(r'ColumnTable8\s*\{\{(.*?)\}\};', src, re.S)
COL8 = [int(x) for x in re.findall(r'\d+', m.group(1))]
BLOCK8 = [BLOCK8[i:i+8] for i in range(0, 32, 8)]
COL8 = [COL8[i:i+16] for i in range(0, 256, 16)]

def deswizzle8(data, width, height):
    """Deswizzle PSMT8 texture data. data: bytes in PS2 swizzled order."""
    out = bytearray(width * height)
    bw = width // 64  # buffer width in 64-px units
    for y in range(height):
        for x in range(width):
            page = (y >> 6) * (bw >> 1) + (x >> 7)
            block = page * 32 + BLOCK8[(y >> 4) & 3][(x >> 4) & 7]
            col = COL8[y & 15][x & 15]
            src_idx = block * 256 + col
            if src_idx < len(data):
                out[y * width + x] = data[src_idx]
    return bytes(out)

if __name__ == '__main__':
    import sys
    from PIL import Image
    data = open('char001.ppk','rb').read()
    chunk = data[0x2971:0x2971+16143]
    # pad to 16384 for 128x128
    padded = chunk + b'\x00' * (16384 - len(chunk))
    pixels = deswizzle8(padded, 128, 128)
    # save as grayscale (indices)
    im = Image.frombytes('L', (128, 128), pixels)
    im = im.resize((512, 512), Image.NEAREST)
    im.save('test_deswizzle_128.png')
    print('saved test_deswizzle_128.png')
    # also try raw linear (no deswizzle) for comparison
    im2 = Image.frombytes('L', (128, 128), padded[:16384])
    im2 = im2.resize((512, 512), Image.NEAREST)
    im2.save('test_linear_128.png')
    print('saved test_linear_128.png')
