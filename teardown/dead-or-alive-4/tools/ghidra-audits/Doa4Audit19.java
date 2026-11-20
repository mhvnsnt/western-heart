// Audit19: identify the 00dfxxxx thunk-target region (Audit15-18 lead)
// @category DOA4
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
public class Doa4Audit19 extends GhidraScript {
  public void run() throws Exception {
    Memory mem = currentProgram.getMemory();
    AddressFactory af = currentProgram.getAddressFactory();
    // dump bytes 00dfd4a0..00dfd560
    Address a = af.getDefaultAddressSpace().getAddress(0xdfd4a0L);
    byte[] b = new byte[0xc0];
    mem.getBytes(a, b);
    StringBuilder sb = new StringBuilder();
    for (int i=0;i<b.length;i++){ if(i%16==0) sb.append(String.format("\n%08x: ",0xdfd4a0+i)); sb.append(String.format("%02x",b[i]&0xff)); }
    println("BYTES 00dfd4a0-00dfd560:"+sb);
    // count how many places in .text contain the savegprlr pattern fa81ff98 (std r20,-0x68(r1))
    byte[] pat = {(byte)0xfa,(byte)0x81,(byte)0xff,(byte)0x98};
    Address cur = af.getDefaultAddressSpace().getAddress(0x6e0000L);
    Address end = af.getDefaultAddressSpace().getAddress(0xf4adffL);
    int hits=0; String first="";
    while (cur.compareTo(end)<0) {
      Address f = mem.findBytes(cur, end, pat, null, true, monitor);
      if (f==null) break;
      hits++; if(hits<=5) first += f.toString()+" ";
      cur = f.add(4);
    }
    println("savegprlr-pattern fa81ff98 hits in .text: "+hits+" first: "+first);
    // who calls 00dfd4a8? count bl targets in that range: scan is done by capstone externally; report block info
    MemoryBlock blk = mem.getBlock(af.getDefaultAddressSpace().getAddress(0xdfd4a8L));
    println("block containing 00dfd4a8: "+(blk==null?"(none)":blk.getName()+" "+blk.getStart()+"-"+blk.getEnd()));
  }
}
