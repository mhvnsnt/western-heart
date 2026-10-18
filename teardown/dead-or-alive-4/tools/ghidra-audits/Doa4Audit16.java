import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.util.*;

/**
 * DOA4 AUDIT 16: chase the real crypto routines behind the thunks.
 *  1. createFunction() at the 5 Audit11 "unowned" call sites
 *     (0x00b8c7b4, 0x00b92058, 0x00b91fdc, 0x00b8dc94, 0x00b8df88) so they become
 *     analyzable; re-verify ownership.
 *  2. Disassemble + createFunction + decompile the REAL thunk targets:
 *     FUN_00dfd4a8 (behind 00b91ec8) and FUN_00dfd4c8 (behind 00b92120).
 *     Full call list, crypto-flavor mnemonic counts, decompile, and 1-level
 *     callee listing for any bl targets in the 00dfxxxx range.
 */
public class Doa4Audit16 extends GhidraScript {
    DecompInterface decomp;

    public void run() throws Exception {
        println("=== DOA4 AUDIT 16: real crypto routines behind thunks ===");
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        AddressFactory af = currentProgram.getAddressFactory();
        Listing listing = currentProgram.getListing();

        // 1. createFunction at unowned sites
        long[] un = {0x00b8c7b4L, 0x00b92058L, 0x00b91fdcL, 0x00b8dc94L, 0x00b8df88L};
        for (long v : un) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionContaining(a);
            if (f == null) {
                try {
                    f = createFunction(a, null);
                    println("  createFunction @ 0x" + Long.toHexString(v) + " => "
                        + (f != null ? f.getName() + " " + f.getBody() : "FAILED"));
                } catch (Exception e) {
                    println("  createFunction @ 0x" + Long.toHexString(v) + " EXCEPTION: " + e.getMessage());
                }
            } else {
                println("  0x" + Long.toHexString(v) + " already in " + f.getName() + "@" + f.getEntryPoint());
            }
        }

        // 2. real targets
        long[] targets = {0x00dfd4a8L, 0x00dfd4c8L};
        for (long v : targets) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            // disassemble if undefined
            if (listing.getInstructionAt(a) == null) {
                try { disassemble(a); println("  disassembled @ 0x" + Long.toHexString(v)); }
                catch (Exception e) { println("  disassemble @ 0x" + Long.toHexString(v) + " FAILED: " + e.getMessage()); }
            }
            Function f = getFunctionAt(a);
            if (f == null) f = getFunctionContaining(a);
            if (f == null) {
                try { f = createFunction(a, null); } catch (Exception e) {}
            }
            println("=== target 0x" + Long.toHexString(v)
                + " func=" + (f != null ? f.getName() + " " + f.getBody() : "(none)") + " ===");
            if (f == null) continue;
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            Set<String> calls = new TreeSet<String>();
            int nins = 0, xors = 0, rots = 0, muls = 0;
            Set<Long> calleeDf = new TreeSet<Long>();
            while (it.hasNext() && nins < 6000) {
                Instruction ins = it.next(); nins++;
                String s = ins.toString();
                if (s.startsWith("xor ")) xors++;
                if (s.startsWith("rlwinm ") || s.startsWith("rlwimi ") || s.startsWith("rotl")) rots++;
                if (s.startsWith("mulli ") || s.startsWith("mullw ")) muls++;
                for (Reference r : ins.getReferencesFrom()) {
                    if (r.getReferenceType().isCall()) {
                        long tgt = r.getToAddress().getOffset();
                        String nm = "?";
                        if (tgt >= 0xf58764 && ((tgt - 0xf58764) % 0x10) == 0)
                            nm = "thunk-slot" + ((tgt - 0xf58764) / 0x10);
                        Function tf = getFunctionAt(r.getToAddress());
                        calls.add(ins.getAddress() + " -> 0x" + Long.toHexString(tgt)
                            + " " + nm + (tf != null ? " " + tf.getName() : ""));
                        if (tgt >= 0xdf0000 && tgt < 0xe00000) calleeDf.add(tgt);
                    }
                }
            }
            println("  instructions: " + nins + " xor=" + xors + " rot=" + rots + " mul=" + muls);
            for (String c : calls) println("  call: " + c);
            println("  00dfxxxx callees: " + calleeDf);
            try {
                DecompileResults res = decomp.decompileFunction(f, 120, monitor);
                if (res != null && res.decompileCompleted()) {
                    String[] lines = res.getDecompiledFunction().getC().split("\n");
                    println("  decompiled lines: " + lines.length);
                    for (int q = 0; q < Math.min(150, lines.length); q++) println("  C: " + lines[q]);
                    if (lines.length > 150) println("  ... (" + (lines.length - 150) + " more lines)");
                } else println("  decompile failed");
            } catch (Exception e) { println("  decompile exception: " + e); }
        }
        decomp.dispose();
        println("=== AUDIT 16 DONE ===");
    }
}
