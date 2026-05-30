#!/usr/bin/env python3
"""
jianpu2midi.py — Convert Chinese Jianpu (numbered notation) to MIDI audio.

Usage:
    python jianpu2midi.py "5 5 6 5 | 3 2 1 — |"              # Single line
    python jianpu2midi.py --file score.txt                    # Read from file
    python jianpu2midi.py --bpm 100 --instrument 22 "..."     # Custom tempo/instrument

Input format:
    Numbers 0-7 separated by spaces. 0 = rest.
    |  = bar line (ignored, but helps readability)
    —  = held note (extends previous note by 1 beat)
    .  = dotted note (extends previous by 50%)
    ,  = staccato (shortens note)
    ^n = octave shift: ^1 = up 1 octave, _1 = down 1 octave
    >n = accent (louder)

Example:
    "5 5 6 5 | 3 2 1 — | 5 5 6 5 | 3 2 1 — |"
    "5 5 ^5 3 | 2 2 ^2 1 | 6 6 5 3 | 2 1 2 3 |"

Output: Writes score_name.mid to current directory.
         Also prints a practice guide with fingering hints.

Instrument numbers (General MIDI):
    22  = Harmonica (口风琴/closest match)
    80  = Ocarina
    75  = Pan Flute
    79  = Recorder (木笛)
    0   = Acoustic Grand Piano
"""

import argparse, re, os, sys

def parse_jianpu(text, bpm=80):
    """Parse jianpu text into (notes, durations) list.
    
    Returns list of (midi_note, duration_in_beats, velocity) tuples.
    """
    # Clean and tokenize
    text = re.sub(r'\|', ' ', text)  # Remove bar lines
    text = re.sub(r'\s+', ' ', text.strip())
    
    tokens = text.split()
    
    # Default scale: C major (1=C, 2=D, 3=E, 4=F, 5=G, 6=A, 7=B)
    base_notes = {0: -1, 1: 60, 2: 62, 3: 64, 4: 65, 5: 67, 6: 69, 7: 71}
    
    results = []
    i = 0
    default_duration = 1.0  # One beat
    
    while i < len(tokens):
        token = tokens[i]
        
        # Check for octave shift prefix
        octave_shift = 0
        while token.startswith('^'):
            octave_shift += 12
            token = token[1:]
        while token.startswith('_'):
            octave_shift -= 12
            token = token[1:]
        
        # Check for accent
        velocity = 80  # mf
        while token.startswith('>'):
            velocity = 100
            token = token[1:]
        while token.startswith('<'):
            velocity = 60
            token = token[1:]
        
        if not token:
            i += 1
            continue
        
        # Check for duration suffix
        duration = default_duration
        note_str = token
        
        if note_str == '—' or note_str == '-' or note_str == '－':
            # Held note — extend previous note
            if results:
                prev_note, prev_dur, prev_vel = results[-1]
                results[-1] = (prev_note, prev_dur + duration, prev_vel)
            i += 1
            continue
        
        # Parse number
        try:
            num = int(note_str[0])
        except ValueError:
            i += 1
            continue
        
        note_part = note_str[0]
        rest = note_str[1:]
        
        # Dotted
        dotted = '.' in rest or '·' in rest
        staccato = ',' in rest
        
        if num == 0:
            midi_note = -1  # Rest
        elif num in base_notes:
            midi_note = base_notes[num] + octave_shift
        
        dur = duration
        if dotted:
            dur *= 1.5
        if staccato:
            dur *= 0.5
        
        results.append((midi_note, dur, velocity))
        i += 1
    
    return results, bpm


