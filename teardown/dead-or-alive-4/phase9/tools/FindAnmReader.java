import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

public class FindAnmReader extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Phase9: hunt anm.afs reader via string xrefs ===");
        Listing lst = currentProgram.getListing();
        DataIterator di = lst.getDefinedData(true);
        List<Address> hits = new ArrayList<>();
        while (di.hasNext()) {
            Data d = di.next();
            Object v = d.getValue();
            if (v != null) {
                String s = v.toString().toLowerCase();
                if (s.contains("anm") || s.contains(".afs") || s.contains("cri_adx") || s.contains("adx")) {
                    println("STR " + d.getAddress() + " : " + v.toString().replaceAll("\\s+", " ").substring(0, Math.min(80, v.toString().length())));
                    hits.add(d.getAddress());
                }
            }
        }
        println("string hits: " + hits.size());
        Set<Function> fns = new TreeSet<>(Comparator.comparing(Function::getEntryPoint));
        for (Address a : hits) {
            ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(a);
            while (ri.hasNext()) {
                Reference r = ri.next();
                Function f = getFunctionContaining(r.getFromAddress());
                if (f != null) { fns.add(f); println("XREF " + a + " <- " + f.getName() + " @ " + f.getEntryPoint() + " from " + r.getFromAddress()); }
            }
        }
        println("=== candidate functions: " + fns.size() + " ===");
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        int n = 0;
        for (Function f : fns) {
            if (n++ >= 6) break;
            println("----- DECOMP " + f.getName() + " @ " + f.getEntryPoint() + " -----");
            DecompileResults res = dec.decompileFunction(f, 60, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                String c = res.getDecompiledFunction().getC();
                println(c.substring(0, Math.min(6000, c.length())));
            } else println("(decompile failed)");
        }
        println("=== Done ===");
    }
}
