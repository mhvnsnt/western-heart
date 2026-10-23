// FUN_009b53d8 @ Ghidra 009b53d8 / true VA 825b53d8

/* WARNING: Control flow encountered bad instruction data */

void FUN_009b53d8(void)

{
  undefined1 in_vs37 [16];
  undefined1 in_vs38 [16];
  undefined1 in_vs39 [16];
  undefined1 in_vs40 [16];
  
  vectorMergeHighWord(in_vs40,in_vs38);
  vectorMergeHighWord(in_vs39,in_vs37);
  vectorMergeLowWord(in_vs40,in_vs38);
  vectorMergeLowWord(in_vs39,in_vs37);
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

