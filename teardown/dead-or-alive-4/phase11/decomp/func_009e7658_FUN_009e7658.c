// FUN_009e7658 @ Ghidra 009e7658 / true VA 825e7658

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_009e7658(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int in_r11;
  undefined4 unaff_r30;
  int unaff_r31;
  undefined4 uStack00000054;
  
  uStack00000054 = param_3;
  (**(code **)(in_r11 + 0x10))
            ((double)fRam822aa07c,(double)fRam821b6508,(double)fRam822a9e60,(double)fRam821b6f20,
             (double)_DAT_8204fea0,unaff_r30);
  _DAT_82e62d8c = *(int *)(unaff_r31 + 0x10) + unaff_r31;
  iRam82e62d88 = *(int *)(unaff_r31 + 0xc) + unaff_r31;
  _DAT_82e62d84 = 0x9b;
  func_0x009501c8();
  (**(code **)(_DAT_82e62e40 + 8))((double)_DAT_8217e91c,&DAT_82e62e40,0,0,0,0);
  uRam82e62ed8 = 0;
  uRam82e62edc = 0;
  uRam82e62ed4 = 0;
  func_0x009501c8();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

