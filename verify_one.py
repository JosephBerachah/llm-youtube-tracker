import json

video_id = "aJvP3nXWkwM"

with open("data/videos.json", encoding="utf-8") as f:
    videos = json.load(f)

with open("data/videos_enriched.json", encoding="utf-8") as f:
    enriched = json.load(f)["videos"]

v = next((v for v in videos if v["video_id"] == video_id), None)
e = next((e for e in enriched if e["video_id"] == video_id), None)

if v:
    print(f"Title: {v['title']}")
    print(f"Channel: {v['channel']}")
    print(f"\nTranscript ({len(v.get('transcript') or '')} chars):")
    print((v.get("transcript") or "NO TRANSCRIPT")[:500])
    print(f"\nAI Summary: {e['summary'] if e else 'N/A'}")
else:
    print("Video not found in data — not fetched yet")
