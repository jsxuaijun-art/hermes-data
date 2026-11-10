# auxiliary.vision 模型被下架/读不了图时的检修工作流

2026-11-05 实测记录: 本机 auxiliary.vision 此前指向 chudian `deepseek-v4-flash-vision-exp`,
该模型被平台下架 → 一切看图功能失效(browser_vision / vision_analyze 全部出错)。

## 症状识别
- `vision_analyze` / `browser_vision` 报 404「已停用 / model_not_found」,或中转网关报鉴权/密钥错。
- 视觉辅助失败 ≠ 截图失败: browser_vision 的截图仍能落盘 `~/.hermes/cache/screenshots/`,报错只发生在"肉眼验收"环节。
- 反复出现主模型报 `does not accept input types: image`(纯文本模型收到图)= 视觉链没接上 aux,把图转发给了主模型。

## 诊断(以真实网关为准,绝不照抄外部文档)
用配置里的 key 直问网关模型列表,看它现在实际提供哪些模型:
```bash
# telecom 示例(TELECOM_DOUBAO_KEY 从 ~/.hermes/.env 读)
curl -sS https://aigw.telecomjs.com/v1/models -H "Authorization: Bearer $TELECOM_DOUBAO_KEY"
```
实测 telecom 对 TELECOM_DOUBAO_KEY 只返回 `Doubao-Seed-2.1-Pro`(字节多模态,能读图)——即应指向的模型。

## 修复(config.yaml 受保护,优先 `hermes config set`)
```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.$(date +%Y%m%d_%H%M%S)
hermes config set auxiliary.vision.provider custom
hermes config set auxiliary.vision.model Doubao-Seed-2.1-Pro
hermes config set auxiliary.vision.base_url https://aigw.telecomjs.com/v1
hermes config set auxiliary.vision.api_key '${TELECOM_DOUBAO_KEY}'   # 用 env 变量名占位,运行时展开
```
改完重读 `config.yaml` 确认四项齐全。

## 验证(必须实弹,不能只看配置)
给目标端点 POST 一张"已知随机码"的图,模型读对=真支持视觉(不可用"能描述图"当通过标准——弱模型会顺着提示词编):
```python
import base64, json, urllib.request
key = "你的key"   # 从 ~/.hermes/.env 读
b64 = base64.b64encode(open("/tmp/图.png","rb").read()).decode()
payload = {"model":"Doubao-Seed-2.1-Pro","max_tokens":300,"messages":[
  {"role":"user","content":[
    {"type":"text","text":"请读出图中的英文和数字(原样),并说出边框颜色。"},
    {"type":"image_url","image_url":{"url":"data:image/png;base64,"+b64}}]}]}
req = urllib.request.Request("https://aigw.telecomjs.com/v1/chat/completions",
  data=json.dumps(payload).encode(),
  headers={"Content-Type":"application/json","Authorization":"Bearer "+key})
print(json.loads(urllib.request.urlopen(req, timeout=120).read())["choices"][0]["message"]["content"])
```
读对 = 真视觉;报 `does not accept input types: image` = 纯文本模型。

## 会话缓存坑(重要)
- 已运行的 Hermes 会话可能缓存旧 auxiliary 配置: config 已改、直连验证通过,但当前会话的 `vision_analyze` 仍偶发把图误发给主模型(报「deepseek-v4-flash 不支持 image」)。
- 对策: 需要看图时直接对目标端点 POST base64 图验收(上方脚本,绕开会话内部路由,结果同样可靠);并提醒用户**重启会话**让新配置稳定生效。
- 主模型给出不可靠的 supports_vision 元数据(目录标 true 但实为纯文本)时,用 provider 级覆盖 `hermes config set providers.<name>.models.<model>.supports_vision false` 纠正,防图片被塞进 tool-result 历史导致会话卡死。
