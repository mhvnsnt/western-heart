import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import java.util.*;

/**
 * DOA4 AUDIT 10 (Lead 3): full disassembly + decompile of FUN_00d9df70
 * (crypto-flavored caller: unnamed externals + constants 0xfffe07d1,
 * 0x82b7e67c, 0x26404, mode flags 0x10000/0x20000), plus one-level callee walk.
 */
public class Doa4Audit10 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 10: FUN_00d9df70 deep dive ===");
        Address faddr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x00d9df70L);
        Function f = getFunctionAt(faddr);
        if (f == null) {
            println("no function at 00d9df70; trying to disassemble + create");
            try { disassemble(faddr); } catch (Exception e) { println("disasm err " + e); }
            f = getFunctionAt(faddr);
        }
        println("function: " + (f != null ? f.getName() + " body=" + f.getBody() : "(none)"));
        if (f == null) { println("=== AUDIT 10 DONE (no func) ==="); return; }

        // full disassembly of the function body
        Listing listing = currentProgram.getListing();
        println("--- disassembly ---");
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        int n = 0;
        while (it.hasNext() && n < 4000) {
            Instruction ins = it.next();
            println(ins.getAddress() + "  " + ins.toString());
            n++;
        }
        println("instructions printed: " + n);

        // decompile
        println("--- decompile ---");
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        try {
            DecompileResults res = decomp.decompileFunction(f, 120, monitor);
            if (res != null && res.decompileCompleted()) {
                String c = res.getDecompiledFunction().getC();
                String[] lines = c.split("\n");
                println("decompiled lines: " + lines.length);
                for (String ln : lines) println("C: " + ln);
            } else {
                println("decompile failed: " + (res != null ? res.getErrorMessage() : "null"));
            }
        } catch (Exception e) { println("decompile exception: " + e); }

        // one-level callee walk: for each call in f, print target + its callees
        println("--- callee walk (1 level) ---");
        Set<Function> callees = new HashSet<Function>();
        for (Reference r : currentProgram.getReferenceManager().getReferencesFrom(f.getEntryPoint())) {
            // use instruction iteration instead: scan calls
        }
        InstructionIterator it2 = listing.getInstructions(f.getBody(), true);
        while (it2.hasNext()) {
            Instruction ins = it2.next();
            for (Reference r : ins.getReferencesFrom()) {
                if (r.getReferenceType().isCall()) {
                    Function tgt = getFunctionAt(r.getToAddress());
                    if (tgt != null && callees.add(tgt)) {
                        println("call @ " + ins.getAddress() + " -> " + tgt.getName() + " (" + tgt.getEntryPoint() + ")");
                        // target callees
                        Set<String> sub = new HashSet<String>();
                        InstructionIterator it3 = listing.getInstructions(tgt.getBody(), true);
                        int k = 0;
                        while (it3.hasNext() && k < 2000) {
                            Instruction i3 = it3.next(); k++;
                            for (Reference r3 : i3.getReferencesFrom()) {
                                if (r3.getReferenceType().isCall()) {
                                    Function t3 = getFunctionAt(r3.getToAddress());
                                    sub.add((t3 != null ? t3.getName() : r3.getToAddress().toString()));
                                }
                            }
                        }
                        println("    subcalls: " + sub);
                        // decompile small callees
                        if (tgt.getName().startsWith("FUN_")) {
                            try {
                                DecompileResults res2 = decomp.decompileFunction(tgt, 60, monitor);
                                if (res2 != null && res2.decompileCompleted()) {
                                    String[] cl = res2.getDecompiledFunction().getC().split("\n");
                                    println("    decompiled " + tgt.getName() + " (" + cl.length + " lines), first 40:");
                                    for (int q = 0; q < Math.min(40, cl.length); q++) println("    C: " + cl[q]);
                                }
                            } catch (Exception e) { println("    decompile err " + e); }
                        }
                    }
                }
            }
        }
        decomp.dispose();
        println("=== AUDIT 10 DONE ===");
    }
}
