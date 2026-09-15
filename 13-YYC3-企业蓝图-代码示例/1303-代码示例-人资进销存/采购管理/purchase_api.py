from flask import Flask, request, jsonify
from purchase_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "purchase_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/supplier/evaluate', methods=['POST'])
def evaluate_supplier():
    """供应商评估接口"""
    data = request.json
    result = model_inference({
        "task": "supplier_evaluation",
        "supplier_data": data.get("supplier_data", {})
    })
    return jsonify(result)

@app.route('/procurement/recommend', methods=['POST'])
def recommend_procurement():
    """采购建议接口"""
    data = request.json
    result = model_inference({
        "task": "procurement_recommendation",
        "requirements": data.get("requirements", [])
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
