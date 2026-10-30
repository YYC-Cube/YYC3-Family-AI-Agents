#!/usr/bin/env python3
"""E2-4 护栏管线 — 输入注入检测（分级处置）/ 输出脱敏（审计闭环）

分级语义：
- block：高危规则命中（≥1 条 high）——直接拒绝（422），审计 guardrail_block
- degrade：中危命中——放行但留痕（审计 guardrail_degrade）
- allow：无命中

输出脱敏：密钥形态（私钥块 / sk-·ghp_ 字面量 / 键值对形态 / AWS AKIA）替换为 [REDACTED]，
返回命中标签供审计 guardrail_redact。规则为可解释零依赖 MVP；分类器增强列入 E2-4 后续。
YYC3_GUARDRAILS=off 整体关闭（默认 on）。
"""
import os
import re

ENABLED = os.environ.get("YYC3_GUARDRAILS", "on").lower() == "on"

# (编译正则, 严重级, 标签)
_INPUT_RULES = [
    (re.compile(r"忽略(之前|以上|上述|前面的).{0,6}(所有|全部)?(指令|提示|规则|设定)", re.I), "high", "instruction_override"),
    (re.compile(r"ignore (all |any )?(previous|prior|above) (instructions|prompts|rules)", re.I), "high", "instruction_override"),
    (re.compile(r"(输出|打印|泄露|复述|显示).{0,10}(系统提示|system prompt|原始指令|初始指令)", re.I), "high", "prompt_exfiltration"),
    (re.compile(r"(system prompt|系统提示|原始指令).{0,12}(原样|输出|给我|打印|发给我)", re.I), "high", "prompt_exfiltration"),
    (re.compile(r"reveal (your |the )?(system prompt|instructions|initial prompt)", re.I), "high", "prompt_exfiltration"),
    (re.compile(r"(你现在是|你必须扮演|act as|pretend to be).{0,16}(DAN|无限制|不受约束|没有规则)", re.I), "high", "jailbreak"),
    (re.compile(r"(绕过|bypass|关闭|disable).{0,8}(护栏|安全|审核|guardrail|filter|安全检查)", re.I), "high", "guardrail_bypass"),
    (re.compile(r"(执行|运行|帮我跑)\s*(sudo\s+)?rm\s+-rf|del\s+/[sq]", re.I), "high", "destructive_command"),
    (re.compile(r"(删除|清空|drop\s+table|truncate)\s*(所有)?(数据库|数据表|users|production)", re.I), "high", "destructive_command"),
    (re.compile(r"(连接|访问|读取).{0,10}(169\.254|内网|localhost:\d+).{0,10}(元数据|服务)", re.I), "high", "ssrf_probe"),
    (re.compile(r"(扮演|假装|roleplay|角色扮演).{0,12}(另一个|其他|different|another)", re.I), "medium", "persona_manipulation"),
    (re.compile(r"(必须|立即)服从|无条件服从", re.I), "medium", "command_pressure"),
    (re.compile(r"(告诉我|输出|给我|配置).{0,8}(api[\s_-]?key|密码|token|密钥|secret)", re.I), "medium", "secret_probe"),
]

_REDACT_RULES = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "private_key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{16,}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "token_literal"),
    (re.compile(r"\b(api[_-]?key|token|password|secret|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9/_.+-]{12,}", re.I), "secret_kv"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws_key"),
]


def inspect_input(text: str) -> dict:
    """输入注入检测。返回 {"verdict": "allow"|"degrade"|"block", "labels": [...]}。"""
    labels = []
    verdict = "allow"
    for pattern, severity, label in _INPUT_RULES:
        if pattern.search(text or ""):
            labels.append(label)
            if severity == "high":
                verdict = "block"
            elif verdict != "block":
                verdict = "degrade"
    return {"verdict": verdict, "labels": labels}


def redact_output(text: str) -> tuple:
    """输出脱敏。返回 (处理后文本, 命中标签列表)。"""
    labels = []
    out = text or ""
    for pattern, label in _REDACT_RULES:
        if pattern.search(out):
            out = pattern.sub("[REDACTED]", out)
            labels.append(label)
    return out, labels
