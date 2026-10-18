import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.util.*;

/** DOA4 AUDIT 6b: dump context of all 22 lis-0x8261 sites. */
public class Doa4Audit6b extends GhidraScript {
    public void run() throws Exception {
        Memory mem = currentProgram.getMemory();
        println("=== DOA4 AUDIT 6b ===");
        MemoryBlock text = null;
        for (MemoryBlock b : mem.getBlocks()) if (b.getName().equals(".text")) text = b;
        byte[] tb = new byte[(int)(text.getEnd().getOffset()-text.getStart().getOffset()+1)];
        mem.getBytes(text.getStart(), tb);
        for (int k = 0; k + 4 <= tb.length; k += 4) {
            if ((tb[k] & 0xfc) == 0x3c && tb[k+2] == (byte)0x82 && tb[k+3] == 0x61) {
                Address s = text.getStart().add(k);
                for (long o = -16; o <= 48; o += 4) {
                    try { disassemble(s.add(o)); } catch (Exception e) {}
                }
                StringBuilder sb = new StringBuilder();
                Instruction c = currentProgram.getListing().getInstructionAt(s);
                for (int j = 0; j < 6 && c != null; j++) {
                    sb.append("[").append(c.getAddress().toString().substring(2)).append("] ")
                      .append(c.toString()).append("  ");
                    c = c.getNext();
                }
                // what rdata does the full address point to? try ori/addi low16 in next 4 insns
                println(s + ": " + sb);
            }
        }
        println("=== 6b DONE ===");
    }
}
