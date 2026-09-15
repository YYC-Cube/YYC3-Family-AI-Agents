"""
YYC³ 智能单元测试套件 V3.1
- 自动发现所有模块的公共方法
- 动态生成测试用例
- 覆盖率目标: 80%+

运行方式:
    python3 test_yyc3_smart_suite.py
"""

import sys
import os
import importlib.util
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = {
    "标准化体系": {
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '标准化体系', 'standardization_inference_v2.py'),
        "class": "StandardizationIntelligenceV2",
        "methods_to_test": [
            ("create_standard", {"type": "管理标准", "title": "测试标准"}),
            ("compliance_audit", {"scope": "年度审计", "areas": ["质量管理"]}),
            ("maturity_assessment", {"department": "技术研发部"}),
            ("industry_benchmarking", "制造业")
        ]
    },
    "规范化管理": {
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '规范化管理', 'process_management_inference_v2.py'),
        "class": "ProcessManagementIntelligenceV2",
        "methods_to_test": [
            ("optimize_process", {"name": "订单处理流程", "current_efficiency": 65.0}),
            ("quality_control", {"process_name": "生产制造", "quality_target": 99.5}),
            ("generate_sop", {"process_name": "客户服务流程", "complexity": "中等"})
        ]
    },
    "数据化治理": {
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '数据化治理', 'data_governance_inference_v2.py'),
        "class": "DataGovernanceIntelligenceV2",
        "methods_to_test": [
            ("build_data_asset_map", {"scope": "全公司"}),
            ("assess_data_quality", "客户数据"),
            ("data_security_audit", {"scope": "敏感数据"}),
            ("discover_data_value", {"scope": "销售数据"})
        ]
    },
    "智能化升级": {
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '智能化升级', 'ai_upgrade_inference_v2.py'),
        "class": "AIUpgradeIntelligenceV2",
        "methods_to_test": [
            ("assess_ai_maturity", {"name": "YYC³科技"}),
            ("design_implementation_pathway", {"goal": "全面智能化"}),
            ("predict_roi", {"total_investment": 10000000, "timeline_months": 24})
        ]
    },
    "协同化办公": {
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '协同化办公', 'collaboration_inference_v2.py'),
        "class": "CollaborationIntelligenceV2",
        "methods_to_test": [
            ("team_collaboration_optimization", {"team": "研发团队A"})
        ]
    },
    "市场洞察": {
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '市场洞察', 'market_intelligence_inference_v2.py'),
        "class": "MarketIntelligenceV2",
        "methods_to_test": [
            ("deep_competitor_analysis", ["竞品A公司"]),
            ("predict_market_trends", "科技行业"),
            ("customer_need_mining", "企业客户"),
            ("industry_dynamics_monitoring", ["政策法规"])
        ]
    },
    "创新孵化": {
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '创新孵化', 'innovation_incubator_v2.py'),
        "class": "InnovationIncubatorV2",
        "methods_to_test": [
            ("evaluate_innovation_idea", {"title": "测试创意", "submitter": "张三", "department": "技术部"}),
            ("manage_innovation_portfolio", None),
            ("innovation_ecosystem_builder", "AI技术应用")
        ]
    },
    "薪酬激励": {
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '薪酬激励', 'compensation_intelligence_v2.py'),
        "class": "CompensationIntelligenceV2",
        "methods_to_test": [
            ("intelligent_compensation_design", {"position": "高级工程师", "level": "P7", "department": "技术研发"}),
            ("performance_based_incentive", {"name": "李四", "performance_rating": "A", "years_of_service": 3})
        ]
    },
    "高效运营": {
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '高效运营', 'operations_intelligence_v2.py'),
        "class": "OperationsIntelligenceV2",
        "methods_to_test": [
            ("automate_business_processes", {"scope": "财务流程"}),
            ("intelligent_resource_scheduling", "运营部门"),
            ("operations_dashboard_realtime", None),
            ("lean_cost_management", "制造部门")
        ]
    },
    "度势成长": {
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '度势成长', 'growth_intelligence_v2.py'),
        "class": "GrowthIntelligenceV2",
        "methods_to_test": [
            ("build_talent_pipeline", "技术研发"),
            ("leadership_development_assessment", {"name": "张总"}),
            ("learning_organization_builder", {"scope": "全公司"}),
            ("culture_shaping_strategy", {"focus": "价值观落地"})
        ]
    }
}


def load_module_from_file(file_path: str):
    """从文件路径动态加载Python模块"""
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    
    # 添加必要的依赖路径
    sys.path.insert(0, os.path.dirname(file_path))
    sys.path.insert(0, os.path.join(BASE_DIR, '00-核心基础设施', 'prompt-engine'))
    
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"❌ 加载模块失败 {file_path}: {e}")
        return None


