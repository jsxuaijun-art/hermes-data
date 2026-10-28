#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""faster-whisper 转写 worker —— 由 ~/videoenv 的 python 运行。
用法: <videoenv-python> _whisper_worker.py <wav> <out.md> <size> <prompt>
"""
import sys
from faster_whisper import WhisperModel

wav, out, size, prompt = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
m = WhisperModel(size, device="cpu", compute_type="int8")
segs, info = m.transcribe(wav, language="zh", beam_size=5,
                          vad_filter=True, initial_prompt=prompt)
lines = [f"[{s.start:.1f}-{s.end:.1f}] {s.text}" for s in segs]
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
