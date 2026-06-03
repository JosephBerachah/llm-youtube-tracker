import json

with open("data/videos_enriched.json", encoding="utf-8") as f:
    data = json.load(f)

for v in data["videos"]:
    if v["channel"] == "AI Coffee Break":
        v["channel"] = "Machine Learning Street Talk"

with open("data/videos_enriched.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fixed!")
