import datetime
import json
import pathlib
import re

import requests

html = requests.get("https://ledjanahmati.github.io/clisonix-blog/", timeout=20).text
matches = re.findall(r'href="static/(\d{4}-\d{2}-\d{2})-([^"]+)\.html">', html)
ids = sorted({f"{date}-{slug}" for date, slug in matches})
out = pathlib.Path("/app/data/posted_articles.json")
out.write_text(
    json.dumps(
        {
            "posted": ids,
            "last_updated": datetime.datetime.now().isoformat(),
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"seeded {len(ids)} IDs")
