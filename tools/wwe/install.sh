#!/usr/bin/env bash
# Build the ooz (Oodle Kraken-compatible) helper for the 2K19 toolchain.
# Clones zao/ooz, builds it, and leaves liblibooz.so + the ooz CLI next
# to the tools so oodle_krk.py can find them. Only needed for OODL
# (Oodle Kraken) chunks; everything else works without it.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ooz ]; then
  git clone --depth 1 https://github.com/zao/ooz.git ooz
fi
# ooz needs the simde headers (its submodule); the clone above is
# shallow, so fetch the submodule too.
git -C ooz submodule update --init --depth 1 2>/dev/null || true

cmake -S ooz -B ooz/build -DCMAKE_BUILD_TYPE=Release \
  -DOOZ_BUILD_BUN=OFF -DOOZ_BUILD_VALIDATE=OFF
cmake --build ooz/build -j"$(nproc)"

cp ooz/build/liblibooz.so . 2>/dev/null || cp ooz/build/*.so . 2>/dev/null || true
cp ooz/build/ooz . 2>/dev/null || true
echo "ooz built. liblibooz.so + ooz CLI are in $(pwd)"
python3 -c "import oodle_krk; print('oodle_krk OK:', oodle_krk.available())"
