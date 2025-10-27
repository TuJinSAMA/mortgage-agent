#!/usr/bin/env python3
"""
测试贷款产品筛选接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_no_filters():
    """测试不带筛选条件"""
    print("\n=== 测试1: 不带筛选条件 ===")
    response = requests.post(f"{BASE_URL}/loan-products", json={})
    data = response.json()
    print(f"总产品数: {data['total']}")
    if data['products']:
        print(f"第一个产品: {data['products'][0]['name']}")


def test_credit_score_elite():
    """测试信用分数 >= 700 筛选 ELITE"""
    print("\n=== 测试2: 信用分数 >= 700 (ELITE) ===")
    filters = {
        "creditScore": [780, 850]
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    
    # 验证所有产品都是 ELITE
    elite_count = sum(1 for p in data['products'] if p['tier'] == 'ELITE')
    print(f"ELITE 产品数: {elite_count}")
    print(f"所有产品都是 ELITE: {elite_count == data['total']}")


def test_loan_term():
    """测试贷款期限筛选"""
    print("\n=== 测试3: 贷款期限 30 年 ===")
    filters = {
        "loanTerm": 30
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    if data['products']:
        print(f"前3个产品期限: {[p['term'] for p in data['products'][:3]]}")


def test_arm_or_fixed():
    """测试 ARM/FIXED 筛选"""
    print("\n=== 测试4: 固定利率 (FIXED) ===")
    filters = {
        "armOrFixed": "fix"
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    
    # 验证所有产品都是 FIXED
    fixed_count = sum(1 for p in data['products'] if p['arm_or_fixed'] == 'FIXED')
    print(f"FIXED 产品数: {fixed_count}")
    print(f"所有产品都是 FIXED: {fixed_count == data['total']}")


def test_show_va_loans():
    """测试显示 VA 贷款"""
    print("\n=== 测试5: 显示 VA 贷款 ===")
    filters = {
        "showVaLoans": True,
        "showFhaLoans": False
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    
    # 统计各类型产品数量
    programs = {}
    for p in data['products']:
        programs[p['program']] = programs.get(p['program'], 0) + 1
    print(f"产品类型分布: {programs}")


def test_show_fha_loans():
    """测试显示 FHA 贷款"""
    print("\n=== 测试6: 显示 FHA 贷款 ===")
    filters = {
        "showVaLoans": False,
        "showFhaLoans": True
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    
    # 统计各类型产品数量
    programs = {}
    for p in data['products']:
        programs[p['program']] = programs.get(p['program'], 0) + 1
    print(f"产品类型分布: {programs}")


def test_combined_filters():
    """测试组合筛选条件"""
    print("\n=== 测试7: 组合筛选 (完整示例) ===")
    filters = {
        "mortgageType": "refinance",
        "zipCode": 90011,
        "purchasePrice": 1310000,
        "downPayment": 524000,
        "creditScore": [780, 850],
        "loanTerm": 30,
        "armOrFixed": "fix",
        "showFhaLoans": False,
        "showVaLoans": False
    }
    response = requests.post(f"{BASE_URL}/loan-products", json=filters)
    data = response.json()
    print(f"总产品数: {data['total']}")
    
    if data['products']:
        print("\n前5个产品:")
        for i, p in enumerate(data['products'][:5], 1):
            print(f"{i}. {p['name']} - Tier: {p['tier']}, Program: {p['program']}, "
                  f"Rate: {p['rate']}%, Term: {p['term']}, Type: {p['arm_or_fixed']}")


if __name__ == "__main__":
    try:
        print("开始测试贷款产品筛选接口...")
        print("=" * 60)
        
        test_no_filters()
        test_credit_score_elite()
        test_loan_term()
        test_arm_or_fixed()
        test_show_va_loans()
        test_show_fha_loans()
        test_combined_filters()
        
        print("\n" + "=" * 60)
        print("所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器。请确保服务已启动:")
        print("  uv run fastapi dev app/main.py --port 8000")
    except Exception as e:
        print(f"\n测试出错: {e}")

