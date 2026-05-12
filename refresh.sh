#!/bin/bash
set -e

REPO=/Users/margaret.agwuocha/data-engineering-dashboard
LOG=$REPO/.refresh.log

cd "$REPO"

exec >> "$LOG" 2>&1
echo ""
echo "===== $(date) ====="

export PATH=/Users/margaret.agwuocha/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin

claude -p \
  --add-dir "$REPO" \
  --dangerously-skip-permissions \
  --max-budget-usd 1.00 \
  "Refresh the data engineering dashboard from Notion.

Steps:
1. Use mcp__notionMCP__notion-fetch with id \"3255356b-3971-800c-8d31-f10c0ea77747\" to fetch the latest table data.
2. Read $REPO/index.html.
3. Compare the Notion table rows (team, name, start, end) against the existing 'const RAW = [...]' array. Update any rows whose start or end dates differ, add new rows, remove rows no longer in Notion. Keep the same one-object-per-line JSON format.
4. Update the LAST_REFRESHED constant to the current UTC timestamp formatted as 'Month D, YYYY at HH:MM UTC' (e.g. 'May 12, 2026 at 14:30 UTC').
5. If index.html changed, run from $REPO: git add index.html && git commit -m 'chore: scheduled refresh from Notion' && git push origin main.
6. If nothing changed, print 'no changes' and skip the commit.

Print a one-line summary of what changed."

echo "Done."
