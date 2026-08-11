"""Render a GitHub avatar as a self-contained, animated ASCII SVG."""
from __future__ import annotations

import argparse
import html
import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

CHARS = " .:-=+*#%@"
WIDTH, HEIGHT = 48, 48


def avatar(username: str) -> Image.Image:
    url = f"https://github.com/{username}.png?size=256"
    request = urllib.request.Request(url, headers={"User-Agent": "profile-readme-generator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        image = Image.open(io.BytesIO(response.read())).convert("L")
    image = ImageOps.fit(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    return ImageEnhance.Contrast(image).enhance(1.65)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    image = avatar(args.username)
    pixels = list(image.getdata())
    lines = []
    for y in range(HEIGHT):
        line = "".join(CHARS[pixels[y * WIDTH + x] * (len(CHARS) - 1) // 255] for x in range(WIDTH))
        lines.append(html.escape(line))

    rows = "\n".join(
        f'<text x="20" y="{38 + i * 11}" class="row" style="--delay:{i * 55}ms">{line}</text>'
        for i, line in enumerate(lines)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="590" viewBox="0 0 420 590" role="img" aria-label="Animated ASCII portrait of {html.escape(args.username)}">
<style>
.bg {{ fill:#0d1117 }} .frame {{ fill:none; stroke:#30363d }} .title {{ fill:#58a6ff; font:700 15px monospace }}
.row {{ fill:#c9d1d9; font:10px monospace; opacity:0; animation:appear .45s ease-out forwards; }}
@keyframes appear {{ to {{ opacity:1 }} }}
</style>
<rect class="bg" width="420" height="590" rx="12"/><rect class="frame" x="10" y="10" width="400" height="570" rx="8"/>
<text class="title" x="20" y="28">ali@github:~$ ./portrait --ascii</text>
{rows}
</svg>'''
    output = Path(__file__).parents[1] / "assets" / "ascii-portrait.svg"
    output.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
