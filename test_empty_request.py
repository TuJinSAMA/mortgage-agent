#!/usr/bin/env python3
"""
测试空请求
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_empty_object():
    """测试传入空对象"""
    print("测试1: 传入空对象 {}")
    try:
        response = requests.post(f"{BASE_URL}/loan-products", json={})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功! 返回 {data['total']} 个产品")
            if data['products']:
                print(f"  第一个产品: {data['products'][0]['name']}")
        else:
            print(f"✗ 失败: {response.json()}")
    except Exception as e:
        print(f"✗ 错误: {e}")

def test_no_body():
    """测试不传请求体"""
    print("\n测试2: 不传请求体")
    try:
        response = requests.post(f"{BASE_URL}/loan-products")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功! 返回 {data['total']} 个产品")
        else:
            print(f"✗ 失败: {response.json()}")
    except Exception as e:
        print(f"✗ 错误: {e}")

def test_partial_filters():
    """测试部分筛选条件"""
    print("\n测试3: 只传部分筛选条件")
    try:
        response = requests.post(f"{BASE_URL}/loan-products", json={
            "loanTerm": 30
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功! 返回 {data['total']} 个产品")
            if data['products']:
                print(f"  前3个产品期限: {[p['term'] for p in data['products'][:3]]}")
        else:
            print(f"✗ 失败: {response.json()}")
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("测试贷款产品接口 - 空请求和可选参数")
        print("=" * 60)
        
        test_empty_object()
        test_no_body()
        test_partial_filters()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务器。请确保服务已启动:")
        print("  uv run fastapi dev app/main.py --port 8000")

