import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.util.*;

/**
 * DOA4 AUDIT 15: follow-up on the Audit12 prime lead — decompile
 * FUN_00b91ec8 (SHA-output-fed double call, mode=1) and FUN_00b92120
 * (its sibling in the 00b91xxx crypto neighborhood), list their full call
 * graphs, and re-check whether the 5 Audit11 "unowned" call sites are now
 * inside functions after Audit13's sweep.
 */
public class Doa4Audit15 extends GhidraScript {
    DecompInterface decomp;

    public void run() throws Exception {
        println("=== DOA4 AUDIT 15: prime decrypt-candidate decompile ===");
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        AddressFactory af = currentProgram.getAddressFactory();

        long[] targets = {0x00b91ec8L, 0x00b92120L, 0x00b8d530L, 0x00b8973cL};
        for (long v : targets) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionAt(a);
            if (f == null) f = getFunctionContaining(a);
            println("=== target 0x" + Long.toHexString(v)
                + " func=" + (f != null ? f.getName() + " " + f.getBody() : "(none)") + " ===");
            if (f == null) continue;
            // full disassembly with byte pattern of first 64 bytes (crypto fingerprint)
            dumpFirstBytes(f);
            // all calls made
            Listing listing = currentProgram.getListing();
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            Set<String> calls = new TreeSet<String>();
            int nins = 0;
            while (it.hasNext() && nins < 4000) {
                Instruction ins = it.next(); nins++;
                for (Reference r : ins.getReferencesFrom()) {
                    if (r.getReferenceType().isCall()) {
                        long tgt = r.getToAddress().getOffset();
                        String nm = "?";
                        if (tgt >= 0xf58764 && ((tgt - 0xf58764) % 0x10) == 0)
                            nm = "thunk-slot" + ((tgt - 0xf58764) / 0x10);
                        Function tf = getFunctionAt(r.getToAddress());
                        calls.add(ins.getAddress() + " -> 0x" + Long.toHexString(tgt)
                            + " " + nm + (tf != null ? " " + tf.getName() : ""));
                    }
                }
            }
            println("  instructions: " + nins);
            for (String c : calls) println("  call: " + c);
            // crypto-flavored mnemonics in this function: xor/rlwinm/rlwimi/sraw/mulli
            int xors = 0, rots = 0, muls = 0;
            it = listing.getInstructions(f.getBody(), true);
            int n2 = 0;
            while (it.hasNext() && n2 < 4000) {
                Instruction ins = it.next(); n2++;
                String s = ins.toString();
                if (s.startsWith("xor ")) xors++;
                if (s.startsWith("rlwinm ") || s.startsWith("rlwimi ") || s.startsWith("rotl")) rots++;
                if (s.startsWith("mulli ") || s.startsWith("mullw ")) muls++;
            }
            println("  crypto-flavor counts: xor=" + xors + " rot=" + rots + " mul=" + muls);
            // decompile
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

        // re-check the 5 unowned Audit11 call sites
        println("--- unowned call-site re-check (post-Audit13 sweep) ---");
        long[] un = {0x00b8c7b4L, 0x00b92058L, 0x00b91fdcL, 0x00b8dc94L, 0x00b8df88L};
        for (long v : un) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionContaining(a);
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            println("  0x" + Long.toHexString(v) + " func=" + (f != null ? f.getName() + "@" + f.getEntryPoint() : "(none)")
                + " insn=" + (ins != null ? ins.toString() : "(none)"));
        }
        decomp.dispose();
        println("=== AUDIT 15 DONE ===");
    }

    void dumpFirstBytes(Function f) throws Exception {
        byte[] buf = new byte[64];
        try {
            currentProgram.getMemory().getBytes(f.getEntryPoint(), buf);
            StringBuilder sb = new StringBuilder("  entry-bytes: ");
            for (byte b : buf) sb.append(String.format("%02x", b));
            println(sb.toString());
        } catch (Exception e) { println("  entry-bytes: (read failed)"); }
    }
}
