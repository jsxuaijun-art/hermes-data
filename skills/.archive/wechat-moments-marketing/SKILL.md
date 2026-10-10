---
name: wechat-moments-marketing
title: 微信营销号朋友圈运营（盈信财税）
description: 盈信企业管理（苏州）微信营销号朋友圈内容创作体系 — 针对抖音/视频号引流到微信但未成交的意向客户，通过朋友圈持续唤醒、建立专业信任、引导复联成交。覆盖内容类型、发布节奏、配图规范、私信衔接。
category: productivity
tags: [微信营销, 朋友圈, 私域运营, 财税获客, 客户唤醒, 成交转化]
triggers:
  - 朋友圈 / 微信营销 / 私域 / 唤醒
  - 未成交客户 / 意向客户跟进 / 复联
  - 营销号 / 微信号运营
  - 朋友圈文案 / 朋友圈配图
---

# 微信营销号朋友圈运营 — 盈信财税版

## 适用场景

- 从抖音、视频号、**公众号**引流到微信但未成交的意向客户
- 成交率偏低（询价型/意向不强/暂时无需求）
- 目标：让客户知道「我微信里有一个做公司注册、代理记账的专业人士」，持续唤醒，创造二次沟通机会

## 引流入口设计（公众号→微信）

公众号文章是引流的第一触点。以下设计确保读者能顺畅地从文章跳转到微信添加好友：

### 1. 微信二维码（文章底部）

在公众号文章尾部放置徐总微信二维码图片，并配以下引导文字：

```
 **长按 → 识别图中二维码 → 添加到通讯录**
```

**技术要点：**
- 二维码图片已上传到服务器：`http://127.0.0.1:8080/images/qr_xuaijun.jpg`
- 二维码尺寸888×1131像素，足够清晰，微信读者**长按图片即可识别**（无需扫码枪或扫码界面）
- 图片通过nginx服务（127.0.0.1:8080）引用，发布时wenyan自动抓取上传微信CDN

### 2. 免费资料诱饵（增加添加动机）

在二维码下方设置关键词自动回复，给读者一个「添加好友的理由」：

```
📥 **免费领资料：** 在公众号对话框回复 **「高企自查」** ，领取《2026年高企申报合规自检清单》PDF（含5项核心指标自查表格+打分标准）。
```

用户回复后，在公众号后台手动（或自动回复）引导添加微信。资料的选题必须与文章主题强相关，且是读者确实需要的实用内容。

### 3. 文章尾部CTA（转化动作）

文章末尾设置4个动作引导，其中第❹个是直接转化入口：

- ❶ 收藏 — 方便日后查找
- ❷ 转发 — 社交裂变
- ❸ 关注公众号 — 沉淀为粉丝
- **❹ 咨询 — 扫码加微信，免费做一次[相关服务]预检**

### 4. 公众号菜单栏常设入口

在公众号底部菜单栏固定设置：
- **免费咨询** → 跳转微信客服或引导添加微信
- **业务介绍** → 公司简介+服务流程
- **联系我们** → 电话+微信二维码

### 引流路径概览

```
公众号文章发布
    │
    ├── 读者长按二维码 → 一步添加微信好友 ← 最高效路径
    │
    ├── 读者回复关键词 → 引导加微信 ← 诱饵驱动
    │
    ├── 读者点击菜单栏 → 联系咨询
    │
    └── 读者收藏/关注 → 下次再触达 ← 长期沉淀
```

## 客户分层跟进策略

### A型：纯询价客户（比完价就没了）

**特征**：问完价格说「我考虑考虑」，然后消失了
**问题**：他们不觉得你和其他代账有区别
**策略**：展示差异化——多发团队专业度的内容（高会、TSC、16年）
**唤醒时机**：发了2-3条干货/案例后，私信发一条：
> 「最近朋友圈发了一些实际的案例，您如果有空可以看看。之前聊过代账的事，有什么问题随时找我，不用客气。」

