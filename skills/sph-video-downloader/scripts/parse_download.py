import os, sys, json, urllib.request, urllib.error, urllib.parse

# 清空本地代理，避免被 127.0.0.1:7890 等死代理拦截
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_k, None)

API_URL = "https://qyapi.ipaybuy.cn/api/sph_parse"
APP_ID = os.environ.get("QIYUN_APP_ID", "在此填入你的AppId")
APP_KEY = os.environ.get("QIYUN_APP_KEY", "在此填入你的AppKey")

def main():
    if len(sys.argv) < 2:
        print("用法: python parse_download.py <视频号链接> [输出mp4路径]")
        sys.exit(1)
    url = sys.argv[1]
    vid = url.rstrip("/").split("/")[-1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("videos", vid + ".mp4")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    qs = urllib.parse.urlencode({"appId": APP_ID, "appKey": APP_KEY, "url": url})
    req = urllib.request.Request(f"{API_URL}?{qs}", method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, e.read().decode("utf-8", "ignore")[:300]); sys.exit(1)
    except Exception as e:
        print("RequestError:", e); sys.exit(1)

    code = result.get("code")
    print("code:", code, "| msg:", result.get("msg", ""))
    if str(code) == "200":
        data = result.get("data") or {}
        if data.get("title"):
            print("title:", data["title"])
        media_url = data.get("mediaUrl") or data.get("video_url") or data.get("video_url_v2")
        if not media_url:
            print("无直链，返回:", json.dumps(data, ensure_ascii=False)[:300]); sys.exit(1)
        print("无水印直链:", media_url)
        print("下载中 ->", out)
        vreq = urllib.request.Request(media_url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
            "Referer": "https://weixin.qq.com/",
        })
        try:
            with urllib.request.urlopen(vreq, timeout=180) as r:
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
            print(f"\n已保存: {out}  size={os.path.getsize(out)} bytes")
        except Exception as e:
            print("\n下载失败:", e); sys.exit(1)
    else:
        print("解析失败:", json.dumps(result, ensure_ascii=False)[:500]); sys.exit(1)

if __name__ == "__main__":
    main()
