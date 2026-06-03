import json

with open("data/videos.json", encoding="utf-8") as f:
    videos = json.load(f)

with open("data/videos_enriched.json", encoding="utf-8") as f:
    enriched = json.load(f)["videos"]

# Show transcript preview vs AI summary for first 3 videos
for v in videos[:3]:
    summary = next((e["summary"] for e in enriched if e["video_id"] == v["video_id"]), "N/A")
    print(f"\nChannel: {v['channel']}")
    print(f"Title: {v['title']}")
    print(f"Transcript (first 300 chars): {(v.get('transcript') or 'NO TRANSCRIPT')[:300]}")
    print(f"AI Summary: {summary}")
    print("-" * 80)
