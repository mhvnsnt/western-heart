/* game/js/asset-config.js — remote asset base for split hosting.
 *
 * Owner decision 2026-10-26 ("Split it: Pages shell + GLBs on R2"):
 * GitHub Pages caps a published site at 1 GB; the full deploy set is
 * 6,052.0 MB (measured 2026-10-27). The Pages deploy now ships the
 * tools/deploy/build_pages.py --shell-only); every other .glb/.gltf
 * loads at runtime from the remote asset base below. Nothing is cut
 * from the game, only from the deploy.
 *
 * DECISION (wiring lane 2026-10-26, fixed 2026-10-27): R2 is the
 * remote base (primary candidate); the LOCAL URL is always the next
 * candidate, jsDelivr last. The local fallback is not optional:
 *  - In dev and CI the full repo is served locally; without it, every
 *    non-bundled model fetched from jsDelivr instead of disk, and the
 *    menu-touch e2e fight load timed out (PR #1152, run 40434489083).
 *  - On the Pages shell the local candidate 404s fast (non-bundled
 *    GLBs are not in the shell), so it costs nothing in production.
 *  - jsDelivr 403s every file over 20 MB — exactly the 176 files
 *    (5,914 MB) that are the whole problem — so it can never be a
 *    second base, only a last-resort fallback for small files.
 * One remote base = one manifest, one URL shape, one thing to
 * verify. The fallback costs one extra fetch attempt on failure.
 * GitHub Releases are NOT a candidate: verified live 2026-10-26, their
 * assets send no Access-Control-Allow-Origin header, so fetch() from
 * the game fails. Releases stay the store of record, never the CDN.
 *
 * ONE-LINE CONFIG: set REMOTE_BASE to the bucket's public URL and the
 * game loads remotely. Until then the placeholder below stays in place
 * and remoteBase is NOT ready — see isRemoteReady().
 *
 * Persistent caching (asset-cache.js): downloaded model bytes are
 * stored in the browser Cache API — same-origin AND remote-base
 * loads alike (the cache only stores buffers the game already
 * fetched; see asset-cache.js). Entries carry a 48 h freshness
 * bound, because model files are replaced in place at the same URL
 * when a rig is re-done. Before the 2026-11-01 load-times fix,
 * cross-origin loads were refused by the cache and re-downloaded
 * every session.
 */

export const R2_PUBLIC_URL_PLACEHOLDER = '__WH_R2_PUBLIC_URL__';

/* LIVE since 2026-10-31 — owner no-card route (owner, 2026-10-31:
 * "just move on and do it in a way where we don't have to spend the
 * dollar right now"): the remote base is the PRIVATE Backblaze B2
 * bucket western-heart-assets, served publicly through the Cloudflare
 * Worker below. The Worker signs every request and sends
 * Access-Control-Allow-Origin: *, so the private bucket never needs a
 * public flip or a payment method. No trailing slash.
 * The remote model set (tools/deploy/r2-upload-manifest.json) is
 * uploaded to the bucket under repo-relative paths — the exact shape
 * resolveAssetCandidates() requests. Verified live 2026-10-31 before
 * this was pointed at it: test.txt, zen (29,237,496 B), rave /
 * kiko-tanaka.glb (92,208,012 B, full body), Doc Frank attire4
 * transformed (29,703,496 B) and cyborg-x (41,346,180 B) all return
 * HTTP 200 at exact byte sizes with the CORS header. */
export const ASSET_CONFIG = {
  remoteBase: 'https://western-heart-assets.mhvnsnt.workers.dev',
  jsdelivrBase: 'https://cdn.jsdelivr.net/gh/mhvnsnt/western-heart@main',
};

/* Models bundled in the Pages shell deploy (tools/deploy/build_pages.py
 * --shell-only). build_pages.py reads THIS list out of this file at
 * deploy time, so this is the single source of truth — do not duplicate
 * it by hand anywhere else. Paths are repo-relative. */
