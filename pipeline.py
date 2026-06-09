"""
Incremental pipeline:
  1. Fetch latest videos from RSS (just metadata + attempt transcript)
  2. Load existing enriched data so we KEEP previously-good summaries
  3. Only call GPT for brand-new videos not already in the archive
  4. Merge old + new and save

This means GitHub Actions (where YouTube blocks yt-dlp) won't wipe out
real transcript-based summaries that were generated locally.
"""

import json
import os
from datetime import datetime

import fetcher
import summarizer


# ── Step 1: RSS fetch (titles, thumbnails, transcript attempts) ──────────────
print("=" * 50)
print("Step 1: Fetching YouTube videos...")
print("=" * 50)
fetcher.fetch_all()   # writes data/videos.json

# ── Step 2: Load newly fetched videos ────────────────────────────────────────
with open("data/videos.json", "r", encoding="utf-8") as f:
    new_videos = json.load(f)

# ── Step 3: Load existing enriched archive ───────────────────────────────────
archive = {}
if os.path.exists("data/videos_enriched.json"):
    with open("data/videos_enriched.json", "r", encoding="utf-8") as f:
        existing = json.load(f)
    for v in existing.get("videos", []):
        archive[v["video_id"]] = v
    print(f"\nLoaded {len(archive)} existing enriched videos from archive.")
else:
    print("\nNo existing archive found — will process all videos fresh.")

# ── Step 4: Split into already-known vs truly new ────────────────────────────
already_have = []
to_process   = []

for v in new_videos:
    vid_id = v["video_id"]
    if vid_id in archive:
        existing_entry = archive[vid_id]
        # If we previously got a real transcript and this new fetch didn't,
        # keep the archived summary (don't downgrade to title-only)
        if (existing_entry.get("transcript_source") == "yt-dlp"
                and v.get("transcript_source") != "yt-dlp"):
            already_have.append(existing_entry)
            print(f"  KEEP (has transcript): {v['title'][:60]}")
        else:
            # New fetch has equal or better transcript — re-process
            to_process.append(v)
    else:
        to_process.append(v)

print(f"\nKept {len(already_have)} videos with existing good summaries.")
print(f"Processing {len(to_process)} new/updated videos with GPT...")

# ── Step 5: Summarize only the new/updated videos ────────────────────────────
newly_enriched = []
for i, video in enumerate(to_process):
    print(f"\n[{i+1}/{len(to_process)}] {video['channel']} — {video['title'][:55]}")
    summary  = summarizer.ai_summarize(video["title"], video["channel"], video.get("transcript"))
    topics   = summarizer.extract_topics((video.get("transcript") or "") + " " + video["title"])
    src      = video.get("transcript_source", "none")
    newly_enriched.append({
        **video,
        "summary":           summary,
        "topics":            topics,
        "transcript_source": src,
        "transcript":        None,   # strip raw text to keep JSON small
    })

# ── Step 6: Merge and save ────────────────────────────────────────────────────
all_videos = already_have + newly_enriched

# Sort by published date descending
all_videos.sort(key=lambda v: v.get("published", ""), reverse=True)

os.makedirs("data", exist_ok=True)
with open("data/videos_enriched.json", "w", encoding="utf-8") as f:
    json.dump({
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "model":        summarizer.MODEL,
        "videos":       all_videos,
    }, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"Done. {len(all_videos)} total videos saved to data/videos_enriched.json")
print(f"  - {len(already_have)} kept from archive (good transcripts preserved)")
print(f"  - {len(newly_enriched)} newly processed")
print("Pipeline complete.")
