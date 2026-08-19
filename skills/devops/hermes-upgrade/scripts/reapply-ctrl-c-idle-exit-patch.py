#!/usr/bin/env python3
"""Re-apply the local 'Ctrl+C idle does NOT exit the CLI' customization to cli.py.

Upstream Hermes maps Ctrl+Q as the alternate quit shortcut. This patch makes
the *idle* Ctrl+C stop quitting the CLI (agent-interrupt / buffer-clear
behaviour is unchanged) so a stray Ctrl+C can never kick the user out. To quit
use Ctrl+Q (or /quit). Flip self._ctrl_c_idle_exits to True to restore old
behaviour.

Usage:
    python reapply-ctrl-c-idle-exit-patch.py /path/to/cli.py

Safe to run repeatedly: prints "ALREADY APPLIED" if the patch is present.
If the upstream block changed enough that the anchor no longer matches, it
prints an error and does NOT modify the file.
"""

import io
import sys

MARKER = "# If everything is already empty: local customization"

OLD = """            # If everything is already empty, exit.
            elif event.app.current_buffer.text or self._attached_images:
                event.app.current_buffer.reset()
                self._attached_images.clear()
                event.app.invalidate()
            else:
                self._should_exit = True
                event.app.exit()
"""

NEW = """            # If everything is already empty: local customization \u2014 Ctrl+C
            # does NOT quit the CLI here. It would be too easy to get kicked
            # out by a stray Ctrl+C. To quit use Ctrl+Q (or /quit). Flip
            # self._ctrl_c_idle_exits to True to restore the old behaviour.
            elif event.app.current_buffer.text or self._attached_images:
                event.app.current_buffer.reset()
                self._attached_images.clear()
                event.app.invalidate()
            else:
                if getattr(self, "_ctrl_c_idle_exits", False):
                    self._should_exit = True
                    event.app.exit()
                else:
                    event.app.current_buffer.reset()
                    event.app.invalidate()
                    _cprint(
                        "\\n(Ctrl+C \u4e0d\u4f1a\u9000\u51fa Hermes\u3002\u8981\u9000\u51fa\u8bf7\u7528 Ctrl+Q \u6216 /quit)"
                    )
"""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python reapply-ctrl-c-idle-exit-patch.py /path/to/cli.py")
        return 2
    path = sys.argv[1]
    with io.open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    if MARKER in src:
        print("ALREADY APPLIED - no change.")
        return 0
    if OLD not in src:
        print(
            "ERROR: could not find the upstream idle-Ctrl+C block. "
            "cli.py may have changed upstream; inspect manually before applying."
        )
        return 1
    src = src.replace(OLD, NEW, 1)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    print("APPLIED - idle Ctrl+C no longer exits the CLI (use Ctrl+Q to quit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
