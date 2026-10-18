import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.util.*;
import java.util.regex.*;

/**
 * DOA4 AUDIT 7: find lis/ori|addi pairs building runtime addresses in
 * [0x8261e800, 0x8261ec00] (the AFS filename strings). Report the code sites.
 */
public class Doa4Audit7 extends GhidraScript {
    public void run() throws Exception {
        Memory mem = currentProgram.getMemory();
        println("=== DOA4 AUDIT 7 ===");
        MemoryBlock text = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(".text")) text = b;
        // 1. disassemble everything is too much; instead scan raw for lis 0x8261/0x8260/0x8262
        byte[] tb = new byte[(int)(text.getEnd().getOffset()-text.getStart().getOffset()+1)];
        mem.getBytes(text.getStart(), tb);
        Pattern p = Pattern.compile("(lis|addis)\\s+(r\\d+),(-?0x[0-9a-f]+)");
        int pairs = 0;
        for (int k = 0; k + 4 <= tb.length; k += 4) {
            int b2 = tb[k+2] & 0xff, b3 = tb[k+3] & 0xff;
            if ((tb[k] & 0xfc) != 0x3c) continue;
            if (b2 < 0x82 || b2 > 0x82) continue; // only 0x82xx high
            // disassemble window
            Address s = text.getStart().add(k);
            for (long o = -32; o <= 64; o += 4) {
                try { disassemble(s.add(o)); } catch (Exception e) {}
            }
            Instruction lis = currentProgram.getListing().getInstructionAt(s);
            if (lis == null) continue;
            Matcher m = p.matcher(lis.toString());
            if (!m.find()) continue;
            String reg = m.group(2);
            long hi;
            try { hi = Long.decode(m.group(3)); } catch (Exception e) { continue; }
            if (hi < 0) hi += 0x10000;
            // scan next 12 insns for ori/addi/addis on same reg with low imm
            Instruction c = lis.getNext();
            for (int j = 0; j < 12 && c != null; j++) {
                String t = c.toString();
                // ori rD,rA,imm  / addi rD,rA,imm
                Matcher m2 = Pattern.compile("(ori|addi|addis)\\s+(r\\d+)," + reg + ",(-?0x[0-9a-f]+)").matcher(t);
                if (m2.find()) {
                    long lo;
                    try { lo = Long.decode(m2.group(3)); } catch (Exception e) { lo = 0; }
                    if (lo < 0) lo += 0x10000;
                    long full = ((hi & 0xffff) << 16) | (lo & 0xffff);
                    if (full >= 0x8261e700L && full <= 0x8261ed00L) {
                        pairs++;
                        println("*** PAIR @ " + s + ": " + lis + " / " + t
                            + " => runtime 0x" + Long.toHexString(full)
                            + " (ghidra 0x" + Long.toHexString(full - 0x82000000L) + ")");
                        // show enclosing context
                        Instruction pc = lis;
                        StringBuilder sb = new StringBuilder();
                        for (int q = 0; q < 4; q++) {
                            try { pc = pc.getPrevious(); } catch (Exception e) { break; }
                            if (pc == null) break;
                            sb.insert(0, pc.toString() + " | ");
                        }
                        println("    pre: " + sb);
                        Function f = getFunctionContaining(s);
                        println("    func: " + (f != null ? f.getName() : "(none)"));
                    }
                    break;
                }
                c = c.getNext();
            }
        }
        println("pairs in AFS string range: " + pairs);
        println("=== AUDIT 7 DONE ===");
    }
}
