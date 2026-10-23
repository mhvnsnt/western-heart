// Phase 17 pre-script: print the loader's block map, then shift the
// image base from the PE header placeholder (0x400000) to the true
// XEX VA base 0x82000000 so every section lands at its true VA.
// @category Phase17
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;

public class SetBaseP17 extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("P17-BLOCKS-BEFORE base=" + currentProgram.getImageBase());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            println("P17-BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd()
                + " init=" + b.isInitialized() + " r=" + b.isRead() + " w=" + b.isWrite() + " x=" + b.isExecute());
        }
        Address target = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x82000000L);
        currentProgram.setImageBase(target, true);
        println("P17-BLOCKS-AFTER base=" + currentProgram.getImageBase());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            println("P17-BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd()
                + " init=" + b.isInitialized() + " r=" + b.isRead() + " w=" + b.isWrite() + " x=" + b.isExecute());
        }
    }
}
