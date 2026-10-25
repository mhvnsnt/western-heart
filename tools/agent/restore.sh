#!/usr/bin/env bash
# restore.sh — SessionStart hook: bring back what a container restart wiped, from the newest checkpoint
# (tools/agent/checkpoint.sh). Owner 2026-10-25: "stop losing your progress and your scratch pad on every restart".
#
#   1. the session scratchpad: every file in the checkpoint's scratch/ that is missing on disk is written back
#      (files already on disk are left alone, so a live scratchpad is never overwritten);
#   2. uncommitted repo work: ONLY when the working tree is clean and HEAD is the checkpoint's HEAD (or contains
#      it), the checkpoint's repo/wip.patch is applied (3-way) and its untracked files are written back if absent;
#      otherwise it says what it found and leaves the tree alone (never clobbers);
#   3. big tool downloads listed in manifest.json (Blender 4.0.2 / 5.0.1, the T3 research clone, node tools) are
#      re-fetched in the background if their folder is missing.
# Prints a short report (SessionStart stdout goes into Claude's context). Always exits 0.
set -u
INPUT="$(cat 2>/dev/null || true)"
SID="$(printf '%s' "$INPUT" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
GD="$(git rev-parse --git-dir)"
[ "${CHECKPOINT_DISABLE:-0}" = 1 ] && exit 0

BR="$(git symbolic-ref --short -q HEAD || cat "$GD/checkpoint.branch" 2>/dev/null || true)"
SCRATCH="${CLAUDE_SCRATCHPAD:-}"
[ -z "$SCRATCH" ] && [ -n "$SID" ] && SCRATCH="$(ls -d /tmp/claude-*/*/"$SID"/scratchpad 2>/dev/null | head -1)"
[ -z "$SCRATCH" ] && SCRATCH="$(ls -dt /tmp/claude-*/*/*/scratchpad 2>/dev/null | head -1)"

# newest checkpoint ref: <branch>-checkpoints, else claude-checkpoints/<session>
REF=""
for r in "refs/heads/${BR:-none}-checkpoints" "refs/heads/claude-checkpoints/${SID:-none}"; do
  if timeout 30 git fetch -q origin "+$r:refs/checkpoint/latest" 2>/dev/null; then REF="$r"; break; fi
done
[ -z "$REF" ] && { echo "restore.sh: no checkpoint found for ${BR:-?} / ${SID:-?} (nothing to restore)."; exit 0; }
C="refs/checkpoint/latest"
WHEN="$(git log -1 --format=%ci "$C")"

# 1. scratchpad
NS=0
if [ -n "$SCRATCH" ]; then
  mkdir -p "$SCRATCH"
  while IFS= read -r p; do
    rel="${p#scratch/}"; dst="$SCRATCH/$rel"
    [ -e "$dst" ] && continue
    mkdir -p "$(dirname "$dst")" && git cat-file blob "$C:$p" >"$dst" 2>/dev/null && NS=$((NS + 1))
  done < <(git ls-tree -r --name-only "$C" -- scratch/ 2>/dev/null)
  case "$SCRATCH" in *) find "$SCRATCH" -name '*.sh' -exec chmod +x {} + 2>/dev/null;; esac
fi

# 2. repo work (never over a dirty tree)
CHEAD="$(git cat-file blob "$C:repo/HEAD" 2>/dev/null | tr -d '\n')"
REPO_MSG="no uncommitted repo work in the checkpoint"
if git cat-file -e "$C:repo/wip.patch" 2>/dev/null || [ -n "$(git ls-tree -r --name-only "$C" -- repo/untracked/ 2>/dev/null | head -1)" ]; then
  if [ -n "$(git status --porcelain)" ]; then
    REPO_MSG="checkpoint has uncommitted work but the tree is dirty: NOT applied (git show $C:repo/wip.patch)"
  elif [ -n "$CHEAD" ] && git merge-base --is-ancestor "$CHEAD" HEAD 2>/dev/null; then
    NU=0
    if git cat-file -e "$C:repo/wip.patch" 2>/dev/null; then
      git cat-file blob "$C:repo/wip.patch" >"$GD/restore-wip.patch"
      if git apply --3way --whitespace=nowarn "$GD/restore-wip.patch" 2>"$GD/restore-apply.log"; then AP="applied"; else AP="FAILED to apply cleanly (see $GD/restore-apply.log; patch kept at $GD/restore-wip.patch)"; fi
    else AP="no patch"; fi
    while IFS= read -r p; do
      rel="${p#repo/untracked/}"; [ -e "$rel" ] && continue
      mkdir -p "$(dirname "$rel")" && git cat-file blob "$C:$p" >"$rel" && NU=$((NU + 1))
    done < <(git ls-tree -r --name-only "$C" -- repo/untracked/ 2>/dev/null)
    git reset -q 2>/dev/null   # a 3-way apply may stage; leave everything as plain working-tree changes
    REPO_MSG="uncommitted work: patch $AP, $NU untracked files restored (checkpoint head ${CHEAD:0:9})"
  else
    REPO_MSG="checkpoint work is based on ${CHEAD:0:9}, not in HEAD's history: NOT applied (git show $C:repo/wip.patch)"
  fi
fi

# 3. big downloads, in the background, only when missing
if [ -n "$SCRATCH" ] && [ "${RESTORE_NO_DOWNLOAD:-0}" != 1 ] && git cat-file -e "$C:manifest.json" 2>/dev/null; then
  git cat-file blob "$C:manifest.json" >"$GD/restore-manifest.json"
  ( cd "$SCRATCH" && python3 - "$GD/restore-manifest.json" >>"$GD/restore-downloads.log" 2>&1 <<'PY'
import json, os, subprocess, sys, hashlib, tarfile, tempfile
m = json.load(open(sys.argv[1]))
for it in m.get("redownload", []):
    d = it["dir"]
    # npm trees: the folder can exist (restored small files) without its node_modules
    if os.path.exists(os.path.join(d, "node_modules") if "npm" in it else d): continue
    try:
        if "url" in it:
            os.makedirs(os.path.dirname(d) or ".", exist_ok=True)
            t = tempfile.mktemp(suffix=".tar.xz", dir=os.path.dirname(d) or ".")
            subprocess.run(["curl", "-sSL", "-o", t, it["url"]], check=True)
            if "sha256" in it and hashlib.sha256(open(t, "rb").read()).hexdigest() != it["sha256"]:
                print("sha256 mismatch", d); os.remove(t); continue
            with tarfile.open(t) as tf: tf.extractall(os.path.dirname(d) or ".")
            os.remove(t); print("restored", d)
        elif "git" in it:
            subprocess.run(["git", "clone", "-q", "--depth", "1", it["git"], d], check=True); print("restored", d)
        elif "npm" in it:
            os.makedirs(d, exist_ok=True)
            subprocess.run("npm init -y >/dev/null && npm install -s " + it["npm"], shell=True, cwd=d, check=True); print("restored", d)
    except Exception as e:
        print("failed", d, e)
PY
  ) &
fi

echo "restore.sh: checkpoint $REF ($WHEN): scratchpad $NS files restored to ${SCRATCH:-?}; $REPO_MSG; big tools re-downloading in the background if missing (log $GD/restore-downloads.log)."
exit 0