## 用户身份锚点

- **徐爱军（徐总）** — 盈信企业管理（苏州）负责人
- **核心背书**：上海交通大学管理硕士
- **团队配置**：江敏（苏州本地人，高级会计师，苏州2万家同行不到5家有此资质）、黎经理（注册税务师CTA）、许经理（注册会计师CPA）
- **16年实战**：苏州+上海双城，1000+客户，90%转介绍率
- **TSC五级**：涉税信用最高等级

## 内容定位

**不卖产品，卖「专业人士的日常」。** 朋友圈不是广告位，是让客户看到「这个做财税的人每天都在干什么、信什么、能解决什么问题」。

## 发布节奏

**每周3次**，建议时间：

| 日期 | 时段 | 理由 |
|------|------|------|
| **周二 11:30-12:00** | 午间 | 老板们上午忙完，刷手机等午饭，心情放松看得进内容 |
| **周四 20:00-20:30** | 晚间 | 周四晚上是「周末前奏」，节奏慢下来，看朋友圈活跃度高 |
| **周六 10:00-10:30** | 周末上午 | 周末刷手机时间多，10点刚起不久，还没进入家庭事务，阅读质量最高 |

**不推荐时间**：周一早上（忙）、周五晚上（社交/聚餐）、周末晚上（家庭时间/焦虑明天上班）

## 配图规范

### ⚠️ 配图核心原则（历史教训 — 必读）

**三次迭代后最终方案：真实摄影图，不加任何文字叠加。**

| 迭代 | 方案 | 用户反馈 |
|:----:|------|---------|
| ❌ v1 | 纯色底文字卡（白/深蓝/浅灰） | 「不好看，不是图片」 |
| ❌ v2 | 真实摄影背景+深色遮罩+白色文字 | 「都是这种白色字体的，不好看」 |
| ✅ **v3** | **真实摄影原图，不加任何文字** | 用户确认 |

### 核心原则
- ❌ **不要用文字卡**（纯色底或摄影背景+文字都不行）
- ❌ **不要添加任何文字/遮罩/logo到图片上**
- ✅ **每篇朋友圈必须配 3 张图**
- ✅ **图片必须与主题搭配**
- ✅ **图源：Unsplash 真实摄影图**（WSL可用curl下载，约20秒/张）
- ✅ **不出现外国人面孔**

### 配图制作流程

每篇朋友圈 3 张图：

| 序号 | 用途 | 图源方向 |
|:----:|------|----------|
| 图1 | 主题引入 | 写字楼/商务建筑摄影 |
| 图2 | 干货展开 | 工作场景/数据/办公 |
| 图3 | 行动号召 | 签约/文件场景 |

**制作流程：**
1. 确定主题后，从 Unsplash 下载3张匹配图
2. 尺寸参数 `?w=800&q=80`（文件约40-100KB/张）
3. **图片不加任何文字，保持摄影原图**
4. 文件命名：`<主题>_01_<场景>.jpg`
5. 拷到桌面：`cp /tmp/img_xxx.jpg /mnt/c/Users/Administrator/Desktop/`
6. **交付时明确写出每个文件的完整桌面路径**

**Unsplash 下载命令：**
```bash
curl -L -o /tmp/img.jpg "https://images.unsplash.com/photo-XXXXX?w=800&q=80"
```

### 已验证可用的 Unsplash Photo ID

| 场景 | Photo ID | 描述 |
|------|----------|------|
| 写字楼 | `1486406146926-c627a92ad1ab` | 现代玻璃幕墙写字楼 |
| 办公/数据 | `1554224155-6726b3ff858f` | 办公桌+图表数据 |
| 签约/文件 | `1450101499163-c8848c66ca85` | 签约文件场景 |
| 餐厅 | `1552566626-52f8b828add9` | 餐厅内部 |
| 明亮办公室 | `1497366216548-37526070297c` | 明亮办公室 |
| 城市天际 | `1480714378408-67cf0d13bc1b` | 城市CBD |

