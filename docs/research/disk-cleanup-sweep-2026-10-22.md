# Disk-cleanup sweep record — 2026-10-22 (worker 70)

Archive-only sweep. NO canon entries invented — archive only; canon bridges come
later from the user.

## Coordination (no duplicate bytes)

- **Negativo A1/A2 + Cornerstone (Ryuji Rock) A1 immutable originals + manifests**:
  already archived by worker 67 in PR #715 (`archive/negativo-eye-glow-20261022`),
  with intake note `docs/research/tripo-intake-2026-10-22-negativo-cornerstone.md`
  and immutable-original tags. Byte-verified 3/3 GLBs against
  `~/workspace/tripo-staging/` via git blob SHA — exact matches. Not re-archived here.
- **Buffalo Bill A1/A2 + Theory A1–A4 immutable originals + manifests + proof renders**:
  already archived by PR #703. Byte-verified 12/12 source files via git blob SHA —
  exact matches; every `tpose-delivery/` buffalo-bill/theory render is byte-identical
  to `docs/proof/buffalo-bill-theory-2026-10-22/` (the `*-v2..v5` variants are duplicate
  copies of the same bytes). Not re-archived here.

## What THIS sweep archived

| Staging file | Repo path | Bytes | Git blob SHA |
|---|---|---|---|
| `tpose-delivery/negativo/a1_front.png` | `docs/proof/tpose-delivery-2026-10-22/negativo-a1-front.png` | 247627 | `78e45db04512447c49e1f273f14ed39d1c36b171` |
| `tpose-delivery/negativo/a2_front.png` | `docs/proof/tpose-delivery-2026-10-22/negativo-a2-front.png` | 247237 | `27774b63775123cd83c720ce62c0ef1e8497ef01` |
| `tpose-delivery/cornerstone/a1_front.png` | `docs/proof/tpose-delivery-2026-10-22/ryuji-rock-a1-front.png` | 196712 | `7c8ef5b6f1455fe00dcc755bd733c316866c9505` |
| `tpose-delivery/parvati-tpose.png` | `docs/proof/tpose-delivery-2026-10-22/parvati-tpose.png` | 1682351 | `fb848d79ef9261af027c05baf0b640ec08ea4325` |
| `tripo-staging/buffalo-bill/a1/bb-a1.render.glb` | `roster/buffalo-bill/attires/attire1/source/buffalo-bill-a1-render.glb` | 14265296 | (blob SHA recorded in commit) |
| `tripo-staging/buffalo-bill/a2/bb-a2.render.glb` | `roster/buffalo-bill/attires/attire2/source/buffalo-bill-a2-render.glb` | 14820616 | (blob SHA recorded in commit) |
| `tripo-staging/theory/a1/theory-a1.render.glb` | `roster/theory/attires/attire1/source/theory-a1-render.glb` | 14749152 | (blob SHA recorded in commit) |
| `tripo-staging/theory/a2/theory-a2.render.glb` | `roster/theory/attires/attire2/source/theory-a2-render.glb` | 13460620 | (blob SHA recorded in commit) |
| `tripo-staging/theory/a3/theory-a3.render.glb` | `roster/theory/attires/attire3/source/theory-a3-render.glb` | 14389256 | (blob SHA recorded in commit) |
| `tripo-staging/theory/a4/theory-a4.render.glb` | `roster/theory/attires/attire4/source/theory-a4-render.glb` | 15511084 | (blob SHA recorded in commit) |

## Deliberate deviation (called out per anti-clobber rules)

The 6 `*-render.glb` intermediates (~87 MB) are NOT part of the immutable-originals
pattern, but the sweep's delete rule ("delete ONLY after 100% byte-confirmed in repo,
no exceptions") required them to live in the repo before cleanup. They are archived
under each attire's `source/` dir as `*-render.glb` — render intermediates,
regenerable from the immutable originals, kept only so the staging disk can be reclaimed.

`tpose-delivery/mirko-tpose.png` is a 0-byte empty file — no content to archive; noted
here and removed from staging.

## ARCHIVE-THEN-CLEAN PIPELINE LAW (owner directive 2026-10-22)

Recorded in `roster/TRIPO-REGISTRY.md`: all future Tripo pulls auto-archive to the repo
(immutable originals + manifest + proof renders, dorowani #603 pattern); staging is
cleaned off disk only after every file is byte-confirmed in the repo (git blob SHA
match). No exceptions.
