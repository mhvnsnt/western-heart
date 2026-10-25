#!/usr/bin/env bash
# autosave.sh — Claude Code hook: commit + push unfinished work so it is never
# stranded on a local disk when a session hits its usage limit / ends / compacts.
# Safe by design: never force-pushes, never deletes, never touches main/gh-pages
# directly, never blocks Claude (always exits 0). See docs in CLAUDE.md.
set -u
INPUT="$(cat 2>/dev/null || true)"
EVENT="$(printf '%s' "$INPUT" | sed -n 's/.*"hook_event_name"[[:space:]]*:[[:space:]]*"\([A-Za-z]*\)".*/\1/p' | head -1)"
EVENT="${EVENT:-${1:-manual}}"
DIR="$(printf '%s' "$INPUT" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
cd "${DIR:-${CLAUDE_PROJECT_DIR:-.}}" 2>/dev/null || exit 0
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
GD="$(git rev-parse --git-dir)"
LOG="$GD/autosave.log"
log(){ echo "$(date '+%F %T %Z') [$EVENT] $*" >>"$LOG"; }
[ "${AUTOSAVE_DISABLE:-0}" = 1 ] && exit 0

# one run at a time
LOCK="$GD/autosave.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  # stale lock (>10 min) is cleared; otherwise another run is active
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +10 2>/dev/null)" ]; then rmdir "$LOCK" 2>/dev/null; mkdir "$LOCK" 2>/dev/null || exit 0; else exit 0; fi
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# never mid-merge/rebase, never from a sparse/partial tree (AGENTS.md rule)
for f in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD rebase-merge rebase-apply; do [ -e "$GD/$f" ] && { log "skip: $f in progress"; exit 0; }; done
[ "$(git config --get core.sparseCheckout)" = true ] && { log "skip: sparse checkout"; exit 0; }

# PostToolUse fires constantly: debounce to once per AUTOSAVE_MIN_INTERVAL s (default 600)
STAMP="$GD/autosave.last"
if [ "$EVENT" = PostToolUse ] && [ -f "$STAMP" ]; then
  age=$(( $(date +%s) - $(cat "$STAMP" 2>/dev/null || echo 0) ))
  [ "$age" -lt "${AUTOSAVE_MIN_INTERVAL:-600}" ] && exit 0
fi

[ -z "$(git status --porcelain 2>/dev/null)" ] && [ -z "$(git log '@{u}..' --oneline 2>/dev/null)" ] && exit 0

BR="$(git symbolic-ref --short -q HEAD || true)"
if [ -z "$BR" ]; then log "skip: detached HEAD"; exit 0; fi
if [ "$BR" = main ] || [ "$BR" = master ] || [ "$BR" = gh-pages ]; then
  NEW="claude/autosave-$(date +%Y%m%d-%H%M%S)"
  git switch -q -c "$NEW" || { log "could not create $NEW"; exit 0; }
  log "was on $BR, moved work to $NEW"; BR="$NEW"
fi

if [ -n "$(git status --porcelain)" ]; then
  git add -A -- . 2>>"$LOG" || { log "git add failed"; exit 0; }
  # never delete: unstage every deletion (files stay as they are on disk)
  git diff --cached --name-only --diff-filter=D -z | xargs -0 -r git reset -q -- 2>/dev/null
  # skip files over 100 MB unless LFS-tracked
  git diff --cached --name-only --diff-filter=AM -z | while IFS= read -r -d '' f; do
    [ -f "$f" ] || continue
    sz=$(stat -c %s "$f" 2>/dev/null || stat -f %z "$f" 2>/dev/null || echo 0)
    if [ "$sz" -gt 104857600 ] && [ "$(git check-attr filter -- "$f" | awk '{print $NF}')" != lfs ]; then
      git reset -q -- "$f"; log "skipped >100MB non-LFS: $f"
    fi
  done
  if ! git diff --cached --quiet; then
    # secret scan of staged changes; abort commit on any finding
    if command -v gitleaks >/dev/null 2>&1; then
      if ! gitleaks protect --staged --redact --no-banner >>"$LOG" 2>&1; then
        git reset -q; log "ABORT: gitleaks findings, nothing committed"; exit 0
      fi
    else
      if git diff --cached -U0 | grep -E '^\+' | grep -qE '(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{32,}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[0-9]{8,10}:AA[A-Za-z0-9_-]{30,})'; then
        git reset -q; log "ABORT: secret pattern found (gitleaks not installed), nothing committed"; exit 0
      fi
      log "warn: gitleaks not installed, used fallback regex scan"
    fi
    git -c user.name=mhvnsnt -c user.email=197314870+mhvnsnt@users.noreply.github.com \
      commit -q --no-verify -m "wip(autosave): $(date '+%F %T %Z') [$EVENT]" -m "Auto-saved by tools/agent/autosave.sh so work is not stranded locally. No deletions staged." >>"$LOG" 2>&1 \
      && log "committed on $BR"
  fi
fi

date +%s >"$STAMP"
# plain push, never force; background-safe with a timeout
if command -v timeout >/dev/null 2>&1; then T="timeout ${AUTOSAVE_PUSH_TIMEOUT:-50}"; else T=""; fi
if $T git push -q -u origin "HEAD:refs/heads/$BR" >>"$LOG" 2>&1; then log "pushed $BR"; else log "push failed for $BR (left committed locally; next run retries)"; fi
exit 0
