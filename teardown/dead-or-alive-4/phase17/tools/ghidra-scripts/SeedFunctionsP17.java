// Phase 17: seed Ghidra functions from the XEX .pdata table (15,054
// entries parsed offline by pdata_parse_p17.py; begin/end VAs passed
// as a flat file arg), disassemble + create functions at the target
// VAs, then decompile the target set and report references to the
// 0x9C-record arena base 0x83020188 and the .mot registry 0x82C69A70.
// Args: <pdataCsvPath> <outputDir>
// @category Phase17
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import java.io.File;
import java.io.FileWriter;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

public class SeedFunctionsP17 extends GhidraScript {
    private Address A(long va) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(va);
    }
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        File csv = new File(args[0]);
        File outDir = new File(args[1]);
        outDir.mkdirs();
        int created = 0, existed = 0, failed = 0;
        List<long[]> ranges = new ArrayList<>();
        for (String line : Files.readAllLines(csv.toPath())) {
            line = line.trim();
            if (line.isEmpty()) continue;
            String[] p = line.split(",");
            long b = Long.parseLong(p[0], 16), e = Long.parseLong(p[1], 16);
            ranges.add(new long[]{b, e});
        }
        for (long[] r : ranges) {
            Address b = A(r[0]);
            if (currentProgram.getFunctionManager().getFunctionAt(b) != null) { existed++; continue; }
            DisassembleCommand dc = new DisassembleCommand(b, null, true);
            dc.applyTo(currentProgram, monitor);
            CreateFunctionCmd cf = new CreateFunctionCmd(b, false);
            if (cf.applyTo(currentProgram, monitor)) created++; else failed++;
            if (monitor.isCancelled()) break;
        }
        FileWriter rep = new FileWriter(new File(outDir, "seed-report.txt"));
        rep.write("pdata ranges=" + ranges.size() + " functions created=" + created
            + " existed=" + existed + " failed=" + failed + "\n");
        rep.write("total functions now=" + currentProgram.getFunctionManager().getFunctionCount() + "\n");
        // reference hunt
        long[] bases = {0x83020188L, 0x82C69A70L, 0x830A7C20L};
        for (long base : bases) {
            for (long off = 0; off < 0xA0; off += 4) {
                Address a = A(base + off);
                ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
                while (it.hasNext()) {
                    Reference ref = it.next();
                    Function f = currentProgram.getFunctionManager().getFunctionContaining(ref.getFromAddress());
                    rep.write("REF to " + a + " from " + ref.getFromAddress() + " type=" + ref.getReferenceType()
                        + " func=" + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()) + "\n");
                }
            }
        }
        rep.flush();
        // decompile targets
        long[] targets = {0x8238EA20L, 0x824069D0L, 0x82408930L, 0x823F6CE8L, 0x823F6EC8L,
                          0x823912B0L, 0x8238A808L, 0x82408108L, 0x823FA3D0L, 0x824F3880L,
                          0x824EBDA8L, 0x824F0148L};
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        for (long va : targets) {
            Address a = A(va);
            Function f = currentProgram.getFunctionManager().getFunctionAt(a);
            if (f == null) f = currentProgram.getFunctionManager().getFunctionContaining(a);
            String name = String.format("pdata_%08X", va);
            if (f == null) { rep.write(name + " NO-FUNCTION\n"); continue; }
            DecompileResults res = di.decompileFunction(f, 180, monitor);
            FileWriter cf = new FileWriter(new File(outDir, name + ".c"));
            cf.write("// function " + f.getName() + " entry " + f.getEntryPoint()
                + " body " + f.getBody().getMinAddress() + "-" + f.getBody().getMaxAddress() + "\n");
            if (res != null && res.getDecompiledFunction() != null) cf.write(res.getDecompiledFunction().getC());
            else cf.write("// decompile failed\n");
            cf.close();
            rep.write(name + " decompiled " + f.getEntryPoint() + "\n");
            rep.flush();
        }
        di.dispose();
        rep.close();
        println("P17-SEED-DONE created=" + created);
    }
}
