import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

public class FindAnmReader2 extends GhidraScript {
    String safe(String s){ String t=s.replaceAll("\\s+"," "); return t.length()>100?t.substring(0,100):t; }
    @Override
    public void run() throws Exception {
        println("=== Phase10: anm reader hunt v2 (raw scan + xrefs) ===");
        Memory mem = currentProgram.getMemory();
        String[] pats = {"anm", "ANM", ".afs", ".AFS", "chrone", "chrtwo", "mot", "cri", "CRI", ".bin", "afs"};
        Set<Address> hits = new TreeSet<>();
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            byte[] bytes = new byte[(int)b.getSize()];
            try { mem.getBytes(b.getStart(), bytes); } catch (Exception e) { continue; }
            for (String p : pats) {
                byte[] pb = p.getBytes("US-ASCII");
                for (int i = 0; i + pb.length <= bytes.length; i++) {
                    boolean ok = true;
                    for (int j = 0; j < pb.length; j++) if (bytes[i+j] != pb[j]) { ok = false; break; }
                    if (ok) {
                        Address a = b.getStart().add(i);
                        // print only plausibly-string contexts for short pats
                        if (p.length() >= 3) {
                            String ctx = "";
                            try { byte[] c = new byte[48]; mem.getBytes(a, c); ctx = new String(c, "US-ASCII").replaceAll("[^\\x20-\\x7E]", "."); } catch (Exception e) {}
                            println("RAW " + p + " @ " + a + " : " + ctx);
                        }
                        hits.add(a);
                    }
                }
            }
        }
        println("raw hit addrs: " + hits.size());
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
            if (n++ >= 8) break;
            println("----- DECOMP " + f.getName() + " @ " + f.getEntryPoint() + " -----");
            DecompileResults res = dec.decompileFunction(f, 60, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                String c = res.getDecompiledFunction().getC();
                println(c.length() > 6000 ? c.substring(0, 6000) : c);
            } else println("(decompile failed)");
        }
        println("=== Done v2 ===");
    }
}
