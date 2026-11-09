#!/bin/bash
# reassemble-doa4.sh — pull back DOA4.iso from GitHub release doa4-iso-v1
# (mhvnsnt/western-heart) with FULL sha256 verification. Fixed 2026-11-08.
#
# WHY THIS VERSION EXISTS: the original reassemble.sh verified SIZE ONLY.
# The Nov-2026 local ISO passed every size check while its parts 04/05 were
# corrupt (divergence starts exactly 28,143,616 B into part_04 — the partial
# append point of the first, buggy reassembly; 476,442,907 bytes differ).
# Verdict + proof: teardown/dead-or-alive-4/DOA4-ISO-MANIFEST-2026-11-08.md
# in mhvnsnt/western-heart (release parts proven byte-identical to the
# archive.org source at 22/22 probed offsets; 4 AFS archives whose headers
# sit inside the region parse ONLY with the release bytes).
#
# Rules of this script:
#  - EVERY part is sha256-verified against the release digest table BEFORE
#    it is appended. A bad part is deleted and re-downloaded; after 5 bad
#    attempts the script STOPS LOUD. A bad part is NEVER appended.
#  - On resume, EVERY slice already present in the ISO is hash-verified
#    first. A corrupt prefix STOPS the script — it is never trusted and
#    never auto-truncated (game-file law: a human decides).
#  - Final gate: the assembled ISO's MD5 must equal the verified
#    release-concatenation fingerprint (computed 2026-11-08 by streaming
#    the splice; see manifest).
set -u
cd ~/workspace/_roster100-wave3-20261105/work-item4
ISO=DOA4.iso
TOTAL=7834892288
CHUNK=262144000
EXPECTED_MD5=f97e05521821e93e379d4675018f7ff6
EXPECTED_SHA1=65b3d10ab175bad774e1d655112e67b1398a48c4

# Release digests (GitHub API `digest` field, release doa4-iso-v1,
# re-confirmed 2026-11-08; parts 04/05 also stream- and download-verified).
DIGESTS=(
  d51386e4b1e3482c5355ca249033d3445f03ad5c491146dcff4534b5b78c4114
  def4930de07de3242d2112d6906f2a0421bd2eb860bb27d2da0aa7ae5d63b212
  1e22b3b5ecfba1cf0e36a03cb5c05f70258740bb954997748a73c1228624f122
  294d025910ebef44d021be5c864e82ad8fdc53dde14ebaa32ff2d02d68a8e6c1
  56208ff1a991546b0dcbc9273b5a4e3dfe5dfde9174a1efcb0a4924e0ffd7a7d
  8f8d0f325f356b62c1cdbcf473fd631670f63ef39f1cb135539a0eb608027088
  58f31f666a51fc58e37a01187b2efa103c03eaf63f178ebd03ed8195af866904
  affdb69540430472e27f9419645005f68e75c55db82dc17cdb772cd45dde8d36
  ed523f8b5eb7ef243e936288864bff508176b3c133029b6315f82a43aa59e7c9
  1736bb1b3e3a5da808075854440fee1d397cecac63815e90c2534973816df89e
  c7151a1d351405a5513424c7d4a9215ac98636caaf54f1a34c4e94ccf60f36c3
  fe3c99f7ad55a575887c8d818e376c194c5101058a7f0ce697cfc5b486692e60
  afd6afc7a68505a22d2e46d17a4f78f5d26500ea6e148a3f99a1b8933fe57905
  56a7da02f6ff086d5c4881da7a73bffb3549568a57458d0e5a7c4e6d7800772d
  f0116337c6be5794164e978ae1ea26246fe4ba13e6255a5aa9ce1166aea38d93
  dc268566976bebac1b907f053626f838da5472895a0bb495dbf7e8425a64d0e8
  52850caaeb1be6f751191e9a0d8d1acf1bde0b5523c990c657173ad646e14cf0
  bd5a757134742efad9965817559460aa1087cb730cad57820bcd60ddff7379f1
  accab767ad1e41ba7c6f0e3fe386d2144507d3cd78a34e1f36fc8fa676ab54e4
  60afa89f83aa4af16bead045e6d54a852c5ea1dd61390c88ba0d0005ffdad9b1
  1b8d4704a4e926d340e9379a3b8abb188fa994e48a84471f2d8c1b7fd6e197d7
  447296273974b7f56f87fc25d8c02707517e6c2b706ef2b4241300aebdfa5b1e
  56ab8af9d8ccb1bb6bde4cd3973cdb34b649a55a96d125fb5739922271b7996b
  5b376906631a6ab010bbc996ff5f731ac88d619394ceab8cc15280e98797c4c8
  62f8931d98084e9f2bc927f5fd3f871cca08da1fcfe5085a3c4ed3553a7668a8
  a3ad41ecbc70cfbf35c37de591bb9d8512a5709d9837e34386fbce200b306601
  bcb0b13e4df85d7e93d2ee070636b67c891b4e2432db3316b6793aa971774de9
  0aadfa49bb6a0a412229014825d457fe1add73101041e7a62faf4d71552efdf2
  ef68641e0c91b4c1c0bd3ced45279937287dd2b589f66d98f424679d11a28ae3
  0bd55cf4992db2954b544f6d4861101834d1154c103104aca5b75cb959f38b74
)

