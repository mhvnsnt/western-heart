// FUN_009cc8a8 @ Ghidra 009cc8a8 / true VA 825cc8a8

/* WARNING: Control flow encountered bad instruction data */

void FUN_009cc8a8(void)

{
  byte in_cr6;
  
  if (!(bool)(in_cr6 >> 1 & 1)) {
    thunk_FUN_00e00028();
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

