#!/bin/bash
# codex-ds - One-shot coding agent via Hermes + DeepSeek v4 Flash
#
# Usage:
#   codex-ds "写一个Python脚本，抓取税务总局最新政策"
#   echo "重构这个模块" | codex-ds
#   codex-ds -c "继续，补上单元测试"
#   codex-ds --yolo "自动审批危险命令"
#   codex-ds --help
#
# Installed as part of the 'codex' skill.
# Copy to ~/bin/ and chmod +x for daily use.

set -e

HERMES_ARGS=()
PROMPT=""
CONTINUE=false
SHOW_HELP=false
GITREPO=""
YOLO=false

usage() {
  cat <<EOF
codex-ds - One-shot coding agent via Hermes + DeepSeek v4 Flash

用法:
  codex-ds "你的编程需求"       一行命令编程
  echo "需求" | codex-ds        通过管道传参
  codex-ds -c                   继续上一次会话
  codex-ds --yolo               自动审批所有危险命令
  codex-ds --help               显示此帮助

等效于:
  hermes chat -q "..." -Q --yolo --max-turns 90 \\
    -t terminal,file,web,session_search

选项:
  -c, --continue    继续上一次会话
  -y, --yolo        跳过所有审批（危险命令自动执行）
  -m, --max-turns N 最大迭代次数（默认 90）
  -n, --no-quiet    显示完整输出（不静默）
  --help            显示帮助

示例:
  codex-ds "创建一个Python脚本，解析PDF发票并提取金额"
  codex-ds "重构这个JWT认证模块，添加刷新令牌支持"
  cat requirements.txt | codex-ds "分析依赖，找出过期的包"
  codex-ds -c "继续，把单元测试补完"
EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      SHOW_HELP=true
      shift
      ;;
    -c|--continue)
      CONTINUE=true
      shift
      ;;
    -y|--yolo)
      YOLO=true
      shift
      ;;
    -m|--max-turns)
      HERMES_ARGS+=("--max-turns" "$2")
      shift 2
      ;;
    -n|--no-quiet)
      QUIET=false
      shift
      ;;
    *)
      if [[ -z "$PROMPT" ]]; then
        PROMPT="$1"
      else
        PROMPT="$PROMPT $1"
      fi
      shift
      ;;
  esac
done

# If no prompt argument, try reading from stdin (pipe)
if [[ -z "$PROMPT" && ! "$CONTINUE" == true && "$SHOW_HELP" == false ]]; then
  if [[ ! -t 0 ]]; then
    PROMPT=$(cat)
  fi
fi

# Show help if no prompt and not continuing
if [[ -z "$PROMPT" && "$CONTINUE" == false && "$SHOW_HELP" == false ]]; then
  echo "❌ 请提供任务描述或使用 --continue"
  echo ""
  usage
fi

if [[ "$SHOW_HELP" == true ]]; then
  usage
fi

# Default quiet mode
if [[ "${QUIET:-true}" == true ]]; then
  HERMES_ARGS+=("-Q")
fi

# YOLO mode
if [[ "$YOLO" == true ]]; then
  HERMES_ARGS+=("--yolo")
fi

# Check if we're in a git repo (for context)
if git rev-parse --git-dir 2>/dev/null >/dev/null; then
  GITREPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
fi

# Build the command
HERMES_CMD=("hermes" "chat")

if [[ "$CONTINUE" == true ]]; then
  HERMES_CMD+=("--continue")
  if [[ -n "$PROMPT" ]]; then
    HERMES_CMD+=("-q" "$PROMPT")
  fi
else
  HERMES_CMD+=("-q" "$PROMPT")
fi

# Add default toolsets for coding
HERMES_CMD+=("-t" "terminal,file,web,session_search")

# Add extra args (yolo, max-turns, quiet)
HERMES_CMD+=("${HERMES_ARGS[@]}")

# Execute
if [[ -n "$GITREPO" ]]; then
  echo "⚡ codex-ds [$GITREPO] Hermes + DeepSeek v4 Flash" >&2
else
  echo "⚡ codex-ds Hermes + DeepSeek v4 Flash" >&2
fi
echo "" >&2

exec "${HERMES_CMD[@]}"
