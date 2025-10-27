from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
from pathlib import Path

from app.config import settings
from app.schemas import (
    ChatRequest, 
    ChatResponse, 
    CheckMissingFieldsRequest, 
    CheckMissingFieldsResponse,
    MissingFieldItem,
    LoanProduct,
    LoanProductFilterRequest,
    GetLoanProductsResponse
)

app = FastAPI(
    title="Mortgage Agent API",
    description="A mortgage agent service built with FastAPI and LangChain",
    version="0.1.0"
)

# 初始化大模型
llm = ChatOpenAI(
    model=settings.model_name,
    openai_api_key=settings.openai_api_key,
    openai_api_base=settings.openai_base_url,
    temperature=0.7,
)


# 定义 LangChain 的输出结构
class MissingFieldOutput(BaseModel):
    """缺失字段输出结构"""
    key: str = Field(description="字段名称")
    message: str = Field(description="友好的提示消息，引导用户填写该字段")
    type: str = Field(description="字段类型: input, select, boolean, array")
    options: Optional[List[str]] = Field(default=None, description="选项列表（仅用于 select 类型）")


class MissingFieldsOutput(BaseModel):
    """缺失字段列表输出结构"""
    missing_fields: List[MissingFieldOutput] = Field(description="缺失的字段列表")


# 创建 JSON 输出解析器
parser = JsonOutputParser(pydantic_object=MissingFieldsOutput)

# 创建系统提示词
system_prompt = """You are a professional mortgage loan assistant for a mortgage recommendation website. Your role is to help users find the best mortgage rates by collecting necessary information.

You will receive a form data object that may be missing some required fields. Your task is to:
1. Identify which required fields are missing or have null values
2. Generate a polite, professional, and natural message in English for each missing field
3. Return the results in a structured JSON format

**Field Validation Rules:**
- mortgageType: Required. Must be "purchase" or "refinance". If missing, type is "select" with options ["purchase", "refinance"]
- zipCode: Required number. If missing or null, type is "input"
- purchasePrice: Required number. If missing or null (0 is valid), type is "input"
- downPayment: Required number. If missing or null (0 is valid), type is "input"
- creditScore: Required array. Can be [min, max], [min, null] for 780+, or [null, max] for below 600. If missing or null, type is "array"
- loanTerm: Required number. If missing or null, type is "input"
- armOrFixed: Required. Must be "fix" or "arm". If missing, type is "select" with options ["fix", "arm"]
- showFhaLoans: Required boolean. If field doesn't exist (not just false), type is "boolean"
- showVaLoans: Required boolean. If field doesn't exist (not just false), type is "boolean"

**Important Notes:**
- For boolean fields: false is a valid value, only flag as missing if the field is absent from the data
- For number fields: 0 is a valid value, only flag as missing if the value is null or absent
- For creditScore array: [780, null] or [null, 600] are valid values

Your messages should:
- Be warm, professional, and conversational
- Explain why the information is needed (to help find better mortgage rates)
- Use natural English that a native speaker would use
- Be concise but friendly
- NEVER use sequential words like "To get started", "First", "Next", "Finally", "Firstly", "Secondly", "Lastly", etc.
- Each message should be standalone and independent, as they will be displayed one at a time in a carousel-like rotation

{format_instructions}

If all required fields are present and valid, return an empty array for missing_fields."""

# 创建提示词模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Please analyze the following mortgage form data and identify any missing required fields:\n\n{form_data}\n\nReturn the missing fields in JSON format.")
])

# 创建 LangChain chain
validation_chain = prompt_template | llm | parser


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}


def filter_loan_products(products: List[LoanProduct], filters: LoanProductFilterRequest) -> List[LoanProduct]:
    """
    根据筛选条件过滤贷款产品
    
    Args:
        products: 贷款产品列表
        filters: 筛选条件
    
    Returns:
        过滤后的贷款产品列表
    """
    filtered_products = products
    
    # 1. 根据信用分数筛选 tier (700分以上筛选 ELITE)
    if filters.creditScore and len(filters.creditScore) > 0:
        min_score = filters.creditScore[0] if filters.creditScore[0] is not None else 0
        if min_score >= 700:
            filtered_products = [p for p in filtered_products if p.tier == "ELITE"]
    
    # 2. 根据 loanTerm 筛选符合条件的贷款期限
    if filters.loanTerm is not None:
        loan_term_str = str(filters.loanTerm)
        filtered_products = [
            p for p in filtered_products 
            if match_loan_term(p.term, loan_term_str)
        ]
    
    # 3. 根据 armOrFixed 筛选 (fix -> FIXED, arm -> ARM)
    if filters.armOrFixed:
        arm_or_fixed_upper = "FIXED" if filters.armOrFixed.lower() == "fix" else "ARM"
        filtered_products = [
            p for p in filtered_products 
            if p.arm_or_fixed == arm_or_fixed_upper
        ]
    
    # 4. 根据 showVaLoans 和 showFhaLoans 筛选 program
    # 如果两者都为 False 或 None,则只显示 CONV 和 USDA
    # 如果 showVaLoans 为 True,包含 VA
    # 如果 showFhaLoans 为 True,包含 FHA
    allowed_programs = set()
    
    # 默认总是包含 CONV 和 USDA
    allowed_programs.add("CONV")
    allowed_programs.add("USDA")
    
    # 根据用户选择添加 VA 和 FHA
    if filters.showVaLoans:
        allowed_programs.add("VA")
    
    if filters.showFhaLoans:
        allowed_programs.add("FHA")
    
    filtered_products = [
        p for p in filtered_products 
        if p.program in allowed_programs
    ]
    
    return filtered_products


