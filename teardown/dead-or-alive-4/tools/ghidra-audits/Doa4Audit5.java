import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

/** DOA4 AUDIT 5: full disassembly of the 7 import-calling functions. */
public class Doa4Audit5 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 5 ===");
        String[] fns = {"FUN_00b8973c","FUN_00b8c784","FUN_00b8dc54","FUN_00b8ea08",
                        "FUN_00d9df70","FUN_00d9e1cc","FUN_00d9e1f0"};
        for (String fn : fns) {
            Function f = null;
            FunctionIterator fi = currentProgram.getFunctionManager().getFunctions(true);
            while (fi.hasNext()) { Function g = fi.next(); if (g.getName().equals(fn)) { f = g; break; } }
            if (f == null) { println(fn + ": NOT FOUND"); continue; }
            println("\n########## " + fn + " @ " + f.getEntryPoint() + " ##########");
            InstructionIterator ii = currentProgram.getListing().getInstructions(f.getBody(), true);
            int n = 0;
            while (ii.hasNext() && n < 220) {
                Instruction ins = ii.next();
                // annotate: show ASCII for lis/ori pairs building addresses, and string refs
                println("  " + ins.getAddress() + "  " + ins.toString());
                n++;
            }
        }
        println("=== AUDIT 5 DONE ===");
    }
}
