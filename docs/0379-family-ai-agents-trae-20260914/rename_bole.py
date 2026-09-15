#!/usr/bin/env python3
"""P0-1 命名归一脚本：知遇·伯乐 → 千里·伯乐（以生产层为权威事实源）"""
import pathlib

ROOTS = ["docs/10-YYC3-提示词工程-企业蓝图", "examples/13-YYC3-企业蓝图-代码示例"]
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".bin", ".pyc", ".ico"}
PATTERNS = [
    ("知遇·伯乐", "千里·伯乐"),
    ("知遇-伯乐", "千里-伯乐"),
    ("知遇•伯乐", "千里•伯乐"),
    ("知遇伯乐", "千里伯乐"),
    ("ZhiYuBoLe", "QianLiBoLe"),
    ("zhiyu_bole", "qianli_bole"),
    ("ZHIYU_BOLE", "QIANLI_BOLE"),
    ("ZhiYu_BoLe", "QianLi_BoLe"),
    ("zhiyu-bole", "qianli-bole"),
    ("ZhiYuBole", "QianLiBole"),
    ("zhiyubole", "qianlibole"),
]

changed, skipped = [], []
total_subs = 0
for root in ROOTS:
    for p in pathlib.Path(root).rglob("*"):
        if not p.is_file() or p.suffix.lower() in SKIP_SUFFIX:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            skipped.append(str(p))
            continue
        original = text
        for old, new in PATTERNS:
            count = text.count(old)
            if count:
                text = text.replace(old, new)
                total_subs += count
        if text != original:
            p.write_text(text, encoding="utf-8")
            changed.append(str(p))

print(f"changed_files={len(changed)}")
for c in changed[:10]:
    print(f"  {c}")
print(f"total_substitutions={total_subs}")
print(f"decode_skipped={len(skipped)}")
for s in skipped[:5]:
    print(f"  SKIP {s}")
