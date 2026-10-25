import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.scalar.Scalar;

public class FindAfsMagic extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Searching for AFS magic constant ===");
        InstructionIterator instrs = currentProgram.getListing().getInstructions(true);
        int checked = 0;
        int found = 0;
        while (instrs.hasNext() && found < 20) {
            Instruction instr = instrs.next();
            checked++;
            for (int i = 0; i < instr.getNumOperands(); i++) {
                for (Object o : instr.getOpObjects(i)) {
                    if (o instanceof Scalar) {
                        long val = ((Scalar)o).getValue();
                        if (val == 0x41465300L || val == 0x534641L) {
                            Function f = getFunctionContaining(instr.getAddress());
                            String fname = (f != null) ? f.getName() : "?";
                            println("  @" + instr.getAddress() + " in " + fname + ": " + instr);
                            found++;
                            break;
                        }
                    }
                }
                if (found >= 20) break;
            }
            if (checked > 3000000) break;
        }
        println("Checked " + checked + ", found " + found);
    }
}
