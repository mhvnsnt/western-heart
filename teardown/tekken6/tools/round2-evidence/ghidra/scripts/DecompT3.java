import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompT3 extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        Listing listing = currentProgram.getListing();
        Address lo = addr(0x088b55a00L), hi = addr(0x088b56800L);
        AddressSet set = new AddressSet(lo, hi);
        CodeUnit before = listing.getCodeUnitAt(addr(0x088b55bf0L));
        out.println("codeUnitAt bf0 BEFORE: " + (before == null ? "null" : before.getClass().getSimpleName() + " " + before));
        listing.clearCodeUnits(lo, hi, false, monitor);
        CodeUnit after = listing.getCodeUnitAt(addr(0x088b55bf0L));
        out.println("codeUnitAt bf0 AFTER clear: " + (after == null ? "null" : after.getClass().getSimpleName() + " " + after));
        DisassembleCommand cmd = new DisassembleCommand(addr(0x088b55bf0L), set, true);
        boolean ok = cmd.applyTo(currentProgram, monitor);
        out.println("DisassembleFromBf0 ok=" + ok + " status=" + cmd.getStatusMsg());
        Instruction probe = listing.getInstructionAt(addr(0x088b55bf0L));
        out.println("instructionAt bf0: " + probe);
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
                out.println("NO FUNCTION; listing from seed:");
                Instruction ins = listing.getInstructionAt(a);
                if (ins == null) ins = listing.getInstructionAfter(a);
                for (int n = 0; n < 160 && ins != null; n++) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
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
