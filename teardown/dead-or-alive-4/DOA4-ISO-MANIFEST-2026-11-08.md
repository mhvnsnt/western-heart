# DOA4 ISO — Store Manifest & Correctness Verdict (2026-11-08)

**Verdict: the GitHub release copy is CORRECT. The Nov-2026 local ISO is corrupt in parts 04/05.**
The store the owner ordered (GitHub release `doa4-iso-v1`) was already satisfied — no release asset was changed.

## The store of record

- **Release:** `doa4-iso-v1` on `mhvnsnt/western-heart` — 30 parts, `doa4-250m.part_01` … `part_30`
- **Part size:** 262,144,000 B (parts 01–29); part_30 = 232,716,288 B
- **Full image:** 7,834,892,288 B — Dead or Alive 4 (Xbox 360, XGD), source: archive.org item `dead-or-alive-4-pal-ntscu`
- **Full-image fingerprint of the release concatenation** (computed 2026-11-08 by streaming the verified splice, zero disk staging):
  - MD5 `f97e05521821e93e379d4675018f7ff6`
  - SHA1 `65b3d10ab175bad774e1d655112e67b1398a48c4`
  - CRC32 `1e517470`

## Part digests (sha256 — GitHub API digest field, re-confirmed 2026-11-08)

| Part | Size | SHA-256 |
|---|---|---|
| part_01 | 262,144,000 | `d51386e4b1e3482c5355ca249033d3445f03ad5c491146dcff4534b5b78c4114` |
| part_02 | 262,144,000 | `def4930de07de3242d2112d6906f2a0421bd2eb860bb27d2da0aa7ae5d63b212` |
| part_03 | 262,144,000 | `1e22b3b5ecfba1cf0e36a03cb5c05f70258740bb954997748a73c1228624f122` |
| part_04 | 262,144,000 | `294d025910ebef44d021be5c864e82ad8fdc53dde14ebaa32ff2d02d68a8e6c1` |
| part_05 | 262,144,000 | `56208ff1a991546b0dcbc9273b5a4e3dfe5dfde9174a1efcb0a4924e0ffd7a7d` |
| part_06 | 262,144,000 | `8f8d0f325f356b62c1cdbcf473fd631670f63ef39f1cb135539a0eb608027088` |
| part_07 | 262,144,000 | `58f31f666a51fc58e37a01187b2efa103c03eaf63f178ebd03ed8195af866904` |
| part_08 | 262,144,000 | `affdb69540430472e27f9419645005f68e75c55db82dc17cdb772cd45dde8d36` |
| part_09 | 262,144,000 | `ed523f8b5eb7ef243e936288864bff508176b3c133029b6315f82a43aa59e7c9` |
| part_10 | 262,144,000 | `1736bb1b3e3a5da808075854440fee1d397cecac63815e90c2534973816df89e` |
| part_11 | 262,144,000 | `c7151a1d351405a5513424c7d4a9215ac98636caaf54f1a34c4e94ccf60f36c3` |
| part_12 | 262,144,000 | `fe3c99f7ad55a575887c8d818e376c194c5101058a7f0ce697cfc5b486692e60` |
| part_13 | 262,144,000 | `afd6afc7a68505a22d2e46d17a4f78f5d26500ea6e148a3f99a1b8933fe57905` |
| part_14 | 262,144,000 | `56a7da02f6ff086d5c4881da7a73bffb3549568a57458d0e5a7c4e6d7800772d` |
| part_15 | 262,144,000 | `f0116337c6be5794164e978ae1ea26246fe4ba13e6255a5aa9ce1166aea38d93` |
| part_16 | 262,144,000 | `dc268566976bebac1b907f053626f838da5472895a0bb495dbf7e8425a64d0e8` |
| part_17 | 262,144,000 | `52850caaeb1be6f751191e9a0d8d1acf1bde0b5523c990c657173ad646e14cf0` |
| part_18 | 262,144,000 | `bd5a757134742efad9965817559460aa1087cb730cad57820bcd60ddff7379f1` |
| part_19 | 262,144,000 | `accab767ad1e41ba7c6f0e3fe386d2144507d3cd78a34e1f36fc8fa676ab54e4` |
| part_20 | 262,144,000 | `60afa89f83aa4af16bead045e6d54a852c5ea1dd61390c88ba0d0005ffdad9b1` |
| part_21 | 262,144,000 | `1b8d4704a4e926d340e9379a3b8abb188fa994e48a84471f2d8c1b7fd6e197d7` |
| part_22 | 262,144,000 | `447296273974b7f56f87fc25d8c02707517e6c2b706ef2b4241300aebdfa5b1e` |
| part_23 | 262,144,000 | `56ab8af9d8ccb1bb6bde4cd3973cdb34b649a55a96d125fb5739922271b7996b` |
| part_24 | 262,144,000 | `5b376906631a6ab010bbc996ff5f731ac88d619394ceab8cc15280e98797c4c8` |
| part_25 | 262,144,000 | `62f8931d98084e9f2bc927f5fd3f871cca08da1fcfe5085a3c4ed3553a7668a8` |
| part_26 | 262,144,000 | `a3ad41ecbc70cfbf35c37de591bb9d8512a5709d9837e34386fbce200b306601` |
| part_27 | 262,144,000 | `bcb0b13e4df85d7e93d2ee070636b67c891b4e2432db3316b6793aa971774de9` |
| part_28 | 262,144,000 | `0aadfa49bb6a0a412229014825d457fe1add73101041e7a62faf4d71552efdf2` |
| part_29 | 262,144,000 | `ef68641e0c91b4c1c0bd3ced45279937287dd2b589f66d98f424679d11a28ae3` |
| part_30 | 232,716,288 | `0bd55cf4992db2954b544f6d4861101834d1154c103104aca5b75cb959f38b74` |

