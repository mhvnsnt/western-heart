import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.FileWriter;
import java.io.PrintWriter;
public class DecompRegion extends GhidraScript {
    // args: outfile baseOffsetHex seedOffsetHex...
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        long base = Long.parseLong(args[1], 16);
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (int i = 2; i < args.length; i++) {
            long off = Long.parseLong(args[i], 16);
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off);
            boolean ok = disassemble(a);
            Function f = getFunctionContaining(a);
            if (f == null) { try { f = createFunction(a, "fn_" + args[i]); } catch (Exception e) { out.println("createFunction " + args[i] + ": " + e); } }
            out.println("==== SEED vaddr 0x" + Long.toHexString(base + off) + " (off 0x" + args[i] + ") disasm=" + ok + " func=" + f);
            out.flush();
            if (f != null) {
                DecompileResults res = decomp.decompileFunction(f, 120, monitor);
                if (res != null && res.getDecompiledFunction() != null) out.println(res.getDecompiledFunction().getC());
                else out.println("DECOMPILE FAILED");
                out.flush();
            }
        }
        out.close();
        decomp.dispose();
    }
}
