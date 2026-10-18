import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.util.*;

/**
 * DOA4 AUDIT 12: decompile the crypto/content cluster functions found by Audit11:
 *  FUN_00b8973c (calls XeCryptShaUpdate+Final), FUN_00b8dfd8 (calls XamContentOpenFile),
 *  and identify the unnamed callers at 00b8c7b4, 00b92058, 00b91fdc, 00b8dc94.
 *  Goal: find the game-side AFS keystream/decrypt routine.
 */
public class Doa4Audit12 extends GhidraScript {
    DecompInterface decomp;

    public void run() throws Exception {
        println("=== DOA4 AUDIT 12: crypto/content cluster decompile ===");
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        AddressFactory af = currentProgram.getAddressFactory();

        long[] targets = {0x00b8973cL, 0x00b8dfd8L, 0x00b8c784L, 0x00b8ea08L};
        for (long v : targets) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionAt(a);
            if (f == null) {
                // try enclosing
                f = getFunctionContaining(a);
            }
            println("=== target 0x" + Long.toHexString(v) + " func=" + (f != null ? f.getName() + " " + f.getBody() : "(none)") + " ===");
            if (f == null) continue;
            // list all calls made by this function (resolved via IAT stride where possible)
            Listing listing = currentProgram.getListing();
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            Set<String> calls = new TreeSet<String>();
            int nins = 0;
            while (it.hasNext() && nins < 3000) {
                Instruction ins = it.next(); nins++;
                for (Reference r : ins.getReferencesFrom()) {
                    if (r.getReferenceType().isCall()) {
                        long tgt = r.getToAddress().getOffset();
                        String nm = "?";
                        if (tgt >= 0xf58764 && ((tgt - 0xf58764) % 0x10) == 0) {
                            int slot = (int)((tgt - 0xf58764) / 0x10);
                            nm = "thunk-slot" + slot;
                        }
                        Function tf = getFunctionAt(r.getToAddress());
                        calls.add(ins.getAddress() + " -> 0x" + Long.toHexString(tgt)
                            + " " + nm + (tf != null ? " " + tf.getName() : ""));
                    }
                }
            }
            println("  instructions: " + nins);
            for (String c : calls) println("  call: " + c);
            // decompile
            try {
                DecompileResults res = decomp.decompileFunction(f, 120, monitor);
                if (res != null && res.decompileCompleted()) {
                    String[] lines = res.getDecompiledFunction().getC().split("\n");
                    println("  decompiled lines: " + lines.length);
                    for (int q = 0; q < Math.min(120, lines.length); q++) println("  C: " + lines[q]);
                    if (lines.length > 120) println("  ... (" + (lines.length - 120) + " more lines)");
                } else {
                    println("  decompile failed");
                }
            } catch (Exception e) { println("  decompile exception: " + e); }
        }

        // identify unnamed callers
        long[] un = {0x00b8c7b4L, 0x00b92058L, 0x00b91fdcL, 0x00b8dc94L, 0x00b8df88L};
        for (long v : un) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            Function f = getFunctionContaining(a);
            println("unnamed caller site 0x" + Long.toHexString(v) + " in func=" + (f != null ? f.getName() + "@" + f.getEntryPoint() : "(none)"));
        }
        decomp.dispose();
        println("=== AUDIT 12 DONE ===");
    }
}
