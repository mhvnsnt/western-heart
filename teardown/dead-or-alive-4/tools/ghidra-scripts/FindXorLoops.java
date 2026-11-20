import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;

public class FindXorLoops extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Finding functions with XOR instructions ===");
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        int checked = 0;
        while (funcs.hasNext() && checked < 5000) {
            Function f = funcs.next();
            checked++;
            int xorCount = 0;
            InstructionIterator instrs = currentProgram.getListing().getInstructions(f.getBody(), true);
            while (instrs.hasNext()) {
                Instruction instr = instrs.next();
                String mnem = instr.getMnemonicString().toLowerCase();
                if (mnem.equals("xor") || mnem.equals("xor.") || mnem.startsWith("xor")) {
                    xorCount++;
                }
            }
            // Functions with 5+ XORs might be crypto
            if (xorCount >= 5) {
                println("  " + f.getName() + " @ " + f.getEntryPoint() + " has " + xorCount + " XORs, size=" + f.getBody().getNumAddresses());
            }
        }
        println("Checked " + checked + " functions");
    }
}
