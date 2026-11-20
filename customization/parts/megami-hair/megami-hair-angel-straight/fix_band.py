import bpy, math
from mathutils import Vector, Matrix
# Combined headband fix (fix pass 2026-11-08, replaces the lane's fix_band.py):
# stage 1 = the lane's base fit (x*=0.92, y+=0.04, z+=0.10) + lift so the bottom edge
# lands ON the measured hairline (front z 1.715) + tip back -8deg to follow the
# forehead's curvature instead of slabbing across it.
# stage 2 = hug: radial xy scale 0.96 about the head axis, drop 0.015, tuck -5deg,
# so the band sits against the cap (front surface ~5mm proud of the cap surface).
# Final band bounds: x -0.084..0.084, y -0.113..-0.029, z 1.704..1.762.
# NOTE: in the three.js proof renderer the band (100% 'head'-weighted accessory mesh)
# still renders displaced forward (visor artifact — same mesh-vs-skeleton bind family
# as the v4 body's -0.33 offset, fidelity lane's territory). Shipped straight proofs
# are shot with the band toggled OFF per the fix brief's sanctioned fallback; the band
# stays a toggleable sub-part (node 'AngelHeadband') of the straight part.
LIFT=0.030; TILT_DEG=-8.0; PIVOT=(0.0,-0.02,1.715)
bpy.ops.wm.open_mainfile(filepath='straight-build3.blend')
band=bpy.data.objects['AngelHeadband']
for v in band.data.vertices:
    v.co.x*=0.92; v.co.y+=0.04; v.co.z+=0.10
th=math.radians(TILT_DEG); c=math.cos(th); s=math.sin(th)
py,pz=PIVOT[1],PIVOT[2]
for v in band.data.vertices:
    dy=v.co.y-py; dz=v.co.z-pz
    v.co.y=py + dy*c - dz*s
    v.co.z=pz + dy*s + dz*c + LIFT
AXIS = Vector((0.0, -0.0065, 0.0))
for v in band.data.vertices:
    p = Vector(v.co)
    p.x = AXIS.x + (p.x - AXIS.x) * 0.96
    p.y = AXIS.y + (p.y - AXIS.y) * 0.96
    p.z -= 0.015
    v.co = p
pivot = Vector((0.0, -0.02, 1.70))
R = Matrix.Rotation(math.radians(-5.0), 4, 'X')
for v in band.data.vertices:
    v.co = pivot + R @ (Vector(v.co) - pivot)
vs = [band.matrix_world @ v.co for v in band.data.vertices]
print('band world bounds x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f' % (
    min(v.x for v in vs), max(v.x for v in vs),
    min(v.y for v in vs), max(v.y for v in vs),
    min(v.z for v in vs), max(v.z for v in vs)))
bpy.ops.wm.save_as_mainfile(filepath='straight-build5.blend')
print('SAVED build5')
