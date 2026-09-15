"""
YYC³ 采购管理智能化 API 服务 v2.0
基于 CO-STAR 提示词框架 + AI Family Agent 协同架构

接口列表:
1. GET /health - 健康检查
2. POST /api/v2/purchase/supplier-evaluate - 供应商评估
3. POST /api/v2/purchase/procurement-recommend - 采购建议
4. POST /api/v2/purchase/cost-optimize - 成本优化分析
5. POST /api/v2/agent/coordinate - Agent协同分析
6. GET /api/v2/history - 采购历史查询
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
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from purchase_inference_v2 import (
        PurchaseIntelligenceV2,
        PurchaseContext,
        SupplierProfile,
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
    """获取系统实例（懒加载）"""
    global global_system
    if global_system is None and SYSTEM_AVAILABLE:
        try:
            global_system = PurchaseIntelligenceV2()
            print("[API] 采购管理系统初始化成功")
        except Exception as e:
            print(f"[Error] 系统初始化失败: {e}")
    return global_system


@app.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    system = get_system()
    return jsonify(
        {
            "status": "healthy" if system else "degraded",
            "service": "purchase_ai_v2",
            "version": "2.1.0",
            "framework": "CO-STAR + CRAFT",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/v2/purchase/supplier-evaluate", methods=["POST"])
def evaluate_supplier():
    """
    供应商评估接口

    请求体示例:
    {
        "supplier_id": "SUP-2026-001",
        "supplier_data": {
            "name": "XX供应商",
            "performance_history": {...},
            "financial_health": {...},
            "compliance_status": {...}
        },
        "correlation_id": "optional-trace-id"
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        supplier_data = data.get("supplier_data", {})
        profile = SupplierProfile(
            supplier_id=data.get("supplier_id", ""),
            name=supplier_data.get("name", ""),
            performance_history=supplier_data.get("performance_history", {}),
            financial_health=supplier_data.get("financial_health", {}),
            compliance_status=supplier_data.get("compliance_status", {}),
        )

        system = get_system()
        result = system.evaluate_supplier(profile, correlation_id)

        return jsonify(
            {
                "success": True,
                "data": result,
                "metadata": {
                    "correlation_id": correlation_id,
                    "model": "glm-6",
                    "framework": "CO-STAR",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/api/v2/purchase/procurement-recommend", methods=["POST"])
def recommend_procurement():
    """
    采购建议接口

    请求体示例:
    {
        "requirements": [...],
        "budget_constraint": 100000,
        "correlation_id": "optional-trace-id"
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        context = PurchaseContext(
            requirements=data.get("requirements", []),
            budget_constraint=data.get("budget_constraint", 0),
            timeline=data.get("timeline", ""),
            priority=data.get("priority", "normal"),
        )

        system = get_system()
        result = system.recommend_procurement(context, correlation_id)

        return jsonify(
            {
                "success": True,
                "data": result,
                "metadata": {
                    "correlation_id": correlation_id,
                    "model": "glm-6",
                    "framework": "CO-STAR",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/api/v2/purchase/cost-optimize", methods=["POST"])
def cost_optimize():
    """
    成本优化分析接口

    请求体示例:
    {
        "procurement_history": [...],
        "market_trends": {...},
        "correlation_id": "optional-trace-id"
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        system = get_system()
        result = system.cost_optimization(
            procurement_history=data.get("procurement_history", []),
            market_trends=data.get("market_trends", {}),
            correlation_id=correlation_id,
        )

        return jsonify(
            {
                "success": True,
                "data": result,
                "metadata": {
                    "correlation_id": correlation_id,
                    "model": "glm-6",
                    "framework": "CO-STAR",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/api/v2/agent/coordinate", methods=["POST"])
def coordinate_agents():
    """
    Agent协同分析接口

    请求体示例:
    {
        "task_type": "procurement_optimization",
        "context": {
            "supplier_data": {...},
            "requirements": [...]
        },
        "agents": ["gewu_zongshi", "yujian_xianzhi", "yushu_wanwu"]
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        data = request.json or {}
        correlation_id = data.get("correlation_id", str(uuid.uuid4()))

        system = get_system()
        result = system.coordinate_agents(
            task_type=data.get("task_type", "procurement_optimization"),
            context=data.get("context", {}),
            agents=data.get("agents", []),
            correlation_id=correlation_id,
        )

        return jsonify(
            {
                "success": True,
                "data": result,
                "metadata": {
                    "correlation_id": correlation_id,
                    "agents_coordinated": len(data.get("agents", [])),
                    "coordination_protocol": "A2A",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/api/v2/history", methods=["GET"])
def get_history():
    """采购历史查询接口"""
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
    """系统指标接口"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503

    try:
        system = get_system()
        metrics = system.get_metrics()
        return jsonify({"success": True, "data": metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 25202))
    print(f"[Purchase API v2] 启动采购管理智能服务 | port={port} | framework=CO-STAR+CRAFT")
    app.run(host="0.0.0.0", port=port, debug=False)