#!/usr/bin/env python3
"""Render verification for rig repairs: front view + hand crops + posed proofs.

Pipeline (from the 2026-10-23 audit): headless chromium via playwright,
three.js + meshopt, 1024x1024, front view = camera on the model's facing
axis with NO model Y-rotation, skeleton.update() + precise=true Box3,
preserveDrawingBuffer + canvas.toDataURL().

Usage: verify_render.py <spec.json> <outdir>
spec.json: [{"slug":..., "model": <path>, "face_z": 1|-1 (optional),
             "poses": [{"name":..., "spec": "Bone:local:x:45;..."}],
             "hands": true|false}]
"""
import json, sys, base64
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

VENDOR = Path("/home/hatch/workspace/tripo-staging/vendor")
CHROME = "/opt/meta-chromium/chrome"

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:#fff;width:100%;height:100%;overflow:hidden}
#app{width:1024px;height:1024px}
</style>
<script type="importmap">{"imports":{
"three":"__VENDOR__/three.module.js","three/addons/":"__VENDOR__/addons/"}}</script>
</head><body><div id="app"></div><pre id="out" style="display:none"></pre>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from '__VENDOR__/addons/libs/meshopt_decoder.js';
const app=document.getElementById('app');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setSize(1024,1024); renderer.setClearColor(0xffffff,1);
app.appendChild(renderer.domElement);
const scene=new THREE.Scene(); scene.background=new THREE.Color(0xffffff);
const camera=new THREE.PerspectiveCamera(35,1,0.1,200); camera.up.set(0,1,0);
scene.add(new THREE.HemisphereLight(0xffffff,0x888888,1.2));
const d1=new THREE.DirectionalLight(0xffffff,1.5); d1.position.set(3,5,4); scene.add(d1);
const d2=new THREE.DirectionalLight(0xffffff,0.5); d2.position.set(-3,2,-4); scene.add(d2);
const params=new URLSearchParams(location.search);
const loader=new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
function shot(){return renderer.domElement.toDataURL('image/png');}
function frame(model, facingOverride){
  model.updateMatrixWorld(true);
  model.traverse(o=>{if(o.isSkinnedMesh)o.skeleton.update();});
  let facing=new THREE.Vector3(0,0,1);
  if(facingOverride){facing=new THREE.Vector3(0,0,facingOverride);}
  else{
    const fb={},tb={};
    model.traverse(o=>{if(!o.isBone)return;
      const sd=/^Left/.test(o.name)?'L':(/^Right/.test(o.name)?'R':null); if(!sd)return;
      const nl=o.name.toLowerCase();
      if(/toe/.test(nl))tb[sd]=o; else if(/foot/.test(nl))fb[sd]=o;});
    for(const sd of ['L','R']){if(fb[sd]&&tb[sd]){
      const f=new THREE.Vector3(),t=new THREE.Vector3();
      fb[sd].getWorldPosition(f); tb[sd].getWorldPosition(t);
      const d2v=t.sub(f); d2v.y=0;
      if(d2v.lengthSq()>1e-8){facing=d2v.normalize();break;}}}
  }
  const box=new THREE.Box3().setFromObject(model,true);
  const center=box.getCenter(new THREE.Vector3());
  const size=box.getSize(new THREE.Vector3());
  const maxDim=Math.max(size.x,size.y,size.z);
  model.position.sub(center);
  model.updateMatrixWorld(true);
  const dist=maxDim*2.2;
  camera.position.set(facing.x*dist,facing.y*dist,facing.z*dist);
  camera.lookAt(0,0,0);
  renderer.render(scene,camera);
  return {facing:facing.toArray(), maxDim};
}
function handPx(model){
  const out={};
  model.traverse(o=>{if(!o.isBone)return;
    if(/hand/i.test(o.name)&&!/thumb|index|middle|ring|pinky/i.test(o.name)){
      const v=new THREE.Vector3(); o.getWorldPosition(v); v.project(camera);
      out[o.name]=[Math.round((v.x*0.5+0.5)*1024),Math.round((-v.y*0.5+0.5)*1024)];}});
  return out;
}
loader.load(params.get('model'),(gltf)=>{
  const model=gltf.scene; scene.add(model);
  const res={shots:{}};
  try{
    const fr=frame(model, params.get('faceZ')?parseFloat(params.get('faceZ')):null);
    res.facing=fr.facing; res.maxDim=fr.maxDim;
    res.shots.front=shot();
    res.hands=handPx(model);
    const poses=JSON.parse(params.get('poses')||'[]');
    const bones={}; model.traverse(o=>{if(o.isBone)bones[o.name]=o;});
    for(const p of poses){
      const touched=[];
      for(const part of p.spec.split(';')){
        if(!part.trim())continue;
        const [bn,ax,dg]=part.split(':');
        const b=bones[bn]; if(!b){res['missing_'+bn]=true;continue;}
        const q0=b.quaternion.clone(); touched.push([b,q0]);
        const ang=parseFloat(dg)*Math.PI/180;
        if(ax==='x')b.rotateX(ang); else if(ax==='y')b.rotateY(ang); else b.rotateZ(ang);
      }
      model.updateMatrixWorld(true);
      model.traverse(o=>{if(o.isSkinnedMesh)o.skeleton.update();});
      renderer.render(scene,camera);
      res.shots[p.name]=shot();
      for(const [b,q0] of touched) b.quaternion.copy(q0);
      model.updateMatrixWorld(true);
      model.traverse(o=>{if(o.isSkinnedMesh)o.skeleton.update();});
    }
    document.getElementById('out').textContent=JSON.stringify(res);
    document.title='DONE';
  }catch(e){document.title='ERROR:'+e.message;}
},undefined,(e)=>{document.title='ERROR:'+(e.message||e);});
</script></body></html>"""

def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    outdir = Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"_viewer.html").write_text(HTML.replace("__VENDOR__", "file://"+str(VENDOR)))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, args=[
            "--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files",
            "--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        for item in spec:
            slug = item["slug"]
            page = browser.new_page(viewport={"width":1024,"height":1024})
            q = {"model": "file://"+item["model"],
                 "poses": json.dumps(item.get("poses", []))}
            if "face_z" in item: q["faceZ"] = str(item["face_z"])
            url = "file://%s/_viewer.html?%s" % (outdir.resolve(), "&".join(
                f"{k}={quote(v)}" for k,v in q.items()))
            page.goto(url)
            try:
                page.wait_for_function(
                    "()=>document.title==='DONE'||document.title.startsWith('ERROR')",
                    timeout=300000)
                if page.title().startswith("ERROR"):
                    print(f"FAIL {slug}: {page.title()[:160]}", flush=True)
                    continue
                res = json.loads(page.evaluate(
                    "document.getElementById('out').textContent"))
                (outdir/f"{slug}-verify.json").write_text(json.dumps(
                    {k:v for k,v in res.items() if k not in ('shots',)},
                    indent=1))
                for name, durl in res["shots"].items():
                    p = outdir/f"{slug}-{name}.png"
                    p.write_bytes(base64.b64decode(durl.split(",",1)[1]))
                print(f"OK {slug}: {list(res['shots'])} "
                      f"facing={res.get('facing')}", flush=True)
            except Exception as e:
                print(f"TIMEOUT {slug}: {e}", flush=True)
            page.close()
        browser.close()

if __name__ == "__main__":
    main()
