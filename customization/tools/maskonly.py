import threading, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8961
shot = sys.argv[2] if len(sys.argv) > 2 else "/tmp/csuite-maskonly.png"
srv = HTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
from playwright.sync_api import sync_playwright
HTML = """<!DOCTYPE html><html><body style="margin:0;background:#111">
<canvas id="c" width="900" height="700"></canvas>
<script type="importmap">{"imports":{"three":"/customization/create-fighter/vendor/three.module.js","three/addons/":"/customization/create-fighter/vendor/addons/"}}</script>
<script type="module">
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const renderer = new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true});
renderer.setClearColor(0x141926);
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(38, 900/700, 0.001, 100);
cam.position.set(0.25,0.05,0.45); cam.lookAt(0,0,0);
scene.add(new THREE.HemisphereLight(0xffffff,0x223344,1.2));
const key = new THREE.DirectionalLight(0xffffff,2.0); key.position.set(2,3,4); scene.add(key);
new GLTFLoader().load('/customization/parts/superhero/batgirl/batgirl-domino-mask.glb', gltf=>{
  const bb = new THREE.Box3().setFromObject(gltf.scene);
  const c = new THREE.Vector3(); bb.getCenter(c); gltf.scene.position.sub(c);
  const s = new THREE.Vector3(); bb.getSize(s);
  document.title = 'MASKSIZE:'+[s.x.toFixed(4),s.y.toFixed(4),s.z.toFixed(4)].join(',');
  const m = new THREE.Mesh(new THREE.Box3Helper(bb).geometry, null);
  scene.add(gltf.scene);
  const axes = new THREE.AxesHelper(0.15); scene.add(axes);
  window.__done = true;
  (function tick(){ requestAnimationFrame(tick); renderer.render(scene,cam); })();
});
</script></body></html>"""
open("/home/hatch/workspace/csuite-ui/demo-root/maskonly.html","w").write(HTML)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":900,"height":700})
    pg.goto(f"http://127.0.0.1:{port}/maskonly.html")
    pg.wait_for_function("window.__done===true", timeout=60000)
    pg.wait_for_timeout(8000)
    print("title:", pg.title())
    pg.screenshot(path=shot, timeout=60000)
    b.close()
srv.shutdown()
print("DONE-MASKONLY")
