// function FUN_824f3880 entry 824f3880 body 824f3880-824f3ad3

/* WARNING: Control flow encountered bad instruction data */

void FUN_824f3880(void)

{
  char cVar3;
  int *piVar1;
  int iVar2;
  int in_r8;
  int in_r9;
  int iVar4;
  uint uVar5;
  int unaff_r15;
  int unaff_r16;
  int unaff_r17;
  int unaff_r18;
  int unaff_r19;
  undefined2 unaff_r20;
  int unaff_r22;
  undefined1 unaff_r23;
  int unaff_r24;
  uint unaff_r25;
  int unaff_r26;
  int unaff_r27;
  double dVar6;
  double unaff_f27;
  
  *(undefined1 *)(unaff_r27 + in_r9) = unaff_r23;
  *(undefined1 *)(unaff_r27 + in_r8) = unaff_r23;
  if ((*(char *)(unaff_r24 + 0x40) == '\x01') && (*(char *)(unaff_r27 + unaff_r26 + 0xd4) == '\0'))
  {
    if (((*(char *)(unaff_r24 + 0x66) == '\x02') || (*(char *)(unaff_r24 + 0x66) == '\x04')) &&
       (*(char *)(unaff_r27 + unaff_r26 + 0x95) == '\x01')) {
      cVar3 = *(char *)(unaff_r27 + unaff_r26 + 0x96);
      if (cVar3 == '\x01') {
        *(char *)(unaff_r24 + 0x3e) = (char)unaff_r20;
      }
      else if (cVar3 == '\x02') {
        *(undefined1 *)(unaff_r24 + 0x3e) = unaff_r23;
      }
      cVar3 = *(char *)(unaff_r24 + 0x49);
      iVar4 = *(int *)(unaff_r27 + unaff_r26 + 0xa8) + -0x4000;
      *(int *)(unaff_r24 + 0x14) = iVar4;
      if (((((cVar3 != '\x01') && (cVar3 != '\x04')) && (cVar3 != '\x06')) &&
          ((cVar3 != '\t' && (cVar3 != '\v')))) && ((cVar3 != '\r' && (cVar3 != '\x0f')))) {
        *(int *)(unaff_r24 + 0x14) = iVar4 + unaff_r19;
      }
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    if (*(char *)(unaff_r27 + unaff_r26 + 0x28) == '\x01') {
      *(int *)(unaff_r24 + 0x14) = *(int *)(unaff_r24 + 0x70) + unaff_r19;
    }
    else {
      *(undefined4 *)(unaff_r24 + 0x14) = *(undefined4 *)(unaff_r24 + 0x70);
    }
    *(undefined4 *)(unaff_r24 + 0x1c) = *(undefined4 *)(unaff_r24 + 0x14);
  }
  if (*(char *)(unaff_r24 + 0x66) != '\x04') {
    *(undefined2 *)(unaff_r27 + unaff_r26 + 0xdc) = unaff_r20;
  }
  *(undefined1 *)(unaff_r27 + unaff_r26 + 5) = unaff_r23;
  if (*(char *)(unaff_r27 + unaff_r26 + 0x7a) == '\0') {
    *(undefined1 *)(unaff_r27 + unaff_r26 + 0xcc) = unaff_r23;
  }
  while( true ) {
    do {
      do {
        do {
          unaff_r25 = unaff_r25 + 1 & 0xff;
          if (1 < unaff_r25) {
            FUN_829fe188();
                    /* WARNING: Bad instruction - Truncating control flow here */
            halt_baddata();
          }
          iVar4 = unaff_r25 * 0x9c + unaff_r22;
        } while (((*(char *)(iVar4 + 0x44) == '\x01') &&
                 (((*(char *)(iVar4 + 0x37) == '\n' || (*(char *)(iVar4 + 0x37) == '\v')) &&
                  (*(char *)(iVar4 + 0x66) != '\x02')))) &&
                ((*(char *)(iVar4 + 0x66) != '\x04' &&
                 (cVar3 = FUN_82507060(unaff_r25), cVar3 != '\0'))));
        uVar5 = (uint)*(byte *)(unaff_r16 + -0x6fd9);
        if (*(byte *)(uVar5 + unaff_r18) < 0x33) {
          piVar1 = *(int **)(((uint)*(byte *)(uVar5 + unaff_r18) * 2 + uVar5) * 4 + unaff_r15);
        }
        else {
          piVar1 = *(int **)(uVar5 * 4 + unaff_r15);
        }
        iVar2 = (**(code **)(*piVar1 + 0xec))(piVar1,*(undefined1 *)(unaff_r17 + -0x7059));
      } while (iVar2 != 0);
      uVar5 = (uint)*(byte *)(unaff_r16 + -0x6fd9);
      if (*(byte *)(uVar5 + unaff_r18) < 0x33) {
        piVar1 = *(int **)(((uint)*(byte *)(uVar5 + unaff_r18) * 2 + uVar5) * 4 + unaff_r15);
      }
      else {
        piVar1 = *(int **)(uVar5 * 4 + unaff_r15);
      }
      iVar2 = (**(code **)(*piVar1 + 0xf4))(piVar1,*(undefined1 *)(unaff_r17 + -0x7059));
    } while (iVar2 != 0);
    if ((*(char *)(iVar4 + 0x44) == '\x01') || (*(char *)(iVar4 + 0x44) == '\x04')) break;
    iVar4 = FUN_824f3c08(unaff_r25);
    if (iVar4 != 0) {
      func_0x82509170(unaff_r25);
    }
  }
  iVar2 = unaff_r25 * 0x250;
  dVar6 = (double)(*(float *)(iVar4 + 0x7c) - *(float *)(iVar2 + unaff_r26 + 0xf8));
  if ((dVar6 < unaff_f27) || (NAN(dVar6) || NAN(unaff_f27))) {
    *(undefined1 *)(iVar4 + 0x3a) = unaff_r23;
  }
  else {
    *(char *)(iVar4 + 0x3a) = (char)unaff_r20;
  }
                    /* WARNING: Subroutine does not return */
  FUN_829fa428(-(double)(*(float *)(iVar4 + 0x8c) - *(float *)(iVar2 + unaff_r26 + 0xfc)),
               (double)(*(float *)(iVar4 + 0x84) - *(float *)(iVar2 + unaff_r26 + 0xf4)));
}

