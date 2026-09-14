"""desensitize-read plugin — 读入内容自动脱敏，防止真实主体信息进入模型上下文。

挂一个 ``transform_tool_result`` 钩子：对「读入型」工具的结果（read_file /
search_files / web_extract / web_search / terminal / execute_code / browser_* /
vision_analyze）在追加进对话上下文之前，按固定规则脱敏，返回字符串即替换结果。

脱敏规则（与 security/desensitization skill 一致）：
  ① 精确词表 ~/.hermes/leak-blocklist.txt（real=masked 或单列 real）→ 替换为 masked/[已脱敏]
  ② 未脱敏的统一社会信用代码（18位、首位5或9、末8位非全X、第2~17位含≥2字母）
     → 保留前10位，末8位全部用 X
  ③ 未脱敏的身份证号（18位、含真实出生日期）→ 保留前6位与后4位，中间8位用 X
  ④ 法定身份字段后的姓名（法定代表人/法人代表/负责人/财务负责人/股东/投资人/联系人/办税人：X）
     → 姓名前两个字各用 T 代替（示例：杨建国→TT国；张三→TT）

设计要点：
  * 只作用于「外部读入内容」，不改动 agent 自己产出（write_file 等结果不在目标集）。
  * 词表优先（长串优先）；正则带词边界，避免误伤更长的哈希/标识串。
  * 失败即放行（fail-open）：任何异常都不阻断工具链。
  * 关闭：环境变量 DESENSITIZE_READ_DISABLE=1。自定义目标工具：DESENSITIZE_READ_TOOLS=read_file,terminal
"""

from __future__ import annotations

import logging
import os
import re
import threading
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 「读入型」工具：其结果是外部内容，需脱敏后才进上下文
_DEFAULT_TARGET_TOOLS = {
    "read_file",
    "search_files",
    "web_extract",
    "web_search",
    "terminal",
    "execute_code",
    "browser_navigate",
    "browser_snapshot",
    "browser_console",
    "vision_analyze",
}

# 带词边界，避免命中更长的字母数字串（哈希/标识）内部
_CREDIT_RE = re.compile(r"(?<![0-9A-HJ-NPQRTUWXY])([0-9A-HJ-NPQRTUWXY]{18})(?![0-9A-HJ-NPQRTUWXY])")
_ID_RE = re.compile(
    r"(?<!\d)([1-9][0-9]{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9X])(?!\d)"
)
# 法定身份字段后的姓名（无固定格式，靠上下文识别）
_NAME_CTX_RE = re.compile(
    r"((?:法定代表人|法人代表|法定代表人姓名|法人|负责人|财务负责人|股东|投资人|联系人|办税人)\s*[:：]\s*)"
    r"([\u4e00-\u9fff·]{2,4})"
)

_MAX_BYTES = 2 * 1024 * 1024  # 超过则跳过（大 blob 脱敏无意义且拖慢）

_BLOCKLIST_PATH = os.path.expanduser("~/.hermes/leak-blocklist.txt")
_blocklist_cache: Optional[List[Tuple[str, str]]] = None
_blocklist_mtime: float = -1.0
_blocklist_lock = threading.Lock()


def _disabled() -> bool:
    return os.environ.get("DESENSITIZE_READ_DISABLE", "").lower() in {"1", "true", "yes", "on"}


def _target_tools() -> set:
    extra = os.environ.get("DESENSITIZE_READ_TOOLS", "").strip()
    if extra:
        return {t.strip() for t in extra.split(",") if t.strip()}
    return _DEFAULT_TARGET_TOOLS


def _load_blocklist() -> List[Tuple[str, str]]:
    """加载精确词表，按 mtime 缓存。格式：``real=masked`` 或单列 ``real``（→[已脱敏]）。"""
    global _blocklist_cache, _blocklist_mtime
    try:
        mtime = os.path.getmtime(_BLOCKLIST_PATH)
    except OSError:
        mtime = -1.0
    with _blocklist_lock:
        if _blocklist_cache is not None and mtime == _blocklist_mtime:
            return _blocklist_cache
        pairs: List[Tuple[str, str]] = []
        if mtime >= 0:
            try:
                with open(_BLOCKLIST_PATH, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            real, masked = line.split("=", 1)
                            real, masked = real.strip(), masked.strip()
                        else:
                            real, masked = line, "[已脱敏]"
                        if real:
                            pairs.append((real, masked))
            except OSError:
                pairs = []
        pairs.sort(key=lambda p: len(p[0]), reverse=True)  # 长串优先，避免子串先被替换
        _blocklist_cache, _blocklist_mtime = pairs, mtime
        return pairs


def _mask_credit(tok: str) -> Optional[str]:
    if len(tok) != 18:
        return None
    if tok[0] not in "59":                      # 5=民政(民办非企业/社团) 9=工商(企业)
        return None
    if tok[-8:] == "XXXXXXXX":                  # 已脱敏
        return None
    if sum(c.isalpha() for c in tok[1:17]) < 2: # 真实主体码必有字母；纯数字串不是码
        return None
    return tok[:10] + "XXXXXXXX"


def _mask_id(m: str) -> str:
    return m[:6] + "XXXXXXXX" + m[-4:]


def _desensitize(text: str) -> Tuple[str, int]:
    n = 0
    for real, masked in _load_blocklist():
        if real in text:
            n += text.count(real)
            text = text.replace(real, masked)

    def _c(mo):
        nonlocal n
        masked = _mask_credit(mo.group(1))
        if masked:
            n += 1
            return masked
        return mo.group(0)

    text = _CREDIT_RE.sub(_c, text)

    def _nm(mo):
        nonlocal n
        name = mo.group(2)
        if len(name) >= 2:
            n += 1
            return mo.group(1) + "T" * 2 + name[2:]
        return mo.group(0)

    text = _NAME_CTX_RE.sub(_nm, text)

    def _i(mo):
        nonlocal n
        n += 1
        return _mask_id(mo.group(1))

    text = _ID_RE.sub(_i, text)
    return text, n


def _on_transform_tool_result(
    tool_name: str = "",
    args: Any = None,
    result: Any = None,
    **_: Any,
) -> Optional[str]:
    """读入结果进入上下文前的脱敏闸。返回字符串即替换结果；None 表示不改动。"""
    if _disabled():
        return None
    if tool_name not in _target_tools():
        return None
    if not isinstance(result, str) or not result:
        return None
    if len(result) > _MAX_BYTES:
        return None
    try:
        new_text, n = _desensitize(result)
    except Exception as exc:  # fail-open：绝不阻断工具链
        logger.debug("desensitize-read error: %s", exc)
        return None
    if n <= 0:
        return None
    logger.info("desensitize-read: masked %d sensitive token(s) in %s result", n, tool_name)
    return new_text


def register(ctx) -> None:
    ctx.register_hook("transform_tool_result", _on_transform_tool_result)
