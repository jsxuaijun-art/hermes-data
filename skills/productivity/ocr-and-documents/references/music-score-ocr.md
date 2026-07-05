# Music Score OCR — Jianpu (Chinese Numbered Notation)

## Context

Chinese middle school music classes (especially Shanghai curriculum) often use **jianpu** (简谱 / numbered musical notation) — a notation system using numbers 1–7 for scale degrees, with Chinese characters for dynamics, tempo, and performance instructions. These appear as scanned photographs or photocopies (JPEG/PNG), rarely as PDFs.

## Key Finding

**Standard OCR pipelines (Tesseract, pytesseract) cannot reliably read jianpu scores.** The image typically contains a mix of:

- Numerals (1–7) in musical contexts, not plain text
- Slurs, ties, beams, and other musical articulation marks
- Chinese characters for performance instructions
- Small type size on a gray/noisy background (often phone-photographed)
- Vertical and horizontal staff-like alignment that confuses layout analysis

Even with aggressive preprocessing (contrast enhancement, thresholding, negation, resize, morphological operations) and every PSM mode (3, 4, 6, 11, 12), Tesseract output is garbled beyond usability.

## Approaches Tried & Results

| Approach | Result |
|----------|--------|
| **vision_analyze** (model: deepseek-v4-flash) | ❌ Model rejects image_url content type |
| **Tesseract PSM 12 + chi_sim** | ⚠️ Partial: can recover some Chinese text instructions from bottom of image (performance notes) but fails on actual notation numbers |
| **Tesseract PSM 3 + chi_sim** | ⚠️ Similar — Chinese text at ~50% accuracy, notation numbers at ~10% |
| **Tesseract with ImageMagick preprocessing** (threshold, LAT, normalize, negate, resize 2x) | ❌ No improvement |
| **Tesseract with crop-to-text-areas** | ❌ False — cropped regions returned empty |
| **pytesseract with char whitelists** | ❌ Only recovered 2 Chinese chars and digits '2', '7' from the entire notation area |
| **ImageMagick morphological operations** | ❌ No improvement |

## Vision API Limitations

`vision_analyze` support is **model-dependent**. Some providers/models (e.g. deepseek-v4-flash) do not accept `image_url` content type and return:

```
unknown variant `image_url`, expected `text`
```

If `vision_analyze` fails with this error, the model simply doesn't support image input — fall back directly to the OCR + human-assisted transcription workflow below. No amount of preprocessing or reformatting will make it work; it's a model capability constraint, not an image quality issue.

## Structural Analysis (PIL Row-Darkness Approach)

When Tesseract fails completely, a last-resort approach is to analyze the image's row-by-row pixel density to locate content bands:

```python
import numpy as np
from PIL import Image

gray = np.array(Image.open("score.jpg").convert('L'))
h, w = gray.shape
row_darkness = [np.mean(gray[y, :] < 80) for y in range(h)]

# Find bands with >0.5% dark pixels
bands = []
in_band = False
start = 0
for y in range(h):
    is_ct = row_darkness[y] > 0.005
    if is_ct and not in_band:
        start = y; in_band = True
    elif not is_ct and in_band:
        if y - start > 10:
            bands.append((start, y))
        in_band = False
```

This can identify:
- **Title area** (top ~40-60px)
- **Main notation body** (typically rows 100-1400, ~1300px of content)
- **Performance instructions** (bottom ~80-150px, rows 1450-1550)

Once bands are identified, crop and OCR each band separately for slightly better results. However, even this approach rarely recovers the actual notation numbers — it's mainly useful for confirming the image structure and isolating text-only regions for better OCR.

## What CAN Be Recovered

- **Title**: Usually at top of image — partial OCR may suggest it
- **Tempo/style marking**: e.g. 中速 雄壮地 (medium tempo, majestically)
- **Performance instructions at bottom**: typically 2–3 lines of Chinese text giving playing tips
- **The fact that it IS a jianpu score** (structure of the image, presence of numbered rows with bar lines)

## Recommended Workflow for Music Scores

### If vision_analyze is supported (model-dependent):

```python
# Most reliable — works if the model supports image_url
vision_analyze(
    image_url="/mnt/c/Users/xxx/Desktop/score.jpg",
    question="Transcribe this jianpu music score completely: all numbers, Chinese text, and bar lines"
)
```

### Fallback: Human-assisted transcription

Since OCR can't read jianpu, the most practical approach is:

1. Present what OCR DID recover (title, tempo, performance instructions)
2. Ask the user to read the numbers aloud or type them
3. Use Python (`music21`, `midiutil`, or a simple script) to generate playable audio from the transcribed notes

### If the score needs to be read programmatically:

- **EasyOCR** (with Chinese language pack) may outperform Tesseract on mixed Chinese/number content — but installs ~1GB of models
- **PaddleOCR** — similar tradeoff
- **Custom CNN** — overkill for one-score scenarios
- **Take a photo with better lighting/angle** — sometimes reprocessing the original helps

## Pitfalls

- Do NOT spend more than 5 minutes trying different Tesseract configs on a music score — it will not converge
- Chinese search engines (Baidu, Bing CN) and Bilibili API heavily rate-limit/block automated requests from WSL — searching for educational resources programmatically is unreliable
- Windows proxy (Clash at 127.0.0.1:7890) is NOT accessible from WSL by default — set `HTTP_PROXY` env var in WSL if needed
- The image may be a phone photo with perspective distortion — this further degrades OCR

## Example

From a real session with a Shanghai Grade 7 student's score "星空交响" (Starry Sky Symphony):

- **Title**: 星空交响
- **Tempo**: 中速 雄壮地 (medium march tempo)
- **Notes recovered from OCR**:
  - 凸显进行曲风格，注意节奏稳健
  - 气息连贯，时值饱满
  - 如果乐器没有变化音，可将变化音还原吹奏
- **Notation sections**: 3–4 staves of jianpu with numbers 1–7, Chinese chord annotations, and bar lines
