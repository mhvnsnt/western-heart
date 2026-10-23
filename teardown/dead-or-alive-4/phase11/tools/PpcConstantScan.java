import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
import java.util.*;

// Phase 11 Job 1: PPC lis/addi (+lis/ori, addis/oris, li) constant scan.
// Phase 10 proved ZERO code xrefs exist to the anm.afs file table in
// Ghidra's reference manager (PPC computed addressing), so this scan
// reconstructs materialized constants directly from the instruction
// stream with per-function constant propagation, and flags every
// function that materializes a watched address:
//   A) file table range 0x61E800-0x61EA20 (anm entry exactly 0x61E940)
//   B) the 5 data-side descriptor pointer locations found in phase 10
//      (0x4766B1, 0x47A5CD, 0x4808CD, 0x49276D, 0x583B49) +- 0x10
//   C) anm string addresses: 0x685F3C (anm%d.afs), 0x6784A3 (anime_cm),
//      0x67867F (anm_version.bin)
// Args: [0]=output dir for CSV + decompiles.
public class PpcConstantScan extends GhidraScript {

    static boolean inRange(long v, long lo, long hi) { return v >= lo && v < hi; }

    static String watchTag(long v) {
        if (v == 0x61E940L) return "ANM_TABLE_EXACT";
        if (inRange(v, 0x61E800L, 0x61EA20L)) return "FILE_TABLE";
        long[] desc = {0x4766B1L, 0x47A5CDL, 0x4808CDL, 0x49276DL, 0x583B49L};
        for (long d : desc) if (Math.abs(v - d) <= 0x10) return "DESCRIPTOR_PTR";
        if (v == 0x685F3CL) return "ANM_FMT_STR";
        if (v == 0x6784A3L) return "ANIME_CM_STR";
        if (v == 0x67867FL) return "ANM_VERSION_STR";
        if (inRange(v, 0x685F00L, 0x686000L)) return "ANM_STR_REGION";
        return null;
    }

