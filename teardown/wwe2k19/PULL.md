# WWE 2K19 teardown, batch 1 (offline file extraction only)
Source: Steam app 817130, depot 817131 (owner license), DepotDownloader filelist batch1.txt (42 PACs: edit/body, edit/ch, edit/head, edit/fullbody_type, ingame/motion/body).
Unpacked with tools/wwe/pac_unpack.py (port of WrestleMINUS HSPC/SHDC/ZLIB/OODL/BPE logic). BPE via yuke_bpe (Luigi Auriemma's reversal of unrrbpe), OODL (Kraken) via zao/ooz built on Linux. Rebuild: tools/wwe/install.sh.
Decoded: 42 HSPC, 45 SHDC, 21 ZLIB, 46 OODL, 607 BPE -> 597 DDS textures, 6 YOBJ models, 5 CNPC + 5 CNCT (CAW part data), 1 OneT, ~1059 unidentified Yuke's sub-blocks (.bin, mostly motion data from 50_mpc).
Names are hash IDs (HSPC 16-hex, SHDC 4-hex); no readable wrestler names imported this batch.
Ghidra not needed for this batch: every container decoded from the ported logic.
Verification: FILES-SHA256.txt (every committed file), SOURCE-SHA256.txt (source PACs).
Next: YOBJ->glTF conversion, YANM decode of motion .bin blocks, more batches.
