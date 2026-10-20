#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易163邮箱读信工具 (POP3通道)
背景：163 的 IMAP 对第三方新 IP 触发 "Unsafe Login" 风控，但 POP3 放行。
      himalaya 不支持 POP3（feature 列表无 +pop3），故用 Python poplib 直连。

用法:
  python3 read_163.py            # 列出最近10封
  python3 read_163.py --all      # 列出全部封数
  python3 read_163.py --new      # 只看最近3封
  python3 read_163.py --id 5     # 读第5封全文

服务器: pop.163.com:995 (POP3S/SSL)
凭据: 账号 + 客户端授权码（非登录密码）
"""
import poplib, email, sys
from email.header import decode_header

HOST, PORT = 'pop.163.com', 995
# 替换为实际账号与客户端授权码
USER, PASS = '替换@163.com', '替换授权码'

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

def list_mails(limit=10):
    M = poplib.POP3_SSL(HOST, PORT, timeout=20)
    M.user(USER); M.pass_(PASS)
    n, size = M.stat()
    print(f"📮 邮箱统计：共 {n} 封，{size/1024/1024:.1f} MB\n")
    ids = range(max(1, n - limit + 1), n + 1)
    for i in ids:
        try:
            resp, lines, octets = M.retr(i)
            msg = email.message_from_bytes(b'\r\n'.join(lines))
            subj = decode_str(msg.get('Subject', '(无主题)'))[:38]
            frm = decode_str(msg.get('From', '?'))[:28]
            date = msg.get('Date', '?')[:17]
            print(f"  {i:>2} | {frm:<28} | {date:<17} | {subj}")
        except Exception as e:
            print(f"  {i:>2} | 读取失败: {e}")
    M.quit()

def read_one(i):
    M = poplib.POP3_SSL(HOST, PORT, timeout=20)
    M.user(USER); M.pass_(PASS)
    n, _ = M.stat()
    if i > n:
        print(f"❌ 只有 {n} 封，没有第 {i} 封")
        return
    resp, lines, octets = M.retr(i)
    msg = email.message_from_bytes(b'\r\n'.join(lines))
    print(f"📧 第 {i} 封")
    print(f"  主题: {decode_str(msg.get('Subject',''))}")
    print(f"  发件: {decode_str(msg.get('From',''))}")
    print(f"  时间: {msg.get('Date','')}")
    print("  " + "─" * 50)
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode(part.get_content_charset() or 'utf-8', 'ignore')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or 'utf-8', 'ignore')
    print("正文:\n" + body[:1500])
    M.quit()

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--all' in args:
        list_mails(9999)
    elif '--id' in args:
        read_one(int(args[args.index('--id') + 1]))
    elif '--new' in args:
        list_mails(3)
    else:
        list_mails(10)
