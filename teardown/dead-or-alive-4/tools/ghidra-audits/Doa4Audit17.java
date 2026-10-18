import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.util.*;

/**
 * DOA4 AUDIT 17:
 *  1. Decompile the 5 functions created in Audit16 (the formerly-unowned call
 *     sites): FUN_00b8c7b4, FUN_00b92058, FUN_00b91fdc, FUN_00b8dc94, FUN_00b8df88.
 *     Full disassembly + call list + crypto-flavor counts + decompile.
 *  2. Raw byte dump at 0x00dfd4a8 and 0x00dfd4c8 (the thunk targets that would
 *     not disassemble): 64 bytes each + entropy/zero check, plus the memory
 *     block name/permissions covering each address.
 */
public class Doa4Audit17 extends GhidraScript {
    DecompInterface decomp;

    public void run() throws Exception {
        println("=== DOA4 AUDIT 17: new functions decompile + 00dfxxxx byte dump ===");
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        AddressFactory af = currentProgram.getAddressFactory();
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();

        long[] targets = {0x00b8c7b4L, 0x00b92058L, 0x00b91fdcL, 0x00b8dc94L, 0x00b8df88L};
        for (long v : targets) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionAt(a);
            if (f == null) f = getFunctionContaining(a);
            println("=== 0x" + Long.toHexString(v)
                + " func=" + (f != null ? f.getName() + " " + f.getBody() : "(none)") + " ===");
            if (f == null) continue;
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            int nins = 0, xors = 0, rots = 0, muls = 0;
            while (it.hasNext() && nins < 4000) {
                Instruction ins = it.next(); nins++;
                String s = ins.toString();
                if (s.startsWith("xor ")) xors++;
                if (s.startsWith("rlwinm ") || s.startsWith("rlwimi ") || s.startsWith("rotl")) rots++;
                if (s.startsWith("mulli ") || s.startsWith("mullw ")) muls++;
                if (nins <= 60) println("  D: " + ins.getAddress() + " " + s);
            }
            println("  instructions: " + nins + " xor=" + xors + " rot=" + rots + " mul=" + muls);
            // calls made
            Set<String> calls = new TreeSet<String>();
            it = listing.getInstructions(f.getBody(), true);
            int n2 = 0;
            while (it.hasNext() && n2 < 4000) {
                Instruction ins = it.next(); n2++;
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
            for (String c : calls) println("  call: " + c);
            try {
                DecompileResults res = decomp.decompileFunction(f, 120, monitor);
                if (res != null && res.decompileCompleted()) {
                    String[] lines = res.getDecompiledFunction().getC().split("\n");
                    println("  decompiled lines: " + lines.length);
                    for (int q = 0; q < Math.min(100, lines.length); q++) println("  C: " + lines[q]);
                    if (lines.length > 100) println("  ... (" + (lines.length - 100) + " more lines)");
                } else println("  decompile failed");
            } catch (Exception e) { println("  decompile exception: " + e); }
        }

        // raw byte dumps at the mystery targets
        long[] dumps = {0x00dfd4a8L, 0x00dfd4c8L};
        for (long v : dumps) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            MemoryBlock b = mem.getBlock(a);
            println("=== bytes @ 0x" + Long.toHexString(v) + " block="
                + (b != null ? b.getName() + " r=" + b.isRead() + " w=" + b.isWrite() + " x=" + b.isExecute()
                    + " init=" + b.isInitialized() + " [" + b.getStart() + "-" + b.getEnd() + "]" : "(no block)") + " ===");
            byte[] buf = new byte[64];
            try {
                int n = mem.getBytes(a, buf);
                StringBuilder sb = new StringBuilder("  hex: ");
                int zeros = 0;
                boolean[] seen = new boolean[256];
                int distinct = 0;
                for (int i = 0; i < n; i++) {
                    sb.append(String.format("%02x", buf[i]));
                    if (buf[i] == 0) zeros++;
                    int u = buf[i] & 0xff;
                    if (!seen[u]) { seen[u] = true; distinct++; }
                }
                println(sb.toString());
                println("  zeros=" + zeros + "/64 distinct-bytes=" + distinct);
                Instruction ins = listing.getInstructionAt(a);
                println("  instructionAt=" + (ins != null ? ins.toString() : "(none)"));
                ghidra.program.model.listing.Data d = listing.getDefinedDataAt(a);
                println("  definedDataAt=" + (d != null ? d.toString() : "(none)"));
            } catch (Exception e) { println("  read FAILED: " + e); }
        }
        decomp.dispose();
        println("=== AUDIT 17 DONE ===");
    }
}
