from flask import Flask, request, jsonify
from business_decision_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "business_decision_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/business/insight', methods=['POST'])
def generate_insight():
    """生成经营洞察接口"""
    data = request.json
    result = model_inference({
        "task": "business_insight",
        "data_sources": data.get("data_sources", {})
    })
    return jsonify(result)

@app.route('/trend/predict', methods=['POST'])
def predict_trend():
    """趋势预测接口"""
    data = request.json
    result = model_inference({
        "task": "trend_prediction",
        "historical_metrics": data.get("historical_metrics", [])
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=False)
