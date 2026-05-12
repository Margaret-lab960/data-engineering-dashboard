#!/bin/bash
# Weekly dashboard refresh reminder.
# Shows a notification and opens Terminal with Claude Code in the repo.
# In the new window, type: refresh the dashboard

LOG=~/data-engineering-dashboard/.refresh.log
echo "$(date): firing weekly refresh reminder" >> "$LOG"

osascript <<'EOF'
display notification "Type 'refresh the dashboard' in the Claude window" with title "Weekly Dashboard Refresh" sound name "Glass"

tell application "Terminal"
    activate
    do script "cd ~/data-engineering-dashboard && claude"
end tell
EOF
