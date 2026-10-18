import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

/**
 * DOA4 AUDIT 6: the money scan. Find all `lis *,0x8261` in Ghidra .text
 * (unrelocated refs to .rdata strings at runtime 0x8261xxxx), disassemble
 * around each, flag those followed by ori/addi with 0xe8xx-0xe9xx
 * (the AFS filename string offsets).
 */
public class Doa4Audit6 extends GhidraScript {
    Memory mem;
    public void run() throws Exception {
        mem = currentProgram.getMemory();
        println("=== DOA4 AUDIT 6 ===");
        MemoryBlock text = getBlock(".text");
        byte[] tb = new byte[(int)(text.getEnd().getOffset()-text.getStart().getOffset()+1)];
        mem.getBytes(text.getStart(), tb);
        List<Address> sites = new ArrayList<Address>();
        for (int k = 0; k + 4 <= tb.length; k += 4) {
            if ((tb[k] & 0xfc) == 0x3c && tb[k+2] == (byte)0x82 && tb[k+3] == 0x61) {
                sites.add(text.getStart().add(k));
            }
        }
        println("lis *,0x8261 sites in Ghidra .text: " + sites.size());

        int flagged = 0;
        for (Address s : sites) {
            // disassemble window
            for (long o = -64; o <= 96; o += 4) {
                try { disassemble(s.add(o)); } catch (Exception e) {}
            }
            // look for ori/addi with 0xe8xx..0xe9xx within next 6 insns
            Instruction ins = currentProgram.getListing().getInstructionAt(s);
            boolean hit = false;
            StringBuilder ctx = new StringBuilder();
            Instruction c = ins;
            for (int k = 0; k < 8 && c != null; k++) {
                String t = c.toString();
                ctx.append(t).append(" ; ");
                if (t.matches(".*0xe[89][0-9a-f]{2}.*")) hit = true;
                c = c.getNext();
            }
            if (hit) {
                flagged++;
                println("\n*** AFS-STRING LOADER @ " + s + " ***");
                println("    " + ctx);
                // print a few insns before too
                Instruction p = ins;
                for (int k = 0; k < 6; k++) {
                    try { p = p.getPrevious(); } catch (Exception e) { break; }
                    if (p == null) break;
                }
                StringBuilder pre = new StringBuilder();
                for (int k = 0; k < 6 && p != null && !p.getAddress().equals(ins.getAddress()); k++) {
                    pre.append(p.toString()).append(" ; ");
                    p = p.getNext();
                }
                println("    pre: " + pre);
                Function f = getFunctionContaining(s);
                println("    func: " + (f != null ? f.getName()+"@"+f.getEntryPoint() : "(none yet)"));
            }
        }
        println("\nflagged AFS-string loaders: " + flagged + "/" + sites.size());

        // runtime-address pointer tables in .data/.rdata
        println("--- BE32 0x8261e8xx-0x8261ebxx pointer scan ---");
        for (String bn : new String[]{".data",".rdata"}) {
            MemoryBlock b = getBlock(bn);
            long len = b.getEnd().getOffset()-b.getStart().getOffset()+1;
            if (len > 80_000_000L) continue;
            byte[] buf = new byte[(int)len];
            mem.getBytes(b.getStart(), buf);
            int pc = 0;
            for (int k = 0; k + 4 <= buf.length && pc < 20; k += 4) {
                long v = ((buf[k]&0xffL)<<24)|((buf[k+1]&0xffL)<<16)|((buf[k+2]&0xffL)<<8)|(buf[k+3]&0xffL);
                if (v >= 0x8261e800L && v <= 0x8261eb00L) {
                    println("  " + bn + " slot " + b.getStart().add(k) + " -> 0x" + Long.toHexString(v));
                    pc++;
                }
            }
            if (pc == 0) println("  " + bn + ": none");
        }
        println("=== AUDIT 6 DONE ===");
    }
    MemoryBlock getBlock(String n) {
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(n)) return b;
        return null;
    }
}
