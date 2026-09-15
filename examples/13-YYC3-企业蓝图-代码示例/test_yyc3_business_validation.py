"""
YYC³ 全场景业务逻辑验证套件 V3.2
直接运行每个模块的 __main__ 测试部分

运行方式:
    python3 test_yyc3_business_validation.py
"""

import subprocess
import sys
import os
from typing import Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = [
    {
        "name": "标准化体系",
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '标准化体系', 'standardization_inference_v2.py'),
        "expected_tests": 4,
        "category": "Q3-能力建设"
    },
    {
        "name": "规范化管理",
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '规范化管理', 'process_management_inference_v2.py'),
        "expected_tests": 4,
        "category": "Q3-能力建设"
    },
    {
        "name": "数据化治理",
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '数据化治理', 'data_governance_inference_v2.py'),
        "expected_tests": 4,
        "category": "Q3-能力建设"
    },
    {
        "name": "智能化升级",
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '智能化升级', 'ai_upgrade_inference_v2.py'),
        "expected_tests": 3,
        "category": "Q3-能力建设"
    },
    {
        "name": "协同化办公",
        "path": os.path.join(BASE_DIR, '04-能力建设智能化', '协同化办公', 'collaboration_inference_v2.py'),
        "expected_tests": 1,
        "category": "Q3-能力建设"
    },
    {
        "name": "市场洞察",
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '市场洞察', 'market_intelligence_inference_v2.py'),
        "expected_tests": 4,
        "category": "Q4-价值创造"
    },
    {
        "name": "创新孵化",
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '创新孵化', 'innovation_incubator_v2.py'),
        "expected_tests": 3,
        "category": "Q4-价值创造"
    },
    {
        "name": "薪酬激励",
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '薪酬激励', 'compensation_intelligence_v2.py'),
        "expected_tests": 4,
        "category": "Q4-价值创造"
    },
    {
        "name": "高效运营",
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '高效运营', 'operations_intelligence_v2.py'),
        "expected_tests": 4,
        "category": "Q4-价值创造"
    },
    {
        "name": "度势成长",
        "path": os.path.join(BASE_DIR, '05-价值创造智能化', '度势成长', 'growth_intelligence_v2.py'),
        "expected_tests": 5,
        "category": "Q4-价值创造"
    }
]


