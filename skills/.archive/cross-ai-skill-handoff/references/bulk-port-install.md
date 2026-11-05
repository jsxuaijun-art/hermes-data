# 批量移植实测记录（2026-09：核心技能 → Hermes/WorkBuddy/Codex/Claude Code 四端）

## 四端技能目录矩阵

| 工具 | 运行位置 | 技能目录 | 引用方式 |
|------|---------|---------|---------|
| Hermes | WSL2 | `~/.hermes/skills/` | 软链 `ln -sfn`（或本地副本） |
| WorkBuddy | Windows | `%USERPROFILE%\.workbuddy\skills\` | junction（实测全激活；早期「只报 1 个」是扫描误报，见 workbuddy-skill-activation.md） |
| Codex CLI | WSL2 | `~/.codex/skills/` | 软链 `ln -sfn` |
| Claude Code | Windows | `%USERPROFILE%\.claude\skills\` | junction |

## 单一源 + 链接架构

- 唯一源：`/mnt/d/obsidian-vault/50-Skills/<技能>/SKILL.md`
- 安装脚本（也放在 vault 目录里，改源后重跑即全端生效）：
  - `install-wsl.sh` —— `ln -sfn "$SRC/$s" "$tb/$s"`；支持参数 codex/hermes/all
  - `install-windows.ps1` —— `New-Item -ItemType Junction -Path "$t\$s" -Target "$src\$s" -Force`；目标 WorkBuddy + Claude
- 配套文档：`FORMAT.md`（格式标准）、`SKILLS-INDEX.md`（索引）、`README.md`（维护约定）

## 验证命令（实测用）

```bash
# WSL 端
bash /mnt/d/obsidian-vault/50-Skills/install-wsl.sh codex
ls ~/.codex/skills/ | grep -v '^\.' | wc -l          # 应=技能数(+原有)
ls -la ~/.codex/skills/ | grep -E "wechat-publish"   # 确认 -> /mnt/d/... 软链