## 内容类型四象限

朋友圈内容按「专业度」和「人情味」两个维度分四类，每周3条须覆盖至少3种类型：

```
            专业度高
              │
       案例型  │  干货型
              │
   人情味低 ──┼── 人情味高
              │
       互动型  │  生活型
              │
            专业度低
```

### 第①类：干货型（专业度高 + 人情味适中）

**目的**：展示专业知识，建立「TA真的懂」的印象

**话术结构**：现象/问题 → 一句核心观点 → 行动建议

**示例文案**：
```
注册公司，注册资本写多少？

很多老板觉得写10万就够了，
但要考虑：你的客户招标要求注册资本吗？
要申请某些行业资质吗？后期要融资吗？

写少了后期再增资，流程比注册还麻烦。
来，有注册计划的评论区打个「注册」，我帮你参谋。
```

**配图建议**：3张真实摄影图（写字楼 + 财务办公场景 + 签约文件），不加任何文字

### 第②类：案例型（专业度高 + 人情味高）

**目的**：用真实（脱敏）案例展示解决问题的能力，有温度地建立信任

**话术结构**：客户背景（脱敏） → 我们做了什么 → 结果如何 → 一句话总结

**示例文案**：
```
上个月一个做餐饮的老板找我，
说税务上了黑名单，银行贷款批不下来。
其实问题不大——以前用的是兼职会计，
申报表填错了，滞纳金滚了三个月。

我们帮他更正申报、写说明、申请撤销，
前后一周，银行那边也解冻了。

很多问题不是大事，但没人盯着就成了大事。
```

**配图建议**：3张真实摄影图（餐厅场景 + 办公分析场景 + 计算器/财务场景），不加任何文字

### 第③类：生活型（人情味高 + 专业度低）

**目的**：展示有血有肉的专业人士形象，不只是一台开票机器

**话术结构**：一个生活场景 → 引出一点点专业思考 → 自然收尾

**示例文案**：
```
周末带孩子去上海交大逛了一圈。
他问我：爸，你以前在这上学都学什么？
我说：学管理，管理公司、管人、管钱。
他说：那不就跟我当班长一样？

哈哈，好像也没毛病。
管好小公司和管好大班级，底层逻辑确实是通的。

#交大记忆
```

**配图建议**：
- 图1：真实摄影图（校园/大学场景），不加文字
- **最佳效果**：用自己手机拍的交大校园照片发2-3张，任何文字卡都不如实景照片有感染力

### 第④类：互动型（人情味高 + 专业度适中）

**目的**：降低互动门槛，让客户在评论区或私信里开口

**话术结构**：问一个客户能轻松回答的问题 → 表达关心 → 不给压力

**示例文案**：
```
最近汇算清缴开始了，很多老板被会计催着要票据。
你家的票齐了吗？
齐了的扣1，还在找的扣2，我看看有多少人。
```

**配图建议**：3张真实摄影图（日历/时钟场景 + 办公票据场景 + 电脑/手机场景），不加任何文字

## 三个月内容排期（建议）

| 周次 | 周二·午间 | 周四·晚间 | 周六·上午 |
|:----:|-----------|-----------|-----------|
| 第1周 | 干货·注册资本 | 案例·餐饮客户 | 生活·交大校园 |
| 第2周 | 互动·汇算清缴 | 干货·公转私风险 | 案例·小店被查 |
| 第3周 | 生活·团队合影 | 干货·选择代账标准 | 互动·发票难题 |
| 第4周 | 案例·出口退税 | 干货·股东借款 | 生活·苏州老街 |
| 第5周 | 互动·行业八卦 | 干货·小规模or一般人 | 案例·创业公司 |
| 第6周 | 生活·孩子作文 | 干货·个体户转公司 | 互动·最头疼的事 |
| 第7周 | 案例·建筑老板 | 干货·个税汇算 | 生活·老书店 |
| 第8周 | 互动·你最怕什么 | 干货·注册后要做什么 | 案例·被罚款之后 |
| 第9周 | 生活·晨跑/茶 | 干货·发票丢失怎么办 | 互动·你碰过稽查吗 |
| 第10周 | 案例·股权转让 | 干货·注销流程 | 生活·老照片 |
| 第11周 | 互动·同行价格 | 干货·高会是什么 | 案例·代账到合规 |
| 第12周 | 生活·年终总结 | 干货·印花税变化 | 互动·明年计划 |

