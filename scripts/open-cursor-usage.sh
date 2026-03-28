#!/usr/bin/env bash
# Opens Cursor account / settings in the default browser (no credentials stored or sent).
# Override URL: CURSOR_USAGE_URL='https://cursor.com' ./scripts/open-cursor-usage.sh
set -euo pipefail
URL="${CURSOR_USAGE_URL:-https://cursor.com/settings}"

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open "$URL"
else
  printf 'No xdg-open/open found. Open this URL manually:\n%s\n' "$URL"
  exit 1
fi