export const SHELL_BUNDLED_MODELS = [
  'game/assets/models/demonio.glb', // 8.8 MB — canon fighter, play-verify pair
  'game/assets/models/pantera.glb', // 7.6 MB — play-verify pair
  'game/assets/models/awa-pop.glb', // 0.4 MB
  'game/assets/models/baek.glb', // 0.4 MB
  // Milestone 1 core 8 (game/js/core-set.js): the FIGHT model of each fighter
  // (roster model / first attire), so every core pick loads on the shell
  // while the R2 base is still a placeholder. Over 25 MB is fine on
  // GitHub Pages (100 MB per-file cap); build_pages.py enforces that.
  'roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea-rigged.glb',
  'roster/demonio/attires/attire1/model.glb',
  'roster/demonio/attires/winged-devil/model-rigged.glb',
  'roster/demonio/attires/human/model-rerig.glb',
  'roster/cyborg-x/attires/attire1/model-rigged.glb', // cyborgx fight model (cape-jones-attire1)
  'roster/burger/attires/attire1/model-rigged.glb',
  'roster/burger/attires/attire6/model.glb', // form: speed demon
  'roster/burger/attires/attire7/model.glb', // form: the mouth
  'roster/burger/attires/attire1/model.glb', // form: demon
  'roster/rahkasa/attires/attire1/model-rigged-textured.glb',
  'roster/deathfang/attires/attire1/model.glb',
  'roster/deathfang/attires/attire2/model.glb', // form: werewolf
  'roster/pantera/attires/leomon/model.glb', // select-pane attire 1
  'roster/dio/attires/attire1/source/dio-a1-jade-god-rigged.glb',
  // Doc Frank: the deployed select carries the FULL roster (owner reversal
  // 2026-10-29), and his default fight model (attire 1 transformed) is
  // 25.2 MB — jsDelivr 403s files over 20 MiB and the R2 base is parked,
  // so without bundling every Doc Frank fight fails model load on the
  // live build (404 lane, 2026-10-31).
  'roster/doc-frank/attires/attire1/post-transform/model-rigged.glb',
];

export function isRemoteReady() {
  const b = ASSET_CONFIG.remoteBase;
  return typeof b === 'string' && b.length > 0 && b !== R2_PUBLIC_URL_PLACEHOLDER;
}

/* MODEL_URLS entries are relative to game/ ('assets/models/x.glb',
 * '../roster/...'); customization parts are repo-relative
 * ('customization/parts/...'). Map either form to its repo-relative
 * path so the remote base can serve it at <base>/<repo-path>. */
const REPO_TOPS = ['game/', 'customization/', 'roster/', 'packages/', 'teardown/', 'docs/'];
export function repoPathForModelUrl(url) {
  if (typeof url !== 'string') return url;
  let clean = url.split(/[?#]/, 1)[0];
  if (clean.startsWith('/')) clean = clean.slice(1);
  for (const top of REPO_TOPS) {
    if (clean === top.slice(0, -1) || clean.startsWith(top)) return clean;
  }
  const parts = ['game'];
  for (const seg of clean.split('/')) {
    if (seg === '' || seg === '.') continue;
    // '..' may pop 'game' itself: '../roster/...' is repo-root relative.
    if (seg === '..') { parts.pop(); continue; }
    parts.push(seg);
  }
  return parts.join('/');
}

function isModelUrl(url) {
  return typeof url === 'string' && /\.(glb|gltf)$/i.test(url.split(/[?#]/, 1)[0]);
}

/* Ordered fetch candidates for one MODEL_URLS entry. Local first for
 * bundled models (they ship in the shell); remote first otherwise,
 * then the local URL (dev/CI serve the full repo; on the Pages shell
 * it 404s fast), then jsDelivr as a last resort. Non-model URLs are
 * never rewritten — they ship in the shell. */
export function resolveAssetCandidates(url) {
  if (!isModelUrl(url)) return [url];
  const repoPath = repoPathForModelUrl(url);
  if (SHELL_BUNDLED_MODELS.includes(repoPath)) return [url];
  const out = [];
  if (isRemoteReady()) out.push(`${ASSET_CONFIG.remoteBase}/${repoPath}`);
  out.push(url);
  out.push(`${ASSET_CONFIG.jsdelivrBase}/${repoPath}`);
  return out;
}

/* Fetch + parse one GLB through its candidates, in order, with a
 * GLTFLoader the caller owns. `base` resolves relative candidates
 * (e.g. the repo root for customization parts); omit it to leave
 * relative URLs page-relative, exactly as before. Throws the last
 * candidate's error when every candidate fails. Shared by assets.js,
 * stages.js and customization-consumer.js so all three loaders fail
 * over the same way. */
export async function loadGlbCandidates(loader, url, base) {
  let firstErr = null;
  let lastErr = null;
  for (const cand of resolveAssetCandidates(url)) {
    const fetchUrl = /^https?:\/\//i.test(cand) || !base
      ? cand
      : new URL(cand, base).href;
    try {
      const res = await fetch(fetchUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${fetchUrl}`);
      return await loader.parseAsync(await res.arrayBuffer(), fetchUrl);
    } catch (e) {
      if (!firstErr) firstErr = e;
      lastErr = e;
    }
  }
  // Name the FIRST (primary/local) failure, not only the last fallback's:
  // a local 404 followed by an unreachable CDN used to surface as a bare
  // "Failed to fetch", hiding the asset that is actually missing — the
  // exact failure the 2026-10-24 P0 error-surface fix exists to prevent.
  if (firstErr && lastErr && firstErr !== lastErr) {
    throw new Error(`${firstErr.message || firstErr} (fallback also failed: ${lastErr.message || lastErr})`);
  }
  throw lastErr || new Error(`no candidate loaded for ${url}`);
}
