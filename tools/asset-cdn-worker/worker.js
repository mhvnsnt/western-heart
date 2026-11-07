// western-heart-assets: public front for the western-heart game models.
// Two origins behind one URL shape (owner decision 2026-11-06):
//  1. GitHub Releases (release `assets-cdn-v1` on mhvnsnt/western-heart)
//     serves the keys in RELEASE_ASSETS — the files Backblaze B2 refuses
//     to accept because the bucket is over its no-card storage cap.
//  2. Everything else falls through to the private Backblaze B2 bucket
//     exactly as before, via the SigV4-signed proxy below.
// Env vars (plain): B2_BUCKET, B2_ENDPOINT (host only, e.g. s3.us-east-005.backblazeb2.com)
// Secrets (encrypted): B2_KEY_ID, B2_APP_KEY
const RELEASE_DOWNLOAD = "https://github.com/mhvnsnt/western-heart/releases/download/assets-cdn-v1/";
const RELEASE_ASSETS = {
  "roster/negativo/attires/attire1/source/negativo-a1-refit.glb": "roster__negativo__attires__attire1__source__negativo-a1-refit.glb",
  "roster/purplerain/attires/attire1/model-rerig.glb": "roster__purplerain__attires__attire1__model-rerig.glb",
  "game/assets/models/kiko-tanaka.glb": "game__assets__models__kiko-tanaka.glb",
  "roster/demonio/attires/attire1/model.glb": "roster__demonio__attires__attire1__model.glb",
  "roster/parvati/attires/attire1/model-rigged.glb": "roster__parvati__attires__attire1__model-rigged.glb",
  "roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb": "roster__tsuyu-asui__attires__attire1__model-rigged-textured.glb",
  "roster/vixen/attires/attire1/model-rigged-noplane.glb": "roster__vixen__attires__attire1__model-rigged-noplane.glb",
  "game/assets/accessories/tripo-demo-prop/source/tripo-demo-model.glb": "game__assets__accessories__tripo-demo-prop__source__tripo-demo-model.glb",
  "game/assets/stages/sunra/mars-sky.glb": "game__assets__stages__sunra__mars-sky.glb",
  "roster/doc-frank/attires/attire2/base/model.glb": "roster__doc-frank__attires__attire2__base__model.glb",
  "roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v1-thindisc.glb": "roster__doc-frank__attires__attire2__dome-fix__model-dome-glass-v1-thindisc.glb",
  "roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v4.glb": "roster__doc-frank__attires__attire2__dome-fix__model-dome-glass-v4.glb",
  "roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v5.glb": "roster__doc-frank__attires__attire2__dome-fix__model-dome-glass-v5.glb",
  "roster/doc-frank/attires/attire2/dome-fix/model-dome-glass.glb": "roster__doc-frank__attires__attire2__dome-fix__model-dome-glass.glb",
  "roster/doc-frank/attires/attire2/transformed/model.glb": "roster__doc-frank__attires__attire2__transformed__model.glb",
  "roster/doc-frank/attires/attire3/transformed/model.glb": "roster__doc-frank__attires__attire3__transformed__model.glb",
  "roster/doc-frank/attires/attire4/base/model.glb": "roster__doc-frank__attires__attire4__base__model.glb",
  "roster/doc-frank/attires/attire4/transformed/model.glb": "roster__doc-frank__attires__attire4__transformed__model.glb",
  "roster/negativo/attires/attire2/source/negativo-a2-rigged.glb": "roster__negativo__attires__attire2__source__negativo-a2-rigged.glb",
  "roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb": "roster__pantera__attires__snow-leopard__pantera-snow-leopard.glb",
  "roster/phantom/attires/attire1/model.glb": "roster__phantom__attires__attire1__model.glb",
  "roster/purplerain/attires/attire1/model.glb": "roster__purplerain__attires__attire1__model.glb",
  "roster/sakura/attires/attire1/model.glb": "roster__sakura__attires__attire1__model.glb",
  "roster/sam-ur-a1/attires/attire1/model.glb": "roster__sam-ur-a1__attires__attire1__model.glb",
  "roster/silvertongue/attires/attire1/model.glb": "roster__silvertongue__attires__attire1__model.glb",
  "roster/silvertongue/attires/attire2/model-improved.glb": "roster__silvertongue__attires__attire2__model-improved.glb",
  "roster/silvertongue/attires/attire2/model.glb": "roster__silvertongue__attires__attire2__model.glb",
  "roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb": "roster__silvertongue__attires__spy-debut__silvertongue-spy-debut.glb",
  "roster/skull/attires/attire1/model.glb": "roster__skull__attires__attire1__model.glb",
  "roster/slice/attires/attire1/model.glb": "roster__slice__attires__attire1__model.glb",
  "roster/slice/attires/attire2/model.glb": "roster__slice__attires__attire2__model.glb",
  "roster/star/attires/attire1/model.glb": "roster__star__attires__attire1__model.glb",
  "roster/star/attires/attire2/model.glb": "roster__star__attires__attire2__model.glb",
  "roster/star/attires/attire3/model.glb": "roster__star__attires__attire3__model.glb",
  "roster/star/attires/attire5/model-improved.glb": "roster__star__attires__attire5__model-improved.glb",
  "roster/star/attires/attire5/model.glb": "roster__star__attires__attire5__model.glb",
  "roster/thor/attires/attire1/model.glb": "roster__thor__attires__attire1__model.glb",
  "roster/thor/attires/attire2/model.glb": "roster__thor__attires__attire2__model.glb",
  "roster/vainabel/attires/attire2/model-rigged.glb": "roster__vainabel__attires__attire2__model-rigged.glb",
  "roster/vainabel/attires/attire2/model.glb": "roster__vainabel__attires__attire2__model.glb",
  "roster/vainabel/attires/attire3/model-rigged.glb": "roster__vainabel__attires__attire3__model-rigged.glb",
  "roster/vainabel/attires/attire3/model.glb": "roster__vainabel__attires__attire3__model.glb",
  "roster/vainabel/attires/attire4/model-rigged.glb": "roster__vainabel__attires__attire4__model-rigged.glb",
  "roster/vega/attires/attire1/model.glb": "roster__vega__attires__attire1__model.glb",
  "roster/waterfall/attires/attire1/model-rigged.glb": "roster__waterfall__attires__attire1__model-rigged.glb",
  "roster/waterfall/attires/attire1/model.glb": "roster__waterfall__attires__attire1__model.glb",
  "roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride-rigged.glb": "roster__yukihyo__attires__attire2__source__yukihyo-a2-bobcat-pride-rigged.glb",
  "roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king-rigged.glb": "roster__yukihyo__attires__attire3__source__yukihyo-a3-tiger-king-rigged.glb",
  "roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb": "roster__zafina__attires__butterfly-default__mariposa-butterfly-default.glb",
  "roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb": "roster__zafina__attires__golden-pharaoh__zafina-golden-pharaoh.glb",
  "roster/zangief/attires/attire1/model-rigged.glb": "roster__zangief__attires__attire1__model-rigged.glb",
  "roster/zangief/attires/attire1/model.glb": "roster__zangief__attires__attire1__model.glb",
  "roster/zen/oversoul/model-rigged.glb": "roster__zen__oversoul__model-rigged.glb",
  "roster/zen/spirit/model-rigged.glb": "roster__zen__spirit__model-rigged.glb",
  "roster/zen/tentacle/model-rigged.glb": "roster__zen__tentacle__model-rigged.glb",
  "roster/zui/attires/attire1/model.glb": "roster__zui__attires__attire1__model.glb",
  "roster/zui/attires/attire2/model.glb": "roster__zui__attires__attire2__model.glb",
  "roster/zui/imports/base_v1.glb": "roster__zui__imports__base_v1.glb",
};
const enc = new TextEncoder();
function hmac(key, msg) { return crypto.subtle.sign("HMAC", key, enc.encode(msg)); }
async function importKey(bytes) { return crypto.subtle.importKey("raw", bytes, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); }
async function sha256hex(data) { const h = await crypto.subtle.digest("SHA-256", data); return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, "0")).join(""); }
async function signV4(env, method, host, path, region) {
  const now = new Date();
  const amzdate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");
  const datestamp = amzdate.slice(0, 8);
  const payloadHash = await sha256hex(new Uint8Array(0));
  const canonicalHeaders = `host:${host}\nx-amz-content-sha256:${payloadHash}\nx-amz-date:${amzdate}\n`;
  const signedHeaders = "host;x-amz-content-sha256;x-amz-date";
  const canonicalRequest = [method, path, "", canonicalHeaders, signedHeaders, payloadHash].join("\n");
  const scope = `${datestamp}/${region}/s3/aws4_request`;
  const stringToSign = ["AWS4-HMAC-SHA256", amzdate, scope, await sha256hex(enc.encode(canonicalRequest))].join("\n");
  let k = await importKey(enc.encode("AWS4" + env.B2_APP_KEY));
  for (const part of [datestamp, region, "s3", "aws4_request"]) k = await importKey(new Uint8Array(await hmac(k, part)));
  const signature = [...new Uint8Array(await hmac(k, stringToSign))].map(b => b.toString(16).padStart(2, "0")).join("");
  return {
    "Authorization": `AWS4-HMAC-SHA256 Credential=${env.B2_KEY_ID}/${scope}, SignedHeaders=${signedHeaders}, Signature=${signature}`,
    "x-amz-date": amzdate,
    "x-amz-content-sha256": payloadHash,
  };
}
export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method Not Allowed", { status: 405 });
    const url = new URL(request.url);
    const key = decodeURIComponent(url.pathname.replace(/^\//, ""));
    const asset = RELEASE_ASSETS[key];
    if (asset) {
      const ghHeaders = {};
      const range = request.headers.get("Range");
      if (range) ghHeaders["Range"] = range;
      const upstream = await fetch(RELEASE_DOWNLOAD + asset, { method: request.method, headers: ghHeaders, redirect: "follow" });
      const respHeaders = new Headers(upstream.headers);
      respHeaders.delete("content-disposition");
      respHeaders.set("Access-Control-Allow-Origin", "*");
      respHeaders.set("Cache-Control", "public, max-age=3600");
      return new Response(request.method === "HEAD" ? null : upstream.body, { status: upstream.status, headers: respHeaders });
    }
    const host = env.B2_ENDPOINT;
    const region = host.split(".")[1] === "backblazeb2" ? host.split(".").slice(1, 3).join("-").replace("s3-", "") : "us-east-005";
    const path = `/${env.B2_BUCKET}${url.pathname}`;
    const headers = await signV4(env, request.method, host, path, "us-east-005");
    const upstream = await fetch(`https://${host}${path}`, { method: request.method, headers });
    const respHeaders = new Headers(upstream.headers);
    respHeaders.set("Access-Control-Allow-Origin", "*");
    respHeaders.set("Cache-Control", "public, max-age=3600");
    return new Response(request.method === "HEAD" ? null : upstream.body, { status: upstream.status, headers: respHeaders });
  },
};