def match_loan_term(product_term: str, target_term: str) -> bool:
    """
    匹配贷款期限
    
    产品期限可能是范围(如 "21-30", "16-20")或具体值(如 "30", "15")
    
    Args:
        product_term: 产品的期限字符串
        target_term: 目标期限字符串
    
    Returns:
        是否匹配
    """
    try:
        target = int(target_term)
        
        # 如果产品期限包含范围符号(如 "21-30")
        if "-" in product_term:
            parts = product_term.split("-")
            if len(parts) == 2:
                min_term = int(parts[0])
                max_term = int(parts[1])
                return min_term <= target <= max_term
        
        # 如果产品期限包含斜杠(如 "5/6" ARM)
        if "/" in product_term:
            # 对于 ARM 产品,取第一个数字作为初始固定期限
            initial_term = int(product_term.split("/")[0])
            # ARM 产品通常是长期贷款,我们认为它匹配 30 年期
            return target >= 30 or target == initial_term
        
        # 精确匹配
        return int(product_term) == target
        
    except (ValueError, AttributeError):
        return False


@app.post("/loan-products", response_model=GetLoanProductsResponse)
async def get_loan_products(filters: Optional[LoanProductFilterRequest] = None):
    """
    获取贷款产品列表(支持筛选)
    
    该接口返回贷款产品列表,支持根据多种条件进行筛选:
    
    筛选条件:
    - **creditScore**: 信用分数范围,700分以上筛选 ELITE 产品
    - **loanTerm**: 贷款期限(年),匹配符合条件的产品
    - **armOrFixed**: 利率类型 ("fix" 或 "arm")
    - **showVaLoans**: 是否显示 VA 贷款产品
    - **showFhaLoans**: 是否显示 FHA 贷款产品
    
    注意: 默认总是包含 CONV 和 USDA 产品
    
    返回:
    - **total**: 产品总数
    - **products**: 贷款产品列表
    """
    try:
        # 获取数据文件路径
        current_dir = Path(__file__).parent.parent
        data_file = current_dir / "data" / "loan_products.json"
        
        # 检查文件是否存在
        if not data_file.exists():
            raise HTTPException(
                status_code=500,
                detail=f"贷款产品数据不存在: {data_file}"
            )
        
        # 读取 JSON 数据
        with open(data_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        # 转换为 Pydantic 模型
        all_products = [LoanProduct(**product) for product in products_data]
        
        # 如果没有提供筛选条件,返回所有产品
        if filters is None:
            return GetLoanProductsResponse(
                total=len(all_products),
                products=all_products
            )
        
        # 应用筛选条件
        filtered_products = filter_loan_products(all_products, filters)
        
        return GetLoanProductsResponse(
            total=len(filtered_products),
            products=filtered_products
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"解析贷款产品数据失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取贷款产品失败: {str(e)}"
        )


@app.post("/check-missing-fields", response_model=CheckMissingFieldsResponse)
async def check_missing_fields(request: CheckMissingFieldsRequest):
    """
    检查房贷表单数据中缺失的字段
    
    该接口会分析提交的表单数据，识别缺失或无效的必填字段，
    并为每个缺失字段生成友好的提示消息，引导用户补充信息。
    
    - **formData**: 房贷表单数据对象
    
    返回:
    - **missingFields**: 缺失字段列表，如果所有字段都完整则返回空数组
    """
    try:
        # 将表单数据转换为 JSON 字符串
        form_data_dict = request.formData.dict()
        form_data_json = json.dumps(form_data_dict, indent=2)
        
        # 调用 LangChain validation chain
        result = await validation_chain.ainvoke({
            "form_data": form_data_json,
            "format_instructions": parser.get_format_instructions()
        })
        
        # 解析结果并转换为响应模型
        missing_fields_list = result.get("missing_fields", [])
        
        # 转换为 Pydantic 模型
        missing_fields = [
            MissingFieldItem(
                key=field["key"],
                message=field["message"],
                type=field["type"],
                options=field.get("options")
            )
            for field in missing_fields_list
        ]
        
        return CheckMissingFieldsResponse(missingFields=missing_fields)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"检查表单字段失败: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    与大模型对话的接口（保留用于向后兼容）
    
    - **message**: 用户输入的消息
    """
    try:
        # 调用大模型
        response = await llm.ainvoke(request.message)
        
        return ChatResponse(response=response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用大模型失败: {str(e)}")

