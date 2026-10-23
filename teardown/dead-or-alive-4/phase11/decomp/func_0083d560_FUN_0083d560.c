// FUN_0083d560 @ Ghidra 0083d560 / true VA 8243d560

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0083d560(void)

{
  int iVar1;
  undefined4 uVar2;
  int *in_r8;
  undefined4 *in_r10;
  uint uVar3;
  int *piVar4;
  undefined4 *in_r11;
  int unaff_r23;
  int unaff_r24;
  int *unaff_r30;
  int in_CTR;
  
  do {
    uVar2 = *in_r11;
    in_r11 = in_r11 + 1;
    *in_r10 = uVar2;
    in_r10 = in_r10 + 1;
    in_CTR = in_CTR + -1;
  } while (in_CTR != 0);
  if (*in_r8 == 0) {
    *unaff_r30 = 3;
    FUN_00b896d8(unaff_r30[0x1d1] + 4,0x82285f24,0x14);
    FUN_0083bb80(unaff_r30[0x1d1],1);
  }
  else {
    func_0x0083bcb8(unaff_r30[0x1d1],0);
    if (*(int *)unaff_r30[0x1d1] == 7) {
      *unaff_r30 = unaff_r23;
      halt_baddata();
    }
  }
  iVar1 = _DAT_82e5b450;
  if ((*unaff_r30 == 4) && (*(int *)(_DAT_82e5b450 + 0x10) == 10)) {
    if (unaff_r30[0x3db] == 0) {
      if (*(int *)(_DAT_82e5b450 + 0x10a8) == 0) {
        uVar3 = unaff_r30[0x2f8];
        if (uVar3 < (uint)unaff_r30[0x2f9]) {
          uVar3 = uVar3 + 0x20;
        }
        if (uVar3 != unaff_r30[0x2f9]) {
          if ((*(uint *)(_DAT_82e5b450 + 100) & 2) == 0) {
            FUN_008457f0(_DAT_82e5b450 + 0x18,2);
          }
          if ((*(int *)(_DAT_82e5b450 + 0x60) != 3) && (*(int *)(_DAT_82e5b450 + 0x60) != 0x8a)) {
            halt_baddata();
          }
          func_0x0083dd08(unaff_r30);
          halt_baddata();
        }
      }
      if (((*(uint *)(_DAT_82e5b450 + 100) & 2) != 0) &&
         (uVar3 = *(uint *)(_DAT_82e5b450 + 100) & 0xfffffffd,
         *(uint *)(_DAT_82e5b450 + 100) = uVar3, uVar3 == 0)) {
        func_0x00845928();
      }
    }
    else {
      unaff_r30[0x3db] = 0;
      if (*(int *)(iVar1 + 100) != 0) {
        *unaff_r30 = unaff_r23;
        iVar1 = *(int *)(iVar1 + 0x5c);
        if (iVar1 != 0) {
          piVar4 = unaff_r30 + 0x3dd;
          do {
            *piVar4 = 0;
            piVar4 = piVar4 + 1;
            unaff_r23 = unaff_r23 + -1;
          } while (unaff_r23 != 0);
          func_0x00d5f7d0(iVar1,unaff_r30 + 0x3dd);
          *unaff_r30 = 8;
        }
      }
    }
  }
  else if ((*unaff_r30 == 8) && (unaff_r30[0x3dd] != 0x3e5)) {
    FUN_00b8a308(unaff_r30 + 0x3dd);
    *unaff_r30 = unaff_r24;
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

