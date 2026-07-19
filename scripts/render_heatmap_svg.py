"""
Reads data/contributions.json and draws the classic 53-week x 7-day
contribution grid as an SVG that reveals itself diagonally on load,
then freezes (no infinite looping).
"""
import json
from datetime import datetime, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 30


def load_data():
    with open("data/contributions.json") as f:
        return json.load(f)


def build_grid(days):
    by_date = {d["date"]: d for d in days}
    if not days:
        return []

    dates = sorted(by_date.keys())
    start = datetime.strptime(dates[0], "%Y-%m-%d")
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back up to Sunday
    end = datetime.strptime(dates[-1], "%Y-%m-%d")

    weeks, week, cur = [], [], start
    while cur <= end:
        key = cur.strftime("%Y-%m-%d")
        week.append(by_date.get(key, {"level": 0, "count": 0, "date": key}))
        if cur.weekday() == 5:  # Saturday closes the week
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append({"level": 0, "count": 0, "date": ""})
        weeks.append(week)
    return weeks


def render(weeks, stats):
    width = LEFT_PAD + len(weeks) * (CELL + GAP) + 140
    height = TOP_PAD + 7 * (CELL + GAP) + 60

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace">',
        f'<rect width="{width}" height="{height}" fill="#0d1117" rx="10"/>',
        "<style>",
        ".cell { opacity: 0; }",
        "@keyframes reveal { from { opacity: 0; transform: translate(-6px,-6px); } "
        "to { opacity: 1; transform: translate(0,0); } }",
        "</style>",
    ]

    delay_step = 0.012
    idx = 0
    for w, week in enumerate(weeks):
        for r, day in enumerate(week):
            level = day.get("level", 0)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + r * (CELL + GAP)
            delay = idx * delay_step
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" style="animation: reveal 0.4s ease-out forwards; '
                f'animation-delay: {delay:.3f}s;"/>'
            )
            idx += 1

    # legend
    lx = LEFT_PAD + len(weeks) * (CELL + GAP) + 10
    ly = TOP_PAD
    parts.append(f'<text x="{lx}" y="{ly - 10}" fill="#8b949e" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx + i*14}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    parts.append(f'<text x="{lx + len(PALETTE)*14 + 4}" y="{ly + 10}" fill="#8b949e" font-size="10">More</text>')

    # footer
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = f"{total:,} contributions in the last year \u00b7 current streak {streak}d \u00b7 longest streak {longest}d"
    fy = TOP_PAD + 7 * (CELL + GAP) + 30
    parts.append(f'<text x="{LEFT_PAD}" y="{fy}" fill="#c9d1d9" font-size="12">{footer}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    data = load_data()
    weeks = build_grid(data["days"])
    svg = render(weeks, data["stats"])
    with open("contrib-heatmap.svg", "w") as f:
        f.write(svg)
    print("Wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
