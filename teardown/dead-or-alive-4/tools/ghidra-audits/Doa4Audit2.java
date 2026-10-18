import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

/**
 * DOA4 AUDIT 2: find code referencing AFS strings via raw byte patterns;
 * list idata externals; inspect rebased S-box lead; measure .text coverage.
 */
public class Doa4Audit2 extends GhidraScript {
    Memory mem;
    public void run() throws Exception {
        mem = currentProgram.getMemory();
        println("=== DOA4 AUDIT 2 ===");

        // 1. .idata externals + xref counts
        println("--- .idata externals ---");
        MemoryBlock idata = mem.getBlock("`.idata".substring(1)); // avoid quoting issues
        if (idata == null) idata = getBlockByName(".idata");
        SymbolTable st = currentProgram.getSymbolTable();
        SymbolIterator si = st.getSymbolIterator();
        int ext = 0;
        while (si.hasNext() && ext < 60) {
            Symbol s = si.next();
            if (s.isExternal()) {
                Address a = s.getAddress();
                int xrefs = 0;
                ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(a);
                while (ri.hasNext()) { ri.next(); xrefs++; }
                println("EXT " + s.getName() + " @ " + a + " xrefs=" + xrefs
                    + " lib=" + s.getParentNamespace());
                ext++;
            }
        }
        if (ext == 0) println("(no EXTERNAL symbols; trying label scan of .idata)");

        // 2. byte-scan .text for `lis rX,0x61`  (3C XX 00 61)
        println("--- lis *,0x61 sites in .text ---");
        MemoryBlock text = getBlockByName(".text");
        byte[] tb = new byte[(int)(text.getEnd().getOffset()-text.getStart().getOffset()+1)];
        mem.getBytes(text.getStart(), tb);
        int hits = 0;
        for (int i = 0; i + 4 <= tb.length && hits < 40; i += 4) {
            if ((tb[i] & 0xfc) == 0x3c && tb[i+2] == 0x00 && tb[i+3] == 0x61) {
                Address a = text.getStart().add(i);
                int reg = (tb[i+1] & 0xff);
                println("lis r" + reg + ",0x61 @ " + a);
                // disassemble a small window to show context
                try {
                    AddressSet set = new AddressSet(a.subtract(32), a.add(64));
                    // just print raw disassembly via listing if present
                    Instruction ins = currentProgram.getListing().getInstructionAt(a);
                    println("    disasm: " + (ins != null ? ins.toString() : "(not disassembled)"));
                    Function f = getFunctionContaining(a);
                    println("    func: " + (f != null ? f.getName()+"@"+f.getEntryPoint() : "(none)"));
                } catch (Exception e) { println("    err " + e); }
                hits++;
            }
        }
        println("total lis-0x61 hits: " + hits);

        // 3. UTF-16 scans for wide format string
        println("--- wide-string scan ---");
        scanWide("%ls.anm%d.afs");
        scanWide("anm.afs");
        scanWide("chrone.afs");

        // 4. rebased S-box lead: 0x822f06d0 - 0x82000000 + 0x400000 = 0x006f06d0
        println("--- S-box lead rebased @ 006f06d0 ---");
        AddressFactory af = currentProgram.getAddressFactory();
        Address sb = af.getDefaultAddressSpace().getAddress(0x006f06d0L);
        MemoryBlock mb = mem.getBlock(sb);
        println("block: " + (mb != null ? mb.getName() : "(none)"));
        byte[] buf = new byte[512];
        try {
            mem.getBytes(sb, buf);
            StringBuilder hx = new StringBuilder();
            for (int i = 0; i < 64; i++) hx.append(String.format("%02x", buf[i]));
            println("first 64B: " + hx);
            // distinct-byte count over 256B window (S-box ~ permutation => 256 distinct)
            Set<Byte> uniq = new HashSet<Byte>();
            for (int i = 0; i < 256; i++) uniq.add(buf[i]);
            println("distinct bytes in 256B window: " + uniq.size());
            ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(sb);
            int c = 0;
            while (ri.hasNext() && c < 10) {
                Reference r = ri.next();
                Function f = getFunctionContaining(r.getFromAddress());
                println("  xref from " + r.getFromAddress() + " [" + (f!=null?f.getName():"(data)") + "]");
                c++;
            }
            if (c == 0) println("  (no xrefs to 006f06d0)");
        } catch (Exception e) { println("read err: " + e); }

        // 5. .text disassembly coverage
        println("--- .text coverage ---");
        long insnBytes = 0, insnCount = 0;
        InstructionIterator it = currentProgram.getListing().getInstructions(
            new AddressSet(text.getStart(), text.getEnd()), true);
        while (it.hasNext()) { Instruction in = it.next(); insnBytes += in.getLength(); insnCount++; }
        long total = text.getEnd().getOffset() - text.getStart().getOffset() + 1;
        println("instructions in .text: " + insnCount + ", bytes: " + insnBytes + "/" + total
            + " = " + (100*insnBytes/total) + "%");
        println("=== AUDIT 2 DONE ===");
    }

    MemoryBlock getBlockByName(String n) {
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(n)) return b;
        return null;
    }

    void scanWide(String s) throws Exception {
        // UTF-16LE and UTF-16BE patterns
        byte[] le = new byte[s.length()*2], be = new byte[s.length()*2];
        for (int i = 0; i < s.length(); i++) {
            le[2*i] = (byte)s.charAt(i); le[2*i+1] = 0;
            be[2*i] = 0; be[2*i+1] = (byte)s.charAt(i);
        }
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized() || !b.isRead()) continue;
            long len = b.getEnd().getOffset()-b.getStart().getOffset()+1;
            if (len > 100_000_000L) continue;
            byte[] buf = new byte[(int)len];
            try { mem.getBytes(b.getStart(), buf); } catch (Exception e) { continue; }
            findPat(buf, b, le, s+" [LE]");
            findPat(buf, b, be, s+" [BE]");
        }
    }
    void findPat(byte[] buf, MemoryBlock b, byte[] pat, String tag) {
        int found = 0;
        for (int i = 0; i + pat.length <= buf.length && found < 5; i++) {
            boolean ok = true;
            for (int j = 0; j < pat.length; j++) if (buf[i+j]!=pat[j]) { ok=false; break; }
            if (ok) { println("WIDE \""+tag+"\" @ " + b.getStart().add(i)); found++; }
        }
    }
}
