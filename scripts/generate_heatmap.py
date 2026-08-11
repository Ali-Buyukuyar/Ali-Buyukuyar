"""Fetch the public contribution grid and render a looping Matrix-style SVG."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import urllib.request
from pathlib import Path

CELL, GAP, LEFT, TOP = 11, 3, 22, 48
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def get_days(username: str) -> dict[str, int]:
    url = f"https://github.com/users/{username}/contributions"
    request = urllib.request.Request(url, headers={"User-Agent": "profile-readme-generator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8")
    pairs = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="([0-4])"', page)
    if not pairs:
        reversed_pairs = re.findall(r'data-level="([0-4])"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', page)
        pairs = [(date, level) for level, date in reversed_pairs]
    return {date: int(level) for date, level in pairs}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    days = get_days(args.username)
    ordered = sorted((dt.date.fromisoformat(day), level) for day, level in days.items())
    if not ordered:
        raise RuntimeError("GitHub did not return a contribution calendar.")

    start = ordered[0][0] - dt.timedelta(days=(ordered[0][0].weekday() + 1) % 7)
    cells = []
    for date, level in ordered:
        offset = (date - start).days
        week, weekday = divmod(offset, 7)
        x, y = LEFT + week * (CELL + GAP), TOP + weekday * (CELL + GAP)
        # A different phase per column makes the highlight travel left to right forever.
        phase = round((week / 53) * 6.4 + weekday * 0.028, 3)
        if level:
            animation = (
                f'<animate attributeName="opacity" values=".72;1;.72" dur="6.4s" '
                f'begin="{phase}s" repeatCount="indefinite"/>'
            )
        else:
            animation = ""
        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{COLORS[level]}">{animation}</rect>'
        )

    width = LEFT * 2 + 53 * (CELL + GAP)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="170" viewBox="0 0 {width} 170" role="img" aria-label="Animated GitHub contribution graph for {html.escape(args.username)}">
<style>
.bg {{ fill:#0d1117 }} text {{ font:14px monospace; fill:#c9d1d9 }} .accent {{ fill:#58a6ff; font-weight:bold }}
.cell {{ opacity:.68 }}
</style>
<rect class="bg" width="100%" height="100%" rx="12"/>
<text class="accent" x="22" y="28">ali@github:~$ ./contributions.sh</text>
<text x="22" y="153">Less</text>{''.join(cells)}<text x="{width - 52}" y="153">More</text>
</svg>'''
    Path(__file__).parents[1].joinpath("assets", "contribution-heatmap.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
