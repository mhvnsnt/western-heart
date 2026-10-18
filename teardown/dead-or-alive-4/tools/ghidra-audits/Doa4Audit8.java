import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 8 (Lead 1): expand disassembly coverage of .text as far as
 * possible, then re-run the string-xref hunt (AFS filename strings).
 *
 * Steps:
 *  1. Report memory blocks + current .text disassembly coverage.
 *  2. Sweep .text on a 0x100 grid calling disassemble() on undefined addrs.
 *  3. Re-report coverage; count code xrefs to .rdata AFS filename strings
 *     (ghidra range 0x0061e800-0x0061ec00); re-scan lis-0x8261 pairs whose
 *     low imm lands in the AFS string runtime range; re-scan lis-0x4146 and
 *     the 6 file keys as BE32.
 */
public class Doa4Audit8 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 8: full .text disassembly + string-xref re-hunt ===");
        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();

        for (MemoryBlock b : mem.getBlocks()) {
            println("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd()
                + " size=" + b.getSize() + " r=" + b.isRead() + " w=" + b.isWrite()
                + " x=" + b.isExecute() + " init=" + b.isInitialized());
        }

        MemoryBlock text = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(".text")) text = b;
        if (text == null) { println("NO .text BLOCK"); return; }
        Address t0 = text.getStart(), t1 = text.getEnd();
        long tsize = t1.getOffset() - t0.getOffset() + 1;
        println(".text " + t0 + "-" + t1 + " (" + tsize + " bytes)");

        // 1. coverage BEFORE
        long definedBefore = countDefined(t0, t1);
        println("disassembled-instruction-bytes BEFORE: " + definedBefore
            + " / " + tsize + " (" + pct(definedBefore, tsize) + "%)");

        // 2. disassembly sweep, 0x100 grid, disassemble only undefined addresses
        long attempts = 0, okCalls = 0;
        long tstart = System.currentTimeMillis();
        for (long o = 0; o < tsize; o += 0x100) {
            Address a = t0.add(o);
            if (listing.getInstructionAt(a) == null && listing.getDefinedDataAt(a) == null) {
                attempts++;
                try { disassemble(a); okCalls++; } catch (Exception e) {}
            }
            if ((o & 0xfffff) == 0) {
                println("  sweep @ +" + Long.toHexString(o) + " (" + pct(o, tsize) + "%) attempts=" + attempts
                    + " elapsed=" + (System.currentTimeMillis() - tstart) / 1000 + "s");
            }
        }
        println("sweep done: attempts=" + attempts + " disassemble-calls=" + okCalls
            + " elapsed=" + (System.currentTimeMillis() - tstart) / 1000 + "s");

        long definedAfter = countDefined(t0, t1);
        println("disassembled-instruction-bytes AFTER: " + definedAfter
            + " / " + tsize + " (" + pct(definedAfter, tsize) + "%)");

        // 3. string-xref re-hunt: AFS filename strings ghidra 0x0061e800-0x0061ec00
        long xrefHits = 0;
        AddressRangeImpl rdataRange = null;
        for (long o = 0x61e800; o <= 0x61ec00; o += 4) {
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(o);
            for (Reference r : currentProgram.getReferenceManager().getReferencesTo(a)) {
                if (r.getReferenceType().isFlow() || r.getReferenceType().isRead() || r.getReferenceType().isWrite()) {
                    xrefHits++;
                    println("*** XREF to " + a + " from " + r.getFromAddress()
                        + " type=" + r.getReferenceType() + " in func=" + fname(r.getFromAddress()));
                }
            }
        }
        println("code xrefs to AFS-string range: " + xrefHits);

        // 3b. lis 0x8261 + ori/addi pair scan over newly disassembled code
        long pairs = 0;
        InstructionIterator it = listing.getInstructions(t0, true);
        int scanned = 0;
        while (it.hasNext()) {
            Instruction ins = it.next();
            scanned++;
            String s = ins.toString();
            if (s.startsWith("lis ") || s.startsWith("addis ")) {
                String reg = null; long hi = 0; boolean hiOk = false;
                java.util.regex.Matcher m = java.util.regex.Pattern.compile("(lis|addis)\\s+(r\\d+),(-?0x[0-9a-f]+)").matcher(s);
                if (m.find()) {
                    reg = m.group(2);
                    try { hi = Long.decode(m.group(3)); if (hi < 0) hi += 0x10000; hiOk = true; } catch (Exception e) {}
                }
                if (hiOk && hi == 0x8261) {
                    Instruction c = ins.getNext();
                    for (int j = 0; j < 12 && c != null; j++) {
                        String t = c.toString();
                        java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("(ori|addi|addis)\\s+(r\\d+)," + reg + ",(-?0x[0-9a-f]+)").matcher(t);
                        if (m2.find()) {
                            long lo; try { lo = Long.decode(m2.group(3)); } catch (Exception e) { lo = 0; }
                            if (lo < 0) lo += 0x10000;
                            long full = (0x8261L << 16) | (lo & 0xffff);
                            if (full >= 0x8261e700L && full <= 0x8261ed00L) {
                                pairs++;
                                println("*** PAIR @ " + ins.getAddress() + ": " + s + " / " + t
                                    + " => runtime 0x" + Long.toHexString(full) + " func=" + fname(ins.getAddress()));
                            }
                            break;
                        }
                        c = c.getNext();
                    }
                }
            }
        }
        println("instructions scanned: " + scanned);
        println("lis-0x8261 pairs into AFS string range: " + pairs);

        // 3c. lis *,0x4146 (AFS magic construction) — count in disassembled code
        long a4146 = 0;
        it = listing.getInstructions(t0, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String s = ins.toString();
            if ((s.startsWith("lis ") || s.startsWith("addis ")) && s.contains("0x4146")) {
                a4146++;
                if (a4146 <= 20) println("*** lis-0x4146 @ " + ins.getAddress() + ": " + s + " func=" + fname(ins.getAddress()));
            }
        }
        println("lis-0x4146 total: " + a4146);

        println("=== AUDIT 8 DONE ===");
    }

    long countDefined(Address a0, Address a1) {
        Listing listing = currentProgram.getListing();
        long n = 0;
        InstructionIterator it = listing.getInstructions(a0, true);
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
