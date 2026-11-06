#!/usr/bin/env python3
"""修复 docs/10-* 各子模块 README 中的缩写文件名死链：按数字编号前缀匹配同目录实际文件"""
import pathlib
import re

ROOT = pathlib.Path("docs/10-YYC3-提示词工程-企业蓝图")
PAT = re.compile(r"\]\((\./?)(\d{4,6})-[^)#\s]+?\.md(#[^)]*)?\)")

fixed = 0
unresolved = []
for md in ROOT.rglob("*.md"):
    text = md.read_text(encoding="utf-8")
    orig = text
    for m in PAT.finditer(text):
        prefix, num, anchor = m.group(1), m.group(2), m.group(3)
        target = (md.parent / (prefix + m.group(0)[2:].split("#")[0].lstrip("./"))).resolve()
        # 跳过已存在的链接
        if target.exists():
            continue
        # 在同目录找以该编号开头的 .md
        cands = [p.name for p in md.parent.glob(f"{num}-*.md")]
        if len(cands) == 1:
            new_link = f"]({prefix}{cands[0]}{anchor or ''})"
            text = text.replace(m.group(0), new_link, 1)
            fixed += 1
        elif not cands:
            unresolved.append(f"{md.name} -> {num} (无匹配)")
    if text != orig:
        md.write_text(text, encoding="utf-8")

print(f"fixed={fixed}, unresolved={len(unresolved)}")
for u in unresolved[:15]:
    print(" ", u)
