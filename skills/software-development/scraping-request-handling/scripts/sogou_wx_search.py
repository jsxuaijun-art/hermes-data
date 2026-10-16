#!/usr/bin/env python3
# 搜狗微信文章检索（可靠版）— Python 直连解析器。
# 背景(2026-10 实测): 微信图文对通用搜索引擎不可见，唯一外部入口是搜狗微信(wx.sogou.com)的抽样收录。
#   wechat-article-search 技能的 node 版 search_wechat.js 会静默恒返回 total:0（解析器失效），
#   不要依赖它；直接用本脚本抓结果页解析，检索 + 真实链接还原均已实测可用。
# 用法:
#   python3 sogou_wx_search.py <关键词> [数量]
#   例: python3 sogou_wx_search.py 相城 企业综合服务中心 8
# 输出: 每行 = 公众号名 | 标题 | 日期，下一行 = 还原后的真实 mp.weixin.qq.com 链接
# 局限(记住再交付): ①搜狗只是抽样收录，搜不到≠不存在; ②图片内文字不上索引(要OCR);
#   ③签名链接有时效，过期就提示用户在微信内按公众号名搜索。
import urllib.request, urllib.parse, ssl, re, html as H, http.cookiejar, time, sys

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126 Safari/537.36')

def opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [('User-Agent', UA)]
    return op

OP = opener()

def wx_search(q, num=8):
    u = ('https://weixin.sogou.com/weixin?type=2&query=' + urllib.parse.quote(q)
         + '&ie=utf8&page=1')
    h = OP.open(u, timeout=30).read().decode('utf-8', 'ignore')
    # 每条结果是一个 <li id="sogou_vr_11002601_box_N"> ... </li>；必须用 cookie 会话，
    # 后续 /link 跳转解析依赖本页种下的 cookie（换个新请求会返回空/反爬）。
    items = re.findall(r'<li id="sogou_vr_11002601_box_\d+".*?</li>', h, re.S)
    out = []
    for it in items:
        m = re.search(r'<h3>\s*<a[^>]*href="([^"]+)".*?>(.*?)</a>', it, re.S)
        if not m:
            continue
        def g(p):
            mm = re.search(p, it, re.S)
            return H.unescape(re.sub(r'<[^>]+>', '', mm.group(1))).strip() if mm else ''
        src = g(r'id="sogou_vr_11002601_account_\d+"[^>]*>(.*?)</a>')
        d = re.search(r"timeConvert\('(\d+)'\)", it)
        out.append({
            'title': g(r'<h3>\s*<a[^>]*>(.*?)</a>'),
            'account': src,
            'date': time.strftime('%Y-%m-%d', time.localtime(int(d.group(1)))) if d else '',
            'rel': m.group(1).replace('&amp;', '&'),
        })
    return out[:num]

def resolve(rel):
    # 搜狗中间链接 → 真实 mp.weixin.qq.com/s?src=11&signature=... URL。
    # 页面里是一串 `url += '...'` 语句，拼接后去掉 @（占位符）。
    # 坑: URL 里带空格（query 参数回显时会成字面空格）会报 "URL can't contain control characters"，
    # 必须先 replace(' ','%20')。
    u = ('https://weixin.sogou.com' + rel).replace(' ', '%20')
    try:
        p = OP.open(u, timeout=30).read().decode('utf-8', 'ignore')
        parts = re.findall(r"url \+= '([^']*)'", p)
        return ''.join(parts).replace('@', '')
    except Exception as e:
        return 'RESOLVE_ERR %s' % e

if __name__ == '__main__':
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    try:
        for r in wx_search(q, n):
            print('【%s】%s | %s' % (r['account'], r['title'], r['date']))
            print('   ', resolve(r['rel']))
            time.sleep(2)  # 节流，防 IP 限流
    except Exception as e:
        print('SEARCH_ERR', e)
