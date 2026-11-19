/* ============================================================
   WESTERN HEART — asset-codecs: one place that wires the 2026 web
   asset stack into every GLTFLoader (docs/tech/ASSET-PIPELINE-2026.md).

   * EXT_meshopt_compression  -> MeshoptDecoder (already used before)
   * KHR_texture_basisu (KTX2) -> KTX2Loader + Basis transcoder (wasm,
     vendored in vendor/addons/libs/basis/, no CDN)
   * cooked builds: the deploy step (tools/deploy/cook_assets.py) writes
     a compressed sidecar `<name>.web.glb` next to each original GLB and
     lists it in /cooked-manifest.json. resolveAssetUrl() swaps to the
     sidecar when one exists. Originals stay on the site untouched, so
     any page that doesn't use this module still loads them, and a
     missing manifest just means "load the original".
   ============================================================ */
import * as THREE from 'three';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';

const SITE_ROOT = new URL('../../', import.meta.url); // game/js/ -> site root
let _renderer = null;
let _ownRenderer = null;
let _ktx2 = null;
let _manifest = null;

/** Called by whoever creates the main WebGLRenderer, so KTX2 picks the
 *  best GPU format (ASTC/ETC2 on phones, BC7/S3TC on desktop). */
export function setCodecRenderer(renderer) {
  if (!renderer || _renderer) return;
  _renderer = renderer;
  if (_ktx2) _ktx2.detectSupport(renderer);
}

function ktx2() {
  if (_ktx2) return _ktx2;
  _ktx2 = new KTX2Loader().setTranscoderPath(new URL('../vendor/addons/libs/basis/', import.meta.url).href);
  let r = _renderer;
  if (!r) {
    // No renderer registered yet (tool pages): a 1x1 throwaway just
    // for format detection.
    try { r = _ownRenderer = new THREE.WebGLRenderer({ canvas: document.createElement('canvas') }); }
    catch (e) { r = null; }
  }
  if (r) _ktx2.detectSupport(r);
  if (_ownRenderer) { _ownRenderer.dispose(); _ownRenderer = null; }
  return _ktx2;
}

/** Wire decoders into a GLTFLoader; returns it for chaining. */
export function wireLoader(loader) {
  try { loader.setMeshoptDecoder(MeshoptDecoder); } catch (e) { /* older loader */ }
  try { loader.setKTX2Loader(ktx2()); } catch (e) { console.warn('[WH] KTX2 unavailable:', e && e.message); }
  return loader;
}

function manifest() {
  if (!_manifest) {
    _manifest = fetch(new URL('cooked-manifest.json', SITE_ROOT))
      .then(r => (r.ok ? r.json() : null))
      .then(j => (j && j.entries) || {})
      .catch(() => ({}));
  }
  return _manifest;
}

/** URL of the cooked sidecar for `url` if the deploy made one, else `url`.
 *  `?raw` on the page URL disables the swap (A/B and debugging). */
export async function resolveAssetUrl(url) {
  try {
    if (typeof location !== 'undefined' && /[?&]raw\b/.test(location.search)) return url;
    const abs = new URL(url, typeof document !== 'undefined' ? document.baseURI : SITE_ROOT);
    if (!abs.href.startsWith(SITE_ROOT.href)) return url;
    const rel = decodeURI(abs.pathname.slice(SITE_ROOT.pathname.length));
    const e = (await manifest())[rel];
    return e && e.cooked ? new URL(e.cooked, SITE_ROOT).href : url;
  } catch (e) {
    return url;
  }
}
