// function FUN_824ebda8 entry 824ebda8 body 824ebda8-824ebf2b

/* WARNING: Control flow encountered bad instruction data */

void FUN_824ebda8(void)

{
  int iVar1;
  undefined2 in_r8;
  undefined1 in_r9;
  undefined4 in_r10;
  uint uVar2;
  int unaff_r28;
  int unaff_r29;
  undefined4 *unaff_r30;
  uint unaff_r31;
  undefined1 uVar3;
  undefined4 uStack00000060;
  undefined1 uStack00000065;
  undefined2 uStack00000068;
  undefined2 uStack0000006a;
  undefined1 uStack00000070;
  undefined1 uStack00000071;
  undefined1 uStack00000072;
  
  uStack0000006a = (undefined2)unaff_r31;
  uVar3 = (undefined1)unaff_r31;
  uStack00000060 = in_r10;
  uStack00000065 = in_r9;
  uStack00000068 = in_r8;
  uStack00000070 = uVar3;
  uStack00000071 = uVar3;
  uStack00000072 = uVar3;
  FUN_82305ce8(unaff_r29);
  func_0x82776bb0(0x82f3f68c);
  uRam830a947f = 1;
  uVar2 = 1;
  if (*(int *)(unaff_r29 + 0x4cc) == 0) {
    uVar2 = unaff_r31;
  }
  DAT_830ed4dc = unaff_r31;
  if ((uVar2 & 0xff) != 0) {
    DAT_830ed4dc = 1;
  }
  DAT_830ed4d4 = *unaff_r30;
  DAT_830ed4d8 = unaff_r30[1];
  uRam830ae286 = uVar3;
  uRam830ae287 = uVar3;
  DAT_830b64ca = uVar3;
  uRam830ed4e0 = unaff_r31;
  func_0x8277dff0(&DAT_83579a88,0x80000,0x200,0x1000,0x200,0x1000,0x200);
  if (iRam83579a70 == 0) {
    uRam83579a74 = 0x10000;
    iVar1 = iRam83579a70;
    do {
      iRam83579a70 = iVar1;
      iVar1 = uRam83579a74 << 4;
      if (0xfffffff < uRam83579a74) {
        iVar1 = unaff_r28;
      }
      iRam83579a70 = func_0x829fc500(iVar1,&DAT_82f58f18);
      if (iRam83579a70 != 0) break;
      uRam83579a74 = uRam83579a74 >> 1;
      iVar1 = 0;
    } while (uRam83579a74 != 0);
  }
  DAT_83579a78 = iRam83579a70;
  uRam83579a80 = unaff_r31;
  DAT_83579a84 = iRam83579a70;
  func_0x82471998(&DAT_82e5b6d0);
  func_0x8245c2b8(0x82e5b4d0);
  FUN_824521a8();
  func_0x8246fc28(&DAT_82e5b650,0x100,0x100);
  FUN_8247be48();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

