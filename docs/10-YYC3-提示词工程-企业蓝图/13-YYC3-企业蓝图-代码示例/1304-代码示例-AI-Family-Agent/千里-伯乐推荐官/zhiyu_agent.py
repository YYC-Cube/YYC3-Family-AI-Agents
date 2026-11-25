"""
千里·伯乐 (推荐官) Agent v2.1.0
YYC³ AI Family 推荐引擎 — 个性化推荐与用户画像

角色定位:
- 个性化推荐与匹配
- 用户画像构建
- 人才/资源/方案匹配
- 协同过滤与内容推荐

对齐蓝图: 1200-AI Family Agent v2.1.0
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3

用法:
    python zhiyu_agent.py --port 6004
"""

import os, json, uuid, time, logging
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../08-可观测性"))
try:
    from telemetry import Telemetry
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.zhiyu")
app = Flask(__name__)


class QianLiBoLeAgent:
    """千里·伯乐 — 推荐官 Agent"""
    
    MODEL_CONFIG = {
        "primary": "qwen-4.0",
        "fallback": ["glm-6", "deepseek-v3"],
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    
    def __init__(self, telemetry=None):
        self.agent_name = "千里·伯乐"
        self.role = "推荐官"
        self.version = "2.1.0"
        self.telemetry = telemetry
        self.state = {"status": "initializing", "recommendations_made": 0, "start_time": time.time()}
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    def recommend(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """智能推荐"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        recommend_type = request.get("type", "general")
        user_profile = request.get("user_profile", {})
        candidates = request.get("candidates", [])
        top_k = request.get("top_k", 5)
        
        # 评分计算
        scored = self._score_candidates(user_profile, candidates)
        
        # 多样性保障
        diverse = self._ensure_diversity(scored, top_k)
        
        # 解释生成
        explanations = self._generate_explanations(user_profile, diverse)
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "type": recommend_type,
            "recommendations": [
                {"rank": i + 1, "item": s["item"], "score": s["score"], "explanation": e}
                for i, (s, e) in enumerate(zip(diverse, explanations))
            ],
            "user_profile_summary": self._summarize_profile(user_profile),
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        
        self.state["recommendations_made"] += 1
        logger.info(f"[{self.agent_name}] 推荐完成 | type={recommend_type} | top_k={top_k} | correlationId={correlation_id}")
        return result
    
    def match(self, criteria: Dict[str, Any], candidates: List[Dict]) -> Dict[str, Any]:
        """智能匹配"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        matched = []
        for c in candidates:
            score = self._calculate_match_score(criteria, c)
            if score > 0.5:
                matched.append({"item": c, "score": round(score, 3), "match_details": self._match_details(criteria, c)})
        
        matched.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "total_candidates": len(candidates),
            "matched_count": len(matched),
            "matches": matched[:10],
            "execution_time": round((time.time() - start) * 1000, 2),
        }
    
    def build_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """用户画像构建"""
        correlation_id = str(uuid.uuid4())
        
        profile = {
            "demographic": self._extract_demographic(user_data),
            "behavioral": self._extract_behavioral(user_data),
            "preferences": self._extract_preferences(user_data),
            "interests": self._extract_interests(user_data),
            "skill_level": self._estimate_skill_level(user_data),
        }
        
        return {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "profile": profile,
            "profile_completeness": self._profile_completeness(profile),
        }
    
    def _score_candidates(self, user_profile: Dict, candidates: List[Dict]) -> List[Dict]:
        scored = []
        for c in candidates:
            score = 0.0
            # 兴趣匹配
            if "interests" in user_profile and "tags" in c:
                common = set(user_profile["interests"]) & set(c["tags"])
                score += len(common) / max(len(user_profile["interests"]), 1) * 0.4
            # 技能匹配
            if "skills" in user_profile and "requirements" in c:
                common = set(user_profile["skills"]) & set(c["requirements"])
                score += len(common) / max(len(c["requirements"]), 1) * 0.3
            # 新鲜度
            score += 0.15
            # 热门度
            score += c.get("popularity", 0.5) * 0.15
            scored.append({"item": c, "score": round(min(score, 1.0), 3)})
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
    
    def _ensure_diversity(self, scored: List[Dict], top_k: int) -> List[Dict]:
        selected = []
        seen_categories = set()
        
        for s in scored:
            if len(selected) >= top_k:
                break
            category = s["item"].get("category", "unknown")
            if category not in seen_categories or len(selected) < top_k // 2:
                selected.append(s)
                seen_categories.add(category)
        
        return selected
    
    def _generate_explanations(self, profile: Dict, items: List[Dict]) -> List[str]:
        explanations = []
        for s in items:
            item = s["item"]
            score = s["score"]
            if score > 0.8:
                explanations.append("高度匹配您的偏好和需求")
            elif score > 0.6:
                explanations.append(f"在{item.get('category', '相关')}领域与您匹配")
            else:
                explanations.append("基于协同过滤推荐")
        return explanations
    
    def _calculate_match_score(self, criteria: Dict, candidate: Dict) -> float:
        score = 0.0
        weights = criteria.get("weights", {})
        total_weight = sum(weights.values()) if weights else 1
        
        for field, weight in weights.items():
            if field in criteria and field in candidate:
                c_val = criteria[field]
                cand_val = candidate[field]
                if isinstance(c_val, (int, float)) and isinstance(cand_val, (int, float)):
                    score += (1 - abs(c_val - cand_val) / max(abs(c_val), 1)) * weight
        
        return score / total_weight if total_weight > 0 else 0.5
    
    def _match_details(self, criteria: Dict, candidate: Dict) -> Dict:
        details = {}
        for field in criteria:
            if field in candidate:
                details[field] = {"required": criteria[field], "actual": candidate[field]}
        return details
    
    def _summarize_profile(self, profile: Dict) -> str:
        parts = []
        if profile.get("role"):
            parts.append(f"角色: {profile['role']}")
        if profile.get("department"):
            parts.append(f"部门: {profile['department']}")
        return " | ".join(parts) if parts else "未知用户"
    
    def _extract_demographic(self, data: Dict) -> Dict:
        return {k: data.get(k) for k in ["age_group", "department", "role", "tenure"] if k in data}
    
    def _extract_behavioral(self, data: Dict) -> Dict:
        return data.get("behavior", {})
    
    def _extract_preferences(self, data: Dict) -> List[str]:
        return data.get("preferences", [])
    
    def _extract_interests(self, data: Dict) -> List[str]:
        return data.get("interests", [])
    
    def _estimate_skill_level(self, data: Dict) -> str:
        years = data.get("years_of_experience", 0)
        if years > 10: return "expert"
        if years > 5: return "advanced"
        if years > 2: return "intermediate"
        return "beginner"
    
    def _profile_completeness(self, profile: Dict) -> float:
        fields = [profile["demographic"], profile["behavioral"], profile["preferences"], profile["interests"]]
        filled = sum(1 for f in fields if f)
        return round(filled / len(fields) * 100, 1)


telemetry = Telemetry(service_name="yyc3-zhiyu") if Telemetry else None
agent = QianLiBoLeAgent(telemetry=telemetry)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"agent": agent.agent_name, "version": agent.version, "status": "healthy"})


@app.route("/recommend", methods=["POST"])
def recommend():
    return jsonify(agent.recommend(request.json))


@app.route("/match", methods=["POST"])
def match():
    return jsonify(agent.match(request.json.get("criteria", {}), request.json.get("candidates", [])))


@app.route("/profile", methods=["POST"])
def profile():
    return jsonify(agent.build_profile(request.json))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6004))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)