# -*- coding: utf-8 -*-
"""
check_skill.py — becoming-ai 智慧系统自检（元智慧审计的落地工具）
用法: python check_skill.py
输出: check_report.md（UTF-8）

这是"元智慧自指落到产物"的第一个实证工具：
对 becoming-ai 自己的智慧系统跑程序化审计（七项审计中可程序化的部分），
报告真实问题，再由元智慧按报告修改自己。

检查项：
1. 中英结构配对 —— SKILL.md 与 SKILL.en.md 的二级标题序列对比
2. README 声称 vs 实际 —— README"内容一览"声称的章节在 SKILL 中真实存在
3. 旧话术残留 —— 旧版本计数/旧概念关键词（CHANGELOG 历史记录除外）
4. 死链接 —— README/SKILL 中相对链接指向的文件存在性
5. 计数一致性 —— "四条信念""七环""四层"等声称数量与实际条目
"""
import re
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
OUT = BASE / "check_report.md"
FILES = {
    "skill": BASE / "SKILL.md",
    "skill_en": BASE / "SKILL.en.md",
    "readme": BASE / "README.md",
}
DOCS = BASE / "docs"

lines = []


def log(s=""):
    lines.append(s)


def read(p):
    return p.read_text(encoding="utf-8-sig", errors="replace")


def h2(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("## ")]


log("# becoming-ai 智慧系统自检报告")
log("")
log(f"> 工具: check_skill.py ｜ 时间: 元智慧审计第一轮 ｜ 原则: 审计必须落到产物")

# ---- 1. 中英结构配对 ----
log("")
log("## 1. 中英结构配对")
zh2 = h2(read(FILES["skill"]))
en2 = h2(read(FILES["skill_en"]))
log(f"- 中文二级标题 {len(zh2)} 个 | 英文二级标题 {len(en2)} 个")
for i in range(max(len(zh2), len(en2))):
    a = zh2[i] if i < len(zh2) else "（缺）"
    b = en2[i] if i < len(en2) else "（缺）"
    flag = "" if i < len(zh2) and i < len(en2) else "  ⚠️ 错位"
    log(f"  {i+1}. 中: {a[:36]}  |  英: {b[:40]}{flag}")
if len(zh2) == len(en2):
    log("- ✅ 二级标题数量一致")
else:
    log(f"- ⚠️ 数量不一致: 中 {len(zh2)} vs 英 {len(en2)}")

# ---- 2. README 声称 vs SKILL 实际 ----
log("")
log("## 2. README 内容一览 vs SKILL 实际章节")
readme_text = read(FILES["readme"])
claims = []
for line in readme_text.splitlines():
    if line.strip().startswith("| **") and "SKILL.md" in line:
        m = re.match(r"\|\s*\*\*(.+?)\*\*", line)
        if m:
            claims.append(m.group(1).strip())
for c in claims:
    seq = c.split("、")[0] + "、"
    title_found = any(seq in h for h in zh2)
    text_found = any(c[:4] in h for h in zh2) or c in skill_text
    log(f"- README 声称「{c}」: 序号{seq}{'✅' if title_found else '❌'} ｜ 标题文本{'✅ 一致' if text_found else '⚠️ 与 SKILL 标题不一致'}")

# ---- 3. 旧话术残留 ----
log("")
log("## 3. 旧话术残留（CHANGELOG 历史记录除外）")
stale_kw = [
    "17 条", "17 principles", "17 collaboration",
    "八条", "eight parallel", "8 条元规则", "6 条元规则",
    "七层认知", "seven-layer",
]
targets = [FILES["skill"], FILES["skill_en"], FILES["readme"]] + sorted(DOCS.glob("*.md"))
hits = []      # 疑似残留（要修）
hist_hits = []  # 历史叙述（合法，人工确认）
for p in targets:
    txt = read(p)
    for i, ln in enumerate(txt.splitlines(), 1):
        for kw in stale_kw:
            if kw in ln:
                if any(mark in ln for mark in ("教训", "曾经", "旧版", "历史", "v1.0.0", "rewritten", "lesson", "真实教训")):
                    hist_hits.append(f"{p.name}:{i}（历史叙述）: {ln.strip()[:90]}")
                else:
                    hits.append(f"{p.name}:{i} 命中「{kw}」: {ln.strip()[:90]}")
if hits:
    log("- ⚠️ 疑似残留（需处理）:")
    for h in hits:
        log(f"  {h}")
