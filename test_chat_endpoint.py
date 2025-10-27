"""
测试 /chat 接口的系统提示词功能
"""
import asyncio
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_chat_loan_recommendation():
    """测试贷款产品推荐"""
    response = client.post(
        "/chat",
        json={"message": "我的信用分数是750,想要30年期的固定利率贷款,有什么推荐吗?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 贷款推荐测试 ===")
    print(f"用户: 我的信用分数是750,想要30年期的固定利率贷款,有什么推荐吗?")
    print(f"回复: {data['response']}")


def test_chat_term_explanation():
    """测试专业术语解释"""
    response = client.post(
        "/chat",
        json={"message": "什么是ARM贷款?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 术语解释测试 ===")
    print(f"用户: 什么是ARM贷款?")
    print(f"回复: {data['response']}")


def test_chat_fha_explanation():
    """测试FHA贷款解释"""
    response = client.post(
        "/chat",
        json={"message": "FHA贷款和传统贷款有什么区别?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== FHA贷款解释测试 ===")
    print(f"用户: FHA贷款和传统贷款有什么区别?")
    print(f"回复: {data['response']}")


def test_chat_off_topic():
    """测试无关话题拒绝"""
    response = client.post(
        "/chat",
        json={"message": "今天天气怎么样?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 无关话题测试 ===")
    print(f"用户: 今天天气怎么样?")
    print(f"回复: {data['response']}")


def test_chat_elite_tier():
    """测试ELITE等级产品推荐"""
    response = client.post(
        "/chat",
        json={"message": "我的信用分数是780,想了解精英级的贷款产品"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== ELITE等级产品测试 ===")
    print(f"用户: 我的信用分数是780,想了解精英级的贷款产品")
    print(f"回复: {data['response']}")


def test_chat_english_question():
    """测试英文提问"""
    response = client.post(
        "/chat",
        json={"message": "I have a credit score of 750 and I'm looking for a 30-year fixed rate mortgage. What do you recommend?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 英文提问测试 ===")
    print(f"User: I have a credit score of 750 and I'm looking for a 30-year fixed rate mortgage. What do you recommend?")
    print(f"Response: {data['response']}")


def test_chat_english_term():
    """测试英文术语解释"""
    response = client.post(
        "/chat",
        json={"message": "What is the difference between FHA and conventional loans?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 英文术语解释测试 ===")
    print(f"User: What is the difference between FHA and conventional loans?")
    print(f"Response: {data['response']}")


def test_chat_english_off_topic():
    """测试英文无关话题"""
    response = client.post(
        "/chat",
        json={"message": "What's the weather like today?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("\n=== 英文无关话题测试 ===")
    print(f"User: What's the weather like today?")
    print(f"Response: {data['response']}")


if __name__ == "__main__":
    print("开始测试 /chat 接口...")
    print("=" * 80)
    
    # 中文测试
    print("\n【中文测试】")
    test_chat_loan_recommendation()
    test_chat_term_explanation()
    test_chat_fha_explanation()
    test_chat_off_topic()
    test_chat_elite_tier()
    
    # 英文测试
    print("\n【English Tests】")
    test_chat_english_question()
    test_chat_english_term()
    test_chat_english_off_topic()
    
    print("\n" + "=" * 80)
    print("所有测试完成! / All tests completed!")

