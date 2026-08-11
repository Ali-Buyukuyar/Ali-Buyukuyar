"""Render a decorative, endlessly flowing Matrix-style contribution grid."""
from __future__ import annotations

import argparse
import html
from pathlib import Path

CELL, GAP, LEFT, TOP = 11, 3, 22, 48
WEEKS, DAYS = 53, 7


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    args = parser.parse_args()

    cells = []
    for week in range(WEEKS):
        for day in range(DAYS):
            x = LEFT + week * (CELL + GAP)
            y = TOP + day * (CELL + GAP)
            # Staggered begins create a vertical trail that travels left to right.
            begin = round(week * 0.10 + day * 0.018, 3)
            shade = ["#006d32", "#26a641", "#39d353"][day % 3]
            cells.append(f'''<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="#0e4429">
  <animate attributeName="fill" values="#0e4429;{shade};#39d353;#0e4429" dur="5.4s" begin="{begin}s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".35;1;1;.35" dur="5.4s" begin="{begin}s" repeatCount="indefinite"/>
</rect>''')

    width = LEFT * 2 + WEEKS * (CELL + GAP)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="170" viewBox="0 0 {width} 170" role="img" aria-label="Animated Matrix-style contribution graph for {html.escape(args.username)}">
<style>.bg {{ fill:#0d1117 }} text {{ font:14px monospace; fill:#c9d1d9 }}</style>
<rect class="bg" width="100%" height="100%" rx="12"/>
{''.join(cells)}
</svg>'''
    Path(__file__).parents[1].joinpath("assets", "contribution-heatmap.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
