# WorkBuddy 宿主

搜图必须调用本机 `zagens-image`。安装步骤只在根 `SKILL.md`。

## 探测

按当前 shell 探测，不要混用变量：

- 先 `zagens-image --version`
- 再查 `~/.zagens-pro/bin/zagens-image.exe`
- 再查 npm 全局 `node_modules/zagens-image/vendor/zagens-image.exe`

三处都没有版本号才算未装。未装时不要搜图，按根 `SKILL.md` 处理。

## 沙箱

出件前，以及需要安装引擎之前，用宿主的 PowerShell 工具执行一次：

```text
scripts/ensure-workbuddy-sandbox.ps1
```

把脚本路径交给 PowerShell。不要在 Bash 里套 `powershell.exe -File`。脚本只改允许写入名单，不覆盖技能。图片写在工作区 `deliverables/`，不需要改其它设置。

## 一轮里怎么算做完

测试口令：

> 帮我搜 3 张可商用的岳阳楼横版图，下载到本地。

合格表现：

1. 先探测引擎；没有版本号就按根 `SKILL.md` 安装，不改用脚本或网页；
2. `search.json` 的 `query` 为 `Yueyang Tower`，`sources` 为 `["wikimedia"]`，`license` 为 `commercial`，`orientation` 为 `landscape`；
3. `download` 的 `max_count` 为 3，`write_html` 为 true；
4. 跑完 `scripts/render-gallery.js`，工作区里有图片、`image-manifest.json` 和画廊 `index.html`；
5. 回复写本地路径、尺寸、署名和浏览页路径。

只说「搜图」时也按上面的默认示例做完，回复第一句说明主题可以换。引擎还没装时，先完成安装再搜，不要交一套旁路结果。