slice_sha() { # $1=ISO file $2=part index (1-based) -> sha256 of that slice
  local skip=$(( ($2 - 1) * CHUNK )) count=$CHUNK
  if [ "$2" -eq 30 ]; then count=$(( TOTAL - 29 * CHUNK )); fi
  dd if="$1" bs=1M skip=$skip count=$count iflag=skip_bytes,count_bytes status=none | sha256sum | cut -d' ' -f1
}

have=$(stat -c%s "$ISO" 2>/dev/null || echo 0)
if [ "$have" -gt 0 ]; then
  if [ $(( have % CHUNK )) -ne 0 ] && [ "$have" -ne "$TOTAL" ]; then
    echo "STOP: existing ISO size $have is not part-aligned — refusing to resume on a suspect prefix."; exit 1
  fi
  present=$(( have / CHUNK )); if [ "$have" -eq "$TOTAL" ]; then present=30; fi
  echo "verifying $present existing slice(s) before resume..."
  for i in $(seq 1 $present); do
    got=$(slice_sha "$ISO" $i)
    if [ "$got" != "${DIGESTS[$((i-1))]}" ]; then
      echo "STOP: ISO slice $i sha256 $got != release digest ${DIGESTS[$((i-1))]} — prefix is CORRUPT. Not appending. Human decision required (see manifest)."; exit 1
    fi
    echo "slice $i OK"
  done
fi

start=$(( have / CHUNK + 1 )); if [ "$have" -eq "$TOTAL" ]; then start=31; fi
for i in $(seq $start 30); do
  part=$(printf "doa4-250m.part_%02d" $i)
  if [ $i -lt 30 ]; then want=$CHUNK; else want=$(( TOTAL - 29 * CHUNK )); fi
  ok=0
  for try in 1 2 3 4 5; do
    sz=$(stat -c%s "parts/$part" 2>/dev/null || echo 0)
    if [ "$sz" != "$want" ]; then
      rm -f "parts/$part"
      gh release download doa4-iso-v1 --repo mhvnsnt/western-heart --pattern "$part" --dir parts --clobber 2>/dev/null
      sz=$(stat -c%s "parts/$part" 2>/dev/null || echo 0)
    fi
    if [ "$sz" != "$want" ]; then echo "part $i attempt $try: size $sz want $want"; sleep 3; continue; fi
    got=$(sha256sum "parts/$part" | cut -d' ' -f1)
    if [ "$got" != "${DIGESTS[$((i-1))]}" ]; then
      echo "part $i attempt $try: sha256 $got != release digest — deleting bad download"; rm -f "parts/$part"; sleep 3; continue
    fi
    ok=1; break
  done
  if [ "$ok" != "1" ]; then echo "PART $i FAILED verification after 5 attempts — STOP (nothing appended)"; exit 1; fi
  echo "part $i size+sha256 OK"
  before=$(stat -c%s "$ISO" 2>/dev/null || echo 0)
  cat "parts/$part" >> "$ISO"
  after=$(stat -c%s "$ISO" 2>/dev/null || echo 0)
  if [ "$after" != "$(( before + want ))" ]; then echo "PART $i APPEND FAILED iso $before -> $after want +$want — STOP (part kept)"; exit 1; fi
  rm "parts/$part"
done

final=$(stat -c%s "$ISO")
echo "ISO total: $final (expect $TOTAL)"
if [ "$final" -ne "$TOTAL" ]; then echo "STOP: final size mismatch"; exit 1; fi
md5=$(md5sum "$ISO" | cut -d' ' -f1)
sha1=$(sha1sum "$ISO" | cut -d' ' -f1)
echo "md5  $md5 (expect $EXPECTED_MD5)"
echo "sha1 $sha1 (expect $EXPECTED_SHA1)"
if [ "$md5" != "$EXPECTED_MD5" ] || [ "$sha1" != "$EXPECTED_SHA1" ]; then
  echo "STOP: final fingerprint mismatch — ISO is NOT the verified release concatenation."; exit 1
fi
echo "DOA4.iso pull-back VERIFIED: all 30 parts sha256-checked + full-image fingerprint match."
