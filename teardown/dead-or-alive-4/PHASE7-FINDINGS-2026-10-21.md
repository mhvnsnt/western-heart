# DOA4 Phase 7 — Keystream Re-Examination, anm Structure, Wiring Prep (2026-10-21)

Follow-on to PR #435 (phase 6). Branch:
`feat/doa4-phase7-keystream-anim-wiring-20261021` (stacked on
`feat/doa4-phase6-batch-skinned-tx2d-20261021`). State file:
`~/workspace/_doa4p2-scratch/PHASE7-STATE.md`.
Tools: `tools/phase7/` in this PR. All byte work below was run this
lane on freshly range-fetched bytes from release
`doa4-mirror-20261017` (extracted tar, 524288000-byte parts; fetch tool
copied from phase 6 as `tools/phase7/fetch.py`).

## 0. Data acquired this lane (tar data-start offsets, sizes verified)

| file | tar data offset | size | first 4 bytes |
|---|---|---|---|
| chrone.afs | 1212324864 | 366094336 | `3e84aa31` |
| chrtwo.afs | 1578419712 | 548042752 | `3ebe10dc` |
| chrthree.afs | 2135433728 | 762955776 | `bf3f690f` |
| mot.afs | 1136446976 | 75393024 | `3c06f63e` |
| stg.afs | 321167872 | 815278080 | `3c086e2e` |
| anm.afs | 2898390016 | 2949120 | `c1ff2852` |

anm.afs was fetched whole (2.9MB); the other five as 256KB heads.
Tar walk that located anm.afs (it sits directly after chrthree.afs,
before avt.afs): `tools/phase7/tarwalk.py`.

## 1. G1 — the "keystream" re-examined: the premise fails on the real bytes

### 1.1 The six "header keys" carry no independent information

The keys in `ENCRYPTION-ANALYSIS.md` (anm `80b97b52`, chrone
`7fc2f931`, chrtwo `7ff843dc`, chrthree `fe793a0f`, mot `7d40a53e`,
stg `7d4e3d2e`) were each *derived* by XORing that file's first 4
bytes against the assumed plaintext `AFS\0`. Any 4 bytes XOR to
`AFS\0` under exactly one 4-byte key, so the derivation cannot fail
and the keys corroborate nothing. This also explains the prior
lanes' negative results, which are exactly what non-existent keys
predict: the keys are not stored in the PE (searched), are not
filename hashes (MD5/SHA1/CRC32/djb2/sdbm/FNV-1a all tested), and no
algorithm reproduces them (Audit 19: 0/6). Job 1 route (c) — the six
keys as simultaneous equations on a generator — is therefore void:
the equations are identities, not constraints.

### 1.2 chrone/chrtwo/chrthree/mot/stg do NOT begin with an AFS TOC