## 三种客户的差异化唤醒策略

### A型：纯询价客户（比完价就没了）

**特征**：问完价格说「我考虑考虑」，然后消失了
**问题**：他们不觉得你和其他代账有区别
**策略**：展示差异化——多发团队专业度的内容（高会、TSC、16年）
**唤醒时机**：发了2-3条干货/案例后，私信发一条：
> 「最近朋友圈发了一些实际的案例，您如果有空可以看看。之前聊过代账的事，有什么问题随时找我，不用客气。」

### B型：意向不强（随便问问）

**特征**：问了几句，回得很慢，不积极
**问题**：现在不是他们的紧急事项
**策略**：多发痛点场景内容，让他们在刷到时触发「这事我也得处理一下」
**唤醒时机**：有案例型内容或政策变化型内容时，私信转发：
> 「刚发了条关于XX的案例，感觉您可能也会遇到，顺手转给您看看。」

### C型：暂时无需求（确实没到那步）

**特征**：刚创业/还没注册公司，暂时不需要代账
**问题**：以后可能有需求，但到时候不一定想起你
**策略**：保持存在感，多发创业相关知识，让他们觉得「这人一直在」
**唤醒时机**：3-6个月后私信问候：
> 「好久没聊，最近生意怎么样？公司注册/税务上有什么新情况吗，有需要随时说。」

## 私信衔接SOP

发了朋友圈后，什么时机跟进私信：

| 朋友圈内容 | 私信跟进时机 | 私信话术 |
|-----------|-------------|---------|
| 干货型 | 发出1天后 | 「XX总，昨天发了条关于X的内容，感觉您可能用得上，顺手转给您看看」 |
| 案例型 | 发出1天后 | 「XX总，昨天那个案例我觉得挺典型，您要是遇到类似情况随时找我聊」 |
| 互动型 | 评论出现后 | 直接回复评论，有需求标签的单独私信 |
| 生活型 | 不主动私信 | 有自然共鸣才私信，不要为了跟进而跟进 |

**核心原则**：私信不是为了「催成交」，是为了「让客户知道你还记得他」。给信息不给压力。

## 月复盘模板

每月末执行一次朋友圈运营复盘：

1. 本月发了多少条？每类各几条？
2. 每条点赞评论数多少？哪条效果最好？为什么？
3. 当月通过朋友圈→私信→二次沟通成交了多少？
4. 下月重点调整什么？

## 双重交付流程

每次生成朋友圈素材后，**必须同时执行两种交付方式**：

### 方式一：文件交付到桌面

```
cp /tmp/img_xxx.jpg "/mnt/c/Users/Administrator/Desktop/<主题>_01_<场景>.jpg"
```

交付时写出完整路径：`C:\Users\Administrator\Desktop\注册资本_01_写字楼.jpg`

### 方式二：企微API发送（自动化）

企业微信凭证（已验证可用）：
- CorpID: `wwc7fc356cf7297e7f`
- AgentId: `1000036`
- Secret: `ww-gknY3ZjQXa9NpsSlxMsP8Z7VEP7D20Mjz3o5vNKE`
- 用户ID: `XuAiJun`（徐爱军）

