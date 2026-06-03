import yt_dlp

def get_transcript_ytdlp(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US"],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get("subtitles", {}) or {}
            auto = info.get("automatic_captions", {}) or {}
            captions = subs.get("en") or subs.get("en-US") or auto.get("en") or auto.get("en-US") or []
            for fmt in captions:
                if fmt.get("ext") == "json3":
                    import urllib.request
                    with urllib.request.urlopen(fmt["url"]) as r:
                        import json
                        data = json.loads(r.read())
                        parts = []
                        for event in data.get("events", []):
                            for seg in event.get("segs", []):
                                t = seg.get("utf8", "").strip()
                                if t and t != "\n":
                                    parts.append(t)
                        return " ".join(parts)[:6000]
    except Exception as e:
        print(f"Error: {e}")
    return None

# Test on a Yannic Kilcher video
result = get_transcript_ytdlp("xHi8PUIVyoo")
if result:
    print(f"SUCCESS! Got {len(result)} chars")
    print("Preview:", result[:300])
else:
    print("FAILED - no transcript")
