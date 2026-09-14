#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leak_scan.py — 推送前「真实身份泄漏扫描」
作用：扫描 git 仓库(同步夹)内所有被跟踪文件的文本，检出疑似未脱敏的敏感主体信息。
规则(与 security/desensitization skill 一致)：
  ① 统一社会信用代码(18位)：若末8位不是 XXXXXXXXX(全X) → 判定为未脱敏真实码
  ② 身份证号(18位)：含真实出生日期字段(8位数字) → 判定为未脱敏真实号
  ③ 可选精确词块表：从外部文件读入的精确字符串(绝对不用写本文件避免再泄漏)
用法(在 hermes_push.sh 里、git add 之后/sync_guard 之前调用)：
  python3 <本脚本> <同步夹路径> [--blocklist <精确词表文件>]
  返回 0 = 干净可推送；1 = 检测到泄漏，中止
本文件本身不含任何真实身份字符串(全部用正则), 可安全入库。
"""
import os, re, subprocess, sys

CREDIT_ALPHABET = '0123456789ABCDEFGHJKLMNPQRTUWXY'  # 统一社会信用代码合法字符集
# 候选：字母表内 18 个连续字符
CREDIT_RE = re.compile(r'[0-9A-HJ-NPQRTUWXY]{18}')


def is_suspicious_credit(tok):
    """判断是否疑似『未脱敏』的真实统一社会信用代码。
    收紧规则(滤掉数字串/二进制/随机串/政务机关码之类的误报)：
      ① 必须正好18位
      ② 首位是 5 或 9(客户主体:5=民政/民办非企业·社团,9=工商/企业；机关事业单位码以1开头,属政务公开数据不拦)
      ③ 末8位不是全 X(全 X 即已脱敏,跳过)
      ④ 第2~17位至少含2个字母(真实主体码必有字母,纯数字串不是码)
    """
    if len(tok) != 18:
        return False
    if tok[0] not in '59':
        return False
    if tok[-8:] == 'XXXXXXXX':
        return False           # 已脱敏
    letters = sum(1 for ch in tok[1:17] if ch.isalpha())
    return letters >= 2
# ② 身份证号：6位地区 + 真实8位出生日期(19xx/20xx, 月日合理) + 3位 + 校验位
ID_RE = re.compile(
    r'(?<!\d)([1-9][0-9]{5}(?:19|20)[0-9]{2}'
    r'(?:0[1-9]|1[0-2])(?:0[1-9]|[12][0-9]|3[01])[0-9]{3}[0-9X])(?!\d)')


def tracked_files(repo):
    try:
        out = subprocess.check_output(
            ['git', '-C', repo, 'ls-files', '-z'],
            stderr=subprocess.DEVNULL)
        return [f for f in out.decode('utf-8', 'replace').split('\0') if f]
    except Exception:
        return []


def scan_file(path, blocklist):
    leaks = []
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except Exception:
        return []
    # 只扫文本类(跳过二进制/极大文件)
    if len(raw) > 5_000_000:
        return []
    try:
        text = raw.decode('utf-8', 'replace')
    except Exception:
        return []
    # ① 信用代码
    for m in CREDIT_RE.findall(text):
        if is_suspicious_credit(m):
            leaks.append((m[:4] + '…', '信用代码疑似未脱敏'))
    # ② 身份证号(含真实出生日期)
    for m in ID_RE.findall(text):
        leaks.append((m[:6] + '…', '身份证号疑似未脱敏'))
    # ③ 精确词块(外部 blocklist)
    for tok in blocklist:
        if tok and tok in text:
            leaks.append((tok[:8] + '…', '命中精确词块'))
    return leaks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print('[leak_scan] 用法: leak_scan.py <同步夹> [--blocklist <词表文件>]')
        return 2
    repo = args[0]
    blocklist = []
    if '--blocklist' in sys.argv:
        i = sys.argv.index('--blocklist')
        if i + 1 < len(sys.argv):
            bp = sys.argv[i + 1]
            try:
                with open(bp, 'r', encoding='utf-8') as f:
                    blocklist = [ln.strip() for ln in f
                                 if ln.strip() and not ln.lstrip().startswith('#')]
            except Exception:
                blocklist = []
    # 默认本地精确词表(不随 skill 推送, 存 ~/.hermes/leak-blocklist.txt)
    if not blocklist:
        default = os.path.expanduser('~/.hermes/leak-blocklist.txt')
        if os.path.exists(default):
            try:
                with open(default, 'r', encoding='utf-8') as f:
                    blocklist = [ln.strip() for ln in f
                                 if ln.strip() and not ln.lstrip().startswith('#')]
            except Exception:
                blocklist = []

    findings = []
    for rel in tracked_files(repo):
        full = rel if os.path.isabs(rel) else os.path.join(repo, rel)
        if os.path.isfile(full):
            for tok, why in scan_file(full, blocklist):
                findings.append((rel, tok, why))

    if findings:
        print('')
        print('=' * 70)
        print('[leak_scan 🔴] 检测到疑似未脱敏的真实身份信息，推送已中止：')
        print('=' * 70)
        for rel, tok, why in findings:
            print(f'   ✗ {rel}  [{why}] {tok}')
        print('  (请先用 security/desensitization skill 脱敏后重试)')
        print('  (若确需强制推送:  export LEAK_SCAN_BYPASS=1 再跑 — 风险自负)')
        print('=' * 70)
        return 1 if os.environ.get('LEAK_SCAN_BYPASS') != '1' else 0
    print('[leak_scan] ✅ 未检出疑似敏感身份信息，可安全推送。')
    return 0


if __name__ == '__main__':
    sys.exit(main())