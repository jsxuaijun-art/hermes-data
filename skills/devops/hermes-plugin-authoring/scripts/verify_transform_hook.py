#!/usr/bin/env python3
"""验证 transform_tool_result 钩子真实生效的端到端探针。

用法:
    python3 verify_transform_hook.py
    cd ~/hermes-agent && python3 ~/.hermes/skills/devops/hermes-plugin-authoring/scripts/verify_transform_hook.py

原理:
    造一个含"目标模式"的临时文件 → 真走 model_tools.handle_function_call('read_file')
    → 断言进入模型上下文的内容已被钩子处理。

默认测「法定身份后的姓名」规则（names 不会被推送前 leak_scan 扫，故默认样例可安全随 repo 推送）:
    VB_SENSITIVE      写入原文件的敏感串（默认: 赵六，虚构占位名）
    VB_EXPECTED_MASK  期望出现的脱敏形式（默认: TT，姓名前两字→T）

⚠ 要测信用代码/身份证规则时，请用本地环境变量指向「你自己本地词表」里的脱敏对
(如 VB_SENSITIVE=本地词表真实值, VB_EXPECTED_MASK=其脱敏值)，绝不要把真实码写进本脚本——
本脚本会被 hermes_push.sh 的 leak_scan.py 扫描，任何未脱敏 18 位码形都会中止推送。

退出码: 0=钩子生效; 1=未生效/被误改。
注意: 若尚未 `hermes plugins enable <name>`，本探针会如实失败——这正是要在下次会话复验的信号。
"""
import os
import sys
import tempfile


def main() -> int:
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    os.environ["HERMES_HOME"] = hermes_home

    # 默认皆虚构/脱敏安全样本，可随仓库推送；真实码检测靠本地环境变量覆盖。
    sensitive = os.environ.get("VB_SENSITIVE", "赵六")
    expected_mask = os.environ.get("VB_EXPECTED_MASK", "TT")
    untouched = os.environ.get("VB_UNTOUCHED", "5,100,000.00")

    body = f"验证材料\n法定代表人：{sensitive}\n本季销售额：{untouched}\n"
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="vb_probe_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(body)

    try:
        import model_tools  # noqa: F401
        from hermes_cli.lifecycle import has_hook

        print("transform_tool_result 已注册:", has_hook("transform_tool_result"))

        result = model_tools.handle_function_call("read_file", {"path": path})
        text = result if isinstance(result, str) else str(result)

        print("--- 模型实际看到的内容 ---")
        print(text[:500])

        ok = True
        if sensitive in text:
            print(f"[FAIL] 敏感内容未脱敏: {sensitive}")
            ok = False
        if expected_mask not in text:
            print(f"[FAIL] 未见脱敏形式: {expected_mask}")
            ok = False
        if untouched not in text:
            print(f"[FAIL] 无关内容被误改: {untouched}")
            ok = False
        if ok:
            print("[PASS] 钩子生效: 敏感已替换、脱敏形式在位、无关内容未动")
        else:
            print("[FAIL] 见上，检查 plugins.enabled 与 has_hook 状态")
            print("提示: 未启用时先 `hermes plugins enable <name>` 并重开会话再复验")
        return 0 if ok else 1
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())