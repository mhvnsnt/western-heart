#!/bin/bash
# loop.sh n...  : per PR, up to 4 rounds of (merge main in, wait CI, merge if main unchanged)
cd /workspace/sweep
for n in "$@"; do b=$(gh pr view $n -R mhvnsnt/money-machine-hq --json headRefName -q .headRefName)
 for round in 1 2 3 4; do
  (cd mm.git && git fetch -q origin 2>/dev/null)
  out=$(timeout 300 ./step1.sh mm.git $n $b 2>&1 | tail -1); echo "$(date +%T) $out"
  case "$out" in *PUSHED*|*UPTODATE*) c=$(echo $out|awk '{print $3}');; *) break;; esac
  sleep 120
  for i in $(seq 1 40); do o=$(gh api "repos/mhvnsnt/money-machine-hq/commits/$c/check-runs?per_page=100" -q '[.check_runs[]|(.conclusion//.status)]|unique|join(",")' 2>/dev/null); case "$o" in *in_progress*|*queued*) sleep 30;; "") [ $i -gt 4 ] && break; sleep 30;; *) break;; esac; done
  echo "$(date +%T) $n checks: $o"
  case "$o" in *failure*|*cancelled*|*timed_out*) break;; esac
  (cd mm.git && git fetch -q origin 2>/dev/null; git merge-base --is-ancestor main $c) || continue
  d=$(cd mm.git && git diff --diff-filter=D --name-only main $c | wc -l); [ "$d" = 0 ] || { echo "$n DEL"; break; }
  gh pr merge $n -R mhvnsnt/money-machine-hq --merge --match-head-commit $c 2>&1 | tail -1
  echo "$(date +%T) $n RESULT $(gh pr view $n -R mhvnsnt/money-machine-hq --json state -q .state)"; break
 done
done
