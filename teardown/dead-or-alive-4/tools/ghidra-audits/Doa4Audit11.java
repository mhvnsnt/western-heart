import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 11: find every code caller of the crypto/content import thunks.
 * Thunk VA = 0x00f58764 + 16*slot (stride verified in Audit9).
 * Targets: XeKeysVerifyRSASignature(4), VdSwap(5), StfsControlDevice(6),
 * XeCryptShaUpdate(33), XeCryptShaFinal(34), XamContentOpenFile(99),
 * XamContentCreateEx(157), XamContentClose(159), XamContentLaunchImageFromFileInternal(166).
 */
public class Doa4Audit11 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 11: callers of crypto/content thunks ===");
        int[] slots = {4, 5, 6, 33, 34, 99, 157, 159, 166};
        String[] names = {"XeKeysVerifyRSASignature", "VdSwap", "StfsControlDevice",
            "XeCryptShaUpdate", "XeCryptShaFinal", "XamContentOpenFile",
            "XamContentCreateEx", "XamContentClose", "XamContentLaunchImageFromFileInternal"};
        AddressFactory af = currentProgram.getAddressFactory();
        for (int i = 0; i < slots.length; i++) {
            long va = 0x00f58764L + 16L * slots[i];
            Address a = af.getDefaultAddressSpace().getAddress(va);
            println("--- slot " + slots[i] + " " + names[i] + " thunk=0x" + Long.toHexString(va) + " ---");
            // find code refs: scan all bl instructions? cheaper: ask references to the SUB_ symbol if any
            Symbol sym = currentProgram.getSymbolTable().getPrimarySymbol(a);
            int n = 0;
            if (sym != null) {
                for (Reference r : currentProgram.getReferenceManager().getReferencesTo(a)) {
                    if (!r.getReferenceType().isCall()) continue;
                    n++;
                    Function cf = getFunctionContaining(r.getFromAddress());
                    println("  caller: " + r.getFromAddress() + " in " + (cf != null ? cf.getName() + "@" + cf.getEntryPoint() : "(none)"));
                }
            }
            // fallback: raw scan of .text for bl-with-target==va (LI field match)
            if (n == 0) {
                println("  (no symbol xrefs; raw bl-target scan)");
                n = rawBlScan(va, names[i]);
            }
            println("  total callers: " + n);
        }
        println("=== AUDIT 11 DONE ===");
    }

    int rawBlScan(long targetVa, String name) throws Exception {
        ghidra.program.model.mem.Memory mem = currentProgram.getMemory();
        ghidra.program.model.listing.Listing listing = currentProgram.getListing();
        ghidra.program.model.mem.MemoryBlock text = null;
        for (ghidra.program.model.mem.MemoryBlock b : mem.getBlocks())
            if (b.getName().equals(".text")) text = b;
        if (text == null) return 0;
        int n = 0;
        InstructionIterator it = listing.getInstructions(text.getStart(), true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (ins.getAddress().compareTo(text.getEnd()) > 0) break;
            String s = ins.toString();
            if (!s.startsWith("bl ")) continue;
            for (Reference r : ins.getReferencesFrom()) {
                if (r.getReferenceType().isCall() && r.getToAddress().getOffset() == targetVa) {
                    n++;
                    Function cf = getFunctionContaining(ins.getAddress());
                    println("  caller: " + ins.getAddress() + " in " + (cf != null ? cf.getName() + "@" + cf.getEntryPoint() : "(none)"));
                    break;
                }
            }
        }
        return n;
    }
}
