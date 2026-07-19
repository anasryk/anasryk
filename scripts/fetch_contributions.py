"""
Scrapes the public (no-auth) contribution calendar GitHub serves at
https://github.com/users/<username>/contributions and writes
data/contributions.json with raw days + derived stats.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "anasryk"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html():
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Current GitHub markup: <td data-date="YYYY-MM-DD" data-level="0-4">
    cells = soup.select("td[data-date]")
    if cells:
        for td in cells:
            date_str = td.get("data-date")
            level = td.get("data-level")
            level = int(level) if level is not None else 0
            count = 0
            tooltip_id = td.get("id")
            if tooltip_id:
                tt = soup.find("tool-tip", attrs={"for": tooltip_id})
                if tt and tt.text:
                    first_tok = tt.text.strip().split(" ")[0].replace(",", "")
                    if first_tok.isdigit():
                        count = int(first_tok)
            days.append({"date": date_str, "level": level, "count": count})
    else:
        # Fallback for older <rect> markup
        for rect in soup.select("rect.ContributionCalendar-day"):
            date_str = rect.get("data-date")
            level = int(rect.get("data-level", 0))
            days.append({"date": date_str, "level": level, "count": 0})

    days = [d for d in days if d["date"]]
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    if total == 0:
        # tooltip text isn't always parseable; fall back to level-weighted estimate
        total = sum(d["level"] for d in days)

    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0 or d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = running = 0
    for d in days:
        if d["level"] > 0 or d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": dict(monthly),
    }


def main():
    html = fetch_html()
    days = parse_days(html)
    if not days:
        print("No contribution days parsed — GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)
    out = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "days": days,
        "stats": stats,
    }
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(days)} days, total={stats['total']}")


if __name__ == "__main__":
    main()
