import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompRaw extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        out.println("BEFORE rebase imageBase=" + currentProgram.getImageBase());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks())
            out.println("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " init=" + b.isInitialized());
        // rebase raw load (file offset 0 == vaddr 0x8804018)
        try {
            currentProgram.setImageBase(addr(0x08804018L), true);
            out.println("rebased ok, imageBase=" + currentProgram.getImageBase());
        } catch (Exception e) { out.println("rebase failed: " + e); }
        out.flush();
        Listing listing = currentProgram.getListing();
        Address lo = addr(0x088b55a00L), hi = addr(0x088b56800L);
        AddressSet set = new AddressSet(lo, hi);
        DisassembleCommand cmd = new DisassembleCommand(addr(0x088b55bf0L), set, true);
        boolean ok = cmd.applyTo(currentProgram, monitor);
        out.println("disasm ok=" + ok + " status=" + cmd.getStatusMsg());
        out.println("instructionAt bf0: " + listing.getInstructionAt(addr(0x088b55bf0L)));
        out.flush();
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (int i = 1; i < args.length; i++) {
            long va = Long.parseLong(args[i], 16);
            Address a = addr(va);
            out.println("==== SEED 0x" + args[i] + " ====");
            Function f = getFunctionContaining(a);
            if (f == null) { try { f = createFunction(a, "seed_" + args[i]); } catch (Exception e) { out.println("createFunction: " + e); } }
            if (f == null) {
                out.println("NO FUNCTION; listing:");
                Instruction ins = listing.getInstructionAt(a);
                if (ins == null) ins = listing.getInstructionAfter(a);
                for (int n = 0; n < 200 && ins != null; n++) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
                out.flush(); continue;
            }
            out.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint());
            DecompileResults res = decomp.decompileFunction(f, 180, monitor);
            if (res != null && res.getDecompiledFunction() != null) out.println(res.getDecompiledFunction().getC());
            else out.println("DECOMPILE FAILED");
            out.flush();
        }
        out.close();
        decomp.dispose();
    }
    Address addr(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
}