## What was wrong

The local ISO (`_roster100-wave3-20261105/work-item4/DOA4.iso`, full sha256
`c1f34b1ca8f978b4922032856713725f7c125306a5c7d8e2fc740f171e744010`) was reassembled
from this release in Nov 2026 with **size-only** per-part checks, over a flaky route.
Its slices 04/05 do not match the release digests (local 04 `ab9d8e84…`, local 05
`a944c7ed…`). Byte-differ (2026-11-08): the local image matches the release for
exactly the first **28,143,616 bytes** of part_04, then **476,442,907 of the
remaining ~496 MB differ** — 28,143,616 B is precisely the partial-append length
recorded when the first, buggy reassembly died mid-part-04 on 2026-11-06. The
second run resumed at part 6 and trusted the corrupt 5-part prefix. Size checks
could not see any of this.

## Proof (2026-11-08, all read-only on the local ISO; splice done via a streaming substituting reader — no multi-GB staging)

1. **Digest chain** — release parts 04/05 confirmed three ways against the Oct-2026
   ingest digests: GitHub API digest field, API stream → sha256sum, and a fresh
   `gh release download` → sha256sum. All agree (`294d0259…`, `56208ff1…`).
2. **archive.org range probes (decisive)** — 22 HTTP Range probes (1 MB + 64 KB)
   against the original source file, spread across the whole disputed span
   (814,575,616 … 1,310,720,000) plus controls at the part_04 head, 4.0 GB, and
   the image tail: **22/22 match the release bytes; 0/22 match the local bytes**
   inside the span; all three agree at every control offset.
3. **XDVDFS parse, both versions** — directory tree (partition base 0xFD90000)
   walks clean under both byte versions: 59 files, 3 dirs, 0 errors, identical
   listings (directory tables live outside the disputed span — the tree alone
   cannot discriminate; file contents do). `extract-xiso -l` on the local ISO
   independently lists the same 59 files / 7,157,955,438 B.
4. **AFS structure inside the span** — four archives whose headers sit inside
   parts 04/05 are garbage under the local bytes and parse cleanly under the
   release bytes:
   - `spr.afs` — local magic `00 00 0d bc f0 10 de eb` ✗ · release: AFS OK (53 entries)
   - `mot.afs` — local magic `00 88 7c ff 00 82 71 fe` ✗ · release: AFS OK (197 entries)
   - `anm.afs` — local magic `00 80 80 ff 00 80 80 ff` ✗ · release: AFS OK (26 entries)
   - `chrthree.afs` — local magic `c6 37 b5 95 fa 7f 68 f8` ✗ · release: AFS OK (188 entries)
   - `snd.afs` (header before the divergence point): table OK under both, payload differs.
   - `avt.afs` / `cmn.afs` (entirely before the divergence point): byte-identical under both, as expected.

## Open footnote (honest, does not affect the verdict)

Neither the local ISO (md5 `00f2eacb…`) nor the verified release concatenation
(md5 `f97e0552…`) reproduces archive.org's *catalogue* full-image checksums for
the item (md5 `b50b59e71dc5105ffa0ed6336c38792d`, sha1 `638f0341…`, crc32
`b9d1a614`). Yet at all 22 probed ranges — including controls outside parts
04/05 — the stored bytes match the file archive.org serves today. The catalogue
checksums therefore appear stale relative to the currently served file; the
per-range byte probes (direct evidence at the disputed offsets) govern the
04/05 question. Full-image equivalence to the 2021 catalogue checksums is
**not** claimed.

## Pull-back (verified procedure)

Use `tools/reassemble-doa4.sh` in this directory (repo copy of the fixed
script). It downloads each part from release `doa4-iso-v1`, **sha256-verifies
every part against the table above before appending**, hash-verifies any
already-present prefix before resuming (a corrupt prefix stops it — never
auto-truncated), and gates the finished image on the MD5/SHA1 fingerprint
above. Manual equivalent:

```bash
gh release download doa4-iso-v1 --repo mhvnsnt/western-heart --pattern 'doa4-250m.part_*'
# verify each part against the table above (sha256sum), then:
cat doa4-250m.part_01 … doa4-250m.part_30 > DOA4.iso   # in numeric order
md5sum DOA4.iso   # must be f97e05521821e93e379d4675018f7ff6
```

## Status of copies after this verdict

- **Release `doa4-iso-v1`: the store of record. Unchanged.**
- **Local ISO: corrupt in parts 04/05 — do not extract from it.** It is
  clearable under the ONE-STORE RULE (100% byte-verified store + retrievability
  proven by the pull-back verification above), pending the parent/owner clear
  decision. A fresh pull-back via the fixed script restores a verified ISO in
  minutes.
- The DOA4 teardown itself is **not** 100% — extraction/decoding continues in
  idle time (see TEARDOWN-IDLE-QUEUE). Note: the workdir extract `mot.afs`
  (27,062,272 B) does not match the verified tree size (75,393,024 B) —
  re-extract from verified bytes before trusting workdir extracts.