流程：
1. 获取 token → `GET https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=...&corpsecret=...`
2. 上传图片 → `POST /cgi-bin/media/upload?access_token={token}&type=image`（multipart/form-data）
3. 发消息 → `POST /cgi-bin/message/send` 包含：
   - 先发一段 text 消息（含完整文案+操作说明）
   - 再逐条发 image 消息（3张图，每条单独请求）

> **⚠️ 可信IP**：API调用需要先在企微管理后台配置当前IP为可信IP。
> 当前 WSL 公网IP：用 `curl -s ifconfig.me` 获取。
> 配置路径：企微管理后台 → 应用管理 → AgentId对应的应用 → 企业可信IP。

### Python 发送模板

```python
import json, urllib.request, os

def upload_and_send(image_paths, text_content, touser="XuAiJun"):
    token = json.loads(urllib.request.urlopen(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwc7fc356cf7297e7f&corpsecret=ww-gknY3ZjQXa9NpsSlxMsP8Z7VEP7D20Mjz3o5vNKE"
    ).read())["access_token"]
    
    text_payload = {"touser": touser, "msgtype": "text", "agentid": 1000036,
        "text": {"content": text_content}}
    req = urllib.request.Request(
        f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
        data=json.dumps(text_payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req).read()
    
    for img_path in image_paths:
        boundary = "----Boundary"
        with open(img_path, "rb") as f:
            data = f.read()
        filename = os.path.basename(img_path)
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"{filename}\"\r\n"
                f"Content-Type: image/jpeg\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image",
            data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        media_id = json.loads(urllib.request.urlopen(req).read())["media_id"]
        
        img_payload = {"touser": touser, "msgtype": "image", "agentid": 1000036,
            "image": {"media_id": media_id}}
        req = urllib.request.Request(
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
            data=json.dumps(img_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req).read()
```

## 配图制作流程

每次需要配图时，按以下步骤执行：

### 选图主题匹配表

| 内容类型 | 图1（主题引入） | 图2（干货展开） | 图3（收尾号召） |
|----------|----------------|----------------|----------------|
| 干货型 · 注册资本 | 写字楼建筑 | 财务数据/办公桌 | 签约文件 |
| 干货型 · 公转私风险 | 银行大楼 | 电脑屏幕/转账 | 安全锁/法院 |
| 干货型 · 选择代账标准 | 多人会议 | 证件/资质证书 | 握手/合作 |
| 干货型 · 股东借款 | 会议室 | 文件/合同 | 计算器 |
| 干货型 · 个税汇算 | 手机/App | 日历/时间 | 钱包/算账 |
| 案例型 · 餐饮客户 | 餐厅内部 | 办公分析 | 计算器/财务 |
| 案例型 · 小店被查 | 商店门面 | 文件/账本 | 盖章/通知 |
| 案例型 · 股权转让 | 写字楼 | 签约文件 | 握手 |
| 生活型 · 交大校园 | 校园景观 | 手机照片 | 手机照片 |

### 交付流程（双重交付）

每次出朋友圈素材，必须同时走两条路径：

**路径一：桌面文件（个人微信朋友圈）**
1. 确定内容类型和主题
2. 按上表选 Unsplash 图
3. 用 curl 下载3张图到 /tmp/
4. 拷到桌面：`cp /tmp/img_*.jpg "/mnt/c/Users/Administrator/Desktop/<主题>_<序号>_<场景>.jpg"`
5. **交付时明确写出每个文件的完整 Windows 路径**

**路径二：企业微信推送（企微营销号）**
每次出图后，通过企微API发送给徐总：
1. 获取token：`POST qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwc7fc356cf7297e7f&corpsecret=ww-gknY3ZjQXa9NpsSlxMsP8Z7VEP7D20Mjz3o5vNKE`
2. 上传图片文件获得media_id（multipart/form-data上传）
3. 先发一条text消息（含完整文案+发布说明）
4. 再发3条image消息（每张图一条）
5. 接收人：`XuAiJun`（徐爱军的企业微信userid）
6. AgentId: `1000036`

