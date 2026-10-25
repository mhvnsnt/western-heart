import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import java.io.FileWriter;
import java.io.PrintWriter;
public class DecompMore extends GhidraScript {
    // args: outfile seedOffsetHex...
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (int i = 1; i < args.length; i++) {
            long off = Long.parseLong(args[i], 16);
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off);
            disassemble(a);
            Function f = getFunctionContaining(a);
            if (f == null) { try { f = createFunction(a, "fn_" + args[i]); } catch (Exception e) { out.println("createFunction " + args[i] + ": " + e); } }
            out.println("==== SEED off 0x" + args[i] + " func=" + f);
            out.flush();
            if (f != null) {
                DecompileResults res = decomp.decompileFunction(f, 120, monitor);
                if (res != null && res.getDecompiledFunction() != null) out.println(res.getDecompiledFunction().getC());
                else out.println("DECOMPILE FAILED");
                out.flush();
            }
        }
        out.println("==== LISTING 0x1dd0-0x2300 ====");
        Instruction ins = currentProgram.getListing().getInstructionAt(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x1dd0));
        if (ins == null) ins = currentProgram.getListing().getInstructionAfter(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x1dd0));
        Address end = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x2300);
        while (ins != null && ins.getAddress().compareTo(end) < 0) {
            out.println(ins.getAddress() + "  " + ins.toString());
            ins = ins.getNext();
        }
        out.close();
        decomp.dispose();
    }
}
