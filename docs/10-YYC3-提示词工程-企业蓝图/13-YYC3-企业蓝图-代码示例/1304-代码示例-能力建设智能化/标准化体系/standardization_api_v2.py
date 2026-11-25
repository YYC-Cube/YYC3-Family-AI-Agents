"""
YYC³ 标准化体系智能化 API 服务 v2.0
基于 Flask + AI Family Agent 协同架构

API端点:
- POST /api/v2/standardization/create-standard - 创建新标准
- POST /api/v2/standardization/compliance-audit - 合规审计
- GET  /api/v2/standardization/maturity-assessment - 成熟度评估
- GET  /api/v2/standardization/benchmarking - 行业对标
- GET  /api/v2/agents - Agent信息查询
"""

from flask import Flask, request, jsonify
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '00-核心基础设施', 'prompt-engine'))

try:
    from standardization_inference_v2 import StandardizationIntelligenceV2
    STANDARDIZATION_AVAILABLE = True
except ImportError:
    STANDARDIZATION_AVAILABLE = False

app = Flask(__name__)

if STANDARDIZATION_AVAILABLE:
    std_system = StandardizationIntelligenceV2()
else:
    std_system = None


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "YYC³ 标准化体系智能化 API V2.0",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "five_s_model": True,
            "ai_family_agents": 8,
            "compliance_frameworks": ["ISO9001", "ISO14001", "ISO45001"],
            "maturity_model": "五级成熟度模型"
        }
    })


@app.route('/api/v2/standardization/create-standard', methods=['POST'])
def create_standard():
    """
    创建新标准
    
    请求体:
    {
        "type": "管理标准|技术标准|工作标准|安全标准",
        "title": "标准名称",
        "department": "责任部门",
        "priority": "高|中|低"
    }
    """
    if not std_system:
        return jsonify({"success": False, "error": "系统初始化失败"}), 500

    try:
        data = request.get_json()
        
        result = std_system.create_standard(data)
        
        return jsonify({
            "success": True,
            "data": result,
            "message": f"标准创建成功: {result['process_metadata']['process_id']}"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "标准创建失败"
        }), 500


@app.route('/api/v2/standardization/compliance-audit', methods=['POST'])
def compliance_audit():
    """
    合规审计
    
    请求体:
    {
        "scope": "审计范围",
        "areas": ["质量管理", "安全管理", ...]
    }
    """
    if not std_system:
        return jsonify({"success": False, "error": "系统初始化失败"}), 500

    try:
        data = request.get_json()
        
        result = std_system.compliance_audit(data)
        
        return jsonify({
            "success": True,
            "data": result,
            "message": f"合规审计完成，总体得分: {result['overall_compliance_score']:.1f}"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "合规审计失败"
        }), 500


@app.route('/api/v2/standardization/maturity-assessment', methods=['GET'])
def maturity_assessment():
    """标准化成熟度评估"""
    if not std_system:
        return jsonify({"success": False, "error": "系统初始化失败"}), 500

    try:
        result = std_system.standard_maturity_assessment()
        
        return jsonify({
            "success": True,
            "data": result,
            "message": f"当前成熟度等级: {result['maturity_level']}级"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "成熟度评估失败"
        }), 500


@app.route('/api/v2/standardization/benchmarking', methods=['GET'])
def benchmarking():
    """行业对标分析"""
    if not std_system:
        return jsonify({"success": False, "error": "系统初始化失败"}), 500

    try:
        industry = request.args.get('industry', '通用')
        
        result = std_system.industry_benchmarking(industry)
        
        return jsonify({
            "success": True,
            "data": result,
            "message": f"行业对标完成: {result['competitive_position']}"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "行业对标失败"
        }), 500


@app.route('/api/v2/agents', methods=['GET'])
def get_agents_info():
    """获取Agent信息"""
    agents = [
        {"id": "yuanqi_tianshu", "name": "元启·天枢", "role": "总指挥", "capability": "标准体系战略规划"},
        {"id": "yanqi_qianhang", "name": "言启·千行", "role": "导航员", "capability": "标准检索导航"},
        {"id": "yushu_wanwu", "name": "语枢·万物", "role": "思考者", "capability": "内容分析推理"},
        {"id": "yujian_xianzhi", "name": "预见·先知", "role": "预言家", "capability": "风险预测预警"},
        {"id": "qianli_bole", "name": "千里·伯乐", "role": "推荐官", "capability": "最佳实践推荐"},
        {"id": "zhiyun_shouhu", "name": "智云·守护", "role": "安全官", "capability": "合规安全审计"},
        {"id": "gewu_zongshi", "name": "格物·宗师", "role": "质量官", "capability": "质量审核控制"},
        {"id": "chuangxiang_lingyun", "name": "创想·灵韵", "role": "创意官", "capability": "文档生成优化"}
    ]

    return jsonify({
        "total_agents": len(agents),
        "agents": agents,
        "coordination_mode": "ReAct-C (Reasoning + Acting + Critiquing)",
        "scenario": "标准化体系智能化"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🏢 YYC³ 标准化体系智能化 API 服务 V2.0")
    print("=" * 60)
    print("启动服务...")
    print("访问地址: http://localhost:5030")
    print("API文档: http://localhost:5030/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5030, debug=True)
