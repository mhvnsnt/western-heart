/* game/js/asset-config.js — remote asset base for split hosting.
 *
 * Owner decision 2026-10-26 ("Split it: Pages shell + GLBs on R2"):
 * GitHub Pages caps a published site at 1 GB; the full deploy set is
 * ~5,969 MB. The Pages deploy now ships the shell only (see
 * tools/deploy/build_pages.py --shell-only); every other .glb/.gltf
 * loads at runtime from the remote asset base below. Nothing is cut
 * from the game, only from the deploy.
 *
 * DECISION (wiring lane 2026-10-26): R2-ONLY as the remote base.
 * jsDelivr is kept as a fallback candidate only, not a second base:
 *  - R2 serves every file at any size, CORS-configurable, $0 egress,
 *    and the whole 5,969 MB set fits its free 10 GB tier.
 *  - jsDelivr 403s every file over 20 MB — exactly the 176 files
 *    (5,914 MB) that are the whole problem — so it can never be a
 *    second base, only a fallback for small files when R2 is down.
 *  - One remote base = one manifest, one URL shape, one thing to
 *    verify. The fallback costs one extra fetch attempt on failure.
 * GitHub Releases are NOT a candidate: verified live 2026-10-26, their
 * assets send no Access-Control-Allow-Origin header, so fetch() from
 * the game fails. Releases stay the store of record, never the CDN.
 *
 * ONE-LINE CONFIG: set REMOTE_BASE to the bucket's public URL and the
 * game loads remotely. Until then the placeholder below stays in place
 * and remoteBase is NOT ready — see isRemoteReady().
 *
 * Known limitation (asset-cache.js): the persistent Cache API only
 * stores same-origin or relative URLs, so cross-origin remote loads
 * (R2/jsDelivr) are NOT persistently cached — they re-download each
 * session until served same-origin. R2 egress is $0, so this costs
 * time, not money. Documented, not hidden.
 */

export const R2_PUBLIC_URL_PLACEHOLDER = '__WH_R2_PUBLIC_URL__';

/* Fill in when the R2 bucket exists (owner step — see
 * tools/deploy/DEPLOY-SPLIT.md): the bucket's public URL, e.g.
 *   'https://pub-<account-hash>.r2.dev'
 * or a custom domain in front of the bucket. No trailing slash.
 * Do NOT point this at a bucket that does not exist yet. */
export const ASSET_CONFIG = {
  remoteBase: R2_PUBLIC_URL_PLACEHOLDER,
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
 * bundled models (they ship in the shell); remote first otherwise.
 * Non-model URLs are never rewritten — they ship in the shell. */
export function resolveAssetCandidates(url) {
  if (!isModelUrl(url)) return [url];
  const repoPath = repoPathForModelUrl(url);
  if (SHELL_BUNDLED_MODELS.includes(repoPath)) return [url];
  const out = [];
  if (isRemoteReady()) out.push(`${ASSET_CONFIG.remoteBase}/${repoPath}`);
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
      lastErr = e;
    }
  }
  throw lastErr || new Error(`no candidate loaded for ${url}`);
}
