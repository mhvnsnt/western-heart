# Pass A: import pantera, eye swap, export pants texture for PIL compositing.
import bpy, os

WORK = "/home/hatch/workspace/creation-suite-flagship/work"
FILES = os.path.join(WORK, "files")

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "pantera-attire1.glb"))

def find_image(sub):
    for img in bpy.data.images:
        if sub.lower() in img.name.lower():
            return img
    return None

eye_img = find_image("Eye_D")
new_eye = bpy.data.images.load(os.path.join(FILES, "eye-yellow-tiger.png"))
if eye_img and new_eye:
    w, h = eye_img.size
    new_eye.scale(w, h)
    eye_img.pixels = new_eye.pixels[:]
    eye_img.update()
    print("EYE SWAP OK:", eye_img.name, w, h)
    bpy.data.images.remove(new_eye)

pants = find_image("PantsLower_D")
if pants:
    tmp = os.path.join(FILES, "_pants.png")
    pants.filepath_raw = tmp
    pants.file_format = 'PNG'
    pants.save()
    print("PANTS SAVED:", tmp, pants.size[:])
print("PASS A DONE")
