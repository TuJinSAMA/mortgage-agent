# Mortgage Agent

一个基于 FastAPI 和 LangChain 构建的抵押贷款代理服务。

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **LangChain**: 大模型应用开发框架
- **uv**: Python 包管理工具

## 配置

在项目根目录创建 `.env` 文件，配置 API 密钥：

```bash
OPENAI_API_KEY=your_poe_api_key_here
OPENAI_BASE_URL=https://api.poe.com/v1
MODEL_NAME=GPT-5
```

## 安装依赖

使用 uv 安装项目依赖：

```bash
uv sync
```

## 运行服务

启动开发服务器：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

## API 文档

启动服务后，可以访问以下地址查看和调试 API：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 端点

### 健康检查

- **GET** `/health` - 检查服务健康状态

### 贷款产品接口

- **POST** `/loan-products` - 获取贷款产品列表(支持筛选)
  
  **筛选条件(全部可选):**
  - `creditScore`: 信用分数范围 `[min, max]`,700分以上筛选 ELITE 产品
  - `loanTerm`: 贷款期限(年),匹配符合条件的产品
  - `armOrFixed`: 利率类型 (`"fix"` 或 `"arm"`)
  - `showVaLoans`: 是否显示 VA 贷款产品
  - `showFhaLoans`: 是否显示 FHA 贷款产品
  
  **注意:** 所有筛选条件都是可选的,可以传入空对象 `{}` 获取所有产品
  
  **请求示例:**
  ```json
  {
    "mortgageType": "refinance",
    "zipCode": 90011,
    "purchasePrice": 1310000,
    "downPayment": 524000,
    "creditScore": [780, 850],
    "loanTerm": 30,
    "armOrFixed": "fix",
    "showFhaLoans": false,
    "showVaLoans": false
  }
  ```
  
  **响应示例:**
  ```json
  {
    "total": 5,
    "products": [
      {
        "name": "ELITE 21-30 YEAR",
        "program": "CONV",
        "tier": "ELITE",
        "balance_bucket": "STANDARD",
        "construction_type": "EXISTING",
        "arm_or_fixed": "FIXED",
        "rate": 7.500,
        "price_15_day": -3.766,
        "price_30_day": -3.676,
        "price_45_day": -3.546,
        "term": "21-30",
        "lender": "UWM"
      }
    ]
  }
  ```

### 表单验证接口

- **POST** `/check-missing-fields` - 检查房贷表单数据中缺失的字段
  - 请求体：`{"formData": {...}}`
  - 响应：`{"missingFields": [...]}`

### 聊天接口

- **POST** `/chat` - 与大模型对话(保留用于向后兼容)
  - 请求体：`{"message": "你的问题"}`
  - 响应：`{"response": "大模型的回答"}`

## 测试接口

运行测试脚本验证贷款产品筛选功能:

```bash
# 确保服务已启动
uv run fastapi dev app/main.py --port 8000

# 在另一个终端运行测试
python test_loan_products.py
```

## 项目结构

```
mortgage-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 主应用
│   ├── config.py        # 配置管理
│   └── schemas.py       # 数据模型
├── data/
│   └── loan_products.json  # 贷款产品数据
├── .env                 # 环境变量配置（需自行创建）
├── .gitignore           # Git 忽略文件
├── pyproject.toml       # 项目配置和依赖
├── test_loan_products.py  # 测试脚本
└── README.md            # 项目文档
```

