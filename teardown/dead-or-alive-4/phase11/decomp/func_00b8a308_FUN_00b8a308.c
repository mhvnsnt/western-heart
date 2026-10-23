// FUN_00b8a308 @ Ghidra 00b8a308 / true VA 8278a308

int FUN_00b8a308(int *param_1)

{
  int iVar1;
  
  if (param_1 == (int *)0x0) {
    iVar1 = thunk_FUN_00b8d2c0(0x3e4);
    return iVar1;
  }
  if (*param_1 == 0x3e5) {
    return 0x3e4;
  }
  return param_1[6];
}

