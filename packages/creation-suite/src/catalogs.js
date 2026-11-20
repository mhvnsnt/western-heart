// catalogs.js — unified part-catalog layer for the Creation Suite.
//
// PARTS-REGISTRY.json is the canonical registry, but it carries only a
// slice of the extracted creation data (1,148 of 25,784 indexed parts;
// see customization/CREATION-SUITE-WIRING-AUDIT-2026-10-20.md). Per-source
// catalogs in registry-entry shape (e.g.
// customization/parts/no-mercy/CATALOG.json) carry the full extracted
// sets. This module merges registry + catalogs into one enumeration
// space so UIs and tools browse everything wired — not just the slice.
//
// Dedupe rule: entries are deduped by `file` path; the REGISTRY entry
// wins (it carries bone_aliases / editable / character mapping metadata),
// catalog entries fill in everything the registry does not have.
//
// Data-only, no imports: functions take parsed JSON, like parts.js.

/** Normalize an entry's source: catalogs carry source_game, the
 *  registry carries library; treat them as one axis. */
export function sourceOf(entry) {
  return entry.source_game || entry.library || null;
}

async function fetchJson(url, fetcher) {
  if (!fetcher) throw new Error('catalogs: loadCatalog needs a fetch implementation');
  const res = await fetcher(url);
  if (!res.ok) throw new Error(`catalog fetch failed: ${res.status} ${url}`);
  const data = await res.json();
  if (!Array.isArray(data.parts)) throw new Error(`catalog missing parts[]: ${url}`);
  return data;
}

/** Load one catalog (or the registry — same shape) from a URL. */
export async function loadCatalog(url, fetcher = (typeof fetch !== 'undefined' ? fetch : null)) {
  return fetchJson(url, fetcher);
}

/**
 * Merge a registry object and any number of catalog objects into one
 * flat entry array, deduped by file path (registry first, so it wins).
 * Entries without a file path are always kept.
 */
export function mergeCatalogs(registry, ...catalogs) {
  const seen = new Map();
  const out = [];
  const push = (entry) => {
    const key = entry.file || null;
    if (key && seen.has(key)) return;
    if (key) seen.set(key, entry);
    out.push(entry);
  };
  for (const e of registry?.parts || []) push(e);
  for (const cat of catalogs) for (const e of cat?.parts || []) push(e);
  return out;
}

// --- queries (entries = flat array from mergeCatalogs) ---------------------

export function entriesForSlot(entries, suiteSlot) {
  return entries.filter((p) => p.suite_slot === suiteSlot);
}

export function entriesForSourceSlot(entries, slot) {
  return entries.filter((p) => p.slot === slot);
}

export function entriesForSource(entries, source) {
  return entries.filter((p) => sourceOf(p) === source);
}

export function entriesForClass(entries, partClass) {
  return entries.filter((p) => p.part_class === partClass);
}

export function getEntry(entries, id) {
  return entries.find((p) => p.id === id || p.part_id === id) || null;
}

/** Conversion rollup so a UI can show honest readiness, never a guess. */
export function conversionSummary(entries) {
  const s = { total: entries.length, converted: 0, pending: 0, not_required: 0, failed: 0, none: 0 };
  for (const e of entries) {
    const st = e.conversion?.status;
    if (st && st in s) s[st] += 1;
    else if (e.glb || e.part_class === 'mesh_part') s.none += 1;
    else s.not_required += 1;
  }
  return s;
}

/**
 * Resolve a customization.json v1 profile's part assignments against the
 * merged catalogs. Profile shape (CUSTOMIZATION-JSON-SCHEMA.md):
 *   { parts: { <suite_slot>: { part_id, glb?, placement? } } }
 * Returns one record per assigned slot: the resolved catalog entry, the
 * GLB to load (catalog entry's converted GLB preferred, then the
 * profile's own glb), and a status. Unresolved ids are reported, never
 * silently dropped — a fighter must never lose a part without a trace.
 */
export function resolveProfileParts(entries, profile) {
  const out = [];
  for (const [slot, assignment] of Object.entries(profile?.parts || {})) {
    if (!assignment || typeof assignment !== 'object') continue;
    const partId = assignment.part_id || assignment.id || null;
    const entry = partId ? getEntry(entries, partId) : null;
    out.push({
      slot,
      part_id: partId,
      entry,
      glb: entry?.glb || assignment.glb || null,
      placement: assignment.placement || entry?.placement || null,
      status: entry ? 'resolved' : 'unresolved',
    });
  }
  return out;
}