def generate_midi(notes_data, output_path="output.mid", instrument=22, 
                  bpm=80, time_sig=(4, 4)):
    """Generate a MIDI file from parsed jianpu data.
    
    Args:
        notes_data: (notes, durations, velocities) tuples
        output_path: Output MIDI file path
        instrument: General MIDI instrument number (22=harmonica)
        bpm: Beats per minute
        time_sig: (numerator, denominator)
    """
    try:
        from midiutil import MIDIFile
    except ImportError:
        print("Installing midiutil...")
        import subprocess, sys as _sys
        subprocess.run([_sys.executable, "-m", "pip", "install", "midiutil", "-q"])
        from midiutil import MIDIFile
    
    track = 0
    channel = 0
    
    midi = MIDIFile(1)
    midi.addTrackName(track, 0, "Jianpu Score")
    midi.addTempo(track, 0, bpm)
    midi.addTimeSignature(track, 0, time_sig[0], time_sig[1], 24)
    
    # Set instrument on the track
    midi.addProgramChange(track, channel, 0, instrument)
    
    # Add notes
    time = 0.0
    note_count = 0
    for midi_note, duration, velocity in notes_data:
        if midi_note >= 0:  # Not a rest
            midi.addNote(track, channel, midi_note, time, duration, velocity)
        time += duration
        note_count += 1
    
    with open(output_path, 'wb') as f:
        midi.writeFile(f)
    
    total_beats = time
    duration_sec = (total_beats / bpm) * 60
    minutes = int(duration_sec // 60)
    seconds = int(duration_sec % 60)
    
    return {
        "path": output_path,
        "notes": note_count,
        "duration": f"{minutes}:{seconds:02d}",
        "bpm": bpm,
        "instrument": instrument
    }


def generate_fingering_guide(note_sequence):
    """Generate right-hand fingering suggestions for melodica/jianpu.
    
    Returns a string with finger numbers over the note sequence.
    Principle: thumb on C/F, fingers fall naturally in key of C.
    """
    # Simple fingering rules for C major scale on melodica
    # 1=thumb, 2=index, 3=middle, 4=ring, 5=pinky
    # Default finger map for C major right hand
    finger_map = {
        # Note: midi number -> suggested finger
        60: 1,   # C (1)
        62: 2,   # D (2)  
        64: 3,   # E (3)
        65: 1,   # F (4)
        67: 2,   # G (5)
        69: 3,   # A (6)
        71: 4,   # B (7)
        72: 1,   # C' (高音1)
        74: 2,   # D' (高音2)
        76: 3,   # E' (高音3)
        77: 1,   # F' (高音4)
        79: 2,   # G' (高音5)
        81: 3,   # A' (高音6)
        83: 4,   # B' (高音7)
        48: 4,   # C low (低音1)
        50: 3,   # D low
        52: 2,   # E low
        53: 1,   # F low
        55: 1,   # G low
        57: 2,   # A low
        59: 3,   # B low
    }
    
    fingers = []
    for note, dur, _ in note_sequence:
        if note >= 0:
            f = finger_map.get(note % 12 + 60, "?")  # Normalize to octave for map
            # Adjust for actual octave
            octave = note // 12 - 5
            if octave < 0:
                f = finger_map.get(note, "?")
            fingers.append(str(f))
        else:
            fingers.append(".")
    
    return " ".join(fingers)


def generate_practice_guide(parsed_data, bpm):
    """Generate a structured practice guide for the piece."""
    notes, _ = parsed_data
    
    # Extract range
    pitches = [n for n, d, v in notes if n >= 0]
    if not pitches:
        return "No notes found."
    
    min_pitch = min(pitches)
    max_pitch = max(pitches)
    
    # Estimate difficulty
    range_span = max_pitch - min_pitch
    if range_span > 24:
        difficulty = "较难 (range > 2 octaves)"
    elif range_span > 12:
        difficulty = "中等 (range 1-2 octaves)"
    else:
        difficulty = "简单 (range < 1 octave)"
    
    # Count rests vs notes
    rest_count = sum(1 for n, d, v in notes if n < 0)
    note_count = len(notes) - rest_count
    
    guide = f"""== 练习指南 ==

曲目难度: {difficulty}
音域跨度: {range_span} 个半音 ({min_pitch}–{max_pitch} MIDI)
音符数: {note_count} | 休止符: {rest_count}
速度: ♩= {bpm}

【分步练习】
1. 慢速(♩=60) — 先分手逐小节练习，注意节奏稳定
2. 中速(♩={bpm}) — 连贯吹奏，注意气息
3. 原速(♩={bpm}) — 加表情处理

【指法提示】
- 口风琴右手拇指(1)负责C/F，食指(2)D/G，中指(3)E/A，无名指(4)B
- 遇到连续大跳(>5度)时注意提前换指
- 保持手掌放松，不要抬腕过高

【口风琴注意事项】
- 气息连贯，时值饱满 — 不要断气
- 高音区气流稍急，低音区稍缓
- 如果乐器没有变化音(黑键)，可将变化音还原吹奏
"""
    return guide


def main():
    parser = argparse.ArgumentParser(description="Convert jianpu to MIDI audio")
    parser.add_argument("input", nargs="?", help="Jianpu notation string (e.g. \"5 5 6 5 | 3 2 1 —\")")
    parser.add_argument("--file", "-f", help="Read jianpu from file")
    parser.add_argument("--bpm", type=int, default=80, help="Tempo in BPM (default: 80)")
    parser.add_argument("--instrument", "-i", type=int, default=22, 
                       help="GM instrument number (default: 22=Harmonica)")
    parser.add_argument("--output", "-o", default=None, help="Output MIDI file path")
    parser.add_argument("--guide", action="store_true", help="Print practice guide")
    parser.add_argument("--fingering", action="store_true", help="Print fingering annotations")
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.input:
        text = args.input
    else:
        # Interactive mode
        print("Enter jianpu notation (lines of numbers, empty line to finish):")
        lines = []
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            except EOFError:
                break
        text = " ".join(lines)
    
    if not text.strip():
        print("No input provided. Usage: jianpu2midi.py \"5 5 6 5 | 3 2 1 —\"")
        sys.exit(1)
    
    # Parse
    parsed, bpm = parse_jianpu(text, bpm=args.bpm)
    notes, _ = parsed
    
    if not notes:
        print("Could not parse any notes from input.")
        sys.exit(1)
    
    print(f"Parsed {len(notes)} notes.")
    
    # Generate output filename
    if args.output:
        output_path = args.output
    else:
        output_path = "jianpu_score.mid"
    
    # Generate MIDI
    result = generate_midi(parsed, output_path, instrument=args.instrument, bpm=bpm)
    
    # Print result
    print(f"\n✅ MIDI generated: {result['path']}")
    print(f"   Notes: {result['notes']} | Duration: {result['duration']}")
    print(f"   Tempo: ♩= {result['bpm']} | Instrument: GM#{result['instrument']}")
    
    # Fingering guide
    if args.fingering or args.guide:
        print(f"\n--- 指法参考 ---")
        print(f"  Note: ", " ".join(str(n[0]) if n[0] >= 0 else "·" for n in notes[:30]))
        print(f"  Finger:", generate_fingering_guide(notes[:30]))
        if len(notes) > 30:
            print(f"  ... ({len(notes) - 30} more notes)")
    
    # Practice guide
    if args.guide:
        print(f"\n{generate_practice_guide(parsed, bpm)}")
    
    # Playing instructions
    print(f"\n💡 To play: open {output_path} in any MIDI player or DAW")
    print(f"   Or convert to WAV: timidity {output_path} -Ow -o output.wav")


if __name__ == "__main__":
    main()
