from flask import Flask, request, jsonify
from asset_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "asset_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/asset/track', methods=['POST'])
def track_asset():
    """资产跟踪接口"""
    data = request.json
    result = model_inference({
        "task": "asset_tracking",
        "asset_info": data.get("asset_info", {})
    })
    return jsonify(result)

@app.route('/asset/utilization', methods=['POST'])
def analyze_utilization():
    """资产利用率分析接口"""
    data = request.json
    result = model_inference({
        "task": "utilization_analysis",
        "assets": data.get("assets", [])
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
