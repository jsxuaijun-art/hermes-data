#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号 markdown 文章 → 官网 HTML 转换工具（联动方案A）
====================================================
用途：把 wechat-publish 生成的公众号文章 markdown 源稿，转换成可直接
粘贴进盈信官网后台富文本编辑器（eWebEditor）的 HTML。

微信专属元素会被删除：
  - #话题标签 块
  - CTA「觉得有用？请点屏幕右下角」多动作
  - 二维码图片 / 「长按识别添加」
  - 免费资料引导（公众号对话框回复...）
  - 完整公司落款块（【关于苏州盈信】...）—— 官网有自己公司页，正文只留一句简介

保留：标题、正文、小标题、加粗、表格、列表（含加粗），正文配图。
配图链接的图源前缀可配置（默认指向官网域名 www.yingxinkuaiji.com）。

用法：
  python3 md-to-website-html.py 文章.md [输出.html] [--site 图源前缀] [--with-company-intro]

参数：
  文章.md           必填，公众号 markdown 源稿路径
  输出.html         可选，默认 <输入名>-官网.html 放在输入同目录
  --site PREFIX     图源前缀，默认 https://www.yingxinkuaiji.com
  --with-company-intro  保留一句公司简介（默认保留，新口径"2001年成立、近二十年"）
  --no-company-intro    不保留公司简介

示例：
  python3 md-to-website-html.py /tmp/article_xukai_0802.md
  python3 md-to-website-html.py /tmp/a.md /tmp/官网.html --site https://www.yingxinkuaiji.com
