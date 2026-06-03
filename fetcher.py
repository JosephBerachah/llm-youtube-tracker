import json
import os
import time
import xml.etree.ElementTree as ET
import urllib.request

import yt_dlp

# Channel IDs are stable — handles can change, IDs never do
CHANNELS = [
    {"name": "Yannic Kilcher",              "id": "UCZHmQk67mSJgfCCTn7xBfew"},
    {"name": "AI Explained",               "id": "UCNJ1Ymd5yFuUPtn21xtRbbw"},
    {"name": "Lex Fridman",                "id": "UCSHZKyawb77ixDdsGog4iWA"},
    {"name": "Machine Learning Street Talk","id": "UCMLtBahI5DMrt0NPvDSoIRQ"},
    {"name": "The AI Epiphany",            "id": "UCj8shE7aIn4Yawwbo2FceCQ"},
    {"name": "Weights & Biases",           "id": "UCBp3w4DCEC64FZr4k9ROxig"},
    {"name": "3Blue1Brown",                "id": "UCYO_jab_esuFRV4b17AJtAw"},
    {"name": "Two Minute Papers",          "id": "UCbfYPyITQ-7l4upoX8nvctg"},
    {"name": "bycloud",                    "id": "UCfg9ux4m8P0YDITTPptrmLg"},
    {"name": "Sentdex",                    "id": "UCfzlCWGWYyg7a9ZkXZoCezg"},
]

# Keywords to filter only LLM/AI-relevant videos
LLM_KEYWORDS = [
    "llm", "gpt", "claude", "gemini", "ai", "language model", "transformer",
    "neural", "deep learning", "machine learning", "llama", "mistral",
    "openai", "anthropic", "agent", "rag", "fine-tun", "benchmark",
    "diffusion", "embedding", "inference", "training", "dataset", "paper"
]

def is_llm_related(title):
    title_lower = title.lower()
    return any(kw in title_lower for kw in LLM_KEYWORDS)

MAX_VIDEOS = 15
TRANSCRIPT_LIMIT = 6000
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt":   "http://www.youtube.com/xml/schemas/2015",
    "media":"http://search.yahoo.com/mrss/",
}

def fetch_rss(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace").encode("utf-8")

def parse_rss(xml_bytes, channel_name):
    root = ET.fromstring(xml_bytes)
    videos = []
    for entry in root.findall("atom:entry", NS)[:MAX_VIDEOS]:
        vid_id = entry.find("yt:videoId", NS).text
        title  = entry.find("atom:title", NS).text
        published = entry.find("atom:published", NS).text[:10]
        videos.append({
            "video_id":  vid_id,
            "title":     title,
            "channel":   channel_name,
            "url":       f"https://www.youtube.com/watch?v={vid_id}",
            "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
            "published": published,
            "views":     "N/A",
        })
    return videos

def get_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get("subtitles", {}) or {}
            auto = info.get("automatic_captions", {}) or {}
            captions = (subs.get("en") or subs.get("en-US") or
                       auto.get("en") or auto.get("en-US") or [])
            for fmt in captions:
                if fmt.get("ext") == "json3":
                    with urllib.request.urlopen(fmt["url"]) as r:
                        data = json.loads(r.read())
                        parts = []
                        for event in data.get("events", []):
                            for seg in event.get("segs", []):
                                t = seg.get("utf8", "").strip()
                                if t and t != "\n":
                                    parts.append(t)
                        text = " ".join(parts).strip()
                        return text[:TRANSCRIPT_LIMIT] or None
    except Exception as e:
        print(f"    transcript error {video_id}: {e}")
    return None

def fetch_all():
    os.makedirs("data", exist_ok=True)
    all_videos = []

    for channel in CHANNELS:
        print(f"Fetching {channel['name']}...")
        try:
            xml_bytes = fetch_rss(channel["id"])
            videos = parse_rss(xml_bytes, channel["name"])
            print(f"  Found {len(videos)} videos")
            for v in videos:
                if not is_llm_related(v["title"]):
                    print(f"  SKIP (not LLM): {v['title'][:55]}")
                    continue
                print(f"  - {v['title'][:65]}")
                transcript = get_transcript(v["video_id"])
                v["transcript"] = transcript
                v["transcript_source"] = "yt-dlp" if transcript else "none"
                time.sleep(0.3)
                all_videos.append(v)
        except Exception as e:
            print(f"  Error {channel['name']}: {e}")

    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(all_videos, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_videos)} videos to data/videos.json")

if __name__ == "__main__":
    fetch_all()
