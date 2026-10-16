import os, sys, json, urllib.request, urllib.error

# 清空本地代理，避免被 127.0.0.1:7890 等死代理拦截
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_k, None)

API_URL = "https://redfox.hk/story/api/parseWork/parse"
API_KEY = os.environ.get("REDFOX_API_KEY", "在此填入你的ak_开头Key")

def main():
    if len(sys.argv) < 2:
        print("用法: python parse_download.py <视频号链接> [输出mp4路径]")
        sys.exit(1)
    url = sys.argv[1]
    vid = url.rstrip("/").split("/")[-1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("videos", vid + ".mp4")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    payload = json.dumps({"url": url, "source": "短视频下载器-WorkBuddy"}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, e.read().decode("utf-8", "ignore")[:300]); sys.exit(1)
    except Exception as e:
        print("RequestError:", e); sys.exit(1)

    code = result.get("code")
    print("code:", code, "| msg:", result.get("msg", ""))
    if str(code).startswith("2"):
        data = result.get("data") or {}
        video_url = data.get("videoUrl")
        if not video_url:
            print("无 videoUrl，返回:", json.dumps(data, ensure_ascii=False)[:300]); sys.exit(1)
        print("无水印直链:", video_url)
        print("下载中 ->", out)
        vreq = urllib.request.Request(video_url)
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
        print(f"\n已保存: {out}  size={os.path.getsize(out)} bytes")
    else:
        print("解析失败:", json.dumps(result, ensure_ascii=False)[:500]); sys.exit(1)

if __name__ == "__main__":
    main()
