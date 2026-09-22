import os, sys, json, urllib.request, urllib.error, urllib.parse

# 清空本地代理，避免被 127.0.0.1:7890 等死代理拦截（见 SKILL.md 第六节）
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_k, None)

API_URL = "https://qyapi.ipaybuy.cn/api/video"
APP_ID = os.environ.get("QIYUN_APP_ID", "在此填入你的奇云AppId")
APP_KEY = os.environ.get("QIYUN_APP_KEY", "在此填入你的奇云AppKey")

def _get_json(url):
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        print("HTTPError:", e.code, body); sys.exit(1)
    except Exception as e:
        print("RequestError:", e); sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("用法: python parse_download_qiyun.py <视频号链接> [输出mp4路径]")
        sys.exit(1)
    url = sys.argv[1]
    vid = url.rstrip("/").split("/")[-1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("videos", vid + ".mp4")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    if APP_ID.startswith("在此填入") or APP_KEY.startswith("在此填入"):
        print("错误：未配置奇云凭据。请设置环境变量 QIYUN_APP_ID / QIYUN_APP_KEY，"
              "或在脚本顶部常量填入。注册：https://qyapi.ipaybuy.cn/")
        sys.exit(1)

    q = urllib.parse.urlencode({"appId": APP_ID, "appKey": APP_KEY, "url": url})
    api = f"{API_URL}?{q}"
    print("请求奇云解析接口 ...", API_URL)
    result = _get_json(api)

    code = result.get("code")
    print("code:", code, "| msg:", result.get("msg", ""))
    if str(code) != "200":
        print("解析失败:", json.dumps(result, ensure_ascii=False)[:500]); sys.exit(1)

    data = result.get("data") or {}
    # 奇云返回多个地址：mediaUrl=无加密直链(首选，可直接下载)；video_url=中转地址(兜底)
    video_url = data.get("mediaUrl") or data.get("video_url") or data.get("video_url_v2")
    title = data.get("title")
    if title:
        print("标题:", title)
    if not video_url:
        print("无可用视频地址，返回:", json.dumps(data, ensure_ascii=False)[:300]); sys.exit(1)

    src = "mediaUrl(无加密直链)" if data.get("mediaUrl") else "video_url(中转)"
    print(f"无水印地址[{src}]:", video_url)
    print("下载中 ->", out)
    vreq = urllib.request.Request(video_url)
    vreq.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    vreq.add_header("Referer", "https://weixin.qq.com/")
    try:
        with urllib.request.urlopen(vreq, timeout=120) as r:
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(out, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk); done += len(chunk)
                    if total:
                        print(f"\r{done*100//total}%", end="", flush=True)
    except Exception as e:
        print("\n下载失败:", e); sys.exit(1)
    print(f"\n已保存: {out}  size={os.path.getsize(out)} bytes")

if __name__ == "__main__":
    main()
