// function FUN_823fa3d0 entry 823fa3d0 body 823fa3d0-823fa4db

/* WARNING: Control flow encountered bad instruction data */

void FUN_823fa3d0(void)

{
  char cVar1;
  int *piVar2;
  char *pcVar3;
  int in_r8;
  int in_r9;
  char *pcVar4;
  uint uVar5;
  uint in_r11;
  int iVar6;
  char *pcVar7;
  int *piVar8;
  int *unaff_r31;
  
  if ((in_r9 == in_r8) && ((in_r11 & 0x2000) == 0)) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  uVar5 = 0;
  piVar2 = unaff_r31;
  do {
    piVar8 = piVar2;
    if (*piVar8 == 2) break;
    uVar5 = uVar5 + 0x1c;
    piVar2 = piVar8 + 7;
  } while (uVar5 < 0x118);
  iVar6 = 0;
  do {
    cVar1 = *(char *)((int)&PTR_DAT_82e2cdf4 + iVar6);
    (&stack0x00000050)[iVar6] = cVar1;
    iVar6 = iVar6 + 1;
  } while (cVar1 != '\0');
  pcVar4 = ":\\anm.afs";
  pcVar3 = &stack0x00000050;
  do {
    pcVar7 = pcVar3;
    pcVar3 = pcVar7 + 1;
  } while (*pcVar7 != '\0');
  do {
    cVar1 = *pcVar4;
    pcVar4 = pcVar4 + 1;
    *pcVar7 = cVar1;
    pcVar7 = pcVar7 + 1;
  } while (cVar1 != '\0');
  FUN_829b6a78(*piVar8,&stack0x00000050,0,piVar8[1]);
  do {
    uVar5 = 0;
    piVar2 = unaff_r31;
    do {
      piVar8 = piVar2;
      if (*piVar8 == 2) break;
      uVar5 = uVar5 + 0x1c;
      piVar2 = piVar8 + 7;
    } while (uVar5 < 0x118);
    iVar6 = FUN_829b69b8(*piVar8);
    if (iVar6 == 3) {
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
  } while( true );
}

