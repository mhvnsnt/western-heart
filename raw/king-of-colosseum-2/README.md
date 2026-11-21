# King of Colosseum II — raw files

Complete raw material for King of Colosseum II (Spike, PS2, 2004, SLPM-65602),
landed 2026-11-20 per Mars's order: everything in the repo, split into
<=100MB pieces (piece size 99,000,000 bytes), then deleted from local + VM disk.

## Layout

- `jp/` — Japanese original: the JP ISO (split), the extracted ISO filesystem
  (`iso/`), the extracted archives (`kc2fire000/`, `kc2fire001/`, `kc2fireafs/`,
  `kc2firemvs/`, `modules/`), per-archive SHA-256 manifests, extraction logs.
  JP ISO SHA-256: 7daa1f8c950272f24e9888d26338645fdbac1974da8dbf43b30c0042ceed0511
  (source: Mars's disc / CDRomance; archive.org metadata in the teardown).
- `kactusken-v0.2/` — kactusken's v0.2 English patch (xdelta patches + zip) and
  the built v0.2 English ISO (split). Upstream: https://github.com/kactusken/King-of-Colosseum-II-English
  (public, MIT code; fan translation, non-commercial). v0.2 ISO SHA-256:
  8184f07ac7559d1e1f5fd3695e7a308ded33688281a32433028fed3f41c5327d.
- `english/` — our M2 English ISO (split), built 2026-11-19/20 independent of
  kactusken. SHA-256: e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc.
- `hybrid/` — our M3 hybrid JP/EN ISO (split) + the hybrid KC2FIRE.000 pack.
  Hybrid ISO SHA-256: 4519330547d1974a7f5a40cb4731885a86522129dad6d063e6803c836a082d5c.
  Language toggle: `teardown/king-of-colosseum-2/tools/koc2_lang_toggle.py`.
- `ps2/` — PS2 BIOS zip + memory-card files (scph39001.*).
- `vm-indexes/` — per-archive index.csv files from the VM's /data/koc2 mirror.

## Reassembly

Each split file has a `.manifest.json` next to its pieces (size, SHA-256,
piece list). Reassemble with: `cat <name>.part* > <name>` then verify the
SHA-256 against the manifest.

## Dedupe notes

- The VM's /data/koc2 (2.6G) was verified byte-identical (49,199 files,
  0 mismatches) to the local extract's kc2fire* dirs — landed once here.
- The kactusken repo clone's `extracted/` (4.9G), `rom/` JP ISO copy (4.3G),
  `review/` (84M) and `build/` outputs were NOT landed separately: they are
  regenerable from the landed v0.2 ISO + JP ISO + kactusken's public repo.
- Decoded data (strings, roster, translations, tools) lives in
  `teardown/king-of-colosseum-2/` on this branch (from PR #1770's branch
  muse/koc2, which this branch extends).
