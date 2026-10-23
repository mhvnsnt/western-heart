// FUN_00a47880 @ Ghidra 00a47880 / true VA 82647880

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00a47880(void)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 in_r7;
  int in_r10;
  undefined4 *in_r11;
  undefined4 *unaff_r31;
  undefined4 in_vr0_32_0;
  undefined4 in_vr0_32_1;
  undefined4 in_vr0_32_2;
  undefined4 in_vr0_32_3;
  
  uVar1 = *(undefined4 *)(in_r10 + -0x16e4);
  *unaff_r31 = 0x8228c1d8;
  in_r11[0x13] = uVar1;
  in_r11[0x14] = uVar1;
  in_r11[4] = in_r7;
  in_r11[0x16] = uVar1;
  in_r11[0x1a] = 1;
  in_r11[0x17] = uVar1;
  *in_r11 = 0x8221e890;
  uVar3 = uRam822aa668;
  in_r11[0x18] = uVar1;
  in_r11[0x1d] = uVar1;
  in_r11[0x1e] = uVar1;
  in_r11[0x15] = uVar3;
  in_r11[0x10] = 0;
  puVar2 = (undefined4 *)((uint)(in_r11 + 8) & 0xfffffff0);
  *puVar2 = in_vr0_32_0;
  puVar2[1] = in_vr0_32_1;
  puVar2[2] = in_vr0_32_2;
  puVar2[3] = in_vr0_32_3;
  in_r11[0x11] = 0;
  puVar2 = (undefined4 *)((uint)(in_r11 + 0xc) & 0xfffffff0);
  *puVar2 = in_vr0_32_0;
  puVar2[1] = in_vr0_32_1;
  puVar2[2] = in_vr0_32_2;
  puVar2[3] = in_vr0_32_3;
  in_r11[0x12] = 0;
  in_r11[0x19] = 0;
  in_r11[0x1b] = 0;
  in_r11[0x1c] = 0;
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

