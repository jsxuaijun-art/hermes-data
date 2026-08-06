# 百度文库教育词汇资源爬取

## 2026-07-04 实测：苏州中考英语词汇搜索

### 目标
搜索「苏州中考英语词汇表」的完整 word list，用于生成默写本。

### 使用工具
Playwright（真实浏览器）+ 反检测初始化脚本

### 搜索结果

| 工具 | 结果 |
|------|------|
| Bing CN (cn.bing.com) | ✅ 正常返回搜索结果，但多为中考资讯网站，无直接词汇文件下载 |
| 百度搜索 | ❌ 触发滑块验证码，无法自动化访问 |
| 百度文库搜索 | ✅ 正常加载，可搜到目标文档，预览片段可提取词汇 |
| 百度文库文档页 | ⚠️ 部分文档可看标题/预览，完整内容需登录 + 付费 |

### 百度文库访问模式

**搜索页访问**：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
        locale='zh-CN',
    )
    page = context.new_page()
    # 反检测脚本
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
        window.chrome = { runtime: {} };
    """)
    
    page.goto('https://wenku.baidu.com/search?word=苏州中考词汇表&org=0', 
              wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # 提取页面文本（搜索结果预览包含词汇片段）
    text = page.inner_text('body')
```

**搜索结果预览提取**：
百度文库搜索结果的body text中包含文档预览片段（如前几十个词汇），可通过正则提取：
```python
import re
words = re.findall(r'([a-z]+)\s+(n\.|v\.|adj\.|adv\.)', text, re.IGNORECASE)
```

**文档URL格式**：
```
https://wenku.baidu.com/view/<32位hex>.html?fr=search
```

### 局限性
1. **百度文库文档页需要登录**才能查看完整内容，自动化无法绕过
2. **文档预览仅显示前几条词汇**，不完整
3. **下载需要文库VIP或付费**，无法通过爬虫免费获取
4. **建议方案**：手动在百度文库搜索 → 付费下载 → 提供TXT文件给agent处理

### 已知可用的苏州中考相关文档
| 文档名 | 链接片段 |
|--------|----------|
| 2024中考复习必背初中英语单词词汇表(苏教译林版) | `view/fe165c1b07a1b0717fd5360cba1aa81145318f8e.html` |
| 江苏省中考英语词汇整理(顺序版) | `view/aece7165900ef12d2af90242a8956bec0975a5b6.html` |
| 苏州中考词汇表（59页） | 搜索「苏州中考词汇表」第一个结果 |

### 经验总结
- Playwright + 反检测脚本 ✅ 可以访问百度文库搜索页
- 但完整文档获取需要用户手动操作（付费下载）
- 爬虫能做的是：搜索定位、预览提取、给出精准链接
- 完整词库获取 → 推荐用户从百度文库付费下载后提供
