from flask import Flask, request, jsonify
from sales_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "sales_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sales/trend', methods=['POST'])
def analyze_trend():
    """销售趋势分析接口"""
    data = request.json
    result = model_inference({
        "task": "sales_trend_analysis",
        "historical_data": data.get("historical_data", [])
    })
    return jsonify(result)

@app.route('/customer/conversion', methods=['POST'])
def predict_conversion():
    """客户转化预测接口"""
    data = request.json
    result = model_inference({
        "task": "customer_conversion_prediction",
        "customer_data": data.get("customer_data", {})
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
