#!/bin/bash
set -e

REPO=/Users/margaret.agwuocha/data-engineering-dashboard
TOKEN_FILE=$HOME/.config/notion-token
LOG=$REPO/.refresh.log

cd "$REPO"

exec >> "$LOG" 2>&1
echo ""
echo "===== $(date) ====="

if [ ! -f "$TOKEN_FILE" ]; then
  echo "ERROR: Token file not found at $TOKEN_FILE"
  exit 1
fi
export NOTION_TOKEN=$(cat "$TOKEN_FILE")

export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin

.venv/bin/python fetch_notion.py

if git diff --quiet index.html; then
  echo "No changes to commit."
else
  git add index.html
  git commit -m "chore: scheduled refresh from Notion ($(date -u '+%Y-%m-%d'))"
  git push origin main
  echo "Pushed."
fi
