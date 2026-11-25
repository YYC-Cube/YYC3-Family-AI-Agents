import os
import json
import torch
from transformers import AutoModel, AutoTokenizer

class HRInferenceEngine:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.load_model(model_path)

    def load_model(self, model_path: str):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModel.from_pretrained(model_path).to(self.device)
            print(f"[HR AI] 模型加载成功: {model_path}")
        except Exception as e:
            print(f"[HR AI] 模型加载失败: {e}")

    def resume_screening(self, resume_text: str, job_description: str) -> dict:
        """智能简历筛选"""
        if not self.model:
            return {"error": "模型未加载"}

        inputs = self.tokenizer(
            f"简历: {resume_text}\n岗位要求: {job_description}",
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            similarity_score = torch.cosine_similarity(
                outputs.last_hidden_state.mean(dim=1),
                outputs.last_hidden_state.mean(dim=1)
            ).item()

        return {
            "task": "简历筛选",
            "match_score": round(similarity_score * 100, 2),
            "recommendation": "推荐面试" if similarity_score > 0.7 else "待定",
            "confidence": "高" if similarity_score > 0.8 else ("中" if similarity_score > 0.6 else "低")
        }

    def job_matching(self, candidate_profile: dict, job_requirements: dict) -> dict:
        """岗位匹配"""
        match_details = []
        total_score = 0

        for skill in job_requirements.get("required_skills", []):
            candidate_skills = candidate_profile.get("skills", [])
            if skill in candidate_skills:
                match_details.append({"skill": skill, "matched": True})
                total_score += 20
            else:
                match_details.append({"skill": skill, "matched": False})

        experience_match = min(
            candidate_profile.get("years_experience", 0) / job_requirements.get("min_experience", 1),
            1.0
        ) * 30
        total_score += experience_match

        return {
            "task": "岗位匹配",
            "candidate_id": candidate_profile.get("id"),
            "job_id": job_requirements.get("id"),
            "total_score": round(min(total_score, 100), 2),
            "match_details": match_details,
            "recommendation": "强烈推荐" if total_score >= 80 else ("推荐" if total_score >= 60 else "不推荐")
        }

    def interview_recommendation(self, candidates: list) -> list:
        """面试推荐"""
        ranked_candidates = sorted(
            candidates,
            key=lambda x: x.get("overall_score", 0),
            reverse=True
        )

        recommendations = []
        for idx, candidate in enumerate(ranked_candidates[:5], 1):
            recommendations.append({
                "rank": idx,
                "candidate_id": candidate.get("id"),
                "name": candidate.get("name"),
                "score": candidate.get("overall_score"),
                "priority": "高" if idx <= 2 else ("中" if idx <= 4 else "低")
            })

        return {"task": "面试推荐", "recommended_candidates": recommendations}

def model_inference(input_data: dict) -> dict:
    engine = HRInferenceEngine(os.environ.get("MODEL_PATH", "/workspace/models/hr_model.pt"))

    task_type = input_data.get("task")

    if task_type == "resume_screening":
        return engine.resume_screening(
            input_data.get("resume_text", ""),
            input_data.get("job_description", "")
        )
    elif task_type == "job_matching":
        return engine.job_matching(
            input_data.get("candidate_profile", {}),
            input_data.get("job_requirements", {})
        )
    elif task_type == "interview_recommendation":
        return engine.interview_recommendation(input_data.get("candidates", []))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[HR AI] 启动人力资源智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
