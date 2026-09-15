"""
格物·宗师 (质量官) Agent v2.1.0
YYC³ AI Family 质量保障引擎 — 代码审查与质量保障

角色定位:
- 自动化代码审查
- 质量度量与评估
- 测试覆盖率分析
- 最佳实践推广
- 输出质量审核

对齐蓝图: 1200-AI Family Agent v2.1.0
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3

用法:
    python gewu_agent.py --port 6006
"""

import os, json, uuid, time, logging, re
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../08-可观测性"))
try:
    from telemetry import Telemetry
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.gewu")
app = Flask(__name__)


class GeWuZongShiAgent:
    """格物·宗师 — 质量官 Agent"""
    
    MODEL_CONFIG = {
        "primary": "deepseek-v3",
        "fallback": ["glm-6", "qwen-4.0"],
        "temperature": 0.1,
        "max_tokens": 8192,
    }
    
    QUALITY_METRICS = {
        "code_quality": ["complexity", "duplication", "maintainability", "readability"],
        "test_coverage": ["line_coverage", "branch_coverage", "function_coverage"],
        "performance": ["response_time", "memory_usage", "cpu_usage"],
        "security": ["vulnerability_count", "dependency_risks", "owasp_score"],
        "reliability": ["error_rate", "mtbf", "mttr"],
    }
    
    def __init__(self, telemetry=None):
        self.agent_name = "格物·宗师"
        self.role = "质量官"
        self.version = "2.1.0"
        self.telemetry = telemetry
        self.state = {"status": "initializing", "reviews_completed": 0, "start_time": time.time()}
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    def code_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """代码审查"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        code = review_data.get("code", "")
        language = review_data.get("language", "python")
        review_focus = review_data.get("focus", ["best_practices", "security", "performance"])
        
        issues = []
        
        # 1. 代码复杂度检查
        complexity_issues = self._check_complexity(code, language)
        issues.extend(complexity_issues)
        
        # 2. 安全漏洞检查
        if "security" in review_focus:
            security_issues = self._check_security(code, language)
            issues.extend(security_issues)
        
        # 3. 性能检查
        if "performance" in review_focus:
            performance_issues = self._check_performance(code, language)
            issues.extend(performance_issues)
        
        # 4. 最佳实践检查
        if "best_practices" in review_focus:
            practice_issues = self._check_best_practices(code, language)
            issues.extend(practice_issues)
        
        # 5. 代码风格检查
        style_issues = self._check_code_style(code, language)
        issues.extend(style_issues)
        
        # 质量评分
        total_issues = len(issues)
        critical = sum(1 for i in issues if i["severity"] == "critical")
        high = sum(1 for i in issues if i["severity"] == "high")
        medium = sum(1 for i in issues if i["severity"] == "medium")
        low = sum(1 for i in issues if i["severity"] == "low")
        
        quality_score = max(0, 100 - critical * 10 - high * 5 - medium * 2 - low * 0.5)
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "language": language,
            "lines_of_code": len(code.split("\n")),
            "quality_score": round(quality_score, 1),
            "grade": self._quality_grade(quality_score),
            "issues": {"total": total_issues, "critical": critical, "high": high, "medium": medium, "low": low},
            "findings": issues,
            "suggestions": self._generate_suggestions(issues),
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        
        self.state["reviews_completed"] += 1
        logger.info(f"[{self.agent_name}] 审查完成 | score={quality_score} | issues={total_issues} | correlationId={correlation_id}")
        return result
    
    def quality_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """质量评估"""
        correlation_id = str(uuid.uuid4())
        
        metrics = {}
        overall = 0
        
        for category, sub_metrics in self.QUALITY_METRICS.items():
            category_score = data.get(category, {})
            scores = []
            for m in sub_metrics:
                if m in category_score:
                    scores.append(category_score[m])
            metrics[category] = {
                "score": round(sum(scores) / len(scores), 1) if scores else 0,
                "details": category_score,
            }
            if metrics[category]["score"] > 0:
                overall += metrics[category]["score"]
        
        overall_score = round(overall / len([m for m in metrics.values() if m["score"] > 0]), 1) if any(m["score"] > 0 for m in metrics.values()) else 0
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "overall_score": overall_score,
            "grade": self._quality_grade(overall_score),
            "metrics": metrics,
            "improvement_areas": [c for c, m in metrics.items() if m["score"] < 70],
        }
    
    def output_review(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """输出质量审核"""
        correlation_id = str(uuid.uuid4())
        content = output.get("content", "")
        
        issues = []
        
        # 完整性检查
        if not content or len(content) < 10:
            issues.append({"severity": "high", "type": "completeness", "message": "输出内容过短或不完整"})
        
        # 结构化检查
        if not self._is_structured(content):
            issues.append({"severity": "medium", "type": "structure", "message": "输出缺少结构化格式"})
        
        # 准确性检查
        accuracy_issues = self._check_accuracy(content)
        issues.extend(accuracy_issues)
        
        quality_score = max(0, 100 - len(issues) * 10)
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "quality_score": quality_score,
            "grade": self._quality_grade(quality_score),
            "issues": issues,
            "approved": quality_score >= 70,
        }
    
    def _check_complexity(self, code: str, language: str) -> List[Dict]:
        issues = []
        lines = code.split("\n")
        
        # 函数长度检查
        current_function_lines = 0
        in_function = False
        for line in lines:
            if re.match(r"^\s*(def |function |func |async def )", line):
                if current_function_lines > 50:
                    issues.append({"severity": "medium", "type": "complexity", "message": f"函数过长({current_function_lines}行)", "line": line})
                in_function = True
                current_function_lines = 0
            if in_function:
                current_function_lines += 1
        
        # 嵌套深度检查
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        if max_indent > 16:
            issues.append({"severity": "medium", "type": "complexity", "message": f"嵌套深度过大({max_indent}空格)"})
        
        return issues
    
    def _check_security(self, code: str, language: str) -> List[Dict]:
        issues = []
        
        security_patterns = {
            "hardcoded_secret": (r"(password|secret|token|api_key)\s*=\s*[\"'][^\"']+[\"']", "high", "硬编码密钥"),
            "sql_injection": (r"f[\"'].*SELECT.*\".*format", "critical", "潜在SQL注入"),
            "command_injection": (r"os\.system\(|subprocess\.call\(.*\+", "critical", "潜在命令注入"),
            "eval_usage": (r"\beval\(|\bexec\(", "critical", "使用eval/exec"),
            "insecure_deserialization": (r"pickle\.loads|yaml\.load\(", "high", "不安全反序列化"),
            "open_redirect": (r"redirect\(.*request\.", "medium", "潜在开放重定向"),
        }
        
        for name, (pattern, severity, message) in security_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({"severity": severity, "type": "security", "message": message, "rule": name})
        
        return issues
    
    def _check_performance(self, code: str, language: str) -> List[Dict]:
        issues = []
        
        perf_patterns = [
            (r"for\s+\w+\s+in\s+(?!range|enumerate)", "medium", "避免逐元素循环"),
            (r"\.append\(.*\)\s*in\s*for", "low", "考虑使用列表推导式"),
            (r"\+.*\+\s*in\s*for.*str", "medium", "字符串拼接建议使用join"),
            (r"open\(.*\).*\.read\(\)", "low", "大文件建议逐行读取"),
        ]
        
        for pattern, severity, message in perf_patterns:
            if re.search(pattern, code):
                issues.append({"severity": severity, "type": "performance", "message": message})
        
        return issues
    
    def _check_best_practices(self, code: str, language: str) -> List[Dict]:
        issues = []
        
        best_practice_patterns = [
            (r"except\s*:", "medium", "避免裸except，指定异常类型"),
            (r"class\s+\w+:\s*\n\s*pass", "low", "空类建议添加docstring"),
            (r"import\s+\*", "medium", "避免使用 import *"),
            (r"global\s+\w+", "medium", "谨慎使用global变量"),
            (r"return\s+None", "low", "return None可省略"),
        ]
        
        for pattern, severity, message in best_practice_patterns:
            if re.search(pattern, code):
                issues.append({"severity": severity, "type": "best_practice", "message": message})
        
        return issues
    
    def _check_code_style(self, code: str, language: str) -> List[Dict]:
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({"severity": "low", "type": "style", "message": f"行{i+1}超过120字符", "line": i + 1})
            if line.rstrip() != line:
                issues.append({"severity": "low", "type": "style", "message": f"行{i+1}末尾有空格", "line": i + 1})
        
        return issues
    
    def _check_accuracy(self, content: str) -> List[Dict]:
        issues = []
        if "todo" in content.lower() or "fixme" in content.lower():
            issues.append({"severity": "low", "type": "accuracy", "message": "内容包含待办标记"})
        return issues
    
    def _is_structured(self, content: str) -> bool:
        return bool(re.search(r"[\[\{].*[\}\]]", content)) or "```" in content
    
    def _quality_grade(self, score: float) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B+"
        if score >= 60: return "B"
        if score >= 50: return "C"
        return "D"
    
    def _generate_suggestions(self, issues: List[Dict]) -> List[Dict]:
        suggestions = []
        type_map = {
            "complexity": "重构代码，降低复杂度。考虑拆分长函数，减少嵌套层级。",
            "security": "修复安全漏洞。使用参数化查询，避免硬编码密钥，使用安全库。",
            "performance": "优化性能。使用高效数据结构，避免不必要的循环和内存分配。",
            "best_practice": "遵循最佳实践。参考语言风格指南，提高代码可维护性。",
            "style": "统一代码风格。使用代码格式化工具，保持一致的缩进和命名。",
        }
        for issue_type in set(i["type"] for i in issues):
            if issue_type in type_map:
                suggestions.append({"type": issue_type, "suggestion": type_map[issue_type]})
        return suggestions


telemetry = Telemetry(service_name="yyc3-gewu") if Telemetry else None
agent = GeWuZongShiAgent(telemetry=telemetry)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"agent": agent.agent_name, "version": agent.version, "status": "healthy"})


@app.route("/review", methods=["POST"])
def review():
    return jsonify(agent.code_review(request.json))


@app.route("/quality", methods=["POST"])
def quality():
    return jsonify(agent.quality_assessment(request.json))


@app.route("/output-review", methods=["POST"])
def output_review():
    return jsonify(agent.output_review(request.json))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6006))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)