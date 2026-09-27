---
name: youtube-content
<<<<<<< LOCAL (this PC)
description: >
  Fetch YouTube video transcripts and transform them into structured content
  (chapters, summaries, threads, blog posts). Use when the user shares a YouTube
  URL or video link, asks to summarize a video, requests a transcript, or wants
  to extract and reformat content from any YouTube video.
=======
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
>>>>>>> REPO (github)
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

Use `uv` so the dependency is installed into the same Hermes-managed environment
that runs the helper script:

```bash
<<<<<<< LOCAL (this PC)
pip install youtube-transcript-api
=======
uv pip install youtube-transcript-api
>>>>>>> REPO (github)
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
<<<<<<< LOCAL (this PC)
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
=======
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
>>>>>>> REPO (github)

# Plain text (good for piping into further processing)
<<<<<<< LOCAL (this PC)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only
=======
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only
>>>>>>> REPO (github)

# With timestamps
<<<<<<< LOCAL (this PC)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps
=======
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps
>>>>>>> REPO (github)

# Specific language with fallback chain
<<<<<<< LOCAL (this PC)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
=======
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
>>>>>>> REPO (github)
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

<<<<<<< LOCAL (this PC)
1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
=======
1. **Fetch** the transcript using the helper script with `--text-only --timestamps` via `uv run python3`.
>>>>>>> REPO (github)
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
<<<<<<< LOCAL (this PC)
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
=======
- **Dependency missing**: run `uv pip install youtube-transcript-api` and retry.
>>>>>>> REPO (github)