    @Override
    public void run() throws Exception {
        String outDir = "/tmp/p11scan";
        String[] args = getScriptArgs();
        if (args != null && args.length > 0) outDir = args[0];
        new File(outDir).mkdirs();
        PrintWriter csv = new PrintWriter(new FileWriter(new File(outDir, "constant_hits.csv")));
        csv.println("func_entry,func_name,hit_addr,constant,tag,how");
        PrintWriter weak = new PrintWriter(new FileWriter(new File(outDir, "hi_only_hits.csv")));
        weak.println("func_entry,func_name,hit_addr,lis_imm");

        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        Map<String, Function> candidates = new TreeMap<>();
        Map<String, Integer> shiftCounts = new HashMap<>();
        long totalInstr = 0, totalHits = 0;

        FunctionIterator funcs = fm.getFunctions(true);
        while (funcs.hasNext()) {
            Function f = funcs.next();
            AddressSetView body = f.getBody();
            InstructionIterator it = listing.getInstructions(body, true);
            Map<Integer, Long> regs = new HashMap<>();
            Map<Integer, String> how = new HashMap<>();
            int shiftN = 0;
            while (it.hasNext()) {
                Instruction ins = it.next();
                totalInstr++;
                String mn = ins.getMnemonicString().toLowerCase();
                if (mn.startsWith("rlwinm") || mn.startsWith("srwi") || mn.startsWith("slwi")
                        || mn.startsWith("srawi") || mn.equals("andi.") || mn.equals("andi")) shiftN++;
                // collect operand registers/scalars
                Register rd = null, ra = null;
                Long imm = null; boolean immSigned = true;
                for (int i = 0; i < ins.getNumOperands(); i++) {
                    for (Object o : ins.getOpObjects(i)) {
                        if (o instanceof Register && i == 0 && rd == null) rd = (Register) o;
                        else if (o instanceof Register && i == 1 && ra == null) ra = (Register) o;
                        else if (o instanceof Scalar) imm = ((Scalar) o).getValue();
                    }
                }
                boolean handled = true;
                if (rd != null && imm != null) {
                    int d = rd.getOffset() / 8; // PPC GPR register offset/8 approx: use address offset
                    d = (int) rd.getAddress().getOffset();
                    if (mn.equals("lis")) {
                        long v = (imm << 16) & 0xFFFFFFFFL;
                        if (imm > 0x7FFF) v = ((imm - 0x10000) << 16) & 0xFFFFFFFFL;
                        regs.put(d, v); how.put(d, "lis@" + ins.getAddress());
                        if (imm == 0x61 || imm == 0x62 || imm == 0x60) {
                            weak.println(f.getEntryPoint() + "," + f.getName() + "," + ins.getAddress() + ",0x" + Long.toHexString(imm));
                        }
                    } else if (mn.equals("li")) {
                        long v = imm & 0xFFFFFFFFL;
                        regs.put(d, v); how.put(d, "li@" + ins.getAddress());
                    } else if ((mn.equals("addi") || mn.equals("addis")) && ra != null) {
                        int a = (int) ra.getAddress().getOffset();
                        Long base = regs.get(a);
                        if (base != null) {
                            long add = mn.equals("addis") ? ((imm > 0x7FFF ? imm - 0x10000 : imm) << 16) : (imm > 0x7FFF ? imm - 0x10000 : imm);
                            long v = (base + add) & 0xFFFFFFFFL;
                            regs.put(d, v); how.put(d, how.get(a) + "+" + mn + "@" + ins.getAddress());
                            String tag = watchTag(v);
                            if (tag != null) {
                                csv.println(f.getEntryPoint() + "," + f.getName() + "," + ins.getAddress() + ",0x" + Long.toHexString(v) + "," + tag + "," + how.get(d));
                                candidates.put(f.getEntryPoint().toString(), f);
                                totalHits++;
                            }
                        } else regs.remove(d);
                    } else if ((mn.equals("ori") || mn.equals("oris")) && ra != null) {
                        int a = (int) ra.getAddress().getOffset();
                        Long base = regs.get(a);
                        if (base != null) {
                            long v = mn.equals("oris") ? (base | ((imm & 0xFFFF) << 16)) : (base | (imm & 0xFFFF));
                            v &= 0xFFFFFFFFL;
                            regs.put(d, v); how.put(d, how.get(a) + "+" + mn + "@" + ins.getAddress());
                            String tag = watchTag(v);
                            if (tag != null) {
                                csv.println(f.getEntryPoint() + "," + f.getName() + "," + ins.getAddress() + ",0x" + Long.toHexString(v) + "," + tag + "," + how.get(d));
                                candidates.put(f.getEntryPoint().toString(), f);
                                totalHits++;
                            }
                        } else regs.remove(d);
                    } else handled = false;
                    if (!handled) regs.remove(d);
                } else if (rd != null && ra != null && (mn.equals("or") || mn.equals("mr"))) {
                    int a = (int) ra.getAddress().getOffset();
                    int d = (int) rd.getAddress().getOffset();
                    Long v = regs.get(a);
                    if (v != null) { regs.put(d, v); how.put(d, how.get(a) + "+mr@" + ins.getAddress()); }
                    else regs.remove(d);
                } else if (rd != null) {
                    int d = (int) rd.getAddress().getOffset();
                    if (!(mn.equals("lis") || mn.equals("li"))) regs.remove(d);
                }
                // clear propagation across control flow (conservative)
                FlowType ft = ins.getFlowType();
                if (ft != null && (ft.isCall() || ft.isJump() || ft.isTerminal())) regs.clear();
            }
            if (shiftN > 0) shiftCounts.put(f.getEntryPoint().toString(), shiftN);
        }
        csv.close(); weak.close();
        println("TOTAL instructions scanned: " + totalInstr);
        println("TOTAL watch hits: " + totalHits);
        println("CANDIDATE functions: " + candidates.size());
        for (Map.Entry<String, Function> e : candidates.entrySet()) {
            println("CAND " + e.getKey() + " " + e.getValue().getName()
                + " shift/mask-insns=" + shiftCounts.getOrDefault(e.getKey(), 0));
        }
        // Decompile candidates (cap 40), one file each + console head.
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        int n = 0;
        for (Function f : candidates.values()) {
            if (n++ >= 40) { println("decompile cap reached"); break; }
            DecompileResults res = dec.decompileFunction(f, 90, monitor);
            String c = (res != null && res.getDecompiledFunction() != null) ? res.getDecompiledFunction().getC() : "(decompile failed)";
            File out = new File(outDir, "func_" + f.getEntryPoint() + ".c");
            PrintWriter pw = new PrintWriter(new FileWriter(out));
            pw.println("// " + f.getName() + " @ " + f.getEntryPoint() + " shift/mask-insns=" + shiftCounts.getOrDefault(f.getEntryPoint().toString(), 0));
            pw.print(c); pw.close();
            println("DECOMP " + f.getEntryPoint() + " " + f.getName() + " bytes=" + c.length() + " -> " + out.getName());
        }
        println("=== PpcConstantScan done ===");
    }
}
