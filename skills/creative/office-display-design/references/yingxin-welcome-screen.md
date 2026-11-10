# 盈信 70寸欢迎屏实战记录 (2026-11-05)

会议接待欢迎屏的完整底稿,可直接复用为新的欢迎屏/展板底稿。

## 交付物(v5 最终,2026-11-05)
- 桌面 `C:\Users\Administrator\Desktop\盈信欢迎屏设计_v5_最终.zip`
- 包内含: `欢迎屏设计稿_主打版.png`(1920×1080 RGB)、`欢迎屏设计稿_主打版.html`(可编辑源)、`欢迎屏文字稿.txt`、`logo_transparent.png`(净化版 380×378、无灰白残留)、`logo.png`(原图)
- 历史: `_v4_最终.zip`(去白底+缩30%、未修白线)、`_v3_含LOGO.zip`(第一次加LOGO)、`_v2.zip`(改5行文案无LOGO)、无后缀 zip(v1 首版)。旧包被 Windows 占用删不掉时换新文件名放新版,勿死磕。

## 最终文案(5 行,按徐总 5 条意见定稿)
```
苏州盈信企业管理有限公司                    ← 顶部小字(左上;公司名固定写法: 苏州前缀)
欢迎光临 · 携手同行                          ← 主标题,最大(此句7个备选,徐总暂不修改)
高级会计师带队 · 会计从业二十五年              ← 资质行(「高级会计师+二十五年」)
税务合规 ｜ 代理记帐 ｜ 高端会计 ｜ 企业服务      ← 业务行(按徐总指定原文)
专业诚信 值得托付 · 护航您的企业稳健发展        ← 收尾
```
- 公司名一律「苏州盈信企业管理有限公司」,不要「盈信企业管理(苏州)有限公司」——这是徐总永久偏好。
- 「代理记帐」为徐总指定原文,规范写法「代理记账」已当面提示,用户不改则保留原文。
- 资质行金色强调留给「高级会计师 / 二十五年」比标「会计从业」更有说服力(视觉模型建议)。

## LOGO(右上角)
- 白底+正红传统纹样,深蓝底上高对比醒目;与左上品牌文字组左右均衡、同水平线对齐。
- `height:150px(≈屏高12%) object-fit:contain`;金环装饰线在 LOGO 下层被白底遮挡属正常。
- 视觉模型验收结论: 尺寸合适、无重叠、可直接用;可选微调=缩小10–15% 使上下边与左侧文字组齐平。

### v4: 去白底 + 缩 30%(2026-11-05 最终版,徐总要求)
- 白底 LOGO 在深蓝底上彻底融入: 去白底只留红色图形 → `logo_transparent.png`(用本技能 `scripts/remove_white_bg.py`,min-channel 阈值法;保留不透明像素 27.8%、平均RGB(195,23,31)=红色保住)。
- 缩小 30%: 显示高度 `150px → 105px`;HTML 引用改 `src="logo_transparent.png"`。
- 验收(telecom Doubao 直连看图): 红色 LOGO 清晰、无白边/灰边残留、自然融入深蓝背景、尺寸合适、无重叠 → 通过。
- 交付: `盈信欢迎屏设计_v4_最终.zip`(含 渲染png / html / `logo_transparent.png` / 原logo.png / 文字稿.txt)。
- `logo_transparent.png` 为独立可复用透明红 LOGO 资产,以后做 PPT/名片/公众号图直接引用,无需再处理一遍。

### v5: 修「LOGO 下白线」+ 资质间距(2026-11-05 徐总反馈)
- 症状: 用户报告「LOGO 下面还有一条白色横线」。**根因诊断**: 不是 HTML 元素(border-bottom 是金色 `rgba(201,168,106,.35)`,也不是白线),而是去白底后 PNG **最底边缘一条 ~1-2px 浅灰横线**——原白色块的抗锯齿底边,min-channel 渐变阈值留下的残留,在深蓝底上显成白线。
- 排查法: 直连视觉模型看「透明底白底垫底」放大版 → 精确报出残留位置与颜色(本案例: 最底端横贯全宽的浅灰线 + 底部中间一个白点);再对处理后的渲染稿右上角 crop 放大复验。
- 修复: `remove_white_bg.py` 增加 **pass 2**——把「低饱和 AND 偏亮」(max-min<60 且 min通道>150)像素置透明,清掉 2168 个灰/白残留像素,纯红图形完好(26.3% 占比,平均RGB不变);再次视觉复验右下角/右上角 crop 确认无横线、无灰边。脚本已更新(两分支 numpy+纯PIL 均带 pass 2)。
- 间距: 「高级会计师带队」与「会计从业二十五年」之间 `margin-left:18px → 80px` 拉开,视觉确认明显分开、同行并排。
- 交付: `盈信欢迎屏设计_v5_最终.zip`(渲染png / html / `logo_transparent.png`(净化版) / 原logo.png / 文字稿.txt)。

## 视觉验收路由(直连 POST 最稳,本会话反复验证)
- `browser_vision` 偶发报 `Request denied by Key Auth check. Invalid credentials`——**截图仍会生成**于 `~/.hermes/cache/screenshots/browser_screenshot_*.png`,cp 出来用直连端点验收即可,别误判失败。
- `vision_analyze` 在旧会话缓存下可能把图误发给主模型(deepseek-v4-flash 纯文本报 `does not accept input types: image`)。**最稳 = 直连 telecom Doubao POST base64**。
- **Doubao 响应慢**(实测 5~110s): 请求超时 `timeout=200`,失败重试一次即可;POST 的 JSON 载荷嵌套深,先用独立变量组 content 列表再组装 payload,避免括号对不上(见会话手写脚本教训)。

## 视觉参数(主打版)
- 画布: 1920×1080,深蓝底 `radial-gradient(#123a5e → #0a1a2f → #060f1e)`
- 金色 `#c9a86a`(品牌英文/副标/分隔符/收尾);米白 `#f4f7fb` 正文
- 主标题 118px/800,资质行 40-44px,业务行 40px,收尾 34px
- 背景装饰: 右上金环 + 右下光晕,营造大气感

## 视觉修复记录(本次)
- 症状: 一切看图功能失效——auxiliary.vision 此前指向 chudian `deepseek-v4-flash-vision-exp`,该模型被平台下架(返回 404「已停用」)。
- 修复: `hermes config set auxiliary.vision.provider custom` / `.model Doubao-Seed-2.1-Pro` / `.base_url https://aigw.telecomjs.com/v1` / `.api_key '${TELECOM_DOUBAO_KEY}'`;改前先 `cp config.yaml config.yaml.bak.*`。实测成功读图(逐行念出欢迎屏全部文案、指出「代理记帐」用字问题)。
- 坑: 已运行的会话可能缓存旧 auxiliary 配置——config 已改但本会话 `vision_analyze` 偶发把图误发给主模型(deepseek-v4-flash 报 `does not accept input types: image`)。对策: 直连 telecom 端点 POST base64 图验收(devops/hermes-free-model-channels/scripts/vprobe.py),并提醒用户重启会话让新配置稳定生效。
- 完整检修方法见 devops/hermes-free-model-channels `references/auxiliary-vision-repoint.md`。

## 待核实清单(给徐总)
1. 从业年限「二十五年」/「高级会计师带队」——徐总口述提供,作为已确认事实;若换数字需再核。
2. LOGO 原图已由徐总提供;高清矢量版(如公司VI源文件)可替换 logo.png。
3. 主标题 7 个备选意境词(携手同行/互信共赢/携手共进/共创共赢/同心致远/敬请指教…)徐总表示暂不修改。
