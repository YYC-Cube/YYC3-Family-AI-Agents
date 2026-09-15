from flask import Flask, request, jsonify
from inventory_inference import model_inference
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "inventory_ai"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        result = model_inference(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/predict', methods=['POST'])
def predict_inventory():
    """库存预测接口"""
    data = request.json
    result = model_inference({
        "task": "inventory_prediction",
        "inventory_data": data.get("inventory_data", {})
    })
    return jsonify(result)

@app.route('/inventory/replenish', methods=['POST'])
def recommend_replenishment():
    """自动补货建议接口"""
    data = request.json
    result = model_inference({
        "task": "auto_replenishment",
        "inventory_list": data.get("inventory_list", [])
    })
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=False)
