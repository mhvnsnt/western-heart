import ghidra.app.plugin.core.disassembler.Disassembler;
import ghidra.app.script.GhidraScript;
import ghidra.program.disassemble.DisassemblerContextImpl;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Instruction;
import java.io.FileWriter;
import java.io.PrintWriter;

public class Diag2 extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        Address a = addr(0x088b55bf0L);
        out.println("imageBase=" + currentProgram.getImageBase() + " lang=" + currentProgram.getLanguageID());
        // 1) FlatProgramAPI disassemble
        boolean ok1 = disassemble(a);
        out.println("flat disassemble -> " + ok1 + " instr=" + currentProgram.getListing().getInstructionAt(a));
        out.flush();
        // 2) low-level Disassembler service
        try {
            Disassembler dis = Disassembler.getDisassembler(currentProgram, monitor, msg -> out.println("DISMSG: " + msg));
            AddressSetView res = dis.disassemble(a, new AddressSet(a, addr(0x088b56800L)), true);
            out.println("lowlevel disassembled set empty? " + (res == null ? "null" : res.isEmpty()));
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            out.println("instr after lowlevel: " + ins);
            if (ins != null) {
                for (int n = 0; n < 24 && ins != null; n++) { out.println(ins.getAddress() + "  " + ins.toString()); ins = ins.getNext(); }
            }
        } catch (Throwable t) { out.println("lowlevel EX: " + t); }
        out.close();
    }
    Address addr(long v) { return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
}
