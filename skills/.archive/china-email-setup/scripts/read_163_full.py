#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易163邮箱 · 全文批量读取（triage 专用）
背景: himalaya 对 163 报 NO SELECT Unsafe Login（IMAP 风控），POP3 放行。
      本脚本专为「cron 摘要之后需要读全文做分类」设计：
      read_163_daily.py 只出最近5封主题行，本脚本一次连接批量读最近 N 封的
      完整正文（优先 text/plain；HTML-only 邮件如财新/DeepSeek 通知剥标签兜底）。

用法:
  python3 read_163_full.py                # 读最近5封全文（与 daily 摘要数量一致）
  python3 read_163_full.py 3              # 读最近3封
  python3 read_163_full.py 10 --max 800   # 正文最多800字符

凭据来源（避免多文件重复维护）:
  1) 环境变量 MAIL163_USER / MAIL163_PASS
  2) 解析 ~/.hermes/scripts/read_163_daily.py 里的 USER/PASS（唯一事实源）
  3) 均无 → 报错退出
"""
import poplib, email, re, sys, os
from email.header import decode_header

HOST, PORT = 'pop.163.com', 995
DAILY_SCRIPT = os.path.expanduser('~/.hermes/scripts/read_163_daily.py')


def get_creds():
    u = os.environ.get('MAIL163_USER')
    p = os.environ.get('MAIL163_PASS')
    if u and p:
        return u, p
    if os.path.exists(DAILY_SCRIPT):
        src = open(DAILY_SCRIPT, encoding='utf-8').read()
        m = re.search(r"USER, PASS = '([^']+)', '([^']+)'", src)
        if m:
            return m.group(1), m.group(2)
    raise SystemExit('未找到163凭据: 设 MAIL163_USER/MAIL163_PASS 或确认 read_163_daily.py 存在')


def decode_str(s):
    if not s:
        return ''
    out = []
    for t, enc in decode_header(s):
        if isinstance(t, bytes):
            try:
                out.append(t.decode(enc or 'utf-8', 'ignore'))
            except Exception:
                out.append(t.decode('utf-8', 'ignore'))
        else:
            out.append(t)
    return ''.join(out)


def get_body(msg, maxlen=2000):
    """优先 text/plain；HTML-only 邮件剥标签兜底。"""
    candidates = []          # (priority, payload_bytes, charset)
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            disp = part.get('Content-Disposition') or ''
            if ct == 'text/plain' and 'attachment' not in disp:
                candidates.append((0, payload, part.get_content_charset()))
            elif ct == 'text/html' and 'attachment' not in disp:
                candidates.append((1, payload, part.get_content_charset()))
        if not candidates:
            return '(无文本内容)'
        candidates.sort(key=lambda c: c[0])
        prio, payload, charset = candidates[0]
    else:
        payload = msg.get_payload(decode=True)
        if not payload:
            return '(无文本内容)'
        prio, charset = 0, msg.get_content_charset()
    text = payload.decode(charset or 'utf-8', 'ignore')
    if prio == 1:  # html 兜底
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
    else:
        text = re.sub(r'[ \t]+', ' ', text)
    return text[:maxlen]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
    maxlen = 2000
    if '--max' in sys.argv:
        maxlen = int(sys.argv[sys.argv.index('--max') + 1])
    USER, PASS = get_creds()
    M = poplib.POP3_SSL(HOST, PORT, timeout=30)
    M.user(USER)
    M.pass_(PASS)
    total, _ = M.stat()
    if total == 0:
        print('(邮箱为空)')
        return
    for i in range(max(1, total - n + 1), total + 1):
        try:
            resp, lines, _ = M.retr(i)
            msg = email.message_from_bytes(b'\r\n'.join(lines))
            print('=' * 78)
            print(f'[{i}] From: {decode_str(msg.get("From", "?"))}')
            print(f'    Subject: {decode_str(msg.get("Subject", "(无主题)"))}')
            print(f'    Date: {msg.get("Date", "")}')
            print(f'    Body: {get_body(msg, maxlen)}')
        except Exception as e:
            print(f'[{i}] ERROR: {e}')
    M.quit()


if __name__ == '__main__':
    main()