### 企微API常用代码片段（Python）

```python
# 获取token
import json, urllib.request
url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwc7fc356cf7297e7f&corpsecret=ww-gknY3ZjQXa9NpsSlxMsP8Z7VEP7D20Mjz3o5vNKE"
token = json.loads(urllib.request.urlopen(url).read())["access_token"]

# 上传图片
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
with open(filepath, "rb") as f:
    data = f.read()
body = (f"--{boundary}\\r\\n"
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\\r\\n'
        f"Content-Type: image/jpeg\\r\\n\\r\\n").encode() + data + f"\\r\\n--{boundary}--\\r\\n".encode()
req = urllib.request.Request(
    f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image",
    data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
result = json.loads(urllib.request.urlopen(req).read())

# 发送文本
urllib.request.urlopen(urllib.request.Request(
    f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
    data=json.dumps({"touser": "XuAiJun", "msgtype": "text", "agentid": 1000036,
        "text": {"content": "文案内容"}}, ensure_ascii=False).encode("utf-8"),
    headers={"Content-Type": "application/json"}))

# 发送图片
urllib.request.urlopen(urllib.request.Request(
    f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
    data=json.dumps({"touser": "XuAiJun", "msgtype": "image", "agentid": 1000036,
        "image": {"media_id": media_id}}).encode(),
    headers={"Content-Type": "application/json"}))
```

### 下载命令模板

```bash
# 注册资本主题（已验证）
curl -L -o /tmp/img_01.jpg "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80"
curl -L -o /tmp/img_02.jpg "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80"
curl -L -o /tmp/img_03.jpg "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80"

cp /tmp/img_01.jpg "/mnt/c/Users/Administrator/Desktop/<主题>_01_<场景>.jpg"
cp /tmp/img_02.jpg "/mnt/c/Users/Administrator/Desktop/<主题>_02_<场景>.jpg"
cp /tmp/img_03.jpg "/mnt/c/Users/Administrator/Desktop/<主题>_03_<场景>.jpg"
```

### 已验证可用的 Unsplash Photo ID 库

| 场景 | Photo ID | 文件大小 |
|------|----------|---------|
| 写字楼现代 | `1486406146926-c627a92ad1ab` | ~100KB |
| 办公+数据图表 | `1554224155-6726b3ff858f` | ~53KB |
| 签约文件 | `1450101499163-c8848c66ca85` | ~42KB |
| 餐厅内部 | `1552566626-52f8b828add9` | — |
| 明亮办公室 | `1497366216548-37526070297c` | ~58KB |
| 城市天际线CBD | `1480714378408-67cf0d13bc1b` | ~99KB |

### 参考文件

- `references/配图模板-注册资本-成功案例.md` — 首个发布成功案例（含完整命令）
- 每个新发布的主题，应在 deliverables/ 下保存配图模板供后续复用

## 注意事项 ⚠️

1. **不批量群发**：朋友圈是长线经营，不要一次发5条
2. **不硬广**：不要在朋友圈说「现在签约打8折」，破坏专业感
3. **不转发鸡汤**：不转发「你必须知道的10个税务真相」类文章，自己写原创
4. **客户信息脱敏**：案例型内容必须脱敏，不能暴露客户真实姓名/公司名
5. **评论管理**：客户在评论区问价格/具体问题，不直接在评论区回复，私信说
6. **每篇配3张图，图片与主题搭配**：不允许只用纯文字发朋友圈，也不允许只用1张图
7. **文件交付必须写明完整Windows路径**：`C:\Users\Administrator\Desktop\注册资本_01_写字楼.jpg`，不能只说「在桌面上」
8. **图片素材禁止出现外国人面孔**（用户明确要求）
9. **照片优先于文字卡**：生活型内容尽量用真实照片，比任何设计精良的文字卡都更有感染力
10. **配图尺寸统一800×800正方形**：朋友圈展开后显示最完整