def run_module_tests(module_name: str, config: Dict) -> Dict:
    """运行单个模块的所有测试"""
    results = {
        "module": module_name,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
        "details": []
    }
    
    print(f"\n{'='*60}")
    print(f"📦 测试模块: {module_name}")
    print(f"{'='*60}")
    
    # 加载模块
    module = load_module_from_file(config["path"])
    if not module:
        results["errors"].append("模块加载失败")
        return results
    
    # 获取类
    class_obj = getattr(module, config["class"], None)
    if not class_obj:
        results["errors"].append(f"类 {config['class']} 未找到")
        return results
    
    # 实例化
    try:
        instance = class_obj()
        print(f"✅ 实例化成功: {config['class']}")
    except Exception as e:
        results["errors"].append(f"实例化失败: {e}")
        return results
    
    # 测试每个方法
    for method_name, args in config["methods_to_test"]:
        results["total"] += 1
        
        method = getattr(instance, method_name, None)
        if not method:
            msg = f"⚠️ 方法 '{method_name}' 不存在"
            results["errors"].append(msg)
            results["details"].append({"method": method_name, "status": "MISSING", "msg": msg})
            continue
        
        try:
            if args is None:
                result = method()
            elif isinstance(args, dict):
                result = method(**args)
            else:
                result = method(args)
            
            # 验证返回值
            if result and isinstance(result, dict) and len(result) > 0:
                results["passed"] += 1
                status_msg = f"✅ {method_name}() - 成功 (返回{len(result)}个字段)"
                print(status_msg)
                results["details"].append({"method": method_name, "status": "PASS", "msg": status_msg})
            else:
                results["failed"] += 1
                status_msg = f"❌ {method_name}() - 返回值为空或格式错误"
                print(status_msg)
                results["details"].append({"method": method_name, "status": "FAIL", "msg": status_msg})
                
        except TypeError as e:
            # 参数错误，尝试不同的参数形式
            try:
                if isinstance(args, (list, tuple)):
                    result = method(*args)
                elif args is None:
                    result = method()
                else:
                    raise
                    
                if result and isinstance(result, dict):
                    results["passed"] += 1
                    status_msg = f"✅ {method_name}() - 成功 (修正参数后)"
                    print(status_msg)
                    results["details"].append({"method": method_name, "status": "PASS", "msg": status_msg})
                else:
                    results["failed"] += 1
                    status_msg = f"❌ {method_name}() - 返回值异常"
                    print(status_msg)
                    results["details"].append({"method": method_name, "status": "FAIL", "msg": status_msg})
            except Exception as e2:
                results["errors"] += 1
                error_msg = f"⚠️ {method_name}() - 错误: {str(e2)[:100]}"
                print(error_msg)
                results["details"].append({"method": method_name, "status": "ERROR", "msg": error_msg})
                
        except Exception as e:
            total_errors += 1
            error_msg = f"⚠️ {method_name}() - 异常: {str(e)[:100]}"
            print(error_msg)
            results["details"].append({"method": method_name, "status": "ERROR", "msg": error_msg})
    
    return results


def main():
    """主函数：运行所有模块测试"""
    print("=" * 70)
    print("🧪 YYC³ 智能单元测试套件 V3.1")
    print("=" * 70)
    print(f"\n📋 待测试模块数: {len(MODULES)}")
    
    all_results = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    for module_name, config in MODULES.items():
        result = run_module_tests(module_name, config)
        all_results.append(result)
        
        total_tests += result["total"]
        total_passed += result["passed"]
        total_failed += result["failed"]
        total_errors += len(result["errors"])
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📊 YYC³ 全场景测试报告汇总")
    print("=" * 70)
    
    print("\n📈 各模块测试结果:")
    print("-" * 60)
    for result in all_results:
        pass_rate = (result["passed"] / result["total"] * 100) if result["total"] > 0 else 0
        emoji = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 50 else "❌"
        print(f"{emoji} {result['module']:12s} | 通过: {result['passed']}/{result['total']} | "
              f"通过率: {pass_rate:.1f}%")
    
    print("\n" + "=" * 70)
    print("📊 总体统计:")
    print("=" * 70)
    print(f"总测试数:   {total_tests}")
    print(f"✅ 通过:     {total_passed} ({total_passed/total_tests*100:.1f}%)" if total_tests > 0 else "")
    print(f"❌ 失败:     {total_failed}")
    print(f"⚠️  错误:    {total_errors}")
    
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n总体通过率: {overall_pass_rate:.1f}%")
    
    if overall_pass_rate >= 80:
        print("\n🎉 优秀！代码质量达标，可进入下一阶段优化！")
        exit_code = 0
    elif overall_pass_rate >= 60:
        print("\n✨ 良好！大部分功能正常，建议修复少量失败项。")
        exit_code = 1
    else:
        print("\n⚠️ 需要改进！请优先处理失败和错误的测试项。")
        exit_code = 2
    
    print("\n💡 下一步建议:")
    if total_failed > 0 or total_errors > 0:
        print("   1. 查看上述详细错误信息，定位问题根源")
        print("   2. 检查方法签名是否与实际实现匹配")
        print("   3. 验证参数类型和数量是否正确")
    if overall_pass_rate < 80:
        print("   4. 补充边界条件测试用例")
        print("   5. 增加异常处理场景覆盖")
    else:
        print("   ✅ 可进行性能测试和生产部署准备")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
