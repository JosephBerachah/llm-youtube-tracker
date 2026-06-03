import urllib.request
import re

# Try alternative URLs for missing ones
urls = [
    ("AI Explained", "https://www.youtube.com/@aiexplained-official"),
    ("AI Explained alt", "https://www.youtube.com/c/aiexplained-official"),
    ("Two Minute Papers", "https://www.youtube.com/@TwoMinutePapers"),
    ("Two Minute Papers alt", "https://www.youtube.com/c/TwoMinutePapers"),
    ("Matt Wolfe", "https://www.youtube.com/@mreflow"),
    ("Matt Wolfe alt", "https://www.youtube.com/c/mreflow"),
]

for name, url in urls:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
            match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]{20,})"', html)
            if match:
                print(f"{name} -> {match.group(1)}")
            else:
                print(f"{name} -> NOT FOUND in {url}")
    except Exception as e:
        print(f"{name} -> ERROR: {e}")
