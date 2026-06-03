import urllib.request
import xml.etree.ElementTree as ET

NS = {"atom": "http://www.w3.org/2005/Atom"}

channels = [
    ("Two Minute Papers",  "UCbfYPyITQ-7l4upoX8nvctg"),
    ("Andrej Karpathy",    "UCYO_jab_esuFRV4b17AJtAw"),
    ("Daniel Bourke",      "UCA65IAfAwrdwqOokZcl8mFQ"),
    ("ByCloud AI",         "UCfg9ux4m8P0YDITTPptrmLg"),
    ("Matthew Berman",     "UCbd_PhGT7pzF4K3VEj9bCQw"),
    ("Sam Witteveen",      "UCnUYZLuoy1rq1aVMwx4aTzw"),
]

for name, cid in channels:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            root = ET.fromstring(r.read())
            title = root.find("atom:title", NS).text
            entries = root.findall("atom:entry", NS)
            first = entries[0].find("atom:title", NS).text if entries else "no videos"
            print(f"{name} -> [{title}] | Latest: {first[:60]}")
    except Exception as e:
        print(f"{name} -> ERROR: {e}")
