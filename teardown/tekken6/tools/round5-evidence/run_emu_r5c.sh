#!/bin/bash
# Round-5 attempt-3 PPSSPP launcher: Xvfb on :82 owned by r5c_driver.
cd ~/workspace/_t6r4-work
L=$PWD/ppsspp/squashfs-root/shared/lib
export HOME=$PWD/home DISPLAY=:82 SDL_AUDIODRIVER=dummy LD_PRELOAD=$PWD/sdl_noaudio.so
exec $L/ld-linux-x86-64.so.2 --library-path $L ./run/PPSSPPSDL \
  --windowed --xres 480 --yres 272 iso/tekken6-psp.iso
