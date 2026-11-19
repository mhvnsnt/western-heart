#!/bin/bash
# usage: step1.sh <repo.git> <num> <branch>  -> prints status line
cd "$1"; n=$2; b=$3
export GIT_AUTHOR_NAME=mhvnsnt GIT_AUTHOR_EMAIL=197314870+mhvnsnt@users.noreply.github.com GIT_COMMITTER_NAME=mhvnsnt GIT_COMMITTER_EMAIL=197314870+mhvnsnt@users.noreply.github.com
del=$(git diff --diff-filter=D --name-only main...$b | wc -l)
[ "$del" != 0 ] && { echo "$n DELETES $del"; exit; }
if git merge-base --is-ancestor main $b; then echo "$n UPTODATE $(git rev-parse $b)"; exit; fi
t=$(git merge-tree --write-tree main $b 2>/dev/null) || { echo "$n CONFLICT"; exit; }
t=$(echo "$t"|head -1)
c=$(git commit-tree $t -p $b -p main -m "Merge main into $b (PR sweep)")
[ "$(git diff --diff-filter=D --name-only main $c | wc -l)" != 0 ] && { echo "$n MERGEDEL"; exit; }
gl=$(gitleaks git --log-opts="-1 $c" . 2>&1 | tail -1)
echo "$gl" | grep -q "no leaks" || { echo "$n LEAKS"; exit; }
[ -n "$DRY" ] && { echo "$n WOULDPUSH"; exit; }
git push -q origin $c:refs/heads/$b 2>&1 | tail -1 && echo "$n PUSHED $c"
