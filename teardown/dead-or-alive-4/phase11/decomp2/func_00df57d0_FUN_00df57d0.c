// FUN_00df57d0 @ Ghidra 00df57d0 / true VA 829f57d0

/* WARNING: Control flow encountered bad instruction data */

void FUN_00df57d0(uint param_1,int param_2,undefined4 param_3,uint *param_4,undefined4 param_5,
                 int *param_6,int param_7)

{
  uint uVar1;
  int iVar2;
  uint in_r11;
  uint *unaff_r16;
  int unaff_r31;
  uint uVar3;
  byte in_cr6;
  
  *(undefined4 *)(param_2 + *(int *)(param_7 + 0x1c)) = param_5;
  if ((bool)(in_cr6 >> 3 & 1)) {
    uVar3 = unaff_r31 << 8;
  }
  else {
    in_r11 = in_r11 - 0x20;
    uVar3 = param_1 << (in_r11 & 0x3f);
    param_1 = *param_4;
    param_4 = param_4 + 1;
  }
  uVar1 = uVar3;
  if (in_r11 != 0) {
    uVar1 = param_1 >> (0x20 - in_r11 & 0x3f) | uVar3;
  }
  if (uVar1 >> 0x17 < 0x200) {
                    /* WARNING: Could not emulate address calculation at 0x00df4110 */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)((uVar1 >> 0x17) * 4 + -0x7d61a6e4))();
    return;
  }
  iVar2 = *param_6;
  if (iVar2 != *(int *)(param_7 + 0x10)) {
    iVar2 = -iVar2;
  }
  *param_6 = iVar2;
  *unaff_r16 = uVar3;
  unaff_r16[1] = param_1;
  unaff_r16[2] = in_r11;
  unaff_r16[3] = (uint)param_4;
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

