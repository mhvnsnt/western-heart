// FUN_00783f28 @ Ghidra 00783f28 / true VA 82383f28

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Removing unreachable block (ram,0x007840f8) */
/* WARNING: Removing unreachable block (ram,0x007841ac) */

void FUN_00783f28(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  int unaff_r26;
  undefined4 unaff_r27;
  int unaff_r30;
  
  iVar2 = func_0x00b897b0();
  func_0x00b8b588();
  if (iVar2 != -1) {
    FUN_00b8bfa0(iVar2,&stack0x00000070);
                    /* WARNING: Subroutine does not return */
    FUN_00b89d40(iVar2);
  }
  *(undefined4 *)(unaff_r26 + 0x1edc) = 1;
  func_0x00783d20(unaff_r30);
  func_0x00b8c108();
  func_0x00b8b588();
  *(undefined4 *)(unaff_r26 + 0x1edc) = 0;
  iVar2 = func_0x00783d88();
  if (iVar2 <= unaff_r30 + 1) {
    *(undefined4 *)(unaff_r26 + 0x1edc) = 1;
    iVar3 = 0;
    iVar2 = func_0x00783d88();
    if (iVar2 < 1) {
      FUN_00b8be90(0x8221e9dc,0,0,&stack0x00000060);
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    iVar2 = 0;
    piVar4 = (int *)0x82c6cd7c;
    uVar5 = 0;
    while( true ) {
      if (*piVar4 != 0) {
        iVar2 = iVar2 + 1;
      }
      if (iVar3 + 1 == iVar2) break;
      uVar5 = uVar5 + 0x1c;
      piVar4 = piVar4 + 7;
      if (0x117 < uVar5) {
                    /* WARNING: Bad instruction - Truncating control flow here */
        halt_baddata();
      }
    }
    halt_baddata();
  }
  uVar1 = func_0x00783e38(unaff_r30 + 1);
  uVar1 = func_0x00b897b0(uVar1,unaff_r27,0,0,3,0,0);
  FUN_00b8bfa0(uVar1,&stack0x000000b0);
                    /* WARNING: Subroutine does not return */
  FUN_00b89d40(uVar1);
}

