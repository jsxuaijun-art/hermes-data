#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易163邮箱 · 指定邮件附件下载（POP3）

背景: himalaya 对 163 的 IMAP SELECT 报 "Unsafe Login" 风控，POP3 放行。
      163 的通知类邮件（数电票、合同、回执）正文只是告知，真正的文件在附件里。
      cron 巡检发现可执行邮件（如开给本公司的电子发票）时用本脚本取附件。

凭据: 复用同目录 read_163_full.py 的 get_creds()（事实源是 ~/.hermes/scripts/read_163_daily.py），
      本文件不维护凭据。也可环境变量 MAIL163_USER / MAIL163_PASS 覆盖。

用法:
  # 按 POP3 序号下载（序号来自 read_163_daily.py / read_163_full.py 的输出）
  python3 fetch_163_attachment.py 21

  # 按主题关键词定位最近 N 封内的匹配邮件并下载
  python3 fetch_163_attachment.py --subject "电子发票" --scan 10

  # 指定保存目录（默认在 Windows 桌面建 "邮件附件-<日期>-<主题关键词>" 文件夹）
  python3 fetch_163_attachment.py 21 --out "/mnt/c/Users/Admin/Desktop/某文件夹"

输出: 保存的附件路径列表 + 主题/发件人/日期，便于核对是否下对邮件。
"""
import poplib, email, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_163_full import get_creds, decode_str  # noqa: E402  (同目录复用凭据与头解码，本文件不维护凭据)

HOST, PORT = 'pop.163.com', 995
DESKTOP = '/mnt/c/Users/Admin/Desktop'


def pick_msg(M, total, index=None, subject_kw=None, scan=10):
    """按 POP3 序号或主题关键词选定一封邮件，返回 (序号, message)。"""
    if index is not None:
        resp, lines, _ = M.retr(index)
        return index, email.message_from_bytes(b'\r\n'.join(lines))
    if subject_kw:
        for i in range(total, max(0, total - scan), -1):  # 新的在前
            try:
                resp, lines, _ = M.retr(i)
                msg = email.message_from_bytes(b'\r\n'.join(lines))
                if subject_kw in decode_str(msg.get('Subject', '')):
                    return i, msg
            except Exception:
                continue
        raise SystemExit(f'最近{scan}封内未找到主题含 "{subject_kw}" 的邮件')
    raise SystemExit('请给 POP3 序号 或 --subject 关键词')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    index = int(args[0]) if args and args[0].isdigit() else None
    kw = None
    if '--subject' in sys.argv:
        kw = sys.argv[sys.argv.index('--subject') + 1]
    scan = int(sys.argv[sys.argv.index('--scan') + 1]) if '--scan' in sys.argv else 10

    USER, PASS = get_creds()
    M = poplib.POP3_SSL(HOST, PORT, timeout=30)
    M.user(USER)
    M.pass_(PASS)
    total, _ = M.stat()

    i, msg = pick_msg(M, total, index=index, subject_kw=kw, scan=scan)
    subj = decode_str(msg.get('Subject', '(无主题)'))
    print(f'[{i}] {subj}')
    print(f'    From: {decode_str(msg.get("From", "?"))}  Date: {msg.get("Date", "")}')

    if '--out' in sys.argv:
        outdir = sys.argv[sys.argv.index('--out') + 1]
    else:
        kw_short = (kw or re.sub(r'[^\w\u4e00-\u9fff]+', '', subj)[:12] or 'mail')
        outdir = os.path.join(DESKTOP, f'邮件附件-{msg.get("Date", "")[:16].replace(" ", "")}-{kw_short}')
    os.makedirs(outdir, exist_ok=True)

    n = 0
    for part in msg.walk():
        fn = part.get_filename()
        if not fn:
            continue
        fn = decode_str(fn)
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        path = os.path.join(outdir, fn)
        with open(path, 'wb') as f:
            f.write(payload)
        n += 1
        print(f'    ✔ {path}  ({len(payload)} bytes)')
    if n == 0:
        print('    (该邮件无附件)')
    M.quit()


if __name__ == '__main__':
    main()
