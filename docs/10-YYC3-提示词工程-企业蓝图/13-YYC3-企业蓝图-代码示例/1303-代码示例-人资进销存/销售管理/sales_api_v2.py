"""
YYC³ 销售管理智能化 API 服务 v2.0
基于 CO-STAR 提示词框架 + AI Family Agent 协同架构

接口列表:
1. GET /health - 健康检查
2. POST /api/v2/sales/trend - 销售趋势分析
3. POST /api/v2/sales/conversion - 客户转化预测
4. POST /api/v2/sales/forecast - 销售预测
5. POST /api/v2/agent/coordinate - Agent协同分析
6. GET /api/v2/history - 分析历史查询
7. GET /api/v2/metrics - 系统指标

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sales_inference_v2 import (
        SalesIntelligenceV2,
        SalesContext,
        CustomerProfile,
        model_inference,
    )
    SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] 核心模块加载失败: {e}")
    SYSTEM_AVAILABLE = False

app = Flask(__name__)
CORS(app)

global_system = None


def get_system():
    global global_system
    if global_system is None and SYSTEM_AVAILABLE:
        try:
            global_system = SalesIntelligenceV2()
            print("[API] 销售管理系统初始化成功")
        except Exception as e:
            print(f"[Error] 系统初始化失败: {e}")
    return global_system


@app.route("/health", methods=["GET"])
def health_check():
    system = get_system()
    return jsonify({
        "status": "healthy" if system else "degraded",
        "service": "sales_ai_v2",
        "version": "2.1.0",
        "framework": "CO-STAR + CRAFT",
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/v2/sales/trend", methods=["POST"])
def analyze_trend():
    """销售趋势分析"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        system = get_system()
        result = system.analyze_trend(
            historical_data=data.get("historical_data", []),
            correlation_id=correlation_id,
        )

        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "correlation_id": correlation_id,
                "model": "glm-6",
                "framework": "CO-STAR",
                "timestamp": datetime.now().isoformat(),
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v2/sales/conversion", methods=["POST"])
def predict_conversion():
    """客户转化预测"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        profile = CustomerProfile(
            customer_id=data.get("customer_id", ""),
            interactions=data.get("customer_data", {}).get("interactions", []),
            engagement_metrics=data.get("customer_data", {}).get("engagement_metrics", {}),
            purchase_history=data.get("customer_data", {}).get("purchase_history", []),
        )

        system = get_system()
        result = system.predict_conversion(profile, correlation_id)

        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "correlation_id": correlation_id,
                "model": "glm-6",
                "framework": "CO-STAR",
                "timestamp": datetime.now().isoformat(),
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v2/sales/forecast", methods=["POST"])
def forecast_sales():
    """销售预测"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        context = SalesContext(
            historical_data=data.get("historical_data", []),
            forecast_period=data.get("forecast_period", "Q1"),
            market_factors=data.get("market_factors", {}),
        )

        system = get_system()
        result = system.forecast_sales(context, correlation_id)

        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "correlation_id": correlation_id,
                "model": "glm-6",
                "framework": "CO-STAR",
                "timestamp": datetime.now().isoformat(),
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v2/agent/coordinate", methods=["POST"])
def coordinate_agents():
    """Agent协同分析"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        system = get_system()
        result = system.coordinate_agents(
            task_type=data.get("task_type", "sales_analysis"),
            context=data.get("context", {}),
            agents=data.get("agents", []),
            correlation_id=correlation_id,
        )

        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "correlation_id": correlation_id,
                "agents_coordinated": len(data.get("agents", [])),
                "coordination_protocol": "A2A",
                "timestamp": datetime.now().isoformat(),
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v2/history", methods=["GET"])
def get_history():
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        limit = request.args.get("limit", 20, type=int)
        system = get_system()
        history = system.get_decision_history(limit)
        return jsonify({"success": True, "data": history, "count": len(history)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v2/metrics", methods=["GET"])
def get_metrics():
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        system = get_system()
        metrics = system.get_metrics()
        return jsonify({"success": True, "data": metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 25203))
    print(f"[Sales API v2] 启动销售管理智能服务 | port={port} | framework=CO-STAR+CRAFT")
    app.run(host="0.0.0.0", port=port, debug=False)