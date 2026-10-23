// FUN_00b896d8 @ Ghidra 00b896d8 / true VA 827896d8

void FUN_00b896d8(short *param_1,int param_2,int param_3)

{
  short sVar1;
  
  if (param_3 == 0) {
    return;
  }
  param_2 = param_2 - (int)param_1;
  do {
    sVar1 = *(short *)(param_2 + (int)param_1);
    if (sVar1 == 0) break;
    *param_1 = sVar1;
    param_3 = param_3 + -1;
    param_1 = param_1 + 1;
  } while (param_3 != 0);
  if (param_3 != 0) {
    *param_1 = 0;
    return;
  }
  param_1[-1] = 0;
  return;
}

