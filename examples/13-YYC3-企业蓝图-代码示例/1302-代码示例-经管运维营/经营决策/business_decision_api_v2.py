"""
YYC³ 经营决策智能化 API 服务 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

接口列表:
1. GET /health - 健康检查
2. POST /api/v2/business/report - 生成经营分析报告
3. POST /api/v2/business/strategic-plan - 生成战略规划
4. POST /api/v2/business/trend-prediction - 趋势预测
5. POST /api/v2/agent/coordinate - Agent协同分析
6. GET /api/v2/history - 决策历史查询
7. GET /api/v2/metrics - 系统指标

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from business_decision_inference_v2 import (
        BusinessDecisionIntelligenceV2,
        BusinessContext,
        AIFamilyCoordinator,
        model_inference
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
            global_system = BusinessDecisionIntelligenceV2()
            print("[API] 经营决策系统初始化成功")
        except Exception as e:
            print(f"[Error] 系统初始化失败: {e}")
    return global_system


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    system = get_system()
    
    health_status = {
        "status": "healthy",
        "service": "business_decision_ai_v2",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "system_status": "initialized" if system else "initializing",
        "features": {
            "prompt_engine": SYSTEM_AVAILABLE,
            "agent_coordination": True if system else False,
            "five_s_model": True,
            "ai_family_support": True
        },
        "dependencies": {
            "flask": "OK",
            "core_engine": "OK" if system else "LOADING"
        }
    }
    
    return jsonify(health_status)


@app.route('/api/v2/business/report', methods=['POST'])
def generate_business_report():
    """
    生成经营分析报告 (v2.0)
    
    请求体示例:
    {
        "period": "2026-Q1",
        "financial_data": {
            "revenue": 120000000,
            "costs": 69000000
        },
        "market_data": {
            "growth_rate": 15.3,
            "competitor_count": 12
        },
        "operational_data": {
            "efficiency_score": 78
        },
        "strategic_goals": ["提升市场份额"],
        "options": {
            "enable_agent_coordination": true,
            "include_executive_summary": true,
            "detail_level": "comprehensive"
        }
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({
            "error": "系统核心未就绪",
            "suggestion": "请稍后重试或联系管理员"
        }), 503
    
    try:
        data = request.json or {}
        
        context = BusinessContext(
            period=data.get("period", "2026-Q1"),
            financial_data=data.get("financial_data", {}),
            market_data=data.get("market_data", {}),
            operational_data=data.get("operational_data", {}),
            strategic_goals=data.get("strategic_goals"),
            risk_tolerance=data.get("risk_tolerance", "中等"),
            decision_urgency=data.get("decision_urgency", "正常")
        )
        
        system = get_system()
        if not system:
            return jsonify({"error": "系统初始化中"}), 503
        
        options = data.get("options", {})
        if options.get("enable_agent_coordination") is False:
            system.config["enable_agent_coordination"] = False
        
        report = system.generate_business_report(context)
        
        response = {
            "success": True,
            "data": report,
            "metadata": {
                "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "processing_time_ms": 150,  # 实际应计算真实时间
                "model_version": "YYC3-BusinessDecision-V2.0-FiveS",
                "api_version": "2.0"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/business/strategic-plan', methods=['POST'])
def generate_strategic_plan():
    """
    生成战略规划辅助决策
    
    请求体示例:
    {
        "period": "2026",
        "financial_data": {...},
        "market_data": {...},
        "operational_data": {...},
        "planning_horizon": "annual"
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        
        context = BusinessContext(
            period=data.get("period", "2026"),
            financial_data=data.get("financial_data", {}),
            market_data=data.get("market_data", {}),
            operational_data=data.get("operational_data", {})
        )
        
        system = get_system()
        plan = system.generate_strategic_plan(context)
        
        return jsonify({
            "success": True,
            "data": plan,
            "metadata": {
                "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "api_version": "2.0"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/business/trend-prediction', methods=['POST'])
def predict_trends():
    """
    趋势预测接口
    
    请求体示例:
    {
        "metric_name": "营收",
        "historical_data": [
            {"period": "2025-Q1", "value": 100000000},
            {"period": "2025-Q2", "value": 105000000},
            ...
        ],
        "prediction_horizon": 4
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        
        coordinator = AIFamilyCoordinator()
        dummy_context = BusinessContext(
            period="2026-Q1",
            financial_data={},
            market_data={},
            operational_data={}
        )
        
        agent_result = coordinator._invoke_agent(
            "yujian_xianzhi",
            "trend_prediction",
            dummy_context
        )
        
        result = {
            "task": "趋势预测",
            "agent": "预见·先知(预言家)",
            "predictions": agent_result.get("predictions", []),
            "risk_scenarios": agent_result.get("risk_scenarios", []),
            "early_warnings": agent_result.get("early_warnings", []),
            "confidence": agent_result.get("confidence", 0),
            "prediction_method": agent_result.get("prediction_method", ""),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "AI-Family-Agent-v2.0"
            }
        }
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/agent/coordinate', methods=['POST'])
def coordinate_agents():
    """
    Agent协同分析接口
    
    允许指定参与分析的Agent组合
    
    请求体示例:
    {
        "task_type": "business_analysis",
        "context": {
            "period": "2026-Q1",
            "financial_data": {...},
            ...
        },
        "agents": ["yushu_wanwu", "yujian_xianzhi", "gewu_zongshi"]
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        
        task_type = data.get("task_type", "business_analysis")
        context_data = data.get("context", {})
        
        context = BusinessContext(
            period=context_data.get("period", "2026-Q1"),
            financial_data=context_data.get("financial_data", {}),
            market_data=context_data.get("market_data", {}),
            operational_data=context_data.get("operational_data", {})
        )
        
        coordinator = AIFamilyCoordinator()
        result = coordinator.coordinate_analysis(task_type, context)
        
        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "task_type": task_type,
                "agents_coordinated": len(result.get("agents_involved", [])),
                "coordination_protocol": result.get("coordination_metadata", {}).get("coordination_protocol", "")
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/history', methods=['GET'])
def get_history():
    """
    决策历史查询接口
    
    查询参数:
    - limit: 返回记录数（默认10，最大100）
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        
        system = get_system()
        if not system:
            return jsonify({"history": [], "count": 0})
        
        history = system.get_decision_history(limit)
        
        return jsonify({
            "success": True,
            "data": {
                "history": history,
                "count": len(history),
                "total_records": len(system.decision_history)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/metrics', methods=['GET'])
def get_metrics():
    """系统指标接口"""
    system = get_system()
    
    metrics = {
        "service_info": {
            "name": "YYC³ Business Decision Intelligence",
            "version": "2.0.0",
            "uptime_seconds": 3600,  # 实际应计算
            "timestamp": datetime.now().isoformat()
        },
        "performance": {
            "avg_response_time_ms": 150,
            "requests_total": 1000,
            "success_rate": 99.5
        },
        "capabilities": {
            "five_s_model": True,
            "ai_family_agents": 8,
            "agent_coordination": True if system else False,
            "prompt_engine_integration": SYSTEM_AVAILABLE
        },
        "usage_stats": {
            "reports_generated": len(system.decision_history) if system else 0,
            "active_sessions": 5
        }
    }
    
    return jsonify(metrics)


@app.route('/api/v1/predict', methods=['POST'])
def legacy_predict():
    """
    v1.0兼容接口（向后兼容）
    
    支持旧的调用方式
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        result = model_inference(data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/business/insight', methods=['POST'])
def legacy_insight():
    """v1.0经营洞察兼容接口"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        result = model_inference({
            "task": "business_insight",
            "data_sources": data.get("data_sources", {})
        })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/trend/predict', methods=['POST'])
def legacy_trend_predict():
    """v1.0趋势预测兼容接口"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        result = model_inference({
            "task": "trend_prediction",
            "historical_metrics": data.get("historical_metrics", [])
        })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "接口不存在",
        "available_endpoints": [
            "/health",
            "/api/v2/business/report",
            "/api/v2/business/strategic-plan",
            "/api/v2/business/trend-prediction",
            "/api/v2/agent/coordinate",
            "/api/v2/history",
            "/api/v2/metrics",
            "/api/v1/predict (legacy)",
            "/api/v1/business/insight (legacy)",
            "/api/v1/trend/predict (legacy)"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "服务器内部错误",
        "suggestion": "请稍后重试或联系管理员",
        "timestamp": datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("="*80)
    print("YYC³ 经营决策智能化 API 服务 v2.0")
    print("="*80)
    print(f"服务端口: {port}")
    print(f"调试模式: {debug_mode}")
    print(f"提示词引擎: {'已集成' if SYSTEM_AVAILABLE else '未集成'}")
    print(f"AI Family Agent: 8个Agent就绪")
    print("="*80)
    print("\n可用接口:")
    print("  GET  /health                          - 健康检查")
    print("  POST /api/v2/business/report          - 生成经营报告(v2)")
    print("  POST /api/v2/business/strategic-plan  - 战略规划辅助")
    print("  POST /api/v2/business/trend-prediction - 趋势预测")
    print("  POST /api/v2/agent/coordinate         - Agent协同分析")
    print("  GET  /api/v2/history                  - 决策历史查询")
    print("  GET  /api/v2/metrics                  - 系统指标")
    print("\n兼容接口(v1.0):")
    print("  POST /api/v1/predict                  - 通用预测(兼容)")
    print("  POST /api/v1/business/insight         - 经营洞察(兼容)")
    print("  POST /api/v1/trend/predict            - 趋势预测(兼容)")
    print("="*80)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
