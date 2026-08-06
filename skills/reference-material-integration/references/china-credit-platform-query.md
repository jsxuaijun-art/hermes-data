# 中国企业信用信息公示平台查询指南

> 用途：查询企业信用认证、AAA等级证书、资质信息
> 适用场景：验证客户/本公司的信用评级公示情况，获取证书详情截图

---

## 一、各平台可用性速查

| 平台 | URL | 状态 | 备注 |
|------|-----|------|------|
| 全国信用企业公示网 | credit999.cn | ✅ 可用 | 搜索+详情均可；内容由JS异步加载 |
| 招标投标信用企业公示平台 | creditxy.cn | ❌ 被拦截 | ERR_BLOCKED_BY_CLIENT |
| 企业服务能力评价公示网 | bidtb.cn | ❌ 被拦截 | ERR_BLOCKED_BY_CLIENT |
| 诚信商务企业公示服务平台 | ztb315.cn | ❌ 超时 | 无法访问 |
| 中国招投标网 | credit.cecbid.org.cn | ⚠️ 需验证码 | 搜索需输入验证码，无法自动化 |
| 天眼查 | tianyancha.com | ⚠️ 反爬 | 检测到异常操作会暂停访问 |

## 二、credit999.cn 查询方法

### 2.1 搜索企业

**直接URL搜索（推荐）：**
```
https://www.credit999.cn/index.php?m=home&c=Lists&a=index&tid=78&CompanyName=企业全称
```

示例：
```
https://www.credit999.cn/index.php?m=home&c=Lists&a=index&tid=78&CompanyName=苏州盈信企业管理有限公司
```

**手动搜索（通过浏览器）：**
1. 打开 `https://www.credit999.cn`
2. 在搜索框输入企业全称
3. 点击搜索按钮

### 2.2 获取证书详情页URL

搜索结果页面包含多个认证项，每个都是可点击的链接。URL结构：
```
https://www.credit999.cn/index.php?m=home&c=Lists&a=index&tid=80&orderID={orderID}&creditNum={证书编号}
```

其中 `creditNum` 参数值即证书编号。可以通过浏览器控制台获取所有链接：

```javascript
// 在搜索结果页执行，获取所有证书链接
Array.from(document.querySelectorAll('a[href*="orderID"]')).map(a => ({
  text: a.textContent.trim(),
  href: a.href
}))
```

### 2.3 证书详情页内容

详情页通过JS fetch请求 `/api_search/detail.php?orderID={orderID}&creditNum={creditNum}` 获取数据，然后渲染到页面模板中。

**页面展示的信息：**
- **企业信用信息**：评级类型、证书编码、评级时间、有效期至、评级机构
- **企业基础信息**：公司名称、统一社会信用代码、法定代表人、营业期限、工商登记机关、注册地址、经营范围

**注意：** 该平台仅展示**文字信息**，不包含证书图片/扫描件。如需截图保存需要自行截图。

### 2.4 证书截图方法

由于浏览器工具中模型可能不支持图片输入，但 `browser_vision` 调用**即使 vision 分析失败也会保存截图文件**：

1. 导航到证书详情页
2. 调用 `browser_vision(question="截图")`
3. 截图文件保存在 `/home/administrator/.hermes/cache/screenshots/browser_screenshot_*.png`
4. 复制到桌面：`cp <screenshot_path> /mnt/c/Users/Admin/Desktop/`

## 三、信用查询与合规账的关联

证书公示信息可用于：
- **销售环节**：展示公司AAA认证作为专业背书
- **签约环节**：验证信用评级有效期
- **客户维护**：定期查看客户企业的信用状态变化

## 四、盈信 AAA 认证清单（2026年7月）

可通过上述方法在 credit999.cn 查到以下10项认证：

| # | 认证名称 | 证书编号 |
|:-:|:---------|:---------|
| 1 | AAA级诚信经营示范单位 | ZSTD17830576610430 |
| 2 | AAA级信用企业 | ZSTD17830576610431 |
| 3 | AAA级质量服务诚信单位 | ZSTD17830576610432 |
| 4 | AAA级重合同守信用企业 | ZSTD17830576610433 |
| 5 | AAA级资信企业 | ZSTD17830576610434 |
| 6 | AAA级诚信供应商 | ZSTD17830576610435 |
| 7 | 中国诚信企业家 | ZSTD17830576610436 |
| 8 | 中国诚信经理人 | ZSTD17830576610437 |
| 9 | AAA级重服务守信用企业 | ZSTD17830576610438 |
| 10 | AAA级重质量守信用企业 | ZSTD17830576610439 |

颁发机构：北京泽盛通达信用评估有限公司
评级时间：2026-07-03
有效期至：2029-07-02
