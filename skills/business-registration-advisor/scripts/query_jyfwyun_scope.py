#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直连 jyfwyun.com 经营范围规范表述库 API，按关键词+行政区划码查规范条目。

演示了：省市县三级下钻拿 ac（行政区划码）→ /cross/search 拉规范条目。

用法：
  python3 query_jyfwyun_scope.py --keyword 歌舞娱乐
  python3 query_jyfwyun_scope.py --keyword 食品 --ac 320506      # 指定区（自贸区外交给用户选）
  python3 query_jyfwyun_scope.py --tree                        # 只打印 江苏→苏州→辖区 树

原理要点（勿改）：
  - 请求必须用 JSON body 传 {"keyword","pageNum","pageSize","ac"}；
    把 ac 放 URL query 会返回 “无效的区域码”(code 500)。
  - 结果在 result.data.records，不是 result.list。
  - permitType: 0=一般事项 1=前置许可 2=后置许可 4=备案/行业监管类。
  - 高频请求会被限流(HTTP 503)，须指数退避重试。
"""
import urllib.request, json, sys, time, argparse

H = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
BASE = "https://backapi.jyfwyun.com/cloud-service"


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def retry_post(path, body, attempts=6):
    for i in range(attempts):
        try:
            return post(path, body)
        except Exception:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError("仍 503/失败: %s" % path)


def region_tree():
    # 省级：pcode 为空；下级：pcode=<父节点的 id>（注意用 id，不是 ac）
    provs = retry_post("/cross/regionList", {})
    out = []
    for p in provs.get("result") or []:
        if p.get("text") != "江苏省":
            continue
        out.append((p["text"], p.get("ac"), p.get("id")))
        # 注意：regionList 的子级参数 pcode 必须走 URL query（?pcode=<父id>），
        # 放 JSON body 会被端点忽略、返回省级列表。
        cities = retry_post("/cross/regionList?pcode=" + p["id"], {})
        for c in cities.get("result") or []:
            if c.get("text") != "苏州市":
                continue
            out.append(("  " + c["text"], c.get("ac"), c.get("id")))
            dists = retry_post("/cross/regionList?pcode=" + c["id"], {})
            for d in dists.get("result") or []:
                out.append(("    " + d["text"], d.get("ac"), d.get("id")))
    return out


def search(keyword, ac, pages=3, size=20):
    seen = {}
    for pg in range(1, pages + 1):
        body = {"keyword": keyword, "pageNum": pg, "pageSize": size, "ac": ac}
        d = retry_post("/cross/search", body)
        recs = ((d.get("result") or {}).get("data") or {}).get("records") or []
        for it in recs:
            si = it.get("standardItem")
            if not si:
                continue
            seen[it.get("scopeCode") or si] = {
                "item": si, "gb": it.get("gbName"),
                "permit": it.get("permitType"),
                "desc": (it.get("description") or "")[:70],
            }
        total = ((d.get("result") or {}).get("data") or {}).get("pages") or 1
        if pg >= total:
            break
    return seen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword")
    ap.add_argument("--ac", default=None)
    ap.add_argument("--tree", action="store_true")
    a = ap.parse_args()

    if a.tree:
        for name, ac, _ in region_tree():
            print("%s  ac=%s" % (name, ac))
        sys.exit(0)

    if not a.ac:
        print("先用 --tree 拿到目标区(自贸区外)的 ac，再 --ac 指定；或直接给 --ac。", file=sys.stderr)
        sys.exit(1)
    if not a.keyword:
        print("需要 --keyword", file=sys.stderr)
        sys.exit(1)

    for code, info in sorted(search(a.keyword, a.ac).items(), key=lambda kv: kv[1]["item"]):
        print("%s | %s | %s | permit=%s\n    %s" % (
            code, info["item"], info["gb"], info["permit"], info["desc"]))
