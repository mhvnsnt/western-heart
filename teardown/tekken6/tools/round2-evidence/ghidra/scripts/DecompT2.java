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

public class DecompT2 extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        out.println("imageBase=" + currentProgram.getImageBase() + " lang=" + currentProgram.getLanguageID());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks())
            out.println("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " init=" + b.isInitialized());
        out.flush();
        // Explicitly disassemble the whole inflate region 0x088b55a00-0x088b56500
        Address lo = addr(0x088b55a00L), hi = addr(0x088b56500L);
        AddressSet set = new AddressSet(lo, hi);
        clearListing(lo, hi);
        out.println("cleared listing in region");
        DisassembleCommand cmd = new DisassembleCommand(set, set, true);
        boolean ok = cmd.applyTo(currentProgram, monitor);
        out.println("DisassembleCommand ok=" + ok + " status=" + cmd.getStatusMsg());
        Listing listing = currentProgram.getListing();
        Instruction probe = listing.getInstructionAt(addr(0x088b55bf0L));
        out.println("instructionAt bf0: " + probe);
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (int i = 1; i < args.length; i++) {
            long va = Long.parseLong(args[i], 16);
            Address a = addr(va);
            out.println("==== SEED 0x" + args[i] + " ====");
            Function f = getFunctionContaining(a);
            if (f == null) {
                try { f = createFunction(a, "seed_" + args[i]); } catch (Exception e) { out.println("createFunction: " + e); }
            }
            if (f == null) {
                out.println("NO FUNCTION; listing from seed:");
                Instruction ins = listing.getInstructionAt(a);
                if (ins == null) ins = listing.getInstructionAfter(a);
                for (int n = 0; n < 128 && ins != null; n++) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
                out.flush();
                continue;
            }
            out.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint());
            DecompileResults res = decomp.decompileFunction(f, 180, monitor);
            if (res != null && res.getDecompiledFunction() != null) out.println(res.getDecompiledFunction().getC());
            else {
                out.println("DECOMPILE FAILED; listing:");
                Instruction ins = listing.getInstructionAt(f.getEntryPoint());
                while (ins != null && f.getBody().contains(ins.getAddress())) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
            }
            out.flush();
        }
        out.close();
        decomp.dispose();
    }
    Address addr(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
}