def run_module_test(module: Dict) -> Tuple[bool, str, int]:
    """
    运行单个模块测试
    
    Returns:
        (success: bool, output: str, exit_code: int)
    """
    try:
        result = subprocess.run(
            [sys.executable, module["path"]],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BASE_DIR
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return success, output, result.returncode
        
    except subprocess.TimeoutExpired:
        return False, "⏰ 测试超时（30秒）", -1
    except Exception as e:
        return False, f"❌ 执行异常: {str(e)}", -2


def extract_test_results(output: str) -> Dict[str, int]:
    """从输出中提取测试结果统计"""
    results = {"passed": 0, "failed": 0, "total": 0}
    
    lines = output.split('\n')
    
    for line in lines:
        if '✅' in line and ('测试' in line or '完成'):
            results["passed"] += 1
        elif '❌' in line or '错误' in line or 'Error' in line or 'Traceback' in line:
            results["failed"] += 1
    
    # 检查是否所有测试通过
    if '所有测试通过' in output or '所有测试用例通过' in output:
        results["total"] = results["passed"]
    else:
        results["total"] = results["passed"] + results["failed"]
    
    return results


def main():
    """主函数"""
    print("=" * 80)
    print("🧪 YYC³ 全场景业务逻辑验证套件 V3.2")
    print("=" * 80)
    print(f"\n📋 测试范围: {len(MODULES)} 个业务场景")
    print(f"📂 Q3 能力建设: {sum(1 for m in MODULES if m['category'] == 'Q3-能力建设')} 个")
    print(f"📂 Q4 价值创造: {sum(1 for m in MODULES if m['category'] == 'Q4-价值创造')} 个")
    
    all_results = []
    total_passed_modules = 0
    total_failed_modules = 0
    total_tests_run = 0
    total_tests_passed = 0
    
    print("\n" + "=" * 80)
    print("🔍 开始执行业务逻辑验证...")
    print("=" * 80)
    
    for idx, module in enumerate(MODULES, 1):
        print(f"\n[{idx}/{len(MODULES)}] 📦 测试: {module['name']} ({module['category']})")
        print("-" * 60)
        
        success, output, exit_code = run_module_test(module)
        
        # 提取关键输出行
        key_lines = [line for line in output.split('\n') 
                    if any(keyword in line for keyword in 
                          ['✅', '❌', '⚠️', '测试', '通过', '失败', '错误', 
                           'Traceback', '完成', '所有'])]
        
        # 显示关键信息
        for line in key_lines[:15]:  # 只显示前15行关键信息
            print(f"   {line}")
        
        if len(key_lines) > 15:
            print(f"   ... 还有 {len(key_lines) - 15} 行输出")
        
        # 统计结果
        test_stats = extract_test_results(output)
        
        module_result = {
            "name": module["name"],
            "category": module["category"],
            "success": success,
            "exit_code": exit_code,
            "tests": test_stats,
            "output_summary": key_lines[-3:] if key_lines else ["无输出"]
        }
        all_results.append(module_result)
        
        total_tests_run += test_stats["total"]
        total_tests_passed += test_stats["passed"]
        
        if success:
            total_passed_modules += 1
            status_emoji = "✅"
        else:
            total_failed_modules += 1
            status_emoji = "❌"
        
        print(f"\n   状态: {status_emoji} | 测试数: {test_stats['total']} | "
              f"通过: {test_stats['passed']} | 失败: {test_stats['failed']}")
    
    # 生成最终报告
    print("\n" + "=" * 80)
    print("📊 YYC³ 业务逻辑验证报告")
    print("=" * 80)
    
    print("\n🎯 模块级验证结果:")
    print("-" * 80)
    print(f"{'模块名称':<12} {'类别':<14} {'状态':<6} {'测试数':<8} {'通过':<8} {'详情'}")
    print("-" * 80)
    
    for result in all_results:
        status = "✅ 通过" if result["success"] else "❌ 失败"
        tests_info = f"{result['tests']['total']}"
        passed_info = f"{result['tests']['passed']}"
        
        detail = ""
        if result["output_summary"]:
            detail = result["output_summary"][0][:40] if len(result["output_summary"][0]) > 40 else result["output_summary"][0]
        
        print(f"{result['name']:<12} {result['category']:<14} {status:<6} "
              f"{tests_info:<8} {passed_info:<8} {detail}")
    
    print("-" * 80)
    
    # 统计汇总
    print(f"\n📈 总体统计:")
    print(f"   模块总数:     {len(MODULES)}")
    print(f"   ✅ 通过模块:  {total_passed_modules} ({total_passed_modules/len(MODULES)*100:.1f}%)")
    print(f"   ❌ 失败模块:  {total_failed_modules} ({total_failed_modules/len(MODULES)*100:.1f}%)")
    
    if total_tests_run > 0:
        print(f"\n   测试用例:")
        print(f"      总计:       {total_tests_run}")
        print(f"      ✅ 通过:     {total_tests_passed} ({total_tests_passed/total_tests_run*100:.1f}%)")
        print(f"      ❌ 失败:     {total_tests_run - total_tests_passed}")
    
    # 质量评估
    module_pass_rate = (total_passed_modules / len(MODULES)) * 100
    test_pass_rate = (total_tests_passed / total_tests_run * 100) if total_tests_run > 0 else 0
    
    print(f"\n{'='*80}")
    print("🏆 质量评估")
    print(f"{'='*80}")
    print(f"   模块通过率:   {module_pass_rate:.1f}%")
    print(f"   用例通过率:   {test_pass_rate:.1f}%")
    
    # 判定等级
    if module_pass_rate >= 90 and test_pass_rate >= 85:
        grade = "A+ 优秀 ⭐⭐⭐⭐⭐"
        verdict = "🎉 生产就绪！代码质量优秀，可立即部署！"
        exit_code = 0
    elif module_pass_rate >= 80 and test_pass_rate >= 75:
        grade = "A  良好 ⭐⭐⭐⭐"
        verdict = "✨ 接近生产标准！建议修复少量问题后部署。"
        exit_code = 0
    elif module_pass_rate >= 70 and test_pass_rate >= 65:
        grade = "B+ 合格 ⭐⭐⭐"
        verdict = "💪 基本达标！需要优化部分功能。"
        exit_code = 1
    elif module_pass_rate >= 60:
        grade = "B 待改进 ⭐⭐"
        verdict = "⚠️ 需要改进！存在较多问题需处理。"
        exit_code = 1
    else:
        grade = "C 不合格 ⭐"
        verdict = "❌ 未达标！需要全面检查和重构。"
        exit_code = 2
    
    print(f"   综合评级:     {grade}")
    print(f"\n{verdict}")
    
    # 下一步行动建议
    print(f"\n💡 建议的下一步操作:")
    if total_failed_modules > 0:
        failed_names = [r["name"] for r in all_results if not r["success"]]
        print(f"   1. 🔧 优先修复以下失败模块: {', '.join(failed_names)}")
        print(f"   2. 📝 查看详细错误日志，定位根本原因")
        print(f"   3. ✅ 重新运行此验证脚本确认修复效果")
    if test_pass_rate < 80:
        print(f"   4. 🧪 补充单元测试用例，提高覆盖率至80%+")
    if module_pass_rate >= 90:
        print(f"   5. 🚀 可进入性能优化和生产部署阶段")
        print(f"   6. 📊 准备API文档和用户手册")
        print(f"   7. 🔒 进行安全审计和代码审查")
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 验证脚本异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
