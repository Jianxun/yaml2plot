#!/usr/bin/env bash
set -euo pipefail

#WEBHOOK_URL="http://localhost:5678/webhook-test/1231ab0c-63fb-4fa7-98b9-1cef53d5389c"
WEBHOOK_URL="http://localhost:5678/webhook/1231ab0c-63fb-4fa7-98b9-1cef53d5389c"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"message text\""
  exit 1
fi

msg="$1"

curl -sS -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$msg\",\"user\":\"me\"}"
