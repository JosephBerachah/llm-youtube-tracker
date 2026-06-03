import fetcher
import summarizer

print("=" * 50)
print("Step 1: Fetching YouTube videos...")
print("=" * 50)
fetcher.fetch_all()

print("\n" + "=" * 50)
print("Step 2: Summarizing with AI...")
print("=" * 50)
summarizer.summarize_all()

print("\nPipeline complete. Open index.html in your browser.")
