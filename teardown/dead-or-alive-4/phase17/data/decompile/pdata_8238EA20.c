// function FUN_8238ea20 entry 8238ea20 body 8238ea20-8238eae3

/* WARNING: Control flow encountered bad instruction data */

void FUN_8238ea20(void)

{
  uint uVar1;
  int unaff_r31;
  byte in_cr6;
  undefined1 uStack00000057;
  undefined2 uStack0000005e;
  
  if (!(bool)(in_cr6 >> 1 & 1)) {
    uVar1 = (uint)*(short *)(unaff_r31 + 0x1c);
    uStack0000005e = 0;
    uStack00000057 = 0x10;
    FUN_8238b6b0(0xb0045,((int)*(short *)(unaff_r31 + 0x18) -
                         (((int)uVar1 >> 1) + (uint)((int)uVar1 < 0 && (uVar1 & 1) != 0))) + -7,
                 (int)*(short *)(unaff_r31 + 0x1a),2);
    uVar1 = (uint)*(short *)(unaff_r31 + 0x1c);
    uStack0000005e = 6;
    uStack00000057 = 0x10;
    FUN_8238b6b0(0xb0046,((int)*(short *)(unaff_r31 + 0x18) -
                         (((int)uVar1 >> 1) + (uint)((int)uVar1 < 0 && (uVar1 & 1) != 0))) + -7,
                 (int)*(short *)(unaff_r31 + 0x1a),2);
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

