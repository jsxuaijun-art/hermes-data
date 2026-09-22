---
name: comic-explainer-video
description: "Produce horizontal 1920x1080 purple comic-style explainer short videos with AI-generated illustrations, edge-tts narration, and ffmpeg assembly. Use when a user wants a knowledge, warning, or trend style animated video with a flat purple comic look, white outlines, highlighted subtitles, and a top disclaimer bar, on ANY topic such as profession myths, consumer risks, industry trends, anti-consensus takes, how-to guides, or person stories. Packages a decoupled methodology (visual style plus copywriting structure library T1-T6) and a deterministic build pipeline so the same craft is reusable across unrelated subjects."
agent_created: true
---

# Comic-Style Explainer Video Maker

Make a short, flat-vector, purple comic-book style explainer video. The skill
decouples **craft** (how the video looks and sounds) from **topic** (what it
says), so the exact same production pipeline works for any subject.

## When to use

Trigger this skill when the user asks to create a video that is:
- A "knowledge / debunk / warning / trend" style animated short (not live action).
- Visually consistent with: purple & lavender palette, bold white outlines,
  flat comic illustration, yellow highlighted subtitles, top disclaimer bar.
- Driven by narration + one metaphorical image per line (not real footage).

Examples of user intents that map to this skill:
"做一个讲年轻人不换手机的短视频" / "把'低价代账有风险'做成视频" /
"用漫画风讲一下为什么县城奶茶店不好赚" / "做一个行业趋势科普视频" /
"用黑板手绘风讲一个关于人际关系的隐喻".

This skill supports two animation styles:
- **紫漫解释风** (purple comic explainer) — from `video(7).mp4`.
- **黑板手绘风** (chalkboard hand-drawn) — from `video(22).mp4`.

If the user requests a different visual style (real photo, 3D, watercolor), this
skill does NOT apply — suggest adapting or a different approach.

**Route elsewhere when:**
- The user already has **real live-action talking-head footage** to cut into a
  vertical Douyin-style video → use skill **`auto-douyin-editor`**
  (720×1584, five-act structure, three-layer text system, simulated Douyin UI).
- The user only wants **copywriting / topic selection / follower-growth algorithm**
  advice, not a rendered video → Hermes skill `short-video-copywriting`.

Note: the **T1–T6 copywriting structure library lives here** (`references/methodology.md` §二)
and is the single source of truth — `auto-douyin-editor` references it rather than
duplicating it. Keep it that way.

## How to use this skill

Follow the pipeline in order. Load the two reference files as needed.

### Step 1 — Pick a copywriting structure (topic side)
Read `references/methodology.md`:
1. Use the **structure decision table** (§二) to pick one of T1–T6 based on the
   user's intent (debunk / trend / reverse-opportunity / how-to / person-story /
   list).
2. Fill the chosen structure with the user's topic. The **five-act skeleton**
   (§三) is the fastest starting point for warning/how-to videos.
3. Keep each line short (one image, one idea). Mark key words to highlight.

### Step 2 — Write the shot list
Produce a shot list: for each line of narration, one image + one phrase.
Use the **visual symbol table** (§四 of methodology.md) to turn abstract
concepts into concrete metaphor images (e.g. risk chain → tilted scale + broken
ledger + red warning).

### Step 3 — Choose animation style and generate images (visual side)
1. **Ask the user which style to use**: "你想用哪种画风？1) 紫漫解释风（明亮、紫色漫画、适合科普/警示/趋势），2) 黑板手绘风（深色黑板底、白色手绘线条、适合哲理/隐喻/人性观察）。" If the user has already specified, skip the question.
2. Load `references/styles.md` and use the matching fixed style string. Every
   image MUST include that style suffix so the batch stays consistent.
3. Start with 3 key shots (hook / mechanism / consequence) to validate the look,
   then batch the rest. Use the `ImageGen` tool. Note: each image costs ~5–10 credits.

### Step 4 — Generate narration + assemble (deterministic)
Use `scripts/build_video.py`. Create a manifest JSON (see
`assets/manifest_template.json`) where each shot maps `image` + `text` + `zoom`.
Run with the managed Python venv that has `edge-tts` installed:

```bash
# ensure edge-tts in the venv (one-time)
<managed_python> -m venv <venv> && <venv>/Scripts/pip install edge-tts
# build
<venv>/Scripts/python scripts/build_video.py manifest.json -o final.mp4
```

The script auto-generates edge-tts audio + subtitles per shot, applies a slow
zoom, yellow subtitle highlight, and the top disclaimer bar, then concatenates.
Note: for the chalkboard style, consider white or light-yellow subtitles instead
of bright yellow if readability against the dark background suffers; adjust the
`SUBTITLE_STYLE` in `scripts/build_video.py` if necessary.

### Step 5 — Compliance pass before publishing
Run the **compliance checklist** (§五 of methodology.md): official wording for
policy claims, verifiable data sources, persistent disclaimer for finance/legal/
medical topics, no guaranteed-return or defamatory claims.

## Notes / constraints
- Font default is `C:/Windows/Fonts/simhei.ttf` (Windows). On other OS, set
  `FONT_FILE` in `scripts/build_video.py` to an available CJK font.
- `ffmpeg` and `edge-tts` must be available in the environment.
- PoC approach: validate style with 3 images + a 60s clip before committing to
  a full 3–4 min video.
