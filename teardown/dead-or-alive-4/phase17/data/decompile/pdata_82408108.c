// function FUN_82408108 entry 82408108 body 82408108-8240816b

/* WARNING: Control flow encountered bad instruction data */

void FUN_82408108(int param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5,
                 int param_6,int param_7,undefined2 param_8)

{
  int in_r11;
  int unaff_r24;
  undefined2 unaff_r25;
  undefined2 unaff_r26;
  undefined1 unaff_r27;
  undefined1 unaff_r28;
  double in_f0;
  
  *(undefined1 *)(param_6 + param_1) = unaff_r28;
  *(float *)(unaff_r24 + param_5) = (float)in_f0;
  *(undefined1 *)(param_7 + 0x6b44 + param_1) = unaff_r27;
  *(undefined2 *)(in_r11 + param_4 + -0x77e0) = param_8;
  *(undefined2 *)(&DAT_830a6aac + in_r11) = param_8;
  *(undefined2 *)(&DAT_830a77a8 + in_r11) = unaff_r25;
  *(undefined2 *)(&DAT_830a7b1c + in_r11) = unaff_r26;
  (&DAT_830a6a9c)[param_1] = 3;
  (&DAT_830a7d28)[param_1] = 1;
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

