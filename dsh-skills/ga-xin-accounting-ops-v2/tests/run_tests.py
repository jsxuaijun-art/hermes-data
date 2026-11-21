#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CARE 框架回归评估集 runner

  python run_tests.py                # 跑全部
  python run_tests.py --filter G01,G04b
  python run_tests.py --json         # 机器可读结果

退出码 0 = 全绿；1 = 有失败。任何规则/引擎/框架改动必须先跑全绿。
"""
import argparse
import copy
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
import rnd_engine  # noqa: E402

GOLDEN = ROOT / "tests" / "golden_cases.json"


def deep_merge(base, patch):
    out = copy.deepcopy(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        elif k in out and isinstance(out[k], list) and isinstance(v, list):
            merged = copy.deepcopy(out[k])
            for i, item in enumerate(v):
                if i < len(merged) and isinstance(merged[i], dict) and isinstance(item, dict):
                    merged[i] = deep_merge(merged[i], item)
                elif i < len(merged):
                    merged[i] = copy.deepcopy(item)
                else:
                    merged.append(copy.deepcopy(item))
            out[k] = merged
        else:
            out[k] = copy.deepcopy(v)
    return out


def build_case(spec):
    if spec.get("case"):
        case = copy.deepcopy(spec["case"])
    elif spec.get("case_file"):
        case = json.loads((ROOT / spec["case_file"]).read_text(encoding="utf-8"))
    else:
        raise ValueError("case 或 case_file 必须提供其一")
    if spec.get("case_patch"):
        case = deep_merge(case, spec["case_patch"])
    return case


def get_path(obj, path):
    cur = obj
    for k in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(k)
        elif isinstance(cur, list):
            try:
                cur = cur[int(k)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if cur is None:
            return None
    return cur


def contains(actual, expected):
    if actual is None:
        return False
    if isinstance(actual, str):
        return str(expected) in actual
    if isinstance(actual, dict):
        return expected in actual or expected in actual.values()
    if isinstance(actual, list):
        for item in actual:
            if item == expected:
                return True
            if isinstance(item, dict) and (expected in item or expected in item.values()):
                return True
            if isinstance(item, str) and str(expected) in item:
                return True
        return False
    return actual == expected


def evaluate(res, a):
    if "rule_active" in a or a.get("path") == "rule_active":
        got = a["value"] in res["active_rules"]
        return got, f"active_rules 含 {a['value']}"
    if "rule_expired" in a or a.get("path") == "rule_expired":
        got = a["value"] in res["expired_rules_excluded"]
        return got, f"expired 含 {a['value']}"
    path = a["path"]
    actual = get_path(res, path)
    if "equals" in a:
        want = a["equals"]
        if isinstance(want, bool):
            ok = actual is want
        elif isinstance(want, (int, float)) and isinstance(actual, (int, float)):
            ok = abs(float(actual) - float(want)) < 0.01
        else:
            ok = actual == want
        return ok, f"{path} = {actual!r} (期望 {want!r})"
    if "gte" in a:
        return isinstance(actual, (int, float)) and actual >= a["gte"], f"{path} = {actual!r} >= {a['gte']}"
    if "lte" in a:
        return isinstance(actual, (int, float)) and actual <= a["lte"], f"{path} = {actual!r} <= {a['lte']}"
    if "contains" in a:
        return contains(actual, a["contains"]), f"{path} 含 {a['contains']!r}"
    if a.get("not_empty"):
        return bool(actual), f"{path} 非空 = {bool(actual)}"
    raise ValueError(f"未知断言类型: {a}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", help="只跑指定用例，逗号分隔")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    doc = json.loads(GOLDEN.read_text(encoding="utf-8"))
    cases = doc["cases"]
    if args.filter:
        wanted = set(args.filter.split(","))
        cases = [c for c in cases if c["id"] in wanted]

    results = []
    total_assert = total_pass = total_fail = 0
    for spec in cases:
        try:
            case = build_case(spec)
            if spec.get("mode") == "audit":
                res = rnd_engine.audit(case, spec.get("as_of"))
            else:
                res = rnd_engine.run(case, spec.get("as_of"))
        except Exception as e:
            results.append({"id": spec["id"], "name": spec["name"],
                            "error": str(e), "passed": 0, "failed": 1, "details": []})
            total_fail += 1
            continue
        passed = failed = 0
        details = []
        for a in spec["assertions"]:
            try:
                ok, msg = evaluate(res, a)
            except Exception as e:
                ok, msg = False, f"断言执行异常 {e}"
            passed += int(ok)
            failed += int(not ok)
            total_assert += 1
            total_pass += int(ok)
            total_fail += int(not ok)
            if not ok:
                details.append(msg)
        results.append({"id": spec["id"], "name": spec["name"],
                        "kernel_ids": spec.get("kernel_ids", []),
                        "passed": passed, "failed": failed, "details": details})

    if args.json:
        print(json.dumps({"total_cases": len(results), "total_assertions": total_assert,
                          "passed": total_pass, "failed": total_fail,
                          "results": results}, ensure_ascii=False, indent=2))
    else:
        print("=== CARE 回归评估集 ===")
        for r in results:
            if "error" in r:
                print(f"  ERROR {r['id']}  {r['name']}: {r['error']}")
                continue
            status = "PASS" if r["failed"] == 0 else "FAIL"
            dot = "." * max(1, 44 - len(r["name"]) - len(r["id"]))
            print(f"  {status:<4} {r['id']}  {r['name']} {dot} {r['passed']}/{r['passed'] + r['failed']}")
            for d in r["details"]:
                print(f"        ↳ {d}")
        print(f"\n合计：{len(results)} 组 / {total_assert} 断言 / {total_pass} 通过 / {total_fail} 失败")
        print("RESULT =", "ALL_GREEN" if total_fail == 0 else "FAILED")
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
