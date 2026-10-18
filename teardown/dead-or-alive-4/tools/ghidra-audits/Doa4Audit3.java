import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import ghidra.app.decompiler.*;
import java.util.*;

/**
 * DOA4 AUDIT 3: surgical strikes.
 * 1. Disassemble + decompile around 007725cc (the lone lis-0x61 site).
 * 2. Raw-byte scan .text for lis *,0x4146 (AFS magic construction).
 * 3. Raw-byte scan .text/.rdata/.data for the 6 file keys as BE32.
 * 4. Raw-byte scan .text for `bl` to the 10 external thunks.
 * 5. Addresses + xrefs of the d:\*.afs strings.
 */
public class Doa4Audit3 extends GhidraScript {
    Memory mem;
    public void run() throws Exception {
        mem = currentProgram.getMemory();
        AddressFactory af = currentProgram.getAddressFactory();
        AddressSpace def = af.getDefaultAddressSpace();
        println("=== DOA4 AUDIT 3 ===");

        // 1. disassemble around 007725cc
        Address lis = def.getAddress(0x007725ccL);
        println("--- disassemble @ 007725cc ---");
        try {
            for (long o = -128; o <= 256; o += 4) {
                try { disassemble(lis.add(o)); } catch (Exception e) { /* skip */ }
            }
            println("disassembled window ok");
        } catch (Exception e) { println("disasm err: " + e); }
        Instruction at = currentProgram.getListing().getInstructionAt(lis);
        println("insn @ lis site: " + (at != null ? at.toString() : "(still none)"));
        // print surrounding instructions
        Instruction i = at;
        for (int k = 0; k < 12 && i != null; k++) { println("  + " + i); i = i.getNext(); }
        // try decompile as function
        try {
            Function f = createFunction(lis, null);
            println("created func: " + (f != null ? f.getName() : "(null)"));
            if (f != null) {
                DecompInterface di = new DecompInterface();
                di.openProgram(currentProgram);
                DecompileResults dr = di.decompileFunction(f, 60, monitor);
                if (dr != null && dr.getDecompiledFunction() != null)
                    println("--- decomp ---\n" + dr.getDecompiledFunction().getC().substring(0, Math.min(3000, dr.getDecompiledFunction().getC().length())));
                di.dispose();
            }
        } catch (Exception e) { println("decomp err: " + e); }

        MemoryBlock text = getBlock(".text");
        byte[] tb = new byte[(int)(text.getEnd().getOffset()-text.getStart().getOffset()+1)];
        mem.getBytes(text.getStart(), tb);

        // 2. lis *,0x4146  (3C XX 41 46)
        println("--- lis *,0x4146 sites (AFS magic construction) ---");
        int h = 0;
        for (int k = 0; k + 4 <= tb.length && h < 20; k += 4) {
            if ((tb[k] & 0xfc) == 0x3c && tb[k+2] == 0x41 && tb[k+3] == 0x46) {
                println("  @ " + text.getStart().add(k));
                h++;
            }
        }
        println("  total: " + h);

        // 3. file keys as BE32 in .text/.rdata/.data
        println("--- file-key BE32 scan ---");
        int[] keys = {0x80b97b52, 0x7fc2f931, 0x7ff843dc, 0xfe793a0f, 0x7d40a53e, 0x7d4e3d2e};
        String[] kn = {"anm","chrone","chrtwo","chrthree","mot","stg"};
        for (String bn : new String[]{".text",".rdata",".data"}) {
            MemoryBlock b = getBlock(bn);
            if (b == null) continue;
            long len = b.getEnd().getOffset()-b.getStart().getOffset()+1;
            if (len > 60_000_000L) continue;
            byte[] buf = new byte[(int)len];
            mem.getBytes(b.getStart(), buf);
            for (int ki = 0; ki < keys.length; ki++) {
                byte[] pat = new byte[]{(byte)(keys[ki]>>>24),(byte)(keys[ki]>>>16),(byte)(keys[ki]>>>8),(byte)keys[ki]};
                int c = 0;
                for (int k = 0; k + 4 <= buf.length && c < 5; k++) {
                    if (buf[k]==pat[0]&&buf[k+1]==pat[1]&&buf[k+2]==pat[2]&&buf[k+3]==pat[3]) {
                        println("  key["+kn[ki]+"] in "+bn+" @ "+b.getStart().add(k));
                        c++;
                    }
                }
            }
        }
        println("  (key scan done)");

        // 4. bl -> external thunks
        println("--- bl to external thunks ---");
        long[] thunks = {0x00f58764L,0x00f58774L,0x00f58794L,0x00f587a4L,0x00f587c4L,
                         0x00f58984L,0x00f58a34L,0x00f58c84L,0x00f588c4L,0x00f59154L};
        int blhits = 0;
        for (int k = 0; k + 4 <= tb.length && blhits < 15; k += 4) {
            int w = ((tb[k]&0xff)<<24)|((tb[k+1]&0xff)<<16)|((tb[k+2]&0xff)<<8)|(tb[k+3]&0xff);
            if ((w & 0xfc000001) == 0x48000001) { // bl (AA=0,LK=1)
                int li = (w & 0x03fffffc);
                if ((li & 0x02000000) != 0) li |= 0xfc000000; // sign extend
                long target = text.getStart().add(k).getOffset() + li;
                for (long t : thunks) {
                    if (target == t) {
                        println("  bl -> thunk 0x"+Long.toHexString(t)+" @ "+text.getStart().add(k));
                        blhits++;
                    }
                }
            }
        }
        println("  total bl->thunk: " + blhits);

        // 5. d:\ strings
        println("--- d:\\ strings ---");
        String[] ds = {"d:\\spr.afs","d:\\snd.afs","d:\\mot.afs","d:\\cmn.afs","d:\\anm.afs",
                       "d:\\avt.afs","d:\\stg.afs","d:\\chrthree.afs","d:\\chrtwo.afs","d:\\chrone.afs"};
        for (String s : ds) {
            List<Address> addrs = findBytes(s.getBytes("UTF-8"));
            for (Address a : addrs) {
                int xc = 0;
                ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(a);
                while (ri.hasNext()) { ri.next(); xc++; }
                println("  \"" + s + "\" @ " + a + " xrefs=" + xc);
            }
            if (addrs.isEmpty()) println("  \"" + s + "\" NOT FOUND");
        }
        println("=== AUDIT 3 DONE ===");
    }

    MemoryBlock getBlock(String n) {
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(n)) return b;
        return null;
    }
    List<Address> findBytes(byte[] pat) throws Exception {
        List<Address> out = new ArrayList<Address>();
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized() || !b.isRead()) continue;
            long len = b.getEnd().getOffset()-b.getStart().getOffset()+1;
            if (len > 100_000_000L) continue;
            byte[] buf = new byte[(int)len];
            try { mem.getBytes(b.getStart(), buf); } catch (Exception e) { continue; }
            for (int k = 0; k + pat.length <= buf.length && out.size() < 4; k++) {
                boolean ok = true;
                for (int j = 0; j < pat.length; j++) if (buf[k+j]!=pat[j]) { ok=false; break; }
                if (ok) out.add(b.getStart().add(k));
            }
        }
        return out;
    }
}