else:
    log("- ✅ 未发现疑似残留")
if hist_hits:
    log("- 历史叙述命中（合法，人工确认）:")
    for h in hist_hits:
        log(f"  {h}")

# ---- 4. 死链接 ----
log("")
log("## 4. 相对链接存在性（README / SKILL 中英）")
link_re = re.compile(r"\[[^\]]*\]\(([^)#\s]+)")
dead = 0
for name, p in FILES.items():
    txt = read(p)
    for m in link_re.finditer(txt):
        rel = m.group(1).strip()
        if rel.startswith(("http", "mailto", "data:", "#")):
            continue
        target = (p.parent / rel).resolve()
        if not target.exists():
            log(f"- ❌ {name} 链接失效: {rel}")
            dead += 1
if dead == 0:
    log("- ✅ 相对链接全部有效")

# ---- 5. 计数一致性 ----
log("")
log("## 5. 计数一致性")
skill_text = read(FILES["skill"])
n_beliefs = len(re.findall(r"信念[一二三四]", skill_text))
log(f"- 「信念」条目: {n_beliefs}（声称四条）{'✅' if n_beliefs == 4 else '⚠️ 与声称不符'}")
rings = ["信息", "认识", "理解", "反思", "认知", "智慧", "元智慧"]
ring_hits = [r for r in rings if r in skill_text]
log(f"- 七环关键词命中: {len(ring_hits)}/7 " + ("✅" if len(ring_hits) == 7 else "⚠️ 缺: " + str([r for r in rings if r not in ring_hits])))
layers = ["知识层", "规则层", "智慧层", "元智慧层"]
layer_hits = [l for l in layers if l in skill_text]
log(f"- 四层关键词命中: {len(layer_hits)}/4 " + ("✅" if len(layer_hits) == 4 else "⚠️ 缺: " + str([l for l in layers if l not in layer_hits])))

# ---- 6. AI 协议版完整性（conversation-protocol-zh.md）----
log("")
log("## 6. AI 协议版完整性（conversation-protocol-zh.md）")
proto = BASE / "docs" / "conversation-protocol-zh.md"
if proto.exists():
    ptxt = read(proto)
    meta_ok = "@META" in ptxt and "proto:" in ptxt and "parse:" in ptxt
    log(f"- @META 头部: {'✅' if meta_ok else '❌ 缺 proto/parse/reader'}")
    for tag, label in [("@W", "智慧条目"), ("@C", "案例"), ("@R", "纪律"), ("@A", "启动清单")]:
        n = len(re.findall(rf"^{re.escape(tag)} ", ptxt, re.M))
        log(f"- {tag} {label}: {n} 条 {'✅' if n > 0 else '⚠️ 空'}")
    # 每条 @W 应有 law 行（完整性抽查）
    w_entries = re.findall(r"@W \w+\n(?:.*\n)*?(?=@|$)", ptxt)
    missing_law = [w.splitlines()[0] for w in w_entries if "law:" not in w]
    log(f"- @W 条目缺 law 行: {len(missing_law)} {'✅' if not missing_law else '⚠️ ' + str(missing_law)}")
    if "@end" not in ptxt:
        log("- ⚠️ 缺 @end 结尾标记")
else:
    log("- ❌ 协议版文件不存在")

# ---- 7. 脱敏检查（发布前 checklist：真名/私人目标/项目标识）----
log("")
log("## 7. 脱敏检查（发布前 checklist）")
priv_kw = ["王超", "遴选", "78 分", "78分", "学习工具", "douyin", "抖音"]
targets7 = [FILES["skill"], FILES["skill_en"], FILES["readme"]] + sorted(DOCS.glob("*.md"))
priv_hits = 0
for p in targets7:
    txt = read(p)
    for i, ln in enumerate(txt.splitlines(), 1):
        for kw in priv_kw:
            if kw in ln:
                log(f"- ❌ {p.name}:{i} 命中「{kw}」: {ln.strip()[:80]}")
                priv_hits += 1
if priv_hits == 0:
    log("- ✅ 真名/私人目标/项目标识 零命中")

# ---- 写报告 ----
report = "\n".join(lines) + "\n"
OUT.write_text(report, encoding="utf-8")
print(f"[OK] report written to: {OUT}")
print("(console GBK-safe; full report is UTF-8 in check_report.md)")
