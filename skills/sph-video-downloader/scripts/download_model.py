from modelscope.hub.snapshot_download import snapshot_download

repo = "AI-ModelScope/faster-whisper-medium"
print("downloading repo:", repo)
try:
    path = snapshot_download(repo, revision="master")
    print("MODEL_PATH=", path)
except Exception as e:
    print("TRY1_FAILED:", repr(e)[:300])
    for cand in ["modelcope/faster-whisper-medium", "AI-ModelScope/whisper-medium",
                 "Systran/faster-whisper-medium"]:
        try:
            print("trying", cand)
            path = snapshot_download(cand, revision="master")
            print("MODEL_PATH=", path)
            break
        except Exception as e2:
            print("FAILED", cand, repr(e2)[:200])
