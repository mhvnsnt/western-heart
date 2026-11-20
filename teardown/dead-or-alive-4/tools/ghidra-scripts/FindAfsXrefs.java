import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;

public class FindAfsXrefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Finding XREFs to AFS filename strings ===");
        
        // AFS strings are around 0x0061e8cd - 0x0061e9c0
        // Let's check the memory region for data references
        AddressFactory af = currentProgram.getAddressFactory();
        
        // Get the .data section bounds
        MemoryBlock[] blocks = currentProgram.getMemory().getBlocks();
        for (MemoryBlock block : blocks) {
            if (block.getName().contains("data") || block.getName().contains("DATA")) {
                println("Data block: " + block.getName() + " " + block.getStart() + " - " + block.getEnd());
            }
        }
        
        // For each AFS string address, find ALL references (including data)
        long[] afsAddrs = {0x0061e8cdL, 0x0061e8ecL, 0x0061e908L, 0x0061e924L, 
                           0x0061e964L, 0x0061e988L, 0x0061e9acL};
        for (long addrVal : afsAddrs) {
            Address addr = af.getDefaultAddressSpace().getAddress(addrVal);
            println("\n--- Refs to " + addr + " ---");
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(addr);
            int count = 0;
            while (refs.hasNext() && count < 20) {
                Reference r = refs.next();
                Address from = r.getFromAddress();
                Function f = getFunctionContaining(from);
                String ctx = (f != null) ? f.getName() : "(data)";
                println("  " + r.getReferenceType() + " from " + from + " [" + ctx + "]");
                count++;
            }
            if (count == 0) println("  (no xrefs found)");
        }
        
        // Also: search for functions with "decrypt", "crypt", "xor" in name
        println("\n=== Functions with crypto-like names ===");
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        int fcount = 0;
        while (funcs.hasNext() && fcount < 100) {
            Function f = funcs.next();
            String name = f.getName().toLowerCase();
            if (name.contains("decrypt") || name.contains("crypt") || 
                name.contains("xor") || name.contains("decode")) {
                println("  " + f.getName() + " @ " + f.getEntryPoint());
                fcount++;
            }
        }
        if (fcount == 0) println("  (none found)");
    }
}
