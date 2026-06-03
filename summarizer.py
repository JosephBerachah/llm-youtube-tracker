import json
import os
from datetime import datetime

from openai import OpenAI

def _load_key():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=_load_key())
MODEL = "gpt-4o-mini"

TOPIC_KEYWORDS = {
    "RAG": ["retrieval", "rag", "vector", "embedding", "search"],
    "Agents": ["agent", "agentic", "tool use", "function calling", "autonomous"],
    "Fine-tuning": ["fine-tun", "finetun", "lora", "qlora", "training", "sft"],
    "Benchmarks": ["benchmark", "evaluation", "leaderboard", "mmlu", "score"],
    "Safety": ["safety", "alignment", "guardrail", "bias", "harmful", "jailbreak"],
    "Multimodal": ["multimodal", "vision", "image", "video", "audio", "speech"],
    "Architecture": ["transformer", "attention", "architecture", "layer", "parameter"],
    "Inference": ["inference", "quantization", "speed", "latency", "deployment"],
    "Open Source": ["open source", "open-source", "llama", "mistral", "gemma", "qwen"],
    "Reasoning": ["reasoning", "chain of thought", "cot", "o1", "thinking", "logic"],
}

def extract_topics(text):
    text_lower = text.lower()
    found = [topic for topic, keywords in TOPIC_KEYWORDS.items() if any(kw in text_lower for kw in keywords)]
    return found if found else ["General LLM"]

def ai_summarize(title, channel, transcript):
    if transcript:
        source = f"Transcript (first 2000 chars):\n{transcript[:2000]}"
        instruction = "In 4-5 sentences, summarize what the creator ACTUALLY says. Cover the main points, specific models or techniques mentioned, key claims or findings, and anything surprising or notable. Be specific — avoid generic statements."
    else:
        source = "(No transcript available — base your summary only on the title)"
        instruction = "In exactly 1 sentence, describe what this video is likely about based purely on its title. Do NOT invent details or claims not implied by the title."

    prompt = f"""You are analyzing a YouTube video about LLMs/AI.

Title: {title}
Channel: {channel}
{source}

{instruction}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  GPT error: {e}")
        return (transcript or title)[:200]

def summarize_all():
    if not os.path.exists("data/videos.json"):
        print("data/videos.json not found — run fetcher.py first.")
        return

    with open("data/videos.json", "r", encoding="utf-8") as f:
        videos = json.load(f)

    if not videos:
        print("No videos found.")
        return

    enriched = []
    for i, video in enumerate(videos):
        print(f"[{i+1}/{len(videos)}] {video['channel']} — {video['title'][:55]}")
        summary = ai_summarize(video["title"], video["channel"], video.get("transcript"))
        topics = extract_topics((video.get("transcript") or "") + " " + video["title"])
        enriched.append({
            **video,
            "summary": summary,
            "topics": topics,
            "transcript_source": video.get("transcript_source", "none"),
            "transcript": None,
        })

    os.makedirs("data", exist_ok=True)
    with open("data/videos_enriched.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "model": MODEL,
            "videos": enriched,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(enriched)} videos to data/videos_enriched.json")

if __name__ == "__main__":
    summarize_all()
