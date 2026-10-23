// function FUN_823f6ce8 entry 823f6ce8 body 823f6ce8-823f6ec7

/* WARNING: Control flow encountered bad instruction data */

void FUN_823f6ce8(void)

{
  byte bVar1;
  uint uVar2;
  char cVar3;
  ushort *puVar4;
  ushort *puVar5;
  ushort uVar6;
  ushort uVar7;
  int in_r11;
  ushort uVar8;
  ushort uVar9;
  int iVar10;
  byte *pbVar11;
  
  iVar10 = 0;
  *(undefined1 *)(in_r11 + -0x6508) = 0;
  puVar5 = DAT_83099e04;
  *(undefined1 *)(in_r11 + -0x6507) = 0;
  *(undefined1 *)(in_r11 + -0x6506) = 0;
  puVar4 = DAT_83099ba8;
  if (DAT_83099e20 != 0) {
    if (DAT_83022e92 == '\0') {
      uVar7 = *puVar5;
      uVar6 = (ushort)DAT_82fb9027;
      DAT_82fb9027 = (byte)(uVar7 & 1);
      DAT_8302232f = (uVar7 & 2) != 0;
      uVar8 = uVar7 >> 2 & 0xf;
      uVar9 = (ushort)DAT_83191483;
      DAT_83191483 = (byte)uVar8;
      bRam83191ec0 = (byte)(uVar7 >> 6) & 0xf;
      if (uVar9 != uVar8 || uVar6 != (uVar7 & 1)) {
        func_0x8254b4f0();
      }
    }
    cVar3 = DAT_83022e92;
    uRam83099792 = 0;
    uRam83099797 = 0;
    uVar7 = *puVar5 & 0xc00;
    if (uVar7 < 0x801) {
      if (uVar7 == 0x800) {
        uRam83099792 = 3;
      }
      else if ((*puVar5 & 0xc00) == 0) {
        uRam83099792 = 1;
      }
      else if (uVar7 == 0x400) {
        uRam83099792 = 2;
      }
    }
    else if (uVar7 == 0xc00) {
      uRam83099792 = 5;
    }
    uVar7 = *puVar4;
    uVar8 = uVar7 & 0xc00;
    if (uVar8 < 0x801) {
      if (uVar8 == 0x800) {
        uRam83099797 = 3;
      }
      else if ((uVar7 & 0xc00) == 0) {
        uRam83099797 = 1;
      }
      else if (uVar8 == 0x400) {
        uRam83099797 = 2;
      }
    }
    else if (uVar8 == 0xc00) {
      uRam83099797 = 5;
    }
    uVar7 = puVar4[1] ^ puVar5[1];
    if ((uVar7 & 3) != 0) {
      *(undefined1 *)(in_r11 + -0x6508) = 1;
    }
    if ((uVar7 & 0xc) != 0) {
      *(undefined1 *)(in_r11 + -0x6507) = 1;
    }
    if ((uVar7 & 0xc0) != 0) {
      *(undefined1 *)(in_r11 + -0x6506) = 1;
    }
    if ((puVar5[1] & 0x10) != 0) {
      DAT_830201ab = 1;
    }
    if ((puVar5[1] & 0x20) != 0) {
      uRam83020247 = 1;
    }
    if (cVar3 != '\0') {
      pbVar11 = &DAT_830201a9;
      do {
        if (iVar10 == 0) {
          uVar7 = puVar5[1];
        }
        else {
          uVar7 = puVar5[1] >> 2;
        }
        uVar2 = uVar7 & 3;
        if (uVar2 != *pbVar11) {
          *pbVar11 = (byte)uVar2;
          bVar1 = (&DAT_8301818e)[uVar2 * 8];
          pbVar11[-0x20] = bVar1;
          pbVar11[-0x1f] = bVar1;
          FUN_82412e90(iVar10);
        }
        iVar10 = iVar10 + 1;
        pbVar11 = pbVar11 + 0x9c;
      } while (iVar10 < 2);
    }
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

