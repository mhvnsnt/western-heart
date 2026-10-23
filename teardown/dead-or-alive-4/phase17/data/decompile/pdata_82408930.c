// function FUN_82408930 entry 82408930 body 82408930-8240896f

/* WARNING: Control flow encountered bad instruction data */

void FUN_82408930(void)

{
  undefined4 in_r11;
  int unaff_r29;
  byte in_cr6;
  
  if (!(bool)(in_cr6 >> 3 & 1)) {
    *(undefined4 *)(unaff_r29 + 4) = in_r11;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

