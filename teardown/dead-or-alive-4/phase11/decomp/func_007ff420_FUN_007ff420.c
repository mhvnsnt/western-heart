// FUN_007ff420 @ Ghidra 007ff420 / true VA 823ff420

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Removing unreachable block (ram,0x007ff3f8) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_007ff420(void)

{
  char cVar3;
  int iVar1;
  int iVar2;
  uint uVar4;
  uint uVar5;
  undefined2 *puVar6;
  undefined2 unaff_r24;
  undefined4 unaff_r25;
  uint unaff_r26;
  undefined1 *unaff_r27;
  int unaff_r28;
  char unaff_r29;
  char unaff_r30;
  char *unaff_r31;
  char *pcVar7;
  int *piVar8;
  undefined1 *puVar9;
  
code_r0x007ff420:
  *(undefined2 *)(unaff_r31 + 1) = unaff_r24;
  *(undefined4 *)(unaff_r31 + 3) = unaff_r25;
  *(uint *)(unaff_r31 + 0xb) = unaff_r26;
  func_0x007ff998();
LAB_007ff430:
  pcVar7 = unaff_r31;
  unaff_r28 = unaff_r28 + -1;
  unaff_r31 = pcVar7 + 0x10;
  if (unaff_r28 != 0) {
    if (((*unaff_r31 == -1) || (*unaff_r31 == -2)) || (cVar3 = func_0x007ffd38(), cVar3 != '\0'))
    goto LAB_007ff430;
    func_0x007ffad0(*(undefined2 *)(pcVar7 + 0x11),*(undefined4 *)(pcVar7 + 0x13),
                    *(undefined4 *)(pcVar7 + 0x17));
    pcVar7[0xf] = unaff_r29;
    *unaff_r31 = unaff_r30;
    goto code_r0x007ff420;
  }
  uVar5 = 1;
  if (unaff_r27[5] == -1) {
    uVar5 = unaff_r26;
  }
  *unaff_r27 = (char)uVar5;
  if ((uVar5 & 0xff) != (uint)(byte)unaff_r27[1]) {
    if ((uVar5 & 0xff) == 0) {
      uVar4 = _DAT_833f07ec - 1;
      _DAT_833f07ec = unaff_r26;
      if (((int)uVar4 < 0) || (_DAT_833f07ec = uVar4, uVar4 == 0)) {
        _DAT_83300784 = unaff_r26;
      }
    }
    else {
      _DAT_833f07ec = _DAT_833f07ec + 1;
      if (_DAT_83300784 == 0) {
        _DAT_83300784 = 1;
      }
    }
    unaff_r27[1] = (char)uVar5;
  }
  iVar1 = func_0x00783c68(0x83300760);
  if (iVar1 == 0) {
    iVar1 = 10;
    piVar8 = (int *)0x82c6cd7c;
    do {
      if (*piVar8 != 0) {
        FUN_00db69f8(piVar8[-3],*piVar8,0,piVar8[-2]);
        do {
          iVar2 = FUN_00db69b8(piVar8[-3]);
        } while (iVar2 != 3);
      }
      iVar1 = iVar1 + -1;
      piVar8 = piVar8 + 7;
    } while (iVar1 != 0);
    uRam83300758 = FUN_00db4468(0x8221e9dc,0,0,0);
    _DAT_833507a4 = 1;
  }
  uVar5 = unaff_r26;
  if (_DAT_830a197c != 0) {
    uVar5 = 1;
  }
  if ((int)uVar5 < (int)(uint)(byte)unaff_r27[2]) {
    puVar9 = unaff_r27 + 0xc;
    do {
      if (puVar9[-7] != -2) {
        halt_baddata();
      }
      iVar1 = FUN_007ffc50(*(undefined2 *)(puVar9 + -6),*(undefined4 *)(puVar9 + -4),puVar9,
                           *(undefined4 *)(puVar9 + 4));
      if (iVar1 != -1) {
        puVar9[-7] = (char)iVar1;
        if (*(int *)(puVar9 + -4) != -1) {
          puVar6 = (undefined2 *)(unaff_r27 + 0x804);
          uVar4 = unaff_r26;
          do {
            if (*(int *)(puVar9 + -4) == *(int *)(puVar6 + 2)) {
              *puVar6 = unaff_r24;
              *(undefined4 *)(puVar6 + 2) = unaff_r25;
              *(uint *)(puVar6 + 4) = unaff_r26;
              func_0x007ffba0();
              break;
            }
            uVar4 = uVar4 + 1;
            puVar6 = puVar6 + 6;
          } while ((int)uVar4 < 0x100);
        }
        func_0x007ff998();
        uVar5 = uVar5 + 1;
      }
      puVar9 = puVar9 + 0x10;
    } while ((int)uVar5 < (int)(uint)(byte)unaff_r27[2]);
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

