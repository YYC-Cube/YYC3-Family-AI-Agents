from flask import Flask, request, jsonify
from hr_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "hr_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "请提供JSON数据"}), 400

        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/resume/screen', methods=['POST'])
def screen_resume():
    """简历筛选接口"""
    data = request.json
    result = model_inference({
        "task": "resume_screening",
        "resume_text": data.get("resume_text", ""),
        "job_description": data.get("job_description", "")
    })
    return jsonify(result)

@app.route('/job/match', methods=['POST'])
def match_job():
    """岗位匹配接口"""
    data = request.json
    result = model_inference({
        "task": "job_matching",
        "candidate_profile": data.get("candidate_profile", {}),
        "job_requirements": data.get("job_requirements", {})
    })
    return jsonify(result)

@app.route('/interview/recommend', methods=['POST'])
def recommend_interview():
    """面试推荐接口"""
    data = request.json
    result = model_inference({
        "task": "interview_recommendation",
        "candidates": data.get("candidates", [])
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
