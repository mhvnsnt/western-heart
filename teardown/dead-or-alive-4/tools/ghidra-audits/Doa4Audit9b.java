import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 9b: the 10 externals live in PSFD00 (00f4ae00-00f50943), not the
 * PE import table. Disassemble every thunk there, dump .idata words, and
 * hunt the XEX import-library records (library names + ordinal lists).
 */
public class Doa4Audit9b extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 9b: PSFD00 thunk disasm + idata + import-lib records ===");
        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();

        MemoryBlock psfd = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals("PSFD00")) psfd = b;
        if (psfd == null) { println("NO PSFD00"); return; }
        Address p0 = psfd.getStart(), p1 = psfd.getEnd();
        println("PSFD00 " + p0 + "-" + p1 + " size=" + psfd.getSize());

        // disassemble all of PSFD00, then print each function
        for (long o = 0; o < psfd.getSize(); o += 0x20) {
            Address a = p0.add(o);
            if (listing.getInstructionAt(a) == null) {
                try { disassemble(a); } catch (Exception e) {}
            }
        }
        // label any external-ish functions: print every function's entry disasm
        Set<String> seen = new HashSet<String>();
        InstructionIterator it = listing.getInstructions(p0, true);
        int printed = 0;
        while (it.hasNext() && printed < 60) {
            Instruction ins = it.next();
            if (ins.getAddress().compareTo(p1) > 0) break;
            Function f = getFunctionContaining(ins.getAddress());
            String key = f != null ? f.getName() : ins.getAddress().toString();
            if (seen.add(key)) {
                println("--- " + key + " @ " + ins.getAddress() + " ---");
                Instruction c = ins;
                for (int j = 0; j < 12 && c != null; j++) {
                    println("    " + c.getAddress() + "  " + c.toString());
                    c = c.getNext();
                    if (c != null && getFunctionContaining(c.getAddress()) != f) break;
                }
                printed++;
            }
        }

        // dump .idata words
        MemoryBlock idata = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(".idata")) idata = b;
        if (idata != null) {
            println("--- .idata words (non-zero) ---");
            Address d0 = idata.getStart();
            for (long o = 0; o < idata.getSize(); o += 4) {
                int w;
                try { w = mem.getInt(d0.add(o)); } catch (Exception e) { continue; }
                if (w != 0) println("  idata+" + Long.toHexString(o) + " = 0x" + Integer.toHexString(w));
            }
        }

        // hunt import-library name strings anywhere in the image
        println("--- import library name string hunt ---");
        String[] libs = {"xboxkrnl", "xam.xex", "xbdm.xex", "xact", "xaudio", "xnet"};
        for (MemoryBlock b : mem.getBlocks()) {
            String bn = b.getName();
            if (!(bn.equals(".rdata") || bn.equals(".data") || bn.equals("Headers"))) continue;
            long sz = b.getSize();
            byte[] buf = new byte[(int)Math.min(sz, 4*1024*1024)];
            try { mem.getBytes(b.getStart(), buf); } catch (Exception e) { continue; }
            for (String lib : libs) {
                byte[] needle = lib.getBytes("ASCII");
                for (int k = 0; k + needle.length <= buf.length; k++) {
                    boolean hit = true;
                    for (int q = 0; q < needle.length; q++) if (buf[k+q] != needle[q]) { hit = false; break; }
                    if (hit) {
                        Address a = b.getStart().add(k);
                        println("  '" + lib + "' @ " + a + " block=" + bn);
                        // dump 64 bytes before/after
                        byte[] ctx = new byte[96];
                        try { mem.getBytes(a.add(-32), ctx); } catch (Exception e) {}
                        StringBuilder sb = new StringBuilder();
                        for (byte bb : ctx) sb.append(String.format("%02x ", bb));
                        println("    ctx: " + sb);
                    }
                }
            }
        }
        println("=== AUDIT 9b DONE ===");
    }
}
