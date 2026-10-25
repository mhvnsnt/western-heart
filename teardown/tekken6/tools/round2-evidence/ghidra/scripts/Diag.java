import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import java.io.FileWriter;
import java.io.PrintWriter;

public class Diag extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        out.println("program: " + currentProgram.getName() + " imageBase=" + currentProgram.getImageBase());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            out.println("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " init=" + b.isInitialized() + " exec=" + b.isExecute());
        }
        Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x088b55bf0L);
        byte[] buf = new byte[16];
        int n = currentProgram.getMemory().getBytes(a, buf);
        out.println("bytes at seed: n=" + n + " " + buf[0] + "," + buf[1] + "," + buf[2] + "," + buf[3]);
        boolean ok = disassemble(a);
        out.println("disassemble returned " + ok);
        Instruction ins = currentProgram.getListing().getInstructionAt(a);
        out.println("instructionAt: " + ins);
        out.close();
    }
}
