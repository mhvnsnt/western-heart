// FUN_008ef100 @ Ghidra 008ef100 / true VA 824ef100

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_008ef100(double param_1)

{
  int in_r11;
  int unaff_r31;
  double in_f13;
  
  fRam830a52a0 = (float)(param_1 / (double)(float)in_f13) * *(float *)(in_r11 + 0x6974) *
                 _DAT_822a9e3c;
  FUN_0093d910();
  uRam8319264c = (uint)(unaff_r31 == 0);
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

