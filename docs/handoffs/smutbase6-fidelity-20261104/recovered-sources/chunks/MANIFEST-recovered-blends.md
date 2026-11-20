# Recovered commission blends — chunk manifest (release megami-menajerii-smutbase-20261023)

The two extracted .blend files are stored on this release as numbered
parts. Why parts: uploads larger than ~412 MB from the work VM never
finalized on GitHub's side in this session (assets stuck in "starter"
state, content 404, despite both the gh CLI and a direct curl POST
reporting success — a 419,430,400-byte part failed repeatedly, while
everything at or below 412,236,235 bytes succeeded). Parts are capped
at 300 MB (314,572,800 bytes), uploaded one at a time via direct API
POST, and every part's release digest was verified against the local
file. Reassembly is byte-exact and hash-verified (see pull-back note).

## Parvati(Commission).blend
- Whole file: 595,860,144 B
- Whole-file sha256: cfc9864a15b03989b9dcb559e5fffc02bde8075f26472eeb4308500f01a8612a
- Parts:
  - ParvatiCommission.blend.part-00 — 314,572,800 B — sha256 37941afa278f1a0e984489d81088a69a9f9e3a9f9dfd8d442f9988c2485003c2
  - ParvatiCommission.blend.part-01 — 281,287,344 B — sha256 b8d10570049d6d2a656d048707fb3c58fe0f5e44665471ce5b380d00362c036c
- Reassemble: `cat ParvatiCommission.blend.part-00 ParvatiCommission.blend.part-01 > ParvatiCommission.blend`
  then rename to `Parvati(Commission).blend` if the exact original name is needed,
  and verify sha256 against the whole-file value above.

## Vixen (Commission).blend
- Whole file: 984,617,116 B
- Whole-file sha256: 085d914c6539e0bef89f881ba6887336a1d93115ee6bef792161ec737c375670
- Parts:
  - VixenCommission.blend.part-00 — 314,572,800 B — sha256 88ab6de50ba7eea68c8e1fe6cd33df2c1a1f68966f62c6b19ee1ce172c0f10e4
  - VixenCommission.blend.part-01 — 314,572,800 B — sha256 292fccd12af209f39ef2de1a44e80961e0cbded3ef8f1a4697affe5f742130ba
  - VixenCommission.blend.part-02 — 314,572,800 B — sha256 971939b2489ae4ff90c8c239983c6144166a787b5b638a7ed8ef5a3208b7fa63
  - VixenCommission.blend.part-03 — 40,898,716 B — sha256 38497ad302660189855ca8313b11036974f410cb814c494e4265c4cef64239ce
- Reassemble: `cat VixenCommission.blend.part-00 VixenCommission.blend.part-01 VixenCommission.blend.part-02 VixenCommission.blend.part-03 > VixenCommission.blend`
  then rename to `Vixen (Commission).blend` if the exact original name is needed,
  and verify sha256 against the whole-file value above.

## Archives (stored whole on the same release)
- ParvatiCommission.rar — 326,033,257 B — sha256 2601d9356f5e530cd0abb0956db99fc47e2b70bba4bec58908ce64fc8dc68ff7
- Vixen_Commission.rar — 412,236,235 B — sha256 e6d2754b09f6de050e8a586d6fca3c4ed49f57fcdc4c1f36abfdc41c2be5e5a7

Pull-back verification (2026-11-05): every part re-downloaded from the
release, reassembled, and both whole-file sha256 values reproduced
exactly; the Parvati .rar was likewise re-downloaded and hash-matched.
