import bpy
bpy.ops.wm.open_mainfile(filepath='/home/hatch/workspace/_hair-wire-20261108/straight/straight-build3.blend')
band=bpy.data.objects['AngelHeadband']
for v in band.data.vertices:
    v.co.x*=0.92; v.co.y+=0.04; v.co.z+=0.10
print('band moved; new bounds z %.3f..%.3f y %.3f..%.3f'%(min(v.co.z for v in band.data.vertices),max(v.co.z for v in band.data.vertices),min(v.co.y for v in band.data.vertices),max(v.co.y for v in band.data.vertices)))
bpy.ops.wm.save_as_mainfile(filepath='/home/hatch/workspace/_hair-wire-20261108/straight/straight-build4.blend')
print('SAVED build4')
