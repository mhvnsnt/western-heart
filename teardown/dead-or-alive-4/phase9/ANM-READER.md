# DOA4 Phase 9 — Job 3: XEX anm reader → clips — BLOCKED, exact missing piece named

## Gate
G4. Proof standard (unchanged): a parser that round-trips the anm head byte-exact AND maps records to body streams consistent with the region map (float regions 0x06B000–0x16B000, 0x2AF000–EOF; 8-float groups @0x2B0000 lead). No speculative clips.

## What was attempted
The decisive route named by phase 8: trace the anm reader in the Ghidra project (`~/workspace/ghidra-projects/doa4/DOA4.gpr`, program = default_pe.bin, the decompressed XEX) from the CRI/file-open path. A ready-to-run script was written for exactly this: `phase9/tools/FindAnmReader.java` — it enumerates defined strings containing `anm` / `.afs` / CRI-ADX markers, walks xrefs to containing functions, and decompiles the top candidates (the reader's shift/mask pattern names the head's bit-field widths directly).

## Blocker (environment, verified this session)
**Ghidra cannot start on this VM: there is no Java runtime.** `analyzeHeadless` (Ghidra 12.1.4 at `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/support/analyzeHeadless`) aborts immediately: "ERROR: The 'java' command could not be found in your PATH or with JAVA_HOME." A filesystem search found no `java` binary and no JDK under /usr/lib/jvm, /opt, or ~/workspace/tools. (The phase 1–7 audits ran when a JDK was present; it did not survive VM replacement.) Installing a JDK was out of this lane's scope/timebox and no JDK is mirrored in the workspace stores.

## Status
- No new anm format facts were derived this session; the phase-8 verdict stands verbatim: bit-level field layout + record→stream mapping still missing; records are NOT frame-sequential; ch4/ch5 are a quantized pair on the (v+1)%32 grid; structural round-trip is byte-exact but semantic decode is absent.
- **No clips shipped** (no index → no speculative clips, per gate discipline). Job 3's clip sub-goal is closed-negative for this phase, same as phase 8's Job 3.
- Exact unblock, in order: (1) restore a JDK (any 17/21) on the VM or run the script on any lane host that has one — `analyzeHeadless ~/workspace/ghidra-projects/doa4 DOA4 -noanalysis -scriptPath phase9/tools -postScript FindAnmReader.java`; (2) from the reader's shift/mask pattern, write the bit-unpack parser; (3) validate against the proof standard above before any clip work. Secondary route (also named by phase 8, not run this session): bit-unpack the head at candidate field widths 9–13 bits and re-run the grid/smoothness census on the unpacked fields.
