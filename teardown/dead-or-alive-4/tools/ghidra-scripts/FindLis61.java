import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;

public class FindLis61 extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Finding lis rX, 0x61 (AFS string address construction) ===");
        InstructionIterator instrs = currentProgram.getListing().getInstructions(true);
        int checked = 0;
        int found = 0;
        while (instrs.hasNext() && found < 30) {
            Instruction instr = instrs.next();
            checked++;
            String mnem = instr.getMnemonicString().toLowerCase();
            if (mnem.equals("lis")) {
                for (int i = 0; i < instr.getNumOperands(); i++) {
                    for (Object o : instr.getOpObjects(i)) {
                        if (o instanceof Scalar) {
                            long val = ((Scalar)o).getValue();
                            // lis with 0x61 (or 0x60-0x62 for nearby)
                            if (val == 0x61 || val == 0x60 || val == 0x62) {
                                Function f = getFunctionContaining(instr.getAddress());
                                String fname = (f != null) ? f.getName() : "?";
                                println("  lis 0x" + Long.toHexString(val) + " at " + instr.getAddress() + " in " + fname);
                                found++;
                                break;
                            }
                        }
                    }
                }
            }
            if (checked > 3000000) break;
        }
        println("Checked " + checked + ", found " + found);
    }
}
