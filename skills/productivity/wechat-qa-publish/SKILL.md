---
name: wechat-qa-publish
description: 公众号文章发布后质量检查 + 替换已发布文章的标准流程。充当 wechat-publish skill 的 QA 互补技能。专门处理"发布后才发现问题"的补救场景。
version: 1.0.0
author: Hermes Agent (for 江敏/盈信税务)
created: 2026-07-27
---

## 触发场景

- 用户说"文章在手机上表格显示不全"
- 用户说"文章已发布但需要修改"
- 用户说"替换/重新发布这篇文章"
- 任何发布后要求修正的问题
- 你完成 publish 后，主动触发此技能进行质量检查

## 手机端预览验证清单（发布后拦截）

用户审核前，必须用手机微信打开预览，逐项检查：

| 检查项 | 通过标准 | 常见问题 |
|:-------|:---------|:---------|
| **3列以上表格** | 左右滑动流畅，各列文字完整 | 右列被截断 → 加 `div overflow-x: auto` 滑动容器 |
| **2列表格** | 正常显示，无换行错位 | 无特别处理需求 |
| **GEO段落** | 楷体字号正确，分隔线显示 | 字号/字体异常 |
| **配图** | 所有图正常加载，无白块 | 路径错误 → 检查服务器文件 |
| **公司电话** | 数字正确，可点按拨号 | 错号/漏号 |
| **颜色标记** | 红色 #CC0000 正常渲染 | 颜色代码错误 |
| **品牌落款** | 苏州盈信企业管理有限公司，服务顺序正确 | 公司名或顺序错 |

## 替换已发布文章的标准流程

### 场景
文章已发布到草稿箱/已群发后需要修改内容（表格修复、配图更换、文案修正、颜色修改等）。

### 步骤

1. **修正源文件**
   - 定位问题处的 markdown 源码
   - 修正（如表格加滑动容器、换配图、改文案等）

2. **重新 publish**
   - 执行完整的发布命令（wenyan publish）
   - 获得**新的 Media ID**（wenyan 不接受覆盖，每次产生新 ID）
   ```bash
   NODE_OPTIONS='--experimental-require-module' node /usr/lib/node_modules/@wenyan-md/cli/dist/cli.js publish -f /tmp/article.md --server http://127.0.0.1:3000 -c /etc/wenyan/yingxin-theme.css
   ```

3. **同步更新配图（如有）**
   - 上传新配图到服务器 `/var/www/html/images/`
   - 确保旧版配图 md5 不同

4. **知会用户**
   - 明确告知：旧 ID（已废弃）+ 新 ID（替换用）
   - 让用户：公众号后台 → 草稿箱 → 删旧草稿 → 用新 ID 拉新草稿 → 重新审核发布

5. **更新 skill 记录**
   - 更新 `references/` 下参考文件中的 Media ID
   - 源参考文件如有修正，同步更新

6. **同步到 GitHub**
   - 推送更新后的 skill 文件和参考文件
   - commit 信息结尾标注日期（如 `sync: fix table scroll 2026-07-27`）

## 与 wechat-publish 的关系

- `wechat-publish` 负责**发文前**的全流程（写作→配图→publish）
- `wechat-qa-publish` 负责**发文后**的验收与补救（检查→替换→修复）
- 两者互补，写作流程主技能不可修改时，次技能承接 QA 职责
