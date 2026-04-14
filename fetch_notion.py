#!/usr/bin/env python3
"""
Fetches the Data Engineering Dashboard table from Notion
and regenerates index.html with the latest data.

Required env var: NOTION_TOKEN  (Notion internal integration token)
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import requests

# ── Config ────────────────────────────────────────────────────────────────────
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    sys.exit("ERROR: NOTION_TOKEN environment variable is not set.")

PAGE_ID = "3255356b-3971-800c-8d31-f10c0ea77747"  # Data Engineering Dashboard

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# Column order in the Notion table
COL_TEAM  = 0
COL_NAME  = 1
COL_START = 2
COL_END   = 3


# ── Notion helpers ─────────────────────────────────────────────────────────────
def get_block_children(block_id: str) -> list:
    """Fetch all children blocks for a given block ID (handles pagination)."""
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    results = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return results


def rich_text_to_str(rich_text_list: list) -> str:
    """Flatten a Notion rich-text array to a plain string."""
    return "".join(t.get("plain_text", "") for t in rich_text_list)


# ── Data extraction ────────────────────────────────────────────────────────────
def fetch_table_data() -> list[dict]:
    """
    Walk the page's blocks, find the first table block,
    and return its rows (skipping the header) as a list of dicts.
    """
    print(f"Fetching page blocks for {PAGE_ID} ...")
    blocks = get_block_children(PAGE_ID)

    rows = []
    for block in blocks:
        if block.get("type") != "table":
            continue

        print(f"  Found table block {block['id']}, fetching rows ...")
        table_rows = get_block_children(block["id"])
        header_skipped = False

        for row_block in table_rows:
            if row_block.get("type") != "table_row":
                continue
            cells = row_block["table_row"]["cells"]

            # Skip the header row
            if not header_skipped:
                header_skipped = True
                continue

            if len(cells) < 4:
                continue

            team  = rich_text_to_str(cells[COL_TEAM]).strip()
            name  = rich_text_to_str(cells[COL_NAME]).strip()
            start = rich_text_to_str(cells[COL_START]).strip()
            end   = rich_text_to_str(cells[COL_END]).strip()

            # Basic validation: skip blank or malformed rows
            if not (team and name and start and end):
                continue

            rows.append({"team": team, "name": name, "start": start, "end": end})

        break  # Only process the first table

    print(f"  Extracted {len(rows)} implementation rows.")
    return rows


# ── HTML generation ────────────────────────────────────────────────────────────
def update_html(rows: list[dict]) -> None:
    """Replace the __NOTION_DATA__ and __LAST_REFRESHED__ placeholders in index.html."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    data_json = json.dumps(rows, indent=2, ensure_ascii=False)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    # Replace data placeholder (handles both first-run template and re-runs)
    html = re.sub(
        r"const RAW = __NOTION_DATA__;",
        f"const RAW = {data_json};",
        html,
    )
    # If already replaced on a previous run, swap the old JSON array
    html = re.sub(
        r"const RAW = \[[\s\S]*?\];",
        f"const RAW = {data_json};",
        html,
    )

    # Replace timestamp placeholder
    html = re.sub(
        r'const LAST_REFRESHED = "__LAST_REFRESHED__";',
        f'const LAST_REFRESHED = "{timestamp}";',
        html,
    )
    # Update existing timestamp
    html = re.sub(
        r'const LAST_REFRESHED = ".*?";',
        f'const LAST_REFRESHED = "{timestamp}";',
        html,
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  index.html updated (timestamp: {timestamp}).")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rows = fetch_table_data()
    if not rows:
        sys.exit("ERROR: No rows were extracted from the Notion table. Aborting.")
    update_html(rows)
    print("Done.")
