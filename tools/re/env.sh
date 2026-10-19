# env.sh — source this: sets up Ghidra + JDK + bench tools on PATH.
# Usage: source tools/re/env.sh
_RE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_VERSION="$(cat "$_RE_DIR/GHIDRA-VERSION" | tr -d '[:space:]')"

# VM layout (persistent): ~/workspace/tools/ghidra/
if [ -d "$HOME/workspace/tools/ghidra/ghidra_${_VERSION}_PUBLIC" ]; then
  export GHIDRA_HOME="$HOME/workspace/tools/ghidra/ghidra_${_VERSION}_PUBLIC"
  export JAVA_HOME="$HOME/workspace/tools/ghidra/jdk-21.0.12.1+1"
# Repo-local layout (after ./fetch-ghidra.sh)
elif [ -d "$_RE_DIR/vendor/ghidra_${_VERSION}_PUBLIC" ]; then
  export GHIDRA_HOME="$_RE_DIR/vendor/ghidra_${_VERSION}_PUBLIC"
  export JAVA_HOME="$_RE_DIR/vendor/jdk-21.0.12.1+1"
else
  echo "Ghidra not found. Run tools/re/fetch-ghidra.sh first." >&2
  return 1 2>/dev/null || exit 1
fi

export PATH="$JAVA_HOME/bin:$GHIDRA_HOME/support:$PATH"
# Bench CLI tools (VM layout)
export PATH="$HOME/workspace/tools/p7zip/extracted/usr/bin:$PATH"

echo "GHIDRA_HOME=$GHIDRA_HOME"
java -version 2>&1 | head -1
