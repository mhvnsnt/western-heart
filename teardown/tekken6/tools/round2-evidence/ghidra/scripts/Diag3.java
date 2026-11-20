import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Instruction;
import java.io.FileWriter;
import java.io.PrintWriter;
public class Diag3 extends GhidraScript {
    @Override public void run() throws Exception {
        PrintWriter out = new PrintWriter(new FileWriter(getScriptArgs()[0]));
        Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0);
        out.println("base=" + currentProgram.getImageBase() + " lang=" + currentProgram.getLanguageID() + " compiler=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        CodeUnit cu = currentProgram.getListing().getCodeUnitAt(a);
        out.println("codeUnitAt0=" + cu);
        boolean ok = disassemble(a);
        out.println("flat disassemble=" + ok);
        Instruction ins = currentProgram.getListing().getInstructionAt(a);
        out.println("instrAt0=" + ins);
        DisassembleCommand cmd = new DisassembleCommand(new AddressSet(a, a.add(1023)), new AddressSet(a, a.add(1023)), true);
        boolean ok2 = cmd.applyTo(currentProgram, monitor);
        out.println("cmd=" + ok2 + " status=" + cmd.getStatusMsg());
        ins = currentProgram.getListing().getInstructionAt(a);
        out.println("instrAt0 after cmd=" + ins);
        if (ins != null) { for (int n=0;n<8 && ins!=null;n++){ out.println(ins.getAddress()+"  "+ins); ins=ins.getNext(); } }
        out.close();
    }
}
