import urllib.request
import re

handles = [
    "TwoMinutePapers",
    "AndrejKarpathy",
    "matthew_berman",
    "SamWitteveenAI",
    "aiadvantage",
    "datasciencecastnet",
    "mrdbourke",
    "bycloudai",
]

for handle in handles:
    url = f"https://www.youtube.com/@{handle}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
            match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]{20,})"', html)
            title = re.search(r'"title":"([^"]+)"', html)
            if match:
                print(f"@{handle} -> {match.group(1)} | {title.group(1) if title else ''}")
            else:
                print(f"@{handle} -> NOT FOUND")
    except Exception as e:
        print(f"@{handle} -> ERROR: {e}")
