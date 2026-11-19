#!/bin/bash
# docres.sh n branch : merge main into branch; conflicted .md files resolved with union (keep both sides)
set -e; cd /workspace/sweep/wh.git; n=$1; b=$2
git fetch -q origin 2>/dev/null || true
out=$(git merge-tree --write-tree --name-only --no-messages main "$b") && { echo "$n NOCONF"; exit 0; } || true
tree=$(echo "$out"|head -1); files=$(echo "$out"|tail -n +2)
for f in $files; do case "$f" in *.md) ;; *) echo "$n NONDOC $f"; exit 1;; esac; done
base=$(git merge-base main "$b"); export GIT_INDEX_FILE=/tmp/idx.$n; rm -f $GIT_INDEX_FILE; git read-tree $tree
for f in $files; do d=$(mktemp -d)
 git show "$b:$f" > $d/o 2>/dev/null || : > $d/o; git show "$base:$f" > $d/b 2>/dev/null || : > $d/b; git show "main:$f" > $d/t 2>/dev/null || : > $d/t
 git merge-file --union -p $d/o $d/b $d/t > $d/r || true
 rg -q '^(<<<<<<<|>>>>>>>)' $d/r && { echo "$n MARKERS $f"; exit 1; }
 h=$(git hash-object -w $d/r); git update-index --cacheinfo 100644,$h,"$f"; done
t=$(git write-tree); unset GIT_INDEX_FILE
c=$(GIT_AUTHOR_NAME=mhvnsnt GIT_AUTHOR_EMAIL=197314870+mhvnsnt@users.noreply.github.com GIT_COMMITTER_NAME=mhvnsnt GIT_COMMITTER_EMAIL=197314870+mhvnsnt@users.noreply.github.com git commit-tree $t -p "$b" -p main -m "Merge main into $b (doc conflicts resolved: union, both sides kept)")
[ -z "$(git diff --diff-filter=D --name-only main $c)" ] || { echo "$n MERGEDEL"; exit 1; }
[ -z "$(git diff --diff-filter=D --name-only $b $c)" ] || { echo "$n DELVSBRANCH"; exit 1; }
gitleaks git --log-opts="-1 $c" . 2>&1 | tail -2; gitleaks git --log-opts="-1 $c" . >/dev/null 2>&1 || { echo "$n LEAKS"; exit 1; }
[ -n "$DRY" ] && { echo "$n WOULDPUSH $c"; exit 0; }
git push -q origin $c:refs/heads/$b && echo "$n PUSHED $c"
