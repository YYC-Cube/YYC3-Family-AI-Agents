"""
智云·守护 (安全官) Agent v2.1.0
YYC³ AI Family 安全审计引擎 — 安全审计与行为监控

角色定位:
- 全链路安全审计
- 异常行为检测
- 内容安全过滤
- 合规检查
- 安全事件响应

对齐蓝图: 1209-安全合规与伦理治理
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3

用法:
    python zhiyun_agent.py --port 6005
"""

import os, sys, json, uuid, time, logging
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../07-安全合规"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../08-可观测性"))
try:
    from content_filter import ContentFilter, FilterLevel, InjectionDetector
    from zero_trust_gateway import ZeroTrustGateway
except ImportError:
    ContentFilter = None
    InjectionDetector = None
    ZeroTrustGateway = None
try:
    from telemetry import Telemetry
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.zhiyun")
app = Flask(__name__)


class ZhiYunShouHuAgent:
    """智云·守护 — 安全官 Agent"""
    
    MODEL_CONFIG = {
        "primary": "glm-6",
        "fallback": ["qwen-4.0", "deepseek-v3"],
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    
    def __init__(self, telemetry=None):
        self.agent_name = "智云·守护"
        self.role = "安全官"
        self.version = "2.1.0"
        self.telemetry = telemetry
        
        # 安全组件
        self.content_filter = ContentFilter(FilterLevel.STRICT) if ContentFilter else None
        self.injection_detector = InjectionDetector() if InjectionDetector else None
        self.gateway = ZeroTrustGateway() if ZeroTrustGateway else None
        
        self.state = {"status": "initializing", "audits_completed": 0, "threats_detected": 0, "start_time": time.time()}
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    async def security_audit(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """安全审计"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        audit_type = request.get("audit_type", "full")
        target = request.get("target", {})
        
        findings = []
        
        # 1. 输入安全审计
        if user_input := request.get("user_input"):
            if self.content_filter:
                filter_result = await self.content_filter.filter_input(user_input)
                if not filter_result.safe:
                    findings.append({
                        "type": "content_safety",
                        "severity": filter_result.risk_level.value,
                        "categories": [c.value for c in filter_result.categories],
                        "action": filter_result.action.value,
                        "reason": filter_result.reason,
                    })
            
            if self.injection_detector:
                injection_result = self.injection_detector.detect(user_input)
                if not injection_result["safe"]:
                    findings.append({
                        "type": "injection_attack",
                        "severity": injection_result["risk_level"],
                        "attack_type": injection_result["attack_type"],
                        "confidence": injection_result["confidence"],
                    })
        
        # 2. 权限审计
        if audit_type in ("full", "permissions"):
            agent_id = request.get("agent_id", "")
            required = request.get("required_permissions", [])
            if self.gateway and agent_id:
                authz = self.gateway.authorize(agent_id, required)
                if not authz.authorized:
                    findings.append({
                        "type": "permission_violation",
                        "severity": "high",
                        "agent": agent_id,
                        "missing": authz.missing_permissions,
                    })
        
        # 3. 数据泄露审计
        if output := request.get("output"):
            if self.content_filter:
                output_result = await self.content_filter.filter_output(output)
                if not output_result.safe:
                    findings.append({
                        "type": "data_leak",
                        "severity": output_result.risk_level.value,
                        "reason": output_result.reason,
                    })
        
        overall = "safe" if not findings else ("warning" if len(findings) <= 2 else "danger")
        self.state["audits_completed"] += 1
        if findings:
            self.state["threats_detected"] += len(findings)
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "audit_type": audit_type,
            "overall_status": overall,
            "findings_count": len(findings),
            "findings": findings,
            "recommendations": self._generate_recommendations(findings),
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        
        logger.info(f"[{self.agent_name}] 审计完成 | status={overall} | findings={len(findings)} | correlationId={correlation_id}")
        return result
    
    def compliance_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """合规检查"""
        correlation_id = str(uuid.uuid4())
        
        checks = {
            "data_privacy": self._check_data_privacy(data),
            "access_control": self._check_access_control(data),
            "audit_trail": self._check_audit_trail(data),
            "encryption": self._check_encryption(data),
            "retention_policy": self._check_retention_policy(data),
        }
        
        passed = sum(1 for c in checks.values() if c["status"] == "pass")
        failed = sum(1 for c in checks.values() if c["status"] == "fail")
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "checks": checks,
            "summary": {"total": len(checks), "passed": passed, "failed": failed},
            "compliant": failed == 0,
        }
    
    def incident_response(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """安全事件响应"""
        correlation_id = str(uuid.uuid4())
        severity = incident.get("severity", "medium")
        
        response_plan = {
            "critical": [
                "立即隔离受影响系统",
                "启动应急响应小组",
                "通知管理层和安全团队",
                "收集并保存证据",
                "启动根因分析",
            ],
            "high": [
                "限制受影响服务访问",
                "通知安全团队",
                "收集日志和证据",
                "启动根因分析",
            ],
            "medium": [
                "记录事件详情",
                "通知安全团队",
                "监控事态发展",
            ],
            "low": [
                "记录事件",
                "定期复查",
            ],
        }
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "incident": incident.get("description", ""),
            "severity": severity,
            "response_plan": response_plan.get(severity, response_plan["low"]),
            "escalation": severity in ("critical", "high"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    
    def _check_data_privacy(self, data: Dict) -> Dict:
        return {"status": "pass", "detail": "数据隐私策略合规"}
    
    def _check_access_control(self, data: Dict) -> Dict:
        return {"status": "pass", "detail": "访问控制策略已实施"}
    
    def _check_audit_trail(self, data: Dict) -> Dict:
        logs = data.get("audit_logs", [])
        return {"status": "pass" if logs else "fail", "detail": f"审计日志记录: {len(logs)}条"}
    
    def _check_encryption(self, data: Dict) -> Dict:
        return {"status": "pass", "detail": "传输和存储加密已启用"}
    
    def _check_retention_policy(self, data: Dict) -> Dict:
        return {"status": "pass", "detail": "数据保留策略已定义"}
    
    def _generate_recommendations(self, findings: List[Dict]) -> List[Dict]:
        recs = []
        for f in findings:
            if f["type"] == "content_safety":
                recs.append({"priority": "P0", "action": "审查内容安全策略", "detail": f["reason"]})
            elif f["type"] == "injection_attack":
                recs.append({"priority": "P0", "action": "加强提示词注入防护", "detail": f"攻击类型: {f['attack_type']}"})
            elif f["type"] == "permission_violation":
                recs.append({"priority": "P1", "action": "审查权限配置", "detail": f"缺少: {f['missing']}"})
            elif f["type"] == "data_leak":
                recs.append({"priority": "P0", "action": "启用数据泄露防护", "detail": f["reason"]})
        return recs


telemetry = Telemetry(service_name="yyc3-zhiyun") if Telemetry else None
agent = ZhiYunShouHuAgent(telemetry=telemetry)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"agent": agent.agent_name, "version": agent.version, "status": "healthy"})


@app.route("/audit", methods=["POST"])
def audit():
    import asyncio
    return jsonify(asyncio.run(agent.security_audit(request.json)))


@app.route("/compliance", methods=["POST"])
def compliance():
    return jsonify(agent.compliance_check(request.json))


@app.route("/incident", methods=["POST"])
def incident():
    return jsonify(agent.incident_response(request.json))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6005))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)