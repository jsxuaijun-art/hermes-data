---
name: image-gen-cn
description: 用户说「生图/AI生图/画一张/通义万相/wanx」时触发——用国内云端API出图，替代失效的FAL内置工具。
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [image, generation, wanx, dashscope, siliconflow, 生图, 通义万相]
---

# 国内 AI 生图（通义万相 / 硅基流动）

本机无 NVIDIA GPU，内置 image_gen 工具硬编码走 FAL.ai（海外+付费key）。本skill用**国内云端生图API**替代，是路线B(真AI生图)的落地实现。

## 何时使用
用户说「生图」「AI生图」「生成图片」「画一张xxx」「通义万相」「wanx」「做个AI图的」时触发。配合 wechat-comic-cells 的路线B，产出真·AI绘画质感（用户明确不满意纯SVG手绘风格，要求专业绘画质感）。

## 核心脚本
`/home/dmin/.hermes/scripts/image_gen_cn.py`

## 依赖的 key（二选一）
- **通义万相（主推，免费额度，中文效果好）**：`DASHSCOPE_API_KEY`
  - 申请：https://bailian.console.aliyun.com/ （阿里云百炼，新用户有免费额度）
  - 模型：`wanx2.1-t2i-turbo`（快）默认，`wanx2.1-t2i-plus`（精修质量更高）
- **硅基流动（备用，有免费 FLUX）**：`SILICONFLOW_API_KEY`
  - 申请：https://cloud.siliconflow.cn/ （注册送额度，FLUX.1-schnell 免费）
  - 模型：`black-forest-labs/FLUX.1-schnell`

key 写入 `~/.hermes/.env`（脚本会自动读取），格式：`DASHSCOPE_API_KEY=sk-xxx`

## 用法
```bash
# 通义万相（默认）
python3 /home/dmin/.hermes/scripts/image_gen_cn.py --provider dashscope \
  --prompt "..." --out /tmp/out.png

# 指定更高精修模型 + 竖版尺寸
python3 /home/dmin/.hermes/scripts/image_gen_cn.py --provider dashscope \
  --model wanx2.1-t2i-plus --size 720*1280 --prompt "..." --out /tmp/out.png

# 硅基流动
python3 /home/dmin/.hermes/scripts/image_gen_cn.py --provider siliconflow \
  --prompt "..." --out /tmp/out.png
```

尺寸：通义万相 `1024*1024`(方) / `720*1280`(竖,公众号配图用) / `1280*720`(横)。硅基流动用 `1024x1024` 等 x 分隔。

## 关键命令（当前机器实测）
```bash
python3 /home/dmin/.hermes/scripts/image_gen_cn.py --provider dashscope --prompt "扁平插画风格，会计师江姐(红衫棕长发)在办公室讲解税务政策，对话气泡，暖橙色背景" --out /tmp/jie.png
```

## 工作流（公众号分镜用）
1. 确认 key：`grep DASHSCOPE /home/dmin/.hermes/.env` 或直接跑脚本看是否报「未设置」
2. 出图：按 wechat-comic-cells 的分镜剧本，逐格调用本skill生图
3. 验证：主模型无视觉时，用 RapidOCR 验文字（AI生图文字可能乱码，重要文案慎用AI图）或用 vision_analyze 让有视觉的辅助模型确认画面
4. 发布：传服务器 `/var/www/html/images/`，插 wechat-publish 文章

## Pitfalls
- **AI生图文字会乱码**：含关键政策文案/数字的格子别用AI生图，用路线A(HTML/SVG真实字体)。AI图适合场景/人物/氛围，文字单独用真实排版叠加。
- **无key报错**：脚本报「XXX_API_KEY 未设置」就是 .env 没配。配完要新开 session 才生效。
- **网络**：国内直连，不需要 Clash 代理。
- **通义万相是异步任务**：创建任务后轮询，耗时约 20-60 秒，正常现象。
- **本机无GPU**：绝不要尝试本地 ComfyUI/SD——CPU 硬跑太慢且质量差。
