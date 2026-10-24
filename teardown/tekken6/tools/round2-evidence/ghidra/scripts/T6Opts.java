import ghidra.app.script.GhidraScript;
import ghidra.framework.options.Options;
import ghidra.program.model.listing.Program;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

public class T6Opts extends GhidraScript {
    @Override
    public void run() throws Exception {
        PrintWriter out = new PrintWriter(new FileWriter("/home/hatch/workspace/_t6lane/ghidra_out/opts.txt"));
        Options pl = currentProgram.getOptions(Program.ANALYSIS_PROPERTIES);
        Set<String> keep = new HashSet<>();
        keep.add("Function Start Search");
        keep.add("MIPS Constant Address Analyzer");
        keep.add("ELF Function Analysis");
        for (String name : pl.getOptionNames()) {
            boolean k = keep.contains(name);
            try { pl.setBoolean(name, k); } catch (Exception e) { out.println("skip " + name + ": " + e); }
            out.println((k ? "ON  " : "off ") + name);
        }
        out.close();
    }
}
