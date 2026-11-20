# M2 portrait freshness gate — proof notes (2026-11-05)

Item M2 of docs/handoffs/ROSTER-100-FIX-2026-11-04.md (Roster-100 Wave 2):
extend `test/portraits.test.mjs` to fail on byte-identical placeholder cards
and on manifest claims that contradict capture provenance.

## Measured state on main a0619f3b (before the gate)

- 72 top-level PNGs in `game/assets/portraits/`, 59 `portraits-manifest.json`
  entries, 50 select fighters.
- Exactly two byte-identical groups:
  - byou, gyou, kai, retsu, rin, sha, tou — 6,523 B each, sha256
    `61d84488574aa8ba43a09d1eb4a3ab633ef3b056674ba28a41618340bec789fc`
    (the #1565 placeholder set; the manifest claims steve-fox / pantera
    captures for them while `attiresFor()` returns no attire — `model: null`).
  - ryuji, ryuji-rock — 75,713 B, sha256
    `c688c3eb3b728411dff3e276064d3fff8368535284cd41ae0d949d3d24099618`
    (documented duplicate card; ryuji hidden, same body by design, owner
    ruling #6).
- The old test passed this state silently: it never hashed a PNG.

## Gate design (in `test/portraits.test.mjs`, registry in
## `tools/portraits/KNOWN-PLACEHOLDERS.json`, dated 2026-11-05)

- Every top-level card is sha256-hashed.
- Placeholder bytes may appear ONLY on the 7 registered fighters (exactly
  the L3 missing-model set), and the placeholder-byte group must equal the
  registry set exactly.
- Any other byte-identical group must match a registered
  `knownDuplicateGroups` entry (today: ryuji/ryuji-rock).
- A manifest entry claiming a capture `model` for a fighter with no
  attire-1 model fails (the false-claim class), unless the fighter is
  registered (placeholder set or duplicate group).
- Shrink rules (POSE-BLOCKERS pattern): a registered placeholder whose
  bytes change fails until its entry is removed; a registered duplicate
  group that stops sharing bytes fails until its entry is removed or
  updated. The registry cannot go stale silently in either direction.

## Both-ways proof (this directory)

- `gate-pass.txt` — extended test on the unmodified a0619f3b tree:
  "50 select fighters, 6 pose blockers, 7 registered placeholders / PASS",
  exit 0.
- `gate-fail-unregistered-placeholder.txt` — aotsuki's card replaced by the
  placeholder bytes: FAIL, exit 1 (unregistered placeholder + group
  mismatch).
- `gate-fail-registry-gap.txt` — "rin" removed from the registry while its
  placeholder card and false manifest claim remain: FAIL, exit 1
  (unregistered placeholder + group mismatch + false-claim line naming the
  steve-fox claim — the exact #1565 defect class).
- `gate-fail-duplicate.txt` — skull's card overwritten with pantera's:
  FAIL, exit 1 (unregistered byte-identical group).

Negative runs were made in a disposable sparse clone used only as a test
harness (no commits from it — the PR was built via the Git Data API per
the repo NO-SPARSE-COMMIT LAW); the clone tree was restored after each run.

## Observed, out of scope (not gated, not changed)

13 top-level cards carry no manifest entry: armor-king, blanka,
demonio-bloodline-ember, demonio-human, demonio-winged, doc-frank-hood,
doc-frank-machine-shop, doc-frank-wowomomo, iori, jin_soul,
kronos-attire2, vega, zangief. These are form/variant and base-model-id
cards outside the roster-fighter manifest's scope; the gate deliberately
does not invent a provenance requirement for them.

No card bytes changed by this item. Deletions: none.
