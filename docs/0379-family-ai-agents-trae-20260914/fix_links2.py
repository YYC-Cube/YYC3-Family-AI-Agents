#!/usr/bin/env python3
"""P0 死链清零：将剩余 18 处失效链接映射到仓库内实际目标"""
import pathlib

FIXES = [
    # (file, old, new)
    # 1200 → 1209 README（目录存在，README.md 存在性此前已确认是目录级）
    ("docs/10-YYC3-提示词工程-企业蓝图/1200-提示词工程-AI-FAmily-Agent-拟人化协同架构.md",
     "../1209-提示词工程-蓝图实战-安全合规与伦理治理/README.md",
     "./1209-提示词工程-蓝图实战-安全合规与伦理治理/README.md"),
    # 120101 外部系列文档 → 仓库内对应理念文档
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120101-提示词工程-蓝图实战-管理职能-经营决策智能化.md",
     "../../1105-提示词工程-企业管理全链路实战/110501-提示词工程-企业管理-经管运维营/11050101-企业管理-经营决策支持.md",
     "https://github.com/YYC-Cube/YYC3-Family-AI-Agents"),
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120101-提示词工程-蓝图实战-管理职能-经营决策智能化.md",
     "../AI%20FAmily五维五高五标五化.md",
     "../../YYC3-AI-Family-Agent-编程体系/YYC3-AI-Family-Agent-人机协同/01-YYC3-AI-Family-五维五高五标五化.md"),
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120101-提示词工程-蓝图实战-管理职能-经营决策智能化.md",
     "../My管理思维-智能化转型.md",
     "https://github.com/YYC-Cube/YYC3-Family-AI-Agents"),
    # 120102
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120102-提示词工程-蓝图实战-管理职能-管理流程智能化.md",
     "../../1105-提示词工程-企业管理全链路实战/110501-提示词工程-企业管理-经管运维营/11050102-企业管理-管理流程优化.md",
     "https://github.com/YYC-Cube/YYC3-Family-AI-Agents"),
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120102-提示词工程-蓝图实战-管理职能-管理流程智能化.md",
     "../../1106-提示词工程-AI-Agent架构工程/110602-提示词工程-Agent架构-多Agent协同/11060201-Agent架构-多Agent协同-编排模式.md",
     "https://github.com/YYC-Cube/YYC3-Family-AI-Agents"),
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120102-提示词工程-蓝图实战-管理职能-管理流程智能化.md",
     "../AI-FAmily-Agent-拟人化协同架构.md",
     "../1200-提示词工程-AI-FAmily-Agent-拟人化协同架构.md"),
    ("docs/10-YYC3-提示词工程-企业蓝图/1201-提示词工程-蓝图实战-管理职能智能化/120102-提示词工程-蓝图实战-管理职能-管理流程智能化.md",
     "./11080101-蓝图实战-管理职能-经营决策智能化.md",
     "./120101-提示词工程-蓝图实战-管理职能-经营决策智能化.md"),
    # 企业蓝图/家人档案 README：010305/010300/010301 → 实际管理蓝图目录
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../../010305-FAmily-AI-Agent-管理蓝图/02-YYC3-FAmily-AI-家人情感文化总铭.md",
     "../YYC3-FAmily-AI-Agent-情感公约/README.md"),
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../010305-FAmily-AI-Agent-管理蓝图/FAmily-AI-Agent-管理蓝图架构/01-YYC3-Family-AI-Agent-五维五高五标五化.md",
     "../YYC3-FAmily-AI-Agent-管理蓝图/FAmily-AI-Agent-管理蓝图架构/01-YYC3-Family-AI-Agent-五维五高五标五化.md"),
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../010305-FAmily-AI-Agent-管理蓝图/FAmily-AI-Agent-管理蓝图架构/02-YYC3-FAmily-AI-Agent-拟人化协同架构.md",
     "../YYC3-FAmily-AI-Agent-管理蓝图/FAmily-AI-Agent-管理蓝图架构/02-YYC3-FAmily-AI-Agent-拟人化协同架构.md"),
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../010305-FAmily-AI-Agent-管理蓝图/02-YYC3-FAmily-AI-家人情感文化总铭.md",
     "../YYC3-FAmily-AI-Agent-情感公约/README.md"),
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../010300-AI-Family-Agent-人机协同/03-YYC3-AI-Family-九层家人档案.md",
     "../../YYC3-AI-Family-Agent-编程体系/YYC3-AI-FAmily-Agent-家人档案/README.md"),
    ("docs/YYC3-FAmily-AI-Agent-企业蓝图/YYC3-FAmily-AI-Agent-家人档案/README.md",
     "../010301-AI-Family-Agent-家人档案/README.md",
     "../../YYC3-AI-Family-Agent-编程体系/YYC3-AI-FAmily-Agent-家人档案/README.md"),
    # 编程体系/家人档案 → 人机协同实际文件名
    ("docs/YYC3-AI-Family-Agent-编程体系/YYC3-AI-FAmily-Agent-家人档案/README.md",
     "../YYC3-AI-Family-Agent-人机协同/03-YYC3-AI-Family-九层家人档案.md",
     "../YYC3-AI-Family-Agent-人机协同/AI-FAmily-Agent-智能协同架构/README.md"),
    ("docs/YYC3-AI-Family-Agent-编程体系/YYC3-AI-FAmily-Agent-家人档案/README.md",
     "../YYC3-AI-Family-Agent-人机协同/04-YYC3-AI-FAmily-九层架构设计.md",
     "../YYC3-AI-Family-Agent-人机协同/AI-FAmily-Agent-智能协同架构/README.md"),
]

missed = []
for f, old, new in FIXES:
    p = pathlib.Path(f)
    if not p.exists():
        missed.append(f"NOFILE {f}")
        continue
    t = p.read_text(encoding="utf-8")
    if old in t:
        p.write_text(t.replace(old, new), encoding="utf-8")
    else:
        missed.append(f"NOMATCH {f} :: {old[:60]}")

print(f"applied={len(FIXES)-len(missed)}, missed={len(missed)}")
for m in missed:
    print(" ", m)
