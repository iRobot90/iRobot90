"""Render GitHub's public contribution levels without tokens or invented counts."""
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs and "data-level" in attrs:
            day = date.fromisoformat(attrs["data-date"])
            level = int(attrs["data-level"])
            if not 0 <= level <= 4:
                raise ValueError("Unexpected contribution level")
            self.days[day] = level

def render(days):
    if not 350 <= len(days) <= 371:
        raise ValueError("Incomplete public calendar; keep previous artifact")
    first, last = min(days), max(days)
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190" role="img" aria-labelledby="title desc">',
      '<title id="title">iRobot90 public GitHub contribution calendar</title>',
      '<desc id="desc">Daily intensity levels from the public GitHub calendar. Not an all-time or private contribution total.</desc>',
      '<rect width="900" height="190" rx="12" fill="#0a0a0a"/>',
      '<text x="20" y="27" fill="#00ff41" font-family="monospace" font-size="17">Public GitHub contribution activity</text>']
    for day, level in sorted(days.items()):
        offset = (day - first).days + (first.weekday() + 1) % 7
        x, y = 20 + (offset // 7) * 16, 42 + (offset % 7) * 15
        parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{colors[level]}"><title>{day}: GitHub intensity level {level} of 4</title></rect>')
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts.append(f'<text x="20" y="170" fill="#cccccc" font-family="monospace" font-size="12">{first} to {last} | Updated {stamp} | Public activity only</text></svg>')
    return "".join(parts)

if __name__ == "__main__":
    request = Request("https://github.com/users/iRobot90/contributions", headers={"User-Agent": "iRobot90-profile-calendar"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError("Contribution source unavailable")
        markup = response.read(2_000_001)
    if len(markup) > 2_000_000:
        raise ValueError("Unexpected response size")
    calendar = Calendar()
    calendar.feed(markup.decode("utf-8"))
    svg = render(calendar.days)
    target = Path("dist/github-contribution-calendar.svg")
    target.parent.mkdir(exist_ok=True)
    target.write_text(svg)
    print(f"Rendered {len(calendar.days)} public calendar days")
