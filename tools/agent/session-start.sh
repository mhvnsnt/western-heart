#!/usr/bin/env bash
# SessionStart hook: push anything left over from the last session, then tell
# Claude (via stdout, which Claude Code adds to context) what is still unpushed.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
echo '{"hook_event_name":"SessionStart"}' | bash tools/agent/autosave.sh >/dev/null 2>&1
BR="$(git symbolic-ref --short -q HEAD)"
echo "Autosave is active in this repo (tools/agent/autosave.sh). Current branch: ${BR:-detached}."
LEFT="$(git status --porcelain | wc -l | tr -d ' ')"
[ "$LEFT" != 0 ] && echo "Still uncommitted after autosave: $LEFT paths (check .git/autosave.log). Commit and push them first."
echo "Rule: push every finished piece right away, keep generator scripts under tools/, open the PR after the first commit, reconcile via agent-ops CLAIMS.md. See CLAUDE.md."
exit 0
