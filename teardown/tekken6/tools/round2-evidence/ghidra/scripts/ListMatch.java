import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import java.io.FileWriter;
import java.io.PrintWriter;
public class ListMatch extends GhidraScript {
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        // disassemble from each seed offset, then dump full instruction listing of range
        for (int i = 1; i < args.length; i++) {
            long off = Long.parseLong(args[i], 16);
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(off);
            boolean ok = disassemble(a);
            out.println("seed 0x" + args[i] + " disasm=" + ok);
            out.flush();
        }
        Address lo = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x1c00);
        Address hi = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x1f50);
        InstructionIterator it = currentProgram.getListing().getInstructions(new ghidra.program.model.address.AddressSet(lo, hi), true);
        int n = 0;
        while (it.hasNext()) { Instruction ins = it.next(); out.println(ins.getAddress() + "  " + ins.toString()); n++; }
        out.println("instructions: " + n);
        out.close();
    }
}
