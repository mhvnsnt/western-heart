# tools archive — MANIFEST

Owner-ordered store of the local folder `/home/hatch/workspace/tools` (31294823506 bytes, 251892 files).
Stored as pieces on release `tools-archive-2026-10-31` of `mhvnsnt/western-heart`. Every piece was verified after upload: GitHub asset size == local size AND GitHub sha256 digest == locally computed sha256.
Pull-back test: piece `chunk-020.tar.gz` re-downloaded and hash-matched (2026-11-01T00:25:06+0000).

## How to pull back / reassemble
- `chunk-NNN.tar.gz` — `gunzip | tar -x` at the restore root; the chunks together contain every file (paths relative to the folder root). File lists per chunk are in MANIFEST.json.
- `file__<path>.gz` — `gunzip` to restore that single file.
- `file__<path>.partNN` / `file__<path>.segNN` — byte slices of one large file: `cat` all its slices in order to restore it.
- Empty directories were not preserved (files only).

## Pieces (29), stored bytes total 16610744993

| asset | kind | source | bytes | sha256 |
|---|---|---|---|---|
| chunk-000.tar.gz | targzstream | 29244 files | 737809663 | 6fb3126b6ae8ddd2040b9e6a7815c0ab928416bde90e80515e77e06dd8f12c84 |
| chunk-001.tar.gz | targzstream | 28993 files | 533062024 | 99cced8819701d6052d680567f8a17647785ec5006c1dfb0e7285cf456ab4b17 |
| chunk-002.tar.gz | targzstream | 9877 files | 477961789 | a65c4c63a12b0e3b8f270353768ffd8f564e8360229c6845f7dacdce05a339b6 |
| chunk-003.tar.gz | targzstream | 4313 files | 353828396 | ee6067bbddeb2e09c844d5af297dccd3743f248fb9c9d2999515ff142b0d14a4 |
| chunk-004.tar.gz | targzstream | 6289 files | 354103404 | 9f0525244e787cf0fda9e2d5d278e7ac6c72c1cfae6076f4098f6af1fa8c7a22 |
| chunk-005.tar.gz | targzstream | 5374 files | 801864870 | 510f8a36654c062ed8d7d7c36b10ba3a570e384852ba8995ebd64ea03359ce63 |
| chunk-006.tar.gz | targzstream | 10627 files | 576173817 | 31bc878a0ad20c2ac128daca65d3f816a096ce33a203a400bac7cf702f405f3c |
| chunk-007.tar.gz | targzstream | 13721 files | 826126563 | f69d3bad27a9b567c5c99c524d920db4e6065f126d1d63beeadf6bc978568f74 |
| chunk-008.tar.gz | targzstream | 7448 files | 848592923 | 5d5e70442d6c0b33c45d0bb312f5d41ac53dff8459500347438d5b7ddfeae705 |
| chunk-009.tar.gz | targzstream | 17520 files | 262118795 | 1bcdc88509249a793afc5cbfdf0bb511829867bbd61e97ab88206eb94afd3937 |
| chunk-010.tar.gz | targzstream | 976 files | 261470875 | 9e6efa7af4a1129e6edcb4c89ef76747742937344e2fe84cfebf4117090abbd1 |
| chunk-011b.tar.gz | targzstream | 653 files (split of chunk-011) | 107184729 | d0f6c9de951f8b01b9e4f68286adcc5d0143295e424cf4023f93afd1f796b4a3 |
| chunk-012.tar.gz | targzstream | 9635 files | 471530312 | 77722ba01965daa6345062c0396712b2c38195a6e44b3799804bb0e6d2dc93a9 |
| chunk-013.tar.gz | targzstream | 13201 files | 645504095 | c1fb182636015e859832c96dc2c48efb7ad29cf4f2a27562eb776149447177cd |
| chunk-014.tar.gz | targzstream | 24294 files | 611692652 | a7db50ee29cfd830f480c7ded6d0a179ba34a4de35357e67a9acdeaefd333c16 |
| chunk-015.tar.gz | targzstream | 14257 files | 650435110 | 433d14b597a48f9834517bda34833f8c020002c7cce52945be19436f5c69328f |
| chunk-016.tar.gz | targzstream | 12369 files | 850090946 | a6c2e6718115355450f0b38e247d83c60aa9f47da232c8d1fd2f0718b60135fe |
| chunk-017.tar.gz | targzstream | 15932 files | 883013259 | 304b5aa72cd3cf016a17aac8c0e67393207da5ac362beef572e60805ff908d58 |
| chunk-018.tar.gz | targzstream | 8058 files | 712415036 | fbca09f73d496f86d5aafd17f59361d849b4cf5ddf3b2bf995c035aaf8e1d1a7 |
| chunk-019a.tar.gz | targzstream | 3512 files (split of chunk-019) | 762109131 | d4bb744a7d9a3981c5a14db18f431d6cdb7fff57779270f5c948fab92c018388 |
| chunk-019b.tar.gz | targzstream | 14220 files (split of chunk-019) | 426005743 | 4cf539a382a967a94e7d08afc4a2a962ba281158c6d17535e6fb16ebde93d572 |
| chunk-020.tar.gz | targzstream | 1377 files | 834801 | 60ea0479c7bd199ceeb3b89d4c74023266b462d738352bc440d1049b92bece0e |
| file__godot__Godot_v4.7.2-stable_export_templates.tpz.seg00 | slice | godot/Godot_v4.7.2-stable_export_templates.tpz bytes 0..700000000 (from chunk-011a.tar.gz) | 700000000 | becf601d28b40547e178bf8a0f010247226858c23955b09529f3239b7b61071c |
| file__godot__Godot_v4.7.2-stable_export_templates.tpz.seg01 | slice | godot/Godot_v4.7.2-stable_export_templates.tpz bytes 700000000..1281349702 (from chunk-011a.tar.gz) | 581349702 | 2c4777fba92c087ad585e4c3afb0abf4d7d2b96e45d0d55941ccbc12d6ef7d55 |
| file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.seg00 | slice | tooncrafter/checkpoints/tooncrafter_512_interp-pruned-fp16.safetensors bytes 0..700000000 | 700000000 | e31d0c93aeccaed39b0d69ab2f9b8d9c28a60b9723660eeaa5a0b89d77a3c14e |
| file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.seg01 | slice | tooncrafter/checkpoints/tooncrafter_512_interp-pruned-fp16.safetensors bytes 700000000..1400000000 | 700000000 | 02cd7eef0c395953f1979ae6c9a1f9c770e4c0b7fc61bcf829b30b5cf4674745 |
| file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.seg02 | slice | tooncrafter/checkpoints/tooncrafter_512_interp-pruned-fp16.safetensors bytes 1400000000..2100000000 | 700000000 | 40cefe30863a8edf99cbeb3388a09552ee9aca2f8b09f92f1623f0c703323add |
| file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.seg03 | slice | tooncrafter/checkpoints/tooncrafter_512_interp-pruned-fp16.safetensors bytes 2100000000..2800000000 | 700000000 | 550699ff284a8defc35c765f587cff0a65c2c60e4de851a63fb6174ff3d9707d |
| file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.seg04 | slice | tooncrafter/checkpoints/tooncrafter_512_interp-pruned-fp16.safetensors bytes 2800000000..3175466358 | 375466358 | 98e3213a636525d18b762ad3db936b469ef864b93a0300581bf73086b322a1d2 |

Extra assets on the release not part of the verified tree: file__tooncrafter__checkpoints__tooncrafter_512_interp-pruned-fp16.safetensors.part02
