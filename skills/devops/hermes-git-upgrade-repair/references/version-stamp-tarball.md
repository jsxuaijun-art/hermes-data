# 给 tarball/无 .git 的 Hermes 安装补版本戳（恢复 hermes --version 显示）

目标：某安装目录无 `.git` 时，让 `hermes --version` 显示指定版本号、日期、Install method
（不重装 git、代码照旧）。探测入口是 `hermes_cli/_startup_fast.py::print_fast_version_info()`
（run_agent.py 不参与版本输出），三个字段各自有独立来源：

| 字段 | 来源文件 / 函数 | 备注 |
|---|---|---|
| 版本 vX | `hermes_cli/version_info.py::get_version_info()` | packaged/tarball 优先读 `<install root>/install-stamp.json`（schema 2）；无 stamp 或字段不全即回退 vunknown |
| 日期 (...) | `hermes_cli/__init__.py::__release_date__` | **stamp 不驱动日期**，日期要单独改这里 |
| Install method | `hermes_cli/config.py::detect_install_method()` | 先读 `<install root>/.install_method`，再 `$HERMES_HOME/.install_method`，managed/nix/.git/unknown 兜底 |

关键坑：`config.py::_SUPPORTED_INSTALL_METHODS` 是白名单。若它不含 `tarball`，即使 `.install_method`
写了 tarball 也会被过滤回 `unknown`。**必须把 tarball 加进白名单**，否则前两步白做。

## 步骤

```bash
ROOT=/home/dmin/hermes-agent-v0.20.6   # 活的安装目录（readlink -f $(which hermes) 确认）
EPOCH=$(date -u -d '2026-10-22 00:00:00' +%s)

# 1. 生成 install-stamp.json —— 用官方脚本保证 schema 格式
#    用 venv 的 python3.12 跑：系统 python3.10 缺 datetime.UTC，脚本会崩
/home/dmin/.venv-hermes/bin/python3.12 \
  $ROOT/scripts/write_install_stamp.py \
  --output $ROOT/install-stamp.json \
  --commit 0000000000000000000000000000000000000001 \
  --branch tarball --base-version 0.22.5 --display-version 0.22.5 \
  --distance 0 --commit-date $EPOCH --source tarball --update-mechanism external

# 2. 声明 install method（内容是 tarball + 换行）
printf 'tarball\n' > $ROOT/.install_method
```

3. 把 `tarball` 加进 `config.py::_SUPPORTED_INSTALL_METHODS` 白名单
   （{..."git", "tarball", "unknown"}），并同步 docstring。
4. 改 `__init__.py::__release_date__` 为目标日期（stamp 不驱动日期字段）。

## 验证

新开进程 `hermes --version`（旧会话加载的是启动时的旧显示，须新开进程看）。

## 注意

- `--commit` 必须非全零：`get_version_info()` 对全零 commit 直接忽略整个 stamp → 仍 vunknown。
  tarball 无真 git sha，放 `000...0001` 占位（横幅 `· upstream 00000000` 即来自该占位，正常）。
- 版本正确后横幅若仍报旧 SHA / behind，是 stamp 占位所致，勿当版本错。
- stamp 只影响 `--version` 显示；运行中的代码、升级能力都未变。
- 该目录重新被 git clone / 正规升级覆盖后，这些 patch 可能被冲掉或与 .git 来源冲突，重装后复核。
