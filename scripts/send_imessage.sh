#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/../.env}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

default_to="${IMESSAGE_TO:-}"

if [[ -n "${default_to}" && -n "${1:-}" && -z "${2:-}" ]]; then
  to="$default_to"
  msg="$1"
else
  to="${1:-$default_to}"
  msg="${2:-}"
fi

if [[ -z "$to" || -z "$msg" ]]; then
  echo "Usage: $0 [phone_or_email] <message>"
  exit 1
fi

to_escaped=${to//"/\\"}
msg_escaped=${msg//"/\\"}

osascript <<APPLESCRIPT
tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "$to_escaped" of targetService
  send "$msg_escaped" to targetBuddy
end tell
APPLESCRIPT
