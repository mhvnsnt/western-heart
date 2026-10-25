import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = args[0];
        PrintWriter out = new PrintWriter(new FileWriter(outPath));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        Listing listing = currentProgram.getListing();
        // args[1..] are hex addresses; decompile containing function + dump listing range
        for (int i = 1; i < args.length; i++) {
            long va = Long.parseLong(args[i], 16);
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(va);
            Function f = getFunctionContaining(a);
            out.println("==== ADDR 0x" + args[i] + " ====");
            if (f == null) {
                out.println("NO FUNCTION CONTAINING; listing 64 instrs from addr:");
                Instruction ins = listing.getInstructionAt(a);
                if (ins == null) ins = listing.getInstructionAfter(a);
                for (int n = 0; n < 64 && ins != null; n++) {
                    out.println(ins.getAddress() + "  " + ins.toString());
                    ins = ins.getNext();
                }
                continue;
            }
            out.println("FUNCTION " + f.getName() + " @ " + f.getEntryPoint() + " body " + f.getBody());
            DecompileResults res = decomp.decompileFunction(f, 120, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                out.println(res.getDecompiledFunction().getC());
            } else {
                out.println("DECOMPILE FAILED");
                Instruction ins = listing.getInstructionAt(f.getEntryPoint());
                while (ins != null && f.getBody().contains(ins.getAddress())) {
                    out.println(ins.getAddress() + "  " + ins.toString());
                    ins = ins.getNext();
                }
            }
        }
        out.close();
        decomp.dispose();
    }
}
