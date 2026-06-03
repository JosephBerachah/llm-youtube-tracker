# LLM YouTube Landscape Tracker

A self-updating dashboard that tracks what top AI/LLM YouTube channels are
publishing. A daily GitHub Actions job scrapes recent videos, summarizes each
one with an LLM, and publishes the results as a static site on GitHub Pages.

## How it works

```
pipeline.py
 ├─ fetcher.py     scrapes recent videos + transcripts  → data/videos.json
 └─ summarizer.py  AI summary + topic tags per video     → data/videos_enriched.json
index.html         fetches ./data/videos_enriched.json and renders the dashboard
```

- **`fetcher.py`** uses `scrapetube` + `youtube-transcript-api`. It scrapes
  YouTube directly, so **no YouTube API key is required.**
- **`summarizer.py`** calls the OpenAI API (`gpt-4o-mini`) and reads your key
  from the `OPENAI_API_KEY` environment variable.

## Running locally

```bash
pip install -r requirements.txt

# PowerShell
$env:OPENAI_API_KEY = "sk-..."
python pipeline.py

# bash / macOS / Linux
export OPENAI_API_KEY="sk-..."
python pipeline.py
```

Then open `index.html` in your browser. (Because the page fetches
`./data/videos_enriched.json`, serve the folder over HTTP if your browser
blocks local `file://` fetches — e.g. `python -m http.server`.)

> ⚠️ **Never commit your API key.** Keep it in your shell environment or a
> local `.env` file (which is git-ignored). Only the generated
> `data/videos_enriched.json` is committed.

## Setup: add your API key as a GitHub Secret

The scheduled workflow needs your OpenAI key, supplied as an encrypted
repository secret (never stored in the repo).

1. Push this project to a GitHub repository.
2. In the repo, go to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret**.
4. Set:
   - **Name:** `OPENAI_API_KEY`
   - **Secret:** your OpenAI API key (e.g. `sk-...`)
5. Click **Add secret**.

The workflow (`.github/workflows/update.yml`) reads it as
`${{ secrets.OPENAI_API_KEY }}` and exposes it to `pipeline.py` at runtime.

## Setup: enable GitHub Pages (serve from root `/`)

The site is plain static files (`index.html` + `data/`) at the repository
root, so GitHub Pages can serve it directly:

1. In the repo, go to **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Set **Branch** to `main` and the folder to **`/ (root)`**.
4. Click **Save**.

Your site will be published at `https://<your-username>.github.io/<repo-name>/`,
serving `index.html` from the root of the repo.

## Automatic updates

`.github/workflows/update.yml` runs:

- **On a schedule:** every 24 hours (cron `0 6 * * *`, i.e. 06:00 UTC).
- **On demand:** via the **Run workflow** button on the **Actions** tab
  (`workflow_dispatch`).

Each run:

1. Checks out the repo and sets up Python 3.12.
2. Installs `requirements.txt`.
3. Runs `pipeline.py` (with `OPENAI_API_KEY` from your repository secret).
4. Commits the refreshed `data/videos_enriched.json` back to `main`.

That commit triggers GitHub Pages to rebuild automatically, so the live
dashboard stays up to date with no manual steps. (The commit message includes
`[skip ci]` so it doesn't re-trigger the workflow.)

## Tracked channels

Andrej Karpathy · Yannic Kilcher · AI Explained · Two Minute Papers ·
Lex Fridman · Matt Wolfe · Fireship · Wes Roth

Edit the `CHANNELS` list in `fetcher.py` to customize.
