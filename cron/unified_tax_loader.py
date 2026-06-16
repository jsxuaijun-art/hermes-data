#!/usr/bin/env python3
"""
每日财税监控 + (周一) 每周深度分析脚本
只在周一、周三、周五 09:05 执行
周一额外输出周度分析（含机会雷达+月度战略）
"""
import os
import datetime

today = datetime.date.today()
dow = today.weekday()  # 0=周一, 2=周三, 4=周五
weekday_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
dow_cn = weekday_cn[dow]

# ============================================================
# 1. 每日监控部分
# ============================================================
daily_prompt_path = os.path.expanduser("~/.hermes/cron/daily_tax_intelligence.md")
with open(daily_prompt_path, "r") as f:
    daily_template = f.read()

daily_template = daily_template.replace("{{DATE_YYYY-MM-DD}}", today.strftime("%Y-%m-%d"))
daily_template = daily_template.replace("{{DOW_CN}}", f"{dow_cn}（推送日）" if dow in (0, 2, 4) else dow_cn)

output = []

output.append("=" * 60)
output.append("【执行任务：每日财税监控】")
output.append("=" * 60)
output.append(f"执行日期：{today.strftime('%Y-%m-%d')}（{dow_cn}）")

# 判断推送标记
if dow == 0:
    output.append("推送标记：⚠️ 本报告需发送至企业微信群（周一·含周度分析）")
elif dow == 2:
    output.append("推送标记：⚠️ 本报告需发送至企业微信群（周三）")
elif dow == 4:
    output.append("推送标记：⚠️ 本报告需发送至企业微信群（周五）")
else:
    output.append("⚠️ 错误：本任务应在周一、三、五执行")

output.append("")
output.append(daily_template)
output.append("")
output.append(f"【执行指令：每日报告保存到 ~/tax_intel/daily/{today.strftime('%Y-%m-%d')}.md】")
output.append("")

# ============================================================
# 2. 周一额外输出周度分析
# ============================================================
if dow == 0:
    weekly_prompt_path = os.path.expanduser("~/.hermes/cron/weekly_tax_deep_dive.md")
    with open(weekly_prompt_path, "r") as f:
        weekly_template = f.read()

    # 上周的周一和周日
    prev_monday = today - datetime.timedelta(days=7)
    prev_sunday = prev_monday + datetime.timedelta(days=6)
    week_num = today.isocalendar()[1]

    next_30d = today + datetime.timedelta(days=30)
    next_60d = today + datetime.timedelta(days=60)
    next_90d = today + datetime.timedelta(days=90)

    replacements = {
        "{{PREVIOUS_MONDAY_YYYY-MM_DD}}": prev_monday.strftime("%Y-%m-%d"),
        "{{PREVIOUS_SUNDAY_YYYY-MM_DD}}": prev_sunday.strftime("%Y-%m-%d"),
        "{{WEEK_NUM}}": str(week_num),
        "{{YEAR}}": today.strftime("%Y"),
        "{{DATE_YYYY-MM-DD}}": today.strftime("%Y-%m-%d"),
        "{{DOW_CN}}": dow_cn,
        "{{NEXT_30D}}": next_30d.strftime("%Y-%m-%d"),
        "{{NEXT_60D}}": next_60d.strftime("%Y-%m-%d"),
        "{{NEXT_90D}}": next_90d.strftime("%Y-%m-%d"),
    }
    for k, v in replacements.items():
        weekly_template = weekly_template.replace(k, v)

    output.append("=" * 60)
    output.append("【执行任务：每周深度分析（含机会雷达+月度战略）】")
    output.append("=" * 60)
    output.append("")
    output.append(weekly_template)
    output.append("")
    output.append(f"【执行指令：周度报告保存到 ~/tax_intel/weekly/{today.strftime('%Y')}-W{week_num}.md】")

# ============================================================
# 3. 推送指令 - 生成报告后自动推送到企微群
# ============================================================

import subprocess

push_instructions = []
push_instructions.append("")
push_instructions.append("=" * 60)
push_instructions.append("【推送指令】")
push_instructions.append("=" * 60)
push_instructions.append("")
push_instructions.append("报告生成完成后，请将报告内容推送到企微群：")
push_instructions.append("")
push_instructions.append(f"python3 /opt/wecom-bot/push_report.py ~/tax_intel/daily/{today.strftime('%Y-%m-%d')}.md markdown")
push_instructions.append("")
push_instructions.append("确认推送结果中 errcode == 0，否则需要检查。")

output.extend(push_instructions)

print("\n".join(output))
