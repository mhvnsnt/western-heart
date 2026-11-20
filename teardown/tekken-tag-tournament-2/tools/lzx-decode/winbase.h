#ifndef LZX_WINBASE_STUB
#define LZX_WINBASE_STUB
#include <stdlib.h>
#include <string.h>
static inline void* GetProcessHeap(void) { return NULL; }
static inline void* HeapAlloc(void* h, unsigned flags, size_t n) { (void)h; (void)flags; return malloc(n); }
static inline int HeapFree(void* h, unsigned flags, void* p) { (void)h; (void)flags; free(p); return 1; }
#endif
