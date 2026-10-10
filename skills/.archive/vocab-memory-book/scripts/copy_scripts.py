#!/usr/bin/env python3
"""Copy the full build_suzhou.py from /tmp to skill directory."""
import shutil, os
src = '/tmp/build_suzhou.py'
dst = os.path.expanduser('~/.hermes/skills/productivity/vocab-memory-book/scripts/build_suzhou_full.py')
shutil.copy2(src, dst)
print(f"Copied {os.path.getsize(dst)} bytes")
