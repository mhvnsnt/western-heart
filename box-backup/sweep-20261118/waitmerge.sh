#!/bin/bash
# waitmerge.sh n... : wait for latest checks (gh pr checks) all pass, require 0 behind main and no deletions, merge commit.
for n in "$@"; do
 for i in $(seq 1 60); do
  st=$(gh pr checks $n -R mhvnsnt/western-heart 2>/dev/null | awk -F'\t' '{print $2}' | sort -u | tr '\n' ,)
  case "$st" in *pending*|"") sleep 30; continue;; esac; break; done
 echo "$(date +%T) $n checks: $st"
 [ "$st" = "pass," ] || { echo "$n NOT-GREEN"; continue; }
 j=$(gh pr view $n -R mhvnsnt/western-heart --json headRefOid,baseRefName,headRefName)
 c=$(echo "$j"|jq -r .headRefOid); h=$(echo "$j"|jq -r .headRefName)
 behind=$(gh api repos/mhvnsnt/western-heart/compare/main...$c -q .behind_by)
 dels=$(gh api repos/mhvnsnt/western-heart/compare/main...$c -q '[.files[]|select(.status=="removed")]|length')
 echo "$(date +%T) $n behind=$behind dels=$dels"
 [ "$behind" = 0 ] && [ "$dels" = 0 ] || { echo "$n SKIP"; continue; }
 gh pr merge $n -R mhvnsnt/western-heart --merge --match-head-commit $c 2>&1 | tail -1; echo "$(date +%T) $n MERGED?"
done
