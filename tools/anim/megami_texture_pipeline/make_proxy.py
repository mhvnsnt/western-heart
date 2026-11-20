"""Build the proxy blend: every image scaled to 64x64 (wiring identical,
pixels irrelevant), saved to a NEW file. Decodes one image at a time.
NEVER saves over the input."""
import bpy, sys

OUT = sys.argv[sys.argv.index("--") + 1]
done, failed = [], []
for img in bpy.data.images:
    if img.source in ("VIEWER", "MOVIE", "SEQUENCE"):
        continue
    try:
        img.scale(64, 64)
        img.pack()  # re-pack CURRENT (scaled) pixels; scale alone does not persist
        done.append(img.name)
    except Exception as e:
        failed.append((img.name, str(e)))
print("PROXY_SCALED", len(done), "FAILED", failed)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("PROXY_SAVED", OUT)
