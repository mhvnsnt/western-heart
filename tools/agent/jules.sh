#!/usr/bin/env bash
# Google Jules API helper. Needs JULES_API_KEY in env (never commit it).
# Usage:
#   jules.sh create <owner/repo> "<title>" "<prompt>" [branch=main]
#   jules.sh sessions [pageSize]
#   jules.sh session <id>
#   jules.sh activities <id> [pageSize]
#   jules.sh message <id> "<text>"
#   jules.sh approve <id>
#   jules.sh sources            (all pages)
set -euo pipefail
: "${JULES_API_KEY:?set JULES_API_KEY}"
API=https://jules.googleapis.com/v1alpha
j(){ curl -sS -H "X-Goog-Api-Key: $JULES_API_KEY" -H "Content-Type: application/json" "$@"; }
cmd=${1:-}; shift || true
case "$cmd" in
  create)
    repo=$1 title=$2 prompt=$3 branch=${4:-main}
    body=$(python3 -c 'import json,sys;r,t,p,b=sys.argv[1:];print(json.dumps({"prompt":p,"title":t,"sourceContext":{"source":"sources/github/"+r,"githubRepoContext":{"startingBranch":b}},"automationMode":"AUTO_CREATE_PR","requirePlanApproval":False}))' "$repo" "$title" "$prompt" "$branch")
    j -X POST "$API/sessions" -d "$body";;
  sessions) j "$API/sessions?pageSize=${1:-20}";;
  session) j "$API/sessions/$1";;
  activities) j "$API/sessions/$1/activities?pageSize=${2:-30}";;
  message) j -X POST "$API/sessions/$1:sendMessage" -d "$(python3 -c 'import json,sys;print(json.dumps({"prompt":sys.argv[1]}))' "$2")";;
  approve) j -X POST "$API/sessions/$1:approvePlan";;
  sources) t=""; while :; do r=$(j "$API/sources?pageSize=100&pageToken=$t"); echo "$r" | python3 -c 'import sys,json;[print(s["name"]) for s in json.load(sys.stdin).get("sources",[])]'; t=$(echo "$r"|python3 -c 'import sys,json;print(json.load(sys.stdin).get("nextPageToken",""))'); [ -z "$t" ] && break; done;;
  *) sed -n '2,11p' "$0"; exit 1;;
esac
