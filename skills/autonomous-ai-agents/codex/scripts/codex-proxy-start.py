#!/usr/bin/env python3
"""codex-proxy-start: Start/stop/status for the codex translation proxy.

Usage:
  codex-proxy-start start     Start the proxy daemon
  codex-proxy-start stop      Stop the proxy
  codex-proxy-start restart   Restart the proxy
  codex-proxy-start status    Check if proxy is running
  codex-proxy-start log       Show the proxy log

Install:
  cp .../codex-proxy-start.py ~/bin/codex-proxy-start
  chmod +x ~/bin/codex-proxy-start
"""
import os, sys, signal, time, subprocess

PIDFILE = '/tmp/codex-proxy.pid'
PROXY = os.path.expanduser(
    '~/.hermes/skills/autonomous-ai-agents/codex/scripts/codex-proxy.py'
)
LOGFILE = '/tmp/codex-proxy.log'


def status():
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
        if os.path.isdir(f'/proc/{pid}'):
            return pid, 'running'
    return None, 'stopped'


def cmd_start():
    pid, st = status()
    if st == 'running':
        print(f'Proxy already running (PID {pid})')
        return
    if not os.path.exists(PROXY):
        print(f'Proxy script not found: {PROXY}')
        sys.exit(1)
    p = subprocess.Popen(
        [sys.executable, PROXY],
        stdout=open(LOGFILE, 'w'),
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    with open(PIDFILE, 'w') as f:
        f.write(str(p.pid))
    time.sleep(1.5)
    if os.path.isdir(f'/proc/{p.pid}'):
        print(f'Proxy started (PID {p.pid}), log: {LOGFILE}')
    else:
        print('Proxy failed to start, check log:', LOGFILE)
        sys.exit(1)


def cmd_stop():
    pid, st = status()
    if st == 'stopped':
        print('Proxy not running')
        return
    try:
        os.kill(pid, signal.SIGTERM)
        for _ in range(10):
            time.sleep(0.3)
            if not os.path.isdir(f'/proc/{pid}'):
                break
        if os.path.isdir(f'/proc/{pid}'):
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.3)
        print(f'Proxy stopped (PID {pid})')
    except ProcessLookupError:
        print('Proxy already stopped')
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def cmd_status():
    pid, st = status()
    if st == 'running':
        print(f'Proxy running (PID {pid})')
    else:
        print('Proxy stopped')


def cmd_restart():
    cmd_stop()
    time.sleep(1)
    cmd_start()


def cmd_log():
    if os.path.exists(LOGFILE):
        with open(LOGFILE) as f:
            print(f.read())
    else:
        print('No log file found')


ACTIONS = {
    'start': cmd_start,
    'stop': cmd_stop,
    'restart': cmd_restart,
    'status': cmd_status,
    'log': cmd_log,
}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ACTIONS:
        print('Usage: codex-proxy-start {start|stop|restart|status|log}')
        sys.exit(1)
    ACTIONS[sys.argv[1]]()
