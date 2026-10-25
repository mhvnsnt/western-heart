#!/usr/bin/env bash
# checkpoint.sh — Claude Code hook: back up EVERYTHING a container restart would wipe, to a remote ref.
#
# Owner 2026-10-25: "make something that saves all your progress and checkpoints ... so you stop losing your
# progress and your scratch pad on every restart". On 2026-10-25 a container restart wiped the repo working tree
# (reset to the last pushed commit) AND the session scratchpad: six lanes of uncommitted agent work were lost.
# autosave.sh only covers the repo, and only while HEAD is on a branch.
#
# Each run builds ONE commit with git plumbing (a temporary index; the working tree and the real index are never
# touched) and pushes it to  refs/heads/<branch>-checkpoints  (default: claude-checkpoints/<session>). That ref is a
# backup only: it is never merged and never PR'd. The commit holds:
#   repo/wip.patch          `git diff HEAD` (binary-safe) of the working tree, so it survives a detached HEAD too
#   repo/untracked/<path>   every untracked, non-ignored file under 20 MB, at its repo path
#   repo/HEAD               the commit the patch applies to
#   scratch/<path>          the session scratchpad, files under 20 MB (re-downloadable tool trees are skipped)
#   manifest.json           what was skipped, with the restore commands for the big tool downloads
# Restore with tools/agent/restore.sh (wired to SessionStart).
#
# Safe by design: never touches the working tree/index, never force-pushes, never deletes, gitleaks-scans the
# patch + untracked files (regex fallback) and skips the run on a finding, always exits 0.
set -u
INPUT="$(cat 2>/dev/null || true)"
EVENT="$(printf '%s' "$INPUT" | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p' | head -1)"
EVENT="${EVENT:-${1:-manual}}"
SID="$(printf '%s' "$INPUT" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
GD="$(git rev-parse --git-dir)"
LOG="$GD/checkpoint.log"
log(){ echo "$(date '+%F %T %Z') [$EVENT] $*" >>"$LOG"; }
[ "${CHECKPOINT_DISABLE:-0}" = 1 ] && exit 0

# PostToolUse fires constantly: at most one checkpoint per CHECKPOINT_MIN_INTERVAL seconds (default 300).
STAMP="$GD/checkpoint.last"
if [ "$EVENT" = PostToolUse ] && [ -f "$STAMP" ]; then
  age=$(( $(date +%s) - $(cat "$STAMP" 2>/dev/null || echo 0) ))
  [ "$age" -lt "${CHECKPOINT_MIN_INTERVAL:-300}" ] && exit 0
fi
LOCK="$GD/checkpoint.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  [ -n "$(find "$LOCK" -maxdepth 0 -mmin +15 2>/dev/null)" ] && { rmdir "$LOCK"; mkdir "$LOCK" 2>/dev/null || exit 0; } || exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null; rm -rf "${TMP:-/nonexistent}"' EXIT
date +%s >"$STAMP"

# The session scratchpad: /tmp/claude-<uid>/<project-slug>/<session-id>/scratchpad (CLAUDE_SCRATCHPAD overrides).
SCRATCH="${CLAUDE_SCRATCHPAD:-}"
if [ -z "$SCRATCH" ] && [ -n "$SID" ]; then SCRATCH="$(ls -d /tmp/claude-*/*/"$SID"/scratchpad 2>/dev/null | head -1)"; fi
if [ -z "$SCRATCH" ]; then SCRATCH="$(ls -dt /tmp/claude-*/*/*/scratchpad 2>/dev/null | head -1)"; fi
[ -n "$SID" ] || SID="$(basename "$(dirname "${SCRATCH:-/x/unknown/scratchpad}")")"

BR="$(git symbolic-ref --short -q HEAD || true)"
[ -z "$BR" ] && BR="$(cat "$GD/checkpoint.branch" 2>/dev/null || true)"   # remembered from the last attached run
[ -n "$BR" ] && [ "$BR" != main ] && [ "$BR" != gh-pages ] && echo "$BR" >"$GD/checkpoint.branch"
REF="refs/heads/${CHECKPOINT_REF:-${BR:-claude}-checkpoints}"
case "$BR" in main|gh-pages|"") REF="refs/heads/claude-checkpoints/${SID:-session}";; esac

TMP="$(mktemp -d)"
MAXB=$((20 * 1024 * 1024))
export GIT_INDEX_FILE="$TMP/index"
git read-tree --empty
add_file(){  # $1 = file on disk, $2 = path in the checkpoint tree
  local sz; sz=$(stat -c %s "$1" 2>/dev/null || echo 0)
  if [ "$sz" -gt "$MAXB" ]; then echo "$2 ($sz bytes)" >>"$TMP/skipped.txt"; return; fi
  local b; b=$(git hash-object -w -- "$1" 2>/dev/null) || return
  git update-index --add --cacheinfo "100644,$b,$2" 2>/dev/null
}

