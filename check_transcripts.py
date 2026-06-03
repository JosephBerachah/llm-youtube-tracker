import json

with open("data/videos.json", encoding="utf-8") as f:
    videos = json.load(f)

has_transcript = sum(1 for v in videos if v.get("transcript"))
no_transcript = sum(1 for v in videos if not v.get("transcript"))
print(f"With transcript: {has_transcript}/{len(videos)}")
print(f"Without transcript: {no_transcript}/{len(videos)}")

print("\n--- Sample transcript ---")
for v in videos:
    if v.get("transcript"):
        print(f"Channel: {v['channel']}")
        print(f"Title: {v['title']}")
        print(f"Transcript preview: {v['transcript'][:300]}")
        break
