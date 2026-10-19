import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.PrintWriter;
import java.util.HashSet;

public class FindBoneRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        PrintWriter out = new PrintWriter("/tmp/ghidra-out/bone_refs.txt");
        byte[] pat = "BONE NUM".getBytes("ASCII");
        Memory mem = currentProgram.getMemory();
        Address min = currentProgram.getMinAddress();
        Address max = currentProgram.getMaxAddress();
        out.println("=== BONE NUM occurrences ===");
        HashSet<Function> funcs = new HashSet<Function>();
        HashSet<Address> seen = new HashSet<Address>();
        Address cur = min;
        while (cur != null && cur.compareTo(max) <= 0) {
            Address a = mem.findBytes(cur, max, pat, null, true, monitor);
            if (a == null || seen.contains(a)) break;
            seen.add(a);
            out.println("str @ " + a);
            Reference[] refs = getReferencesTo(a);
            for (Reference r : refs) {
                Address from = r.getFromAddress();
                out.println("  ref from " + from + " (" + r.getReferenceType() + ")");
                Function f = getFunctionContaining(from);
                if (f != null) funcs.add(f);
            }
            cur = a.add(1);
        }
        out.println("\n=== referencing functions: " + funcs.size() + " ===");
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        for (Function f : funcs) {
            out.println("\n########## " + f.getName() + " @ " + f.getEntryPoint() + " ##########");
            DecompileResults res = di.decompileFunction(f, 120, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                out.println(res.getDecompiledFunction().getC());
            } else {
                out.println("(decompile failed)");
            }
            out.flush();
        }
        di.dispose();
        out.close();
        println("wrote /tmp/ghidra-out/bone_refs.txt, funcs=" + funcs.size());
    }
}
