// Phase 17 post-script: acceptance evidence for the faithful project.
//  - block map at the true base
//  - xrefs TO the .mot registry table (0x82C69A70) and its records
//  - xrefs TO the D:\bin registry string block (sample addresses)
//  - decompile the proven target functions at their true VAs
// Args: <outputDir>
// @category Phase17
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.io.File;
import java.io.FileWriter;

public class ExportP17 extends GhidraScript {
    private Address A(long va) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(va);
    }
    private void xrefReport(FileWriter w, long va, String label) throws Exception {
        Address a = A(va);
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
        int n = 0;
        w.write("XREF " + label + " " + String.format("0x%08X", va) + "\n");
        while (it.hasNext()) {
            Reference r = it.next();
            Function f = currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress());
            w.write("  from " + r.getFromAddress() + " type=" + r.getReferenceType()
                + " in " + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()) + "\n");
            n++;
        }
        w.write("  total=" + n + "\n");
    }
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        File outDir = new File(args.length > 0 ? args[0] : "/tmp/p17-ghidra-out");
        outDir.mkdirs();
        FileWriter rep = new FileWriter(new File(outDir, "acceptance.txt"));
        rep.write("imageBase=" + currentProgram.getImageBase() + "\n");
        rep.write("minAddr=" + currentProgram.getMinAddress() + " maxAddr=" + currentProgram.getMaxAddress() + "\n");
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            rep.write("BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " init=" + b.isInitialized() + "\n");
        }
        // registry + a few record starts and name pointers inside records
        xrefReport(rep, 0x82C69A70L, "mot-registry-base");
        xrefReport(rep, 0x82C69A70L + 0x6C, "mot-registry-rec1");
        xrefReport(rep, 0x82278660L, "str-zack.bin");
        xrefReport(rep, 0x82284860L, "str-janlee.mot(rec0-name)");
        // dump registry name fields as Ghidra sees them (pointer chase)
        rep.write("REGISTRY-NAMES\n");
        for (int i = 0; i < 8; i++) {
            Address rec = A(0x82C69A70L + (long) i * 0x6C);
            long namePtr = currentProgram.getMemory().getInt(rec.add(0x18)) & 0xFFFFFFFFL;
            String s = "";
            try {
                Address np = A(namePtr);
                StringBuilder sb = new StringBuilder();
                for (int j = 0; j < 64; j++) {
                    byte c = currentProgram.getMemory().getByte(np.add(j));
                    if (c == 0) break;
                    sb.append((char) c);
                }
                s = sb.toString();
            } catch (Exception e) { s = "<err " + e.getMessage() + ">"; }
            rep.write("  rec" + i + " namePtr=" + String.format("0x%08X", namePtr) + " name=" + s + "\n");
            rep.flush();
        }
        rep.flush();

        // decompile targets
        long[] targets = {0x8238ED10L, 0x82406E48L, 0x824091F0L, 0x823F6D2CL, 0x823F6FA0L,
                          0x823918E8L, 0x8238AC90L, 0x82408290L, 0x823FA430L};
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        FileWriter idx = new FileWriter(new File(outDir, "decompile-index.txt"));
        for (long va : targets) {
            Address a = A(va);
            Function f = currentProgram.getFunctionManager().getFunctionContaining(a);
            if (f == null) f = currentProgram.getFunctionManager().getFunctionAt(a);
            String name = String.format("func_%08X", va);
            if (f == null) {
                idx.write(name + " NO-FUNCTION\n");
                continue;
            }
            idx.write(name + " function=" + f.getName() + " entry=" + f.getEntryPoint()
                + " body=" + f.getBody().getMinAddress() + "-" + f.getBody().getMaxAddress() + "\n");
            DecompileResults res = di.decompileFunction(f, 120, monitor);
            FileWriter cf = new FileWriter(new File(outDir, name + ".c"));
            if (res != null && res.getDecompiledFunction() != null) {
                cf.write(res.getDecompiledFunction().getC());
            } else {
                cf.write("// decompile failed: " + (res == null ? "null" : res.getErrorMessage()) + "\n");
            }
            cf.close();
        }
        di.dispose();
        idx.close();
        println("P17-EXPORT-DONE " + outDir);
    }
}