"""

import io
import re
import sys
import os


def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()


def md_to_html(s):
    """简易 markdown → HTML，面向官网富文本编辑器（h2/p/strong/table/li/img）。"""
    lines = s.split('\n')
    out = []
    in_table = False
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # --- 表格 ---
        if re.match(r'^\|', line):
            if not in_table:
                out.append('<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;">')
                in_table = True
            cells = [c.strip() for c in line.strip('|').split('|')]
            # 跳过分隔行 |---|---|
            if all(re.match(r'^:?-+:?$', c) for c in cells if c):
                i += 1
                continue
            # 第一行是表头（前面是分隔行），后续是 td
            is_header = (
                i + 1 < len(lines)
                and re.match(r'^\|', lines[i + 1])
                and all(re.match(r'^:?-+:?$', c.strip()) for c in lines[i + 1].strip('|').split('|') if c.strip())
            )
            tag = 'th' if is_header else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            i += 1
            continue
        else:
            if in_table:
                out.append('</table>')
                in_table = False

        # --- 标题 ---
        hm = re.match(r'^(#{1,6})\s+(.*)', line)
        if hm:
            lvl = min(len(hm.group(1)), 4)
            out.append(f'<h{lvl}>{hm.group(2)}</h{lvl}>')
            i += 1
            continue

        # --- 图片 ---
        im = re.match(r'!\[(.*?)\]\((.*?)\)', line)
        if im:
            out.append(f'<p><img src="{im.group(2)}" alt="{im.group(1)}" style="max-width:100%;"></p>')
            i += 1
            continue

        # --- 加粗整段 ---
        if line.startswith('**') and line.endswith('**'):
            out.append(f'<p><strong>{line[2:-2]}</strong></p>')
            i += 1
            continue

        # --- 无序列表 ---
        if re.match(r'^\s*[-*]\s+', line):
            li = re.sub(r'^\s*[-*]\s+', '', line)
            li = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', li)
            out.append(f'<p>• {li}</p>')
            i += 1
            continue

        # --- 分隔线 ---
        if re.match(r'^\s*-{3,}\s*$', line):
            i += 1
            continue

        # --- 空行 ---
        if not line:
            i += 1
            continue

        # --- 普通段落（处理行内加粗） ---
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        out.append(f'<p>{para}</p>')
        i += 1

    if in_table:
        out.append('</table>')
    return '\n'.join(out)


def convert(src, out_path, site_prefix, keep_company_intro):
    text = read(src)

    # 1. 分离 frontmatter
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    fm = m.group(1) if m else ''
    body = m.group(2) if m else text
    title_m = re.search(r'title:\s*(.+)', fm)
    title = title_m.group(1).strip() if title_m else os.path.basename(src)

    # 2. 删微信尾部专属内容：从话题标签 / 公司落款 处截断
    #    ⚠️ 注意：`\n#话题` 是话题标签（单个#后直接跟中文），而 `\n## 标题` 是
    #    正文小标题（两个#），不能误截。话题标签通常带空格或无空格紧跟中文，且
    #    前面是空行。用正则精确匹配「空行 + 单个# + 中文标签」。
    tail_marker = None
    # 话题标签块：如 \n#虚开发票 #税务合规 ... （空行后的单#行）
    m_tag = re.search(r'\n\s*\n#(?!#)([\u4e00-\u9fa5])', body)
    if m_tag:
        tail_marker = m_tag.start()
    # 公司落款块：如 【关于苏州盈信】
    m_comp = re.search(r'\n\s*\n【关于(苏州)?盈信】', body)
    if m_comp and (tail_marker is None or m_comp.start() < tail_marker):
        tail_marker = m_comp.start()
    if tail_marker is not None:
        body = body[:tail_marker]
    body = re.sub(r'\n---\s*\n*$', '', body).strip()

    # 3. markdown -> HTML
    body_html = md_to_html(body)

    # 4. 图源前缀替换：把 http://127.0.0.1:8080/ 换成官网图源前缀
    body_html = body_html.replace('http://127.0.0.1:8080/', site_prefix.rstrip('/') + '/')

    # 5. 组装
    company_intro = ''
    if keep_company_intro:
        company_intro = (
            '<p style="color:#888;font-size:12px;margin-top:30px;'
            'border-top:1px solid #eee;padding-top:10px;">'
            '苏州盈信企业管理有限公司成立于2001年，由高级会计师江敏创办，'
            '专注中小企业财税服务近二十年。服务覆盖苏州及上海地区。'
            '</p>'
        )

    html = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        f'<meta charset="UTF-8">\n<title>{title}</title>\n'
        '</head>\n<body>\n'
        f'<h1 style="font-size:22px;color:#333;">{title}</h1>\n'
        '<p style="color:#888;font-size:13px;">苏州盈信企业管理 · 财税知识分享</p>\n<hr>\n'
        f'{body_html}\n'
        f'{company_intro}\n'
        '</body>\n</html>\n'
    )

    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # 自检报告
    checks = {
        '裸**残留': html.count('**'),
        '微信标签(#)': len(re.findall(r'#[\u4e00-\u9fa5]', body_html)),
        '二维码/CTA': len(re.findall(r'二维码|觉得有用|长按识别|免费领资料', html)),
        '图片路径重复images/images': html.count('images/images'),
        '旧口径(2009/16年/17年)': len(re.findall(r'2009年|服务16年|服务17年|17年合规', html)),
        '新口径(2001/近二十年)': html.count('近二十年'),
    }
    print('=== 转换完成 ===')
    print(f'输入 : {src}')
    print(f'输出 : {out_path}')
    print(f'标题 : {title}')
    print(f'图片 : {body_html.count("<img")} 张')
    print('=== 自检 ===')
    ok = True
    for name, val in checks.items():
        if name.startswith('新口径'):
            status = '✓' if val >= 1 else '⚠'
        elif name.startswith('图片路径重复'):
            status = '✓' if val == 0 else '⚠'
        else:
            status = '✓' if val == 0 else '⚠'
        print(f'  {status} {name}: {val}')
        if status == '⚠':
            ok = False
    print('=== ' + ('全部通过 ✅' if ok else '有需人工检查项 ⚠') + ' ===')


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    src = sys.argv[1]
    site_prefix = 'https://www.yingxinkuaiji.com'
    keep_company_intro = True
    out_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--site' and i + 1 < len(args):
            site_prefix = args[i + 1]
            i += 2
        elif args[i] == '--with-company-intro':
            keep_company_intro = True
            i += 1
        elif args[i] == '--no-company-intro':
            keep_company_intro = False
            i += 1
        elif not args[i].startswith('--'):
            out_path = args[i]
            i += 1
        else:
            i += 1

    if not out_path:
        base = os.path.splitext(os.path.basename(src))[0]
        out_path = os.path.join(os.path.dirname(src) or '.', f'{base}-官网.html')

    convert(src, out_path, site_prefix, keep_company_intro)


if __name__ == '__main__':
    main()
