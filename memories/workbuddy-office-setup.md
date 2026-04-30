# WorkBuddy 办公室 PC 配置记录

## 2026-04-28 配置完成

### SSH Key
- 办公室 PC 复用家里电脑的 SSH Key
- 路径：`C:\Users\Administrator\.ssh\`
- GitHub 账号：`jsxuaijun-art`
- 连接测试：通过 ✅

### hermes-data 仓库
- 克隆到：`C:\Users\Administrator\Desktop\HermesAgent\`
- 包含：SOUL.md、config.yaml、memories/、skills/ 等

### 双设备同步说明
| 操作 | 位置 | 说明 |
|------|------|------|
| Push | 办公室电脑 | 把改动推送到 GitHub |
| Pull | 家里电脑 | 从 GitHub 拉取最新版本 |

### 同步规则
- 每次切换设备前先 Push 再 Pull
- GitHub Desktop 选择 hermes-data 仓库 → Push origin / Pull origin
- .workbuddy 文件夹不要同步（包含敏感路径）
