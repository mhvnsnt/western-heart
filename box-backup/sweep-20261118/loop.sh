#!/bin/bash
# loop.sh n...  : per PR, up to 4 rounds of (merge main in, wait CI, merge if main unchanged)
cd /workspace/sweep
for n in "$@"; do b=$(awk -F'\t' -v n=$n '$1==n{print $2}' wh.tsv)
 for round in 1 2 3 4; do
  (cd wh.git && git fetch -q origin 2>/dev/null)
  out=$(timeout 300 ./step1.sh wh.git $n $b 2>&1 | tail -1); echo "$(date +%T) $out"
  case "$out" in *PUSHED*|*UPTODATE*) c=$(echo $out|awk '{print $3}');; *) break;; esac
  sleep 120
  for i in $(seq 1 40); do o=$(gh api "repos/mhvnsnt/western-heart/commits/$c/check-runs?per_page=100" -q '[.check_runs[]|(.conclusion//.status)]|unique|join(",")' 2>/dev/null); case "$o" in *in_progress*|*queued*|"") sleep 30;; *) break;; esac; done
  echo "$(date +%T) $n checks: $o"
  case "$o" in *failure*|*cancelled*|*timed_out*) break;; esac
  (cd wh.git && git fetch -q origin 2>/dev/null; git merge-base --is-ancestor main $c) || continue
  d=$(cd wh.git && git diff --diff-filter=D --name-only main $c | wc -l); [ "$d" = 0 ] || { echo "$n DEL"; break; }
  gh pr merge $n -R mhvnsnt/western-heart --merge --match-head-commit $c 2>&1 | tail -1
  echo "$(date +%T) $n RESULT $(gh pr view $n -R mhvnsnt/western-heart --json state -q .state)"; break
 done
done
