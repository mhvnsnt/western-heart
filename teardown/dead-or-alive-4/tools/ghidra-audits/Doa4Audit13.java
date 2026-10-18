import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 13: continue .text disassembly sweep (Audit8 reached 68.8% with
 * a 0x100 grid) using a finer 0x10 grid on still-undefined addresses, then
 * re-run the string-xref hunt restricted to NEWLY disassembled regions:
 *  - code xrefs into the .rdata AFS-filename string range (ghidra 0x0061e800-0x0061ec00)
 *  - lis 0x8261 + ori/addi pairs building runtime addrs in [0x8261e700,0x8261ed00]
 *  - lis *,0x4146 (AFS magic construction)
 *  - the 6 file keys as BE32 (carried forward from Audit3)
 * Reports coverage before/after and the count of NEW function entry points created.
 */
public class Doa4Audit13 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 13: finer disassembly sweep + string-xref re-hunt ===");
        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        ReferenceManager refs = currentProgram.getReferenceManager();
        AddressFactory af = currentProgram.getAddressFactory();

        MemoryBlock text = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(".text")) text = b;
        if (text == null) { println("NO .text BLOCK"); return; }
        Address t0 = text.getStart(), t1 = text.getEnd();
        long tsize = t1.getOffset() - t0.getOffset() + 1;

        // snapshot instructions before
        Set<Long> before = new HashSet<Long>();
        {
            InstructionIterator it = listing.getInstructions(t0, true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                if (ins.getAddress().compareTo(t1) > 0) break;
                before.add(ins.getAddress().getOffset());
            }
        }
        long definedBefore = insnBytes(t0, t1);
        println(".text " + t0 + "-" + t1 + " (" + tsize + " bytes)");
        println("instructions BEFORE: " + before.size()
            + ", insn-bytes BEFORE: " + definedBefore + " (" + pct(definedBefore, tsize) + "%)");

        // finer sweep: 0x10 grid on still-undefined addresses
        long attempts = 0, okCalls = 0, tstart = System.currentTimeMillis();
        for (long o = 0; o < tsize; o += 0x10) {
            Address a = t0.add(o);
            if (listing.getInstructionAt(a) == null && listing.getDefinedDataAt(a) == null) {
                attempts++;
                try { disassemble(a); okCalls++; } catch (Exception e) {}
            }
            if ((o & 0x3fffff) == 0) println("  sweep @ +" + Long.toHexString(o)
                + " attempts=" + attempts + " elapsed=" + (System.currentTimeMillis() - tstart) / 1000 + "s");
        }
        println("sweep done: attempts=" + attempts + " okCalls=" + okCalls
            + " elapsed=" + (System.currentTimeMillis() - tstart) / 1000 + "s");

        // snapshot after; newly disassembled = after - before
        Set<Long> newAddrs = new HashSet<Long>();
        long definedAfter = 0;
        {
            InstructionIterator it = listing.getInstructions(t0, true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                if (ins.getAddress().compareTo(t1) > 0) break;
                long off = ins.getAddress().getOffset();
                definedAfter += ins.getLength();
                if (!before.contains(off)) newAddrs.add(off);
            }
        }
        println("instructions AFTER: " + (before.size() + newAddrs.size())
            + ", NEW instructions: " + newAddrs.size()
            + ", insn-bytes AFTER: " + definedAfter + " (" + pct(definedAfter, tsize) + "%)");

        // count new function entry points in newly disassembled regions
        long newFuncs = 0;
        FunctionManager fm = currentProgram.getFunctionManager();
        for (Function f : fm.getFunctions(true)) {
            Address e = f.getEntryPoint();
            if (e.compareTo(t0) >= 0 && e.compareTo(t1) <= 0 && newAddrs.contains(e.getOffset())) newFuncs++;
        }
        println("new function entry points in new regions: " + newFuncs);

        // --- HUNT 1: code xrefs to AFS-string ghidra range 0x0061e800-0x0061ec00,
        // only from NEWLY disassembled instructions
        long hits1 = 0;
        for (long o = 0x61e800; o <= 0x61ec00; o += 4) {
            Address a = af.getDefaultAddressSpace().getAddress(o);
            for (Reference r : refs.getReferencesTo(a)) {
                if (newAddrs.contains(r.getFromAddress().getOffset())
                        && (r.getReferenceType().isFlow() || r.getReferenceType().isRead() || r.getReferenceType().isWrite())) {
                    hits1++;
                    if (hits1 <= 40) println("*** NEW-XREF to " + a + " from " + r.getFromAddress()
                        + " type=" + r.getReferenceType() + " func=" + fname(r.getFromAddress()));
                }
            }
        }
        println("HUNT1: new-region xrefs to AFS-string range: " + hits1);

        // --- HUNT 2: lis 0x8261 pairs in new regions
        long hits2 = 0, scanned = 0;
        for (long off : newAddrs) {
            Address a = af.getDefaultAddressSpace().getAddress(off);
            Instruction ins = listing.getInstructionAt(a);
            if (ins == null) continue;
            scanned++;
            String s = ins.toString();
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("(lis|addis)\\s+(r\\d+),(-?0x[0-9a-f]+)").matcher(s);
            if (m.find()) {
                String reg = m.group(2); long hi = 0; boolean ok = false;
                try { hi = Long.decode(m.group(3)); if (hi < 0) hi += 0x10000; ok = true; } catch (Exception e) {}
                if (ok && hi == 0x8261) {
                    Instruction c = ins.getNext();
                    for (int j = 0; j < 12 && c != null; j++) {
                        String t = c.toString();
                        java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("(ori|addi|addis)\\s+(r\\d+)," + reg + ",(-?0x[0-9a-f]+)").matcher(t);
                        if (m2.find()) {
                            long lo; try { lo = Long.decode(m2.group(3)); } catch (Exception e) { lo = 0; }
                            if (lo < 0) lo += 0x10000;
                            long full = (0x8261L << 16) | (lo & 0xffff);
                            if (full >= 0x8261e700L && full <= 0x8261ed00L) {
                                hits2++;
                                println("*** NEW-PAIR @ " + ins.getAddress() + ": " + s + " / " + t
                                    + " => runtime 0x" + Long.toHexString(full) + " func=" + fname(ins.getAddress()));
                            }
                            break;
                        }
                        c = c.getNext();
                    }
                }
            }
        }
        println("HUNT2: new instructions scanned=" + scanned + ", lis-0x8261 pairs in AFS range: " + hits2);

        // --- HUNT 3: lis *,0x4146 in new regions
        long hits3 = 0;
        for (long off : newAddrs) {
            Address a = af.getDefaultAddressSpace().getAddress(off);
            Instruction ins = listing.getInstructionAt(a);
            if (ins == null) continue;
            String s = ins.toString();
            if ((s.startsWith("lis ") || s.startsWith("addis ")) && s.contains("0x4146")) {
                hits3++;
                if (hits3 <= 20) println("*** NEW lis-0x4146 @ " + ins.getAddress() + ": " + s + " func=" + fname(ins.getAddress()));
            }
        }
        println("HUNT3: new-region lis-0x4146: " + hits3);

        // --- HUNT 4: 6 file keys as lis/ori IMMEDIATE CONSTRUCTION in new regions.
        // Audit3's raw BE32 scan found zero, but keys could be built at runtime via
        // lis/ori pairs (which the bytescan can't see). Keys from Doa4Audit3.java:70.
        long[] keys = {0x80b97b52L, 0x7fc2f931L, 0x7ff843dcL, 0xfe793a0fL, 0x7d40a53eL, 0x7d4e3d2eL};
        String[] kn = {"anm", "chrone", "chrtwo", "chrthree", "mot", "stg"};
        long hits4 = 0;
        for (long off : newAddrs) {
            Address a = af.getDefaultAddressSpace().getAddress(off);
            Instruction ins = listing.getInstructionAt(a);
            if (ins == null) continue;
            String s = ins.toString();
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("(lis)\\s+(r\\d+),(-?0x[0-9a-f]+)").matcher(s);
            if (m.find()) {
                String reg = m.group(2); long hi = 0;
                try { hi = Long.decode(m.group(3)); if (hi < 0) hi += 0x10000; } catch (Exception e) { continue; }
                Instruction c = ins.getNext();
                for (int j = 0; j < 8 && c != null; j++) {
                    String t = c.toString();
                    java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("(ori)\\s+(r\\d+)," + reg + ",(-?0x[0-9a-f]+)").matcher(t);
                    if (m2.find()) {
                        long lo; try { lo = Long.decode(m2.group(3)); } catch (Exception e) { lo = 0; }
                        if (lo < 0) lo += 0x10000;
                        long full = ((hi & 0xffff) << 16) | (lo & 0xffff);
                        for (int ki = 0; ki < keys.length; ki++) {
                            if (full == keys[ki]) {
                                hits4++;
                                println("*** NEW key-construct[" + kn[ki] + "] @ " + ins.getAddress() + ": " + s + " / " + t
                                    + " func=" + fname(ins.getAddress()));
                            }
                        }
                        break;
                    }
                    c = c.getNext();
                }
            }
        }
        println("HUNT4: new-region lis/ori key constructions: " + hits4);

        println("=== AUDIT 13 DONE ===");
    }
    long insnBytes(Address a0, Address a1) {
        long n = 0;
        InstructionIterator it = currentProgram.getListing().getInstructions(a0, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (ins.getAddress().compareTo(a1) > 0) break;
            n += ins.getLength();
        }
        return n;
    }
    String pct(long a, long b) { return String.format("%.1f", b == 0 ? 0 : 100.0 * a / b); }
    String fname(Address a) {
        Function f = getFunctionContaining(a);
        return f != null ? f.getName() : "(none)";
    }
}
