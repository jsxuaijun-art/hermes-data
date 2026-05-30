# Jianpu to Audio — Generation Workflow

## Overview

After OCR or manual transcription of a jianpu (Chinese numbered notation) score, the natural next step is generating playable audio. This reference covers the complete workflow from transcribed numbers to MIDI playback, including fingering guidance for melodica (口风琴).

## Prerequisites

```bash
pip install midiutil    # MIDI file generation
# Optional:
apt-get install timidity  # MIDI → WAV conversion
```

## Script

Use `scripts/jianpu2midi.py` — a standalone script that converts jianpu text to MIDI.

### Usage Examples

```bash
# Basic: single line
python scripts/jianpu2midi.py "5 5 6 5 | 3 2 1 — | 5 5 6 5 | 3 2 1 — |"

# From file
python scripts/jianpu2midi.py --file score.txt

# With practice guide and fingering
python scripts/jianpu2midi.py --guide --fingering "5 5 ^5 3 | 2 2 ^2 1 |"

# Custom tempo and instrument (GM#22=Harmonica, #79=Recorder, #75=Pan Flute)
python scripts/jianpu2midi.py --bpm 100 --instrument 22 "..."

# Interactive mode (just run without arguments)
python scripts/jianpu2midi.py
```

### Input Format

| Token | Meaning | Example |
|-------|---------|---------|
| `0-7` | Scale degrees (0=rest) | `5` = sol |
| `\|` | Bar line (ignored) | |
| `—` or `-` | Hold previous note | `1 —` = do held for 2 beats |
| `.` | Dot (lengthen by 50%) | `5.` = dotted quarter |
| `^` | Up one octave | `^5` = high sol |
| `_` | Down one octave | `_3` = low mi |
| `>` | Accent (louder) | `>5` = accented sol |
| `,` | Staccato (shorten) | `5,` = short note |

### Instrument Numbers (GM)

| # | Instrument | Best for |
|---|-----------|----------|
| 22 | Harmonica | 口风琴 (closest match) |
| 79 | Recorder | 木笛/竖笛 |
| 75 | Pan Flute | 排箫 (sweet tone) |
| 80 | Ocarina | 陶笛 |
| 0 | Piano | 钢琴 (practice) |

## Fingering Guidance for 口风琴 (Melodica)

### Right Hand (Default)

| Note (Jianpu) | Finger | Note |
|---------------|--------|------|
| 1 (do) | 1 (thumb) | C |
| 2 (re) | 2 (index) | D |
| 3 (mi) | 3 (middle) | E |
| 4 (fa) | 1 (thumb) | F — use thumb, not 4th |
| 5 (sol) | 2 (index) | G |
| 6 (la) | 3 (middle) | A |
| 7 (si) | 4 (ring) | B |
| ^1 (high do) | 1 (thumb) | C' |
| _7 (low si) | 3 (middle) | Below middle C |

**Key Principle**: Thumb (1) plays C and F. Fingers 1–5 fall naturally for C major scale. For accidentals (if available), use the nearest convenient finger.

### Breath Control (口风琴)

- **高音区** (high register): Blow slightly faster/sharper
- **低音区** (low register): Blow gentler, fuller breath
- **Legato passages**: Keep breath steady, don't re-articulate each note
- **Staccato**: Use tongue to stop the air between notes

## Practice Guide Generation

The `--guide` flag generates a structured practice guide including:

1. **Difficulty assessment** (based on range span)
2. **Phased practice**: Slow (♩=60) → Medium (♩=original) → Full tempo
3. **Fingering suggestions** per note
4. **Melodica-specific tips**: breath control, articulation, register changes

## Converting to Playable Audio

```bash
# MIDI → WAV (requires timidity)
timidity jianpu_score.mid -Ow -o output.wav

# MIDI → MP3 (requires ffmpeg + timidity)
timidity jianpu_score.mid -Ow -o - | ffmpeg -i - output.mp3

# Play MIDI directly (if soundfont available)
timidity jianpu_score.mid
```

## Limitations

- MIDI is a simplified representation — no dynamics curves, breath vibrato, or articulation nuances
- Harmonica (GM#22) is the closest approximation but doesn't reproduce real melodica timbre
- Complex rhythms (triplets, swung eighths) need manual encoding in the script
- This approach assumes simple 4/4 or 2/4 time; compound meters need adjustment

## See Also

- `references/music-score-ocr.md` — OCR limitations and recovery techniques
- `scripts/jianpu2midi.py` — The actual conversion script