Measured on the heads fetched this lane (`tools/phase7/analyze1.py`,
`analyze3.py`): the first 256KB of chrone, chrtwo, chrthree and mot
are big-endian float streams — BE-f32 plausibility (|f| in (0,2],
non-zero) is 0.998 / ~0.99 / 1.000 / 0.977 window after window, with
exponent bytes concentrated at 0x3e/0x3f/0xbe/0xbf. stg scores 0.812
(floats mixed with stage records). Random or cipher bytes score
~0.49 on the same test (anm's head, §2, scores 0.47–0.50). First
floats, chrone: 0.259, 0.551, −0.782, 0.025, −0.623, −0.095, 0.131,
0.081 — unit-range vectors, not table integers.

A standard AFS TOC at offset 0 — the layout the repo's own
`tools/afs_extract.py` parses for the genuinely standard archives
(snd/spr/avt/cmn, extracted fine in 2026-10-17) — is excluded in
both endiannesses: a BE TOC would put 0x00 at every entry's offset
high byte (observed: 0x3e/0x3f modes); an LE TOC would put 0x00 at
aligned low bytes (observed: float exponent bytes). No XOR/ADD
period-16 cipher maps TOC integers to output that is 99.8% plausible
floats; and phases 3–6 already parse these files' packages
(XPR2/MdlGeo/MdlInfo/Hie) as plaintext with no decryption step —
chrone pkg00's own vertex-pool data begins at file offset 0, its
XPR2 directory sits at 3502080 (phase-6 graph in git).

**Conclusion (proven on the fetched heads):** the five model/motion/
stage containers are not encrypted at offset 0 and carry no AFS TOC
there. They are Team Ninja package streams — self-describing per
package via the XPR2 directory, which is why every successful lane
since phase 3 located content by scanning, never by TOC. The "AFS
TOC cipher" that G1 asked this lane to crack does not exist as
specified. What actually remains encrypted-or-encoded is anm.afs's
head (§2) — a different and smaller problem.

### 1.3 XEX route (Ghidra/Capstone) — leads closed, honestly

- The 2026-10-17 "runtime S-box" lead (code at VA 0x822f06d0, BSS
  table at 0x83022eda) was re-checked with Capstone: the region is a
  BSS zero-initialisation routine (hundreds of `stb/sth/stw r31`
  stores of 0 across globals). No table is built there. Lead closed
  as a misread, same class as Audit 19's 00dfxxxx CRT lead.
- A full-.text scan for lis+addi/ori address constructions of the
  BSS table, the .data AFS structs (0x82c48fa0) and the CRI error
  strings found **zero** complete constructions within 8
  instructions (`tools/phase7/scan_refs2.py`): Xenon code reaches
  these via base-register/TOC addressing, so static address hunting
  of this form cannot bound the loader. Combined with Audits 1–19
  (string-xref space exhausted), the static XEX route to a "decrypt
  routine" is closed — and per §1.2 there is no TOC-decrypt routine
  to find. The CRI `adxf_*` library in the binary serves the four
  standard archives.

### 1.4 Five-oracle verdict for G1 (as specified in GRE PR #29)

| Oracle | Result |
|---|---|
| 1. Full-payload XPR2 decode | PASS — but by *absence* of cipher: phase 6 decoded all 148 packages' textures/geometry as plaintext (PR #435). No keystream was applied because none exists on these payloads. |
| 2. Table self-consistency | FAIL as posed / VOID: no AFS TOC exists at the head of chr*/mot/stg to decrypt (§1.2). The premise "decrypted TOC parses as valid AFS table" is untestable — there is no TOC. |
| 3. Animation float plausibility | PARTIAL: anm.afs payload regions are plaintext BE floats (§2) scoring 0.96–0.99; its head region scores ~0.49 and remains undecoded (§2.3). |
| 4. Cross-container consistency | FAIL as posed: no single generator explains six containers, because five need no decryption and the sixth (anm head) matches none of the tested generators (§2.3). |
| 5. Entropy | chr*/mot/stg heads: entropy ~7.0–7.3 *with* 0.98–1.00 float plausibility — float-mantissa entropy, not cipher entropy (the 2026-10-17 lanes read the same numbers as encryption; the plausibility test separates the two). anm head: entropy 6.84 with ~0.49 plausibility — genuinely transformed or natively non-float data. |

**G1 status: NOT PROVEN as a keystream crack, because the object of
the crack does not exist for five of six containers (proven above),
and anm's head resists every generator tested (§2.3). No decoder is
shipped. This is the negative-record outcome the phase brief allows,
with the premise correction documented as the finding.**

## 2. anm.afs — region map and what is actually in it

Full-file map (`tools/phase7/analyze4.py`, `analyze5.py`; 4KB
windows, category transitions):

| range | content |
|---|---|
| `0x000000–0x06B000` | transformed/encoded head (entropy ~6.84, float plausibility ~0.49, zero fraction ~0). See §2.3. |
| `0x06B000–0x16B000` | **plaintext BE float streams** (plausibility 0.96–1.00). At `0x2AF000+` the same class resumes. Sample at 0x2B0000: 8-float groups drifting smoothly group-to-group — keyframe-shaped data (§3). |
| `0x16B000–0x1FB000` | low-entropy mixed region (entropy 1.8–3.9, raw-zero 0.28–0.58): sparse integer/index-like data, not floats, not cipher-grade entropy. |
| `0x1FB000–0x21B000` | float islands in mixed data (plausibility spikes 0.89–0.94). |
| `0x21B000–0x29D000` | zero padding (raw-zero up to 0.88). |
| `0x29D000–0x2AF000` | mixed + a second transformed chunk at `0x2A1000` (entropy 6.82). |
| `0x2AF000–0x2D0000` (EOF) | plaintext BE float streams (plausibility 0.96), with a zero gap at `0x2CD000`. |

This corrects two inherited claims: the 2026-10-20 sweep audit's
"anm is obfuscated through its body / no plaintext BE-float
keyframe streams" (its [-1,1]-run test missed these regions), and
the coordinator premise "the keystream covers the anm.afs BODY"
(the body is mostly plaintext; the head and one mid chunk are not).

### 2.3 The anm head — structure found, generator not found

- Byte-match autocorrelation peaks at P=16 (0.405 over the first
  64KB); exact 16-byte blocks repeat (top block ×21 in 64KB).
- Read as 16-byte records, field `+8..+12` takes only **68 distinct
  values** in the first 2000 records (other fields: 1007–1351) —
  the head is natively structured, not uniformly ciphered. The
  recurring u16 units end in `0x1f`/`0xff` at extreme rates
  (`0x8c1f` ×4742, `0x6c1f` ×4670, `0x8bff` ×3822 in the head).
- Generators tested and excluded (`tools/phase7/analyze6.py`,
  `analyze7.py`): repeating XOR period 16 (excluded by mode
  contradiction — block-0's assumed key byte 0xb9 at position 1
  forces the plaintext mode byte at that position to be 'F' at
  64% frequency), ADD period 16 (same contradiction), 16/32-bit
  byteswap × BE/LE float reads (all score 0.41–0.61, i.e. random).
- Remaining hypotheses, documented not claimed: a native TN
  animation index format whose fields are small integers and
  packed channel data (the 68-value field is the strongest lead),
  or a transform that mixes within each 16-byte record (ECB-like),
  which the exact block repeats permit but no crib has yet cracked.

## 3. G4 animation — status

- mot.afs: motion-adjacent packages were assembled in phases 3–6 as
  model packages (11/11 triangulated GLBs in the old set are pools,
  not clips). No clip-format parse of mot exists yet; mot's head is
  plaintext floats (this lane, §1.2), so mot is *not* gated on any
  cipher — it is gated on format work (record layout of the float
  streams), which is the same work anm's plaintext regions need.
- anm.afs: the plaintext float regions (§2) are decodable in
  principle without G1 — the gate is the undecoded head/index,
  which presumably maps float streams to clips/bones. Decoding the
  streams without the index would be guessing at clip boundaries;
  per the no-guessing law this lane does not ship speculative
  clips. The 8-float drifting groups at 0x2B0000 are recorded as a
  lead (per-frame channel groups), not as a decoded clip.
- No animation is claimed decoded this phase. G4 remains open,
  re-gated on: (a) anm head/index format, (b) mot/anm stream record
  format. Neither is a cipher problem anymore.

## 4. G5 QuickBMS — negative record

No `.bms` is published: there is no proven decryption to publish
(§1.4). Publishing a script that XORs file heads with the §1.1 keys
would corrupt plaintext data and dress a tautology as a crack —
exactly what the phase brief forbids. The extraction that *is*
reproducible is the phase-6 pipeline (XPR2 scan → assembly graph →
skinned GLB), already in git at `tools/phase6/`.

## 5. Pull-in log

- Xenia texture/fetch-constant work (phase 6, BSD) — carried, not
  new this phase.
- Capstone 5.0.7 (BSD) — XEX disassembly checks in
  `tools/phase7/dis_sbox.py`, `scan_refs2.py`.
- parkerallan/doa4-recomp (XenonRecomp output for this XEX) —
  cloned this lane (HEAD, generated C++ in `generated/default/`)
  and grepped: no `chrone`/`anm`/`adxf` references exist in the
  generated code (file names live in data, not code), so the recomp
  offers no shortcut to the loader; tracing the .data descriptor
  tables' runtime-buffer writers through it remains possible
  future work. No code copied.
