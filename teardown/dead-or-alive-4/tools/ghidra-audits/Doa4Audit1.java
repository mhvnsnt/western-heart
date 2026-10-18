import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.block.*;
import java.util.*;

/**
 * DOA4 deep-RE audit: locate the AFS decrypt path by data, not by guesses.
 * 1. Finds AFS filename strings / format strings / CRI error strings BYTES in memory
 *    (does not trust documented addresses), reports real addresses + all xrefs.
 * 2. Scans .data/.rdata for 4-byte BE pointer values pointing at those strings
 *    (pointer-table detection), reports xrefs to the table slots.
 * 3. Reports instruction coverage + memory block map (sanity).
 * 4. Inspects the alleged S-box VA 0x822f06d0 (reports section or absence).
 */
public class Doa4Audit1 extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== DOA4 AUDIT 1: string-driven decrypt-path hunt ===");
        Memory mem = currentProgram.getMemory();
        AddressFactory af = currentProgram.getAddressFactory();
        AddressSpace def = af.getDefaultAddressSpace();

        // block map + instruction coverage sanity
        long insnCount = 0;
        for (MemoryBlock b : mem.getBlocks()) {
            println("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd()
                + " r=" + b.isRead() + " w=" + b.isWrite() + " x=" + b.isExecute()
                + " init=" + b.isInitialized());
        }
        InstructionIterator ii = currentProgram.getListing().getInstructions(true);
        while (ii.hasNext()) { ii.next(); insnCount++; }
        println("TOTAL INSTRUCTIONS: " + insnCount);

        String[] needles = {
            "cache:\\spr.afs", "cache:\\snd.afs", "cache:\\mot.afs",
            "cache:\\cmn.afs", "cache:\\chrthree.afs", "cache:\\chrtwo.afs",
            "cache:\\chrone.afs", "%ls.anm%d.afs", "%s:\\anm.afs",
            "adxf_GetPtStat", "Illigal format(not AFS)"
        };
        List<Address> strAddrs = new ArrayList<Address>();
        for (String n : needles) {
            byte[] pat = n.getBytes("UTF-8");
            boolean found = false;
            for (MemoryBlock b : mem.getBlocks()) {
                if (!b.isInitialized() || !b.isRead()) continue;
                AddressSetView set = mem.getLoadedAndInitializedAddressSet();
                Address start = b.getStart();
                Address end = b.getEnd();
                // naive scan
                long len = end.getOffset() - start.getOffset() + 1;
                if (len > 200_000_000L) continue;
                byte[] buf = new byte[(int)Math.min(len, 64*1024*1024)];
                long off = 0;
                while (off < len) {
                    int chunk = (int)Math.min(buf.length, len - off);
                    try {
                        mem.getBytes(start.add(off), buf, 0, chunk);
                    } catch (Exception e) { break; }
                    for (int i = 0; i + pat.length <= chunk; i++) {
                        boolean ok = true;
                        for (int j = 0; j < pat.length; j++)
                            if (buf[i+j] != pat[j]) { ok = false; break; }
                        if (ok) {
                            Address a = start.add(off + i);
                            println("STRING \"" + n + "\" @ " + a + " [" + b.getName() + "]");
                            strAddrs.add(a);
                            reportXrefs(a);
                            found = true;
                        }
                    }
                    off += chunk;
                }
            }
            if (!found) println("STRING \"" + n + "\" NOT FOUND anywhere");
        }

        // pointer-table scan: any BE32 in initialized data equal to a string addr
        println("\n=== POINTER TABLE SCAN ===");
        Set<Long> targets = new HashSet<Long>();
        for (Address a : strAddrs) targets.add(a.getOffset());
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized() || !b.isRead()) continue;
            String nm = b.getName().toLowerCase();
            if (!(nm.contains("data") || nm.contains("rdata") || nm.contains("rodata"))) continue;
            long len = b.getEnd().getOffset() - b.getStart().getOffset() + 1;
            if (len > 200_000_000L) continue;
            byte[] buf = new byte[(int)len];
            try { mem.getBytes(b.getStart(), buf); } catch (Exception e) { continue; }
            for (int i = 0; i + 4 <= buf.length; i += 4) {
                long v = ((buf[i]&0xffL)<<24)|((buf[i+1]&0xffL)<<16)|((buf[i+2]&0xffL)<<8)|(buf[i+3]&0xffL);
                if (targets.contains(v)) {
                    Address slot = b.getStart().add(i);
                    println("PTR-TABLE slot " + slot + " -> 0x" + Long.toHexString(v));
                    reportXrefs(slot);
                }
            }
        }

        // alleged S-box VA from prior notes
        println("\n=== S-BOX LEAD 0x822f06d0 ===");
        try {
            Address sbox = def.getAddress(0x822f06d0L);
            MemoryBlock mb = mem.getBlock(sbox);
            if (mb == null) {
                println("0x822f06d0 NOT IN ANY MEMORY BLOCK (address space max?)");
            } else {
                println("0x822f06d0 in block " + mb.getName());
                byte[] sb = new byte[64];
                mem.getBytes(sbox, sb);
                StringBuilder hex = new StringBuilder();
                for (byte x : sb) hex.append(String.format("%02x", x));
                println("first 64 bytes: " + hex);
                reportXrefs(sbox);
            }
        } catch (Exception e) { println("0x822f06d0 address error: " + e); }
        println("=== AUDIT 1 DONE ===");
    }

    private void reportXrefs(Address a) {
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(a);
        int c = 0;
        while (refs.hasNext() && c < 25) {
            Reference r = refs.next();
            Function f = getFunctionContaining(r.getFromAddress());
            println("    xref " + r.getReferenceType() + " from " + r.getFromAddress()
                + " [" + (f != null ? f.getName()+"@"+f.getEntryPoint() : "(data)") + "]");
            c++;
        }
        if (c == 0) println("    (no xrefs)");
    }
}