# 1. repo working tree vs HEAD (+ untracked files)
HEADC="$(git rev-parse HEAD)"
echo "$HEADC" >"$TMP/HEAD"; add_file "$TMP/HEAD" repo/HEAD
GIT_INDEX_FILE="$GD/index" git diff --binary HEAD >"$TMP/wip.patch" 2>/dev/null
[ -s "$TMP/wip.patch" ] && add_file "$TMP/wip.patch" repo/wip.patch
GIT_INDEX_FILE="$GD/index" git ls-files --others --exclude-standard -z | while IFS= read -r -d '' f; do
  [ -f "$f" ] && add_file "$f" "repo/untracked/$f"
done

# 2. secret scan of what leaves the machine (patch + untracked files); skip the whole run on a finding
SCAN="$TMP/scan"; mkdir -p "$SCAN"; cp "$TMP/wip.patch" "$SCAN/" 2>/dev/null
GIT_INDEX_FILE="$GD/index" git ls-files --others --exclude-standard -z | while IFS= read -r -d '' f; do
  [ -f "$f" ] && [ "$(stat -c %s "$f")" -lt "$MAXB" ] && mkdir -p "$SCAN/u/$(dirname "$f")" && cp "$f" "$SCAN/u/$f"
done
PAT='(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{32,}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|nfp_[A-Za-z0-9]{30,})'
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-git --source "$SCAN" --redact --no-banner >>"$LOG" 2>&1 || { log "ABORT: gitleaks finding, no checkpoint"; exit 0; }
elif grep -rqE "$PAT" "$SCAN" 2>/dev/null; then log "ABORT: secret pattern, no checkpoint"; exit 0; fi

# 3. the scratchpad (skip trees that restore.sh re-downloads; record them)
SKIP_DIRS='^(blender|blender5|ext|nodetools/node_modules|node_modules|bin)(/|$)'
if [ -n "$SCRATCH" ] && [ -d "$SCRATCH" ]; then
  ( cd "$SCRATCH" && find . -type f -print0 ) | while IFS= read -r -d '' f; do
    rel="${f#./}"
    if printf '%s' "$rel" | grep -qE "$SKIP_DIRS"; then continue; fi
    if printf '%s' "$rel" | grep -qE "$PAT"; then continue; fi
    add_file "$SCRATCH/$rel" "scratch/$rel"
  done
  if grep -rqE "$PAT" --include='*.txt' --include='*.json' --include='*.log' --include='*.md' --include='*.sh' --include='*.mjs' --include='*.py' "$SCRATCH" 2>/dev/null; then
    log "ABORT: secret pattern in scratchpad, no checkpoint"; exit 0
  fi
fi

# 4. manifest: the big re-downloadable tools restore.sh fetches again
cat >"$TMP/manifest.json" <<EOF
{
 "format": "wh-checkpoint/1",
 "time": "$(date -u +%FT%TZ)",
 "event": "$EVENT",
 "session": "$SID",
 "branch": "${BR:-}",
 "head": "$HEADC",
 "scratchpad": "${SCRATCH:-}",
 "skipped_over_20MB": $(python3 -c 'import json,sys; print(json.dumps([l.strip() for l in open(sys.argv[1])] if __import__("os").path.exists(sys.argv[1]) else []))' "$TMP/skipped.txt"),
 "redownload": [
  {"dir": "blender/blender-4.0.2-linux-x64", "url": "https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz", "note": "auto-rig pipeline (WH_BLENDER)"},
  {"dir": "blender5/blender-5.0.1-linux-x64", "url": "https://download.blender.org/release/Blender5.0/blender-5.0.1-linux-x64.tar.xz", "sha256": "8019580ee1b7262e505f4196a00237ccf743c88d205b38d34201510676e60b09", "note": "reads Blender 4.5/5.x .blend files (export_blend_static.py)"},
  {"dir": "ext/t3r", "git": "https://github.com/n0madic/Tekken3Remake", "note": "T3REMAKE_RESEARCH=<scratch>/ext/t3r/tools/research"},
  {"dir": "nodetools", "npm": "@gltf-transform/core @gltf-transform/extensions @gltf-transform/functions meshoptimizer", "note": "NODE_PATH for gltf_codec.mjs"}
 ]
}
EOF
add_file "$TMP/manifest.json" manifest.json

TREE="$(git write-tree)"
unset GIT_INDEX_FILE
PARENT="$(git ls-remote origin "$REF" 2>/dev/null | cut -f1)"
if [ -n "$PARENT" ]; then
  git fetch -q origin "$REF" 2>/dev/null
  [ "$(git rev-parse "$PARENT^{tree}" 2>/dev/null)" = "$TREE" ] && { log "unchanged, nothing to push"; exit 0; }
  P="-p $PARENT"
else P=""; fi
C="$(git -c user.name=mhvnsnt -c user.email=197314870+mhvnsnt@users.noreply.github.com commit-tree "$TREE" $P \
     -m "checkpoint: $(date '+%F %T %Z') [$EVENT] head ${HEADC:0:9}" -m "Backup of uncommitted repo work + the session scratchpad (tools/agent/checkpoint.sh). Never merged; restore with tools/agent/restore.sh.")" || exit 0
if timeout "${CHECKPOINT_PUSH_TIMEOUT:-90}" git push -q origin "$C:$REF" >>"$LOG" 2>&1; then log "pushed $C to $REF"; else log "push failed to $REF (next run retries)"; fi
exit 0
