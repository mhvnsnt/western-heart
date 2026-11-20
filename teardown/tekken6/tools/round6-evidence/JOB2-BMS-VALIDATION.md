# Tekken 6 PSP — ROUND 6 JOB 2: tekken6.bms validation (G5)

Date: 2026-10-21, round 6 attempt 4. Script under test:
`teardown/tekken6/tools/tekken6.bms` (authored round 5, never executed).

## Path taken: equivalence proof (binary execution attempted, blocked)

JOB 2 offered two paths; the binary path was attempted FIRST:

- `https://aluigi.altervista.org/papers/quickbms_linux.zip` (official
  QuickBMS site, Luigi Auriemma; QuickBMS is GPL-2.0) — download
  returned a 5.8 KB **HTML challenge page**, not the zip.
- `https://aluigi.org/papers/quickbms_linux.zip` — connection timed
  out (curl, 90 s).

No QuickBMS binary could be executed in this VM, so validation took
the documented fallback: a line-by-line Python transliteration of the
script's exact semantics, run on real containers and byte-compared
against the proven `decode_all76.py` outputs.

## Transliteration (`round6-evidence/bms_transliteration.py`)

Maps 1:1 onto the .bms: `comtype zlib`; loop `findloc OFF string
"GZIP" 0 FOUND`; `idstring "GZIP"`; `get W1/W2/USIZE/CSIZE long`
(LE u32); `savepos BODY`; `clog NAME BODY CSIZE USIZE` (= zlib
decompress CSIZE bytes, assert USIZE out); `FOUND = OFF + 20`; next.

## Result — 2/2 containers byte-identical

Test file: the raw (decrypted, still-containerised) bytes of gzip
idx0 (entry 454) and idx74 (entry 733, a COM container) taken from
the verified round-6 bulk, concatenated (132,368 bytes):

| Container | USIZE | CSIZE | Transliteration sha256 | decode_all76 sha256 | Match |
|---|---|---|---|---|---|
| @0 (idx0) | 105,472 | 39,139 | `1edcb966…eeaee0ba6` | `1edcb966…eeaee0ba6` | ✅ byte-identical |
| @39168 (idx74) | 607,144 | 93,171 | `ca22c685…f4bca8` | `ca22c685…f4bca8` | ✅ byte-identical |

(Full hashes in `r5_inventory_summary.json` / `decoded76/inventory.json`.)

**G5 verdict: MET via the equivalence-proof path.** The .bms logic
(find-by-magic scan, 20-byte header parse, plain-zlib clog) is proven
equivalent to the adler-exact reference decoder on two dissimilar
containers (a small NDPP plaintext and the largest COM plaintext).
Caveat recorded honestly: the QuickBMS interpreter itself was not
run; if a binary becomes reachable, re-running the same test file
through real QuickBMS is a 5-minute confirmation, not new research.
