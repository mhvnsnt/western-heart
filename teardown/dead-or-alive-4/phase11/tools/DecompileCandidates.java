import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

// Phase 11 Job 1 follow-up: targeted decompile of the PPC constant-scan
// candidate functions. Seeds are GHIDRA-space addresses (true VA minus
// 0x81C00000; the project image base is 0x400000 while code constants
// are true VAs at base 0x82000000). For each seed: containing function,
// its callers (code refs DO exist), its callees; decompile the function
// and (for the first two seeds) its callees one level deep.
// Args: [0]=outdir, [1..]=seed addresses (hex).
public class DecompileCandidates extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outDir = args[0];
        new File(outDir).mkdirs();
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        Set<Function> done = new HashSet<>();
        PrintWriter idx = new PrintWriter(new FileWriter(new File(outDir, "index.txt")));
        for (int ai = 1; ai < args.length; ai++) {
            Address seed = currentProgram.getAddressFactory().getAddress(args[ai]);
            Function f = getFunctionContaining(seed);
            if (f == null) {
                // .pdata-derived entry point (phase 11): create the function.
                disassemble(seed);
                try { f = createFunction(seed, null); } catch (Exception e) { f = null; }
            }
            if (f == null) { idx.println("seed " + args[ai] + " -> NO FUNCTION"); println("seed " + args[ai] + " NO FUNCTION"); continue; }
            idx.println("seed " + args[ai] + " (true VA " + seed.add(0x81C00000L) + ") -> " + f.getName() + " @ " + f.getEntryPoint()
                + " (true VA " + f.getEntryPoint().add(0x81C00000L) + ")");
            // callers
            ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());
            Set<String> callers = new TreeSet<>();
            while (ri.hasNext()) {
                Reference r = ri.next();
                Function cf = getFunctionContaining(r.getFromAddress());
                callers.add(r.getFromAddress() + " in " + (cf != null ? cf.getName() + " @ " + cf.getEntryPoint() : "?"));
            }
            idx.println("  callers (" + callers.size() + "):");
            for (String c : callers) idx.println("    " + c);
            Set<Function> callees = f.getCalledFunctions(monitor);
            idx.println("  callees (" + callees.size() + "):");
            for (Function c : callees) idx.println("    " + c.getName() + " @ " + c.getEntryPoint());
            // decompile f (+ callees for first two seeds)
            List<Function> todo = new ArrayList<>();
            todo.add(f);
            if (ai <= 2) todo.addAll(callees);
            for (Function tf : todo) {
                if (done.contains(tf)) continue;
                done.add(tf);
                DecompileResults res = dec.decompileFunction(tf, 120, monitor);
                String c = (res != null && res.getDecompiledFunction() != null) ? res.getDecompiledFunction().getC() : "(decompile failed)";
                File out = new File(outDir, "func_" + tf.getEntryPoint() + "_" + tf.getName().replaceAll("[^A-Za-z0-9_.-]", "_") + ".c");
                PrintWriter pw = new PrintWriter(new FileWriter(out));
                pw.println("// " + tf.getName() + " @ Ghidra " + tf.getEntryPoint() + " / true VA " + tf.getEntryPoint().add(0x81C00000L));
                pw.print(c); pw.close();
                idx.println("  decompiled " + tf.getName() + " -> " + out.getName() + " (" + c.length() + " chars)");
                println("DECOMP " + tf.getEntryPoint() + " " + tf.getName() + " " + c.length());
            }
        }
        idx.close();
        println("=== DecompileCandidates done ===");
    }
}
