// function FUN_823f6ec8 entry 823f6ec8 body 823f6ec8-823f6f9f

/* WARNING: Control flow encountered bad instruction data */

void FUN_823f6ec8(char param_1)

{
  byte bVar1;
  ushort uVar2;
  uint uVar3;
  uint in_r10;
  int unaff_r27;
  int unaff_r29;
  int unaff_r30;
  byte *pbVar4;
  byte in_cr6;
  
  if (!(bool)(in_cr6 >> 1 & 1)) {
    *(undefined1 *)(unaff_r29 + 1) = 1;
  }
  if ((in_r10 & 0x3c0) != 0) {
    *(undefined1 *)(unaff_r29 + 2) = 1;
  }
  if ((*(ushort *)(unaff_r27 + 2) & 0x10) != 0) {
    DAT_830201ab = 1;
  }
  if ((*(ushort *)(unaff_r27 + 2) & 0x20) != 0) {
    uRam83020247 = 1;
  }
  if (param_1 != '\0') {
    pbVar4 = &DAT_830201a9;
    do {
      if (unaff_r30 == 0) {
        uVar2 = *(ushort *)(unaff_r27 + 2);
      }
      else {
        uVar2 = *(ushort *)(unaff_r27 + 2) >> 2;
      }
      uVar3 = uVar2 & 3;
      if (uVar3 != *pbVar4) {
        *pbVar4 = (byte)uVar3;
        bVar1 = (&DAT_8301818e)[uVar3 * 8];
        pbVar4[-0x20] = bVar1;
        pbVar4[-0x1f] = bVar1;
        FUN_82412e90(unaff_r30);
      }
      unaff_r30 = unaff_r30 + 1;
      pbVar4 = pbVar4 + 0x9c;
    } while (unaff_r30 < 2);
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

