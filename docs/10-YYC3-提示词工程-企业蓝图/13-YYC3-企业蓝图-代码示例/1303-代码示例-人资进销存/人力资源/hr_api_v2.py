"""
YYC³ 人力资源智能化 API 服务 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

接口列表:
1. GET /health - 健康检查
2. POST /api/v2/hr/recruitment - 智能招聘
3. POST /api/v2/hr/performance - 绩效管理
4. POST /api/v2/hr/employee-care - 员工关怀
5. GET /api/v2/hr/candidates - 候选人查询
6. GET /api/v2/agents - Agent信息查询

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hr_inference_v2 import (
        HRIntelligenceV2,
        HRAIFamilyCoordinator,
        CandidateProfile,
        JobRequirement,
        EmployeeData,
        hr_model_inference
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
            global_system = HRIntelligenceV2()
            print("[HR API] 人力资源系统初始化成功")
        except Exception as e:
            print(f"[Error] 系统初始化失败: {e}")
    return global_system


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    system = get_system()
    
    return jsonify({
        "status": "healthy",
        "service": "hr_intelligence_v2",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "system_status": "initialized" if system else "initializing",
        "features": {
            "intelligent_recruitment": True,
            "performance_management": True,
            "employee_wellbeing": True,
            "ai_family_agents": 8,
            "five_s_model": True
        }
    })


@app.route('/api/v2/hr/recruitment', methods=['POST'])
def intelligent_recruitment():
    """
    智能招聘接口
    
    请求体示例:
    {
        "candidates": [
            {
                "id": "C001",
                "name": "张三",
                "skills": ["Python", "ML"],
                "years_experience": 6,
                "education": "硕士",
                "expected_salary": 35000,
                "resume_text": "...",
                "work_history": [...]
            }
        ],
        "job_requirement": {
            "id": "J001",
            "title": "高级AI工程师",
            "department": "技术研发部",
            "required_skills": ["Python", "Machine Learning"],
            "min_experience": 5,
            "salary_range": [30000, 50000],
            "job_description": "..."
        },
        "options": {
            "enable_agent_coordination": true
        }
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        
        candidates_data = data.get("candidates", [])
        candidates = [
            CandidateProfile(
                candidate_id=c.get("id", ""),
                name=c.get("name", ""),
                skills=c.get("skills", []),
                years_experience=c.get("years_experience", 0),
                education=c.get("education", ""),
                expected_salary=c.get("expected_salary", 0),
                resume_text=c.get("resume_text", ""),
                work_history=c.get("work_history", [])
            ) for c in candidates_data
        ]
        
        job_data = data.get("job_requirement", {})
        job_req = JobRequirement(
            job_id=job_data.get("id", ""),
            title=job_data.get("title", ""),
            department=job_data.get("department", ""),
            required_skills=job_data.get("required_skills", []),
            min_experience=job_data.get("min_experience", 0),
            salary_range=tuple(job_data.get("salary_range", (0, 0))),
            job_description=job_data.get("job_description", ""),
            responsibilities=job_data.get("responsibilities", [])
        )
        
        system = get_system()
        if not system:
            return jsonify({"error": "系统初始化中"}), 503
        
        result = system.intelligent_recruitment(candidates, job_req)
        
        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "candidates_processed": len(candidates),
                "job_title": job_req.title,
                "model_version": "YYC3-HR-V2.0-AIFamily"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/hr/performance', methods=['POST'])
def performance_review():
    """
    绩效评估接口
    
    请求体示例:
    {
        "employee_data": {
            "employee_id": "E001",
            "name": "王五",
            "department": "技术研发部",
            "position": "高级工程师",
            "join_date": "2022-03-15",
            "performance_scores": {
                "工作质量": 88,
                "团队合作": 85,
                "创新能力": 78
            },
            "training_records": [...],
            "satisfaction_score": 82
        }
    }
    """
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        emp_data = data.get("employee_data", {})
        
        employee = EmployeeData(
            employee_id=emp_data.get("employee_id", ""),
            name=emp_data.get("name", ""),
            department=emp_data.get("department", ""),
            position=emp_data.get("position", ""),
            join_date=emp_data.get("join_date", ""),
            performance_scores=emp_data.get("performance_scores", {}),
            training_records=emp_data.get("training_records", []),
            satisfaction_score=emp_data.get("satisfaction_score", 0),
            risk_factors=emp_data.get("risk_factors", [])
        )
        
        system = get_system()
        result = system.performance_management(employee)
        
        return jsonify({
            "success": True,
            "data": result,
            "metadata": {
                "request_id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "employee_name": employee.name,
                "api_version": "2.0"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/v2/hr/employee-care', methods=['POST'])
def employee_care():
    """员工关怀接口"""
    if not SYSTEM_AVAILABLE:
        return jsonify({"error": "系统核心未就绪"}), 503
    
    try:
        data = request.json or {}
        emp_data = data.get("employee_data", {})
        
        employee = EmployeeData(
            employee_id=emp_data.get("employee_id", ""),
            name=emp_data.get("name", ""),
            department=emp_data.get("department", ""),
            position=emp_data.get("position", ""),
            join_date=emp_data.get("join_date", ""),
            performance_scores=emp_data.get("performance_scores", {}),
            training_records=emp_data.get("training_records", []),
            satisfaction_score=emp_data.get("satisfaction_score", 0),
            risk_factors=emp_data.get("risk_factors", [])
        )
        
        system = get_system()
        result = system.employee_wellbeing(employee)
        
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


@app.route('/api/v2/agents', methods=['GET'])
def get_agents_info():
    """获取AI Family Agent信息"""
    coordinator = HRAIFamilyCoordinator()
    
    agents_info = []
    for agent_id, agent_info in coordinator.hr_agents.items():
        agents_info.append({
            "agent_id": agent_id,
            "name": agent_info["name"],
            "role": agent_info["role"],
            "hr_specialty": agent_info["hr_specialty"],
            "interaction_style": agent_info["interaction_style"]
        })
    
    return jsonify({
        "success": True,
        "data": {
            "total_agents": len(agents_info),
            "agents": agents_info,
            "coordination_protocol": "YYC3-HR-AIFamily-v2.0"
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5020))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("="*80)
    print("YYC³ 人力资源智能化 API 服务 v2.0")
    print("="*80)
    print(f"服务端口: {port}")
    print(f"调试模式: {debug_mode}")
    print(f"AI Family Agents: 8个Agent就绪")
    print("="*80)
    print("\n可用接口:")
    print("  GET  /health                    - 健康检查")
    print("  POST /api/v2/hr/recruitment     - 智能招聘")
    print("  POST /api/v2/hr/performance     - 绩效评估")
    print("  POST /api/v2/hr/employee-care   - 员工关怀")
    print("  GET  /api/v2/agents             - Agent信息")
    print("="*80)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
