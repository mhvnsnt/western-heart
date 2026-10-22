// FUN_009625a0 @ Ghidra 009625a0 / true VA 825625a0

/* WARNING: Control flow encountered bad instruction data */

void FUN_009625a0(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int *piVar1;
  int in_r10;
  int in_r11;
  undefined4 *unaff_r30;
  undefined4 *unaff_r31;
  undefined4 uStack00000050;
  undefined4 uStack00000054;
  
  piVar1 = *(int **)(in_r11 * 4 + in_r10);
  uStack00000050 = 0;
  uStack00000054 = 0;
  if (param_4 == 0xffffffff) {
    param_4 = (uint)DAT_83191483;
  }
  (**(code **)(*piVar1 + 0x10c))(piVar1,&stack0x00000050,param_3,param_4);
  *unaff_r31 = uStack00000050;
  *unaff_r30 = uStack00000054;
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

