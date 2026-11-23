# Vendored files — manifest

Source: https://github.com/Kiloutre/TKMovesets
Pinned commit: `8e6bfc1` (master, pushed 2026-11-18; v1.1)
Licence: GPL-3.0 (see `LICENSE-GPL-3.0.txt`, vendored verbatim).
Fetched: 2026-11-20 via `gh api repos/Kiloutre/TKMovesets/tarball/master`
(direct `git clone` fails on this box — proxy TLS termination; the tarball
is the same commit, verified by the `8e6bfc1` directory name).
Method: copied byte-for-byte, no edits. Verify with:
`sha256sum <file>` against the hashes below.

| File in this directory | Upstream path | Bytes | sha256 |
|---|---|---|---|
| `docs/file-formats.md` | `docs/file-formats.md` | 28481 | `eeaa1ac8b7d12785353af293de9b53af08f2fdd440decfd665cb953c6f253837` |
| `docs/t7-structures.md` | `docs/t7-structures.md` | 32065 | `8941320a6ff750b0d754729660b3ad56f7ea6aee9f2a094c4ded02e57c45f142` |
| `docs/t7-behaviour.md` | `docs/t7-behaviour.md` | 25276 | `0ee3868046f7ff769480150ea4b6ea86d0657b7f72cc542b93ebf82b461ac575` |
| `editor_t7_properties.txt` | `TKMovesets2/Resources/TKMInterface/editor_t7_properties.txt` | 11716 | `7f58cb933ed90c3d0278046af4269c229b1004ae0366a6c44bcd4fcac177fc78` |
| `editor_t7_requirements.txt` | `TKMovesets2/Resources/TKMInterface/editor_t7_requirements.txt` | 6215 | `e1042843612c71452486329978763f51dd6643dd970ae65f59f626e3e42285dd` |
| `LICENSE-GPL-3.0.txt` | `LICENSE.txt` | 35149 | `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986` |

Re-vendor rule: when TKMovesets2 ships a new version, re-fetch the same six
paths at the new commit, update this table (commit + hashes), and note the
change in the PR body. Do not hand-edit a vendored file — if a correction
is needed, it goes in `tkmvst_to_wh.py` or in a dated note here, never as a
silent edit to the vendored text.