# Windows 端（从 WSL 调用，路径必须用字面量，别经 bash 变量转义）
powershell.exe -NoProfile -Command "Test-Path 'C:\Users\Admin\.workbuddy\skills\wechat-publish\SKILL.md'"
# 或整个脚本
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\obsidian-vault\50-Skills\install-windows.ps1'
ls /mnt/c/Users/Admin/.claude/skills/ | grep -v '^\.' | wc -l
```

## 踩坑明细

1. **PowerShell 5.1 编码**：Windows PowerShell 读 .ps1 按系统 ANSI，UTF-8 中文会乱码 → "字符串缺少终止符"解析错误。**修复：.ps1 全部 ASCII（英文消息）**；要中文说明放 README.md / FORMAT.md（UTF-8 没问题）。
2. **WSL bash → powershell.exe 路径转义**：`"$T\$S"` 经 bash 双引号传给 powershell 会碎掉，junction 静默创建到错误路径或失败。修复：写成 .ps1 用 `-File` 执行，或传字面量路径。调试时别 `2>/dev/null`，先看真实报错。
3. **junction 目标 = Windows 盘符路径**（`D:\obsidian-vault\...`）；WSL 的 `/mnt/d` 路径在 PowerShell 里无效。
4. **`/mnt/d/obsidian-vault` 非 git 仓库**：跨机同步走 `~/obsidian-vault` 镜像 + `obsidian-vault-sync.sh`（rsync→commit→push）。改动 50-Skills 后要跑同步才能到其它机器。
5. **Hermes 独有 frontmatter 字段**（`trigger`/`triggers`/`metadata.hermes`）被 Codex/Claude/WorkBuddy 忽略；要它们自动唤起，触发词写进 `description`。
6. **安装脚本 SKILLS 数组 = 生成时快照**（2026-09 关键教训）：脚本的技能名单在生成那刻按「当时有 SKILL.md 的目录」固化；若某技能当时缺 SKILL.md 会被**整段排除**，之后修好源、重跑也不会建它的链接。**规则：每增补/修复技能后，从 vault 当前所有含 SKILL.md 的目录动态重生成两个脚本再跑**。参考生成逻辑：
   ```python
   skills=[n for n in sorted(os.listdir(DEST))
           if os.path.isdir(os.path.join(DEST,n)) and n!='exchange'
           and os.path.exists(os.path.join(DEST,n,'SKILL.md'))]
   ```
7. **同名不同层目录 → 源选错**：Hermes 里同名技能可能同时存在「顶层 references-only 空壳（无 SKILL.md）」和「分类目录下的完整版」。glob `**/<name>` 取 `hits[0]` 可能抓到空壳，整技能搬成残缺副本。**取源必须选含 SKILL.md 且文件数最多的候选**；搬错后用 `rsync -a --delete 源/ vault/技能/` 整目录覆盖（顺带清掉搬错带入的重复文件）。发现一个搬错后，按全部同名目录清单逐个排查其余技能（`geo-optimization` 顶层 27 文件 vs marketing/ 25 文件——取最多）。

## 2026-09 修复实录：short-video-copywriting 残缺副本（Codex 发现，双重根因）

Codex 回报「vault 里 copywriting 缺 SKILL.md 是残缺副本，真正完整源在 Hermes 的 social-media/ 下」。排查证实是**两层 bug 叠加**：

1. 搬运源选错：glob 取到顶层空壳（1 个放错的重复文件、无 SKILL.md）→ vault 副本残缺。
2. 安装脚本名单生成于修复前：当时短路无 SKILL.md → 它被排除在脚本 SKILLS 数组之外 → 修好源后重跑 install 也【不建链接】（不是 [SKIP]，是根本不遍历它）。三端路径 `…/skills/short-video-copywriting/SKILL.md` 全部 MISSING。

修复步骤（实测）：
1. 修正源 SKILL.md 过期说明（「四子技能已归档」— 实际独立技能仍存在 → 改为「四类已并入统一正文，独立技能仍保留可单独触发」），避免 AI 误判加载目标
2. `rsync -a --delete /home/dmin/.hermes/skills/social-media/short-video-copywriting/ /mnt/d/obsidian-vault/50-Skills/short-video-copywriting/`（整目录覆盖，清掉放错的重复 reference → 30 文件：SKILL.md + 29 refs）
3. 删掉 Hermes 顶层空壳目录（无 SKILL.md，纯死重）
4. 重生成 `install-wsl.sh` + `install-windows.ps1`（名单 = 当前 58 个含 SKILL.md 的目录）
5. 重跑两脚本，三端 spot-check `SKILL.md` 存在且 29 refs 齐
6. 重生成 `SKILLS-INDEX.md`（58 个、无 (无 SKILL.md) 缺口）

**副产品规律**：修好 vault 某一技能 = 所有已建软链/junction 的端自动生效；唯一需要重跑安装脚本的场景是「某端当时被跳过、根本没建链接」。

## 结果基线（2026-09 修复后实测）

- vault 50-Skills：59 个技能全部含 SKILL.md（新增 hermes-credential-rotation；此前 short-video-copywriting 残缺已修复）
- Codex（WSL）：59 软链 OK（+原有 → ls 计数 64）
- WorkBuddy（Windows）：59 链接 OK；WorkBuddy **自查确认全部激活、零断链、frontmatter 全合规**。早期「只报出 1 个」是它扫描未完成时的**误报**，结论已修正（当时幸好没把 58 个 junction 改成物理副本）——见 workbuddy-skill-activation.md
- Claude Code（Windows）：59 junction OK（计数 59）
- Hermes（WSL）：本地技能 63 → 补挂 hermes-credential-rotation 单链后 64（**只补它自己没有的那个，勿全量铺软链**，见 SKILL.md 踩坑）
- 单一源 59 个共享技能；各端差值 = 各工具自带技能数（Codex/Hermes 各 +5 左右，WorkBuddy +22）
- spot-check：`short-video-copywriting` 三端均解析到 vault，29 refs 齐；`wechat-publish`、`company-registration`、`tax-audit-response` 等正常
