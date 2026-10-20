// LD_PRELOAD shim: strip SDL_INIT_AUDIO from SDL_Init so PPSSPP can run headless.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>

typedef int (*sdl_init_t)(uint32_t);
static sdl_init_t real_init = 0;

int SDL_Init(uint32_t flags) {
    if (!real_init) real_init = (sdl_init_t)dlsym(RTLD_NEXT, "SDL_Init");
    flags &= ~(uint32_t)0x10;  // strip SDL_INIT_AUDIO
    return real_init(flags);
}
// SDL3 variant
int SDL_InitSubSystem(uint32_t flags) {
    typedef int (*f)(uint32_t);
    static f real_sub = 0;
    if (!real_sub) real_sub = (f)dlsym(RTLD_NEXT, "SDL_InitSubSystem");
    flags &= ~(uint32_t)0x10;
    return real_sub(flags);
}
