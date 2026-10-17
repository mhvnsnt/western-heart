import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;

public class DecompileAround extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Decompiling around lis 0x62 sites ===");
        long[] addrs = {0x00865d94L, 0x008669a4L, 0x00866ab0L};
        
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        
        for (long a : addrs) {
            Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(a);
            Function f = getFunctionAt(addr);
            if (f == null) {
                // Try to find containing function by looking backwards
                Instruction instr = currentProgram.getListing().getInstructionAt(addr);
                if (instr != null) {
                    println("\n--- Instruction at " + addr + ": " + instr + " ---");
                    // Show surrounding instructions
                    Instruction prev = instr.getPrevious();
                    for (int i = 0; i < 5 && prev != null; i++) {
                        println("  prev: " + prev.getAddress() + ": " + prev);
                        prev = prev.getPrevious();
                    }
                    Instruction next = instr.getNext();
                    for (int i = 0; i < 10 && next != null; i++) {
                        println("  next: " + next.getAddress() + ": " + next);
                        next = next.getNext();
                    }
                } else {
                    println("\n--- No instruction at " + addr + " ---");
                }
            } else {
                println("\n=== Function: " + f.getName() + " @ " + f.getEntryPoint() + " ===");
                DecompileResults res = decomp.decompileFunction(f, 60, monitor);
                if (res != null && res.getDecompiledFunction() != null) {
                    String code = res.getDecompiledFunction().getC();
                    // Print first 100 lines
                    String[] lines = code.split("\n");
                    for (int i = 0; i < Math.min(100, lines.length); i++) {
                        println(lines[i]);
                    }
                }
            }
        }
        decomp.dispose();
    }
}
