import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompTargeted extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = args[0];
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        Listing listing = currentProgram.getListing();
        for (int i = 1; i < args.length; i++) {
            long va = Long.parseLong(args[i], 16);
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(va);
            out.println("==== SEED 0x" + args[i] + " ====");
            // disassemble a window starting at the seed (function entry candidates)
            disassemble(a);
            Function f = getFunctionContaining(a);
            if (f == null) {
                try { f = createFunction(a, "seed_" + args[i]); } catch (Exception e) { out.println("createFunction failed: " + e); }
            }
            if (f == null) {
                out.println("STILL NO FUNCTION; raw listing 96 instrs:");
                Instruction ins = listing.getInstructionAt(a);
                if (ins == null) ins = listing.getInstructionAfter(a);
                for (int n = 0; n < 96 && ins != null; n++) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
                continue;
            }
            out.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint());
            DecompileResults res = decomp.decompileFunction(f, 180, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                out.println(res.getDecompiledFunction().getC());
            } else {
                out.println("DECOMPILE FAILED; listing:");
                Instruction ins = listing.getInstructionAt(f.getEntryPoint());
                while (ins != null && f.getBody().contains(ins.getAddress())) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
            }
            out.flush();
        }
        out.close();
        decomp.dispose();
    }
}
