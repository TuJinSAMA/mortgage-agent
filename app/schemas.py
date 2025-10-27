from typing import List, Optional, Union
from pydantic import BaseModel, Field


class MortgageFormData(BaseModel):
    """房贷表单数据模型"""
    mortgageType: Optional[str] = Field(None, description="贷款类型: purchase 或 refinance")
    zipCode: Optional[int] = Field(None, description="邮编")
    purchasePrice: Optional[float] = Field(None, description="购买价格")
    downPayment: Optional[float] = Field(None, description="首付金额")
    creditScore: Optional[List[Optional[int]]] = Field(None, description="信用分数范围 [min, max]")
    loanTerm: Optional[int] = Field(None, description="贷款期限（年）")
    armOrFixed: Optional[str] = Field(None, description="贷款类型: fix 或 arm")
    showFhaLoans: Optional[bool] = Field(None, description="是否显示 FHA 贷款")
    showVaLoans: Optional[bool] = Field(None, description="是否显示 VA 贷款")


class MissingFieldItem(BaseModel):
    """缺失字段项"""
    key: str = Field(..., description="字段名称")
    message: str = Field(..., description="提示消息")
    type: str = Field(..., description="字段类型: input, select, boolean, array")
    options: Optional[List[str]] = Field(None, description="选项列表（仅用于 select 类型）")


class CheckMissingFieldsRequest(BaseModel):
    """检查缺失字段请求模型"""
    formData: MortgageFormData = Field(..., description="表单数据")


class CheckMissingFieldsResponse(BaseModel):
    """检查缺失字段响应模型"""
    missingFields: List[MissingFieldItem] = Field(..., description="缺失的字段列表")


# 保留原有的 Chat 模型以便向后兼容
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户输入的消息", min_length=1)
    

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="大模型返回的响应")


# 贷款产品相关模型
class LoanProduct(BaseModel):
    """贷款产品模型"""
    name: str = Field(..., description="产品名称")
    program: str = Field(..., description="贷款项目类型: CONV, VA, FHA, USDA")
    tier: str = Field(..., description="产品等级: ELITE, STANDARD")
    balance_bucket: str = Field(..., description="贷款额度分类: STANDARD, HIGH_BALANCE, JUMBO")
    construction_type: str = Field(..., description="建筑类型: EXISTING, OTC_ONE_TIME_CLOSE")
    arm_or_fixed: str = Field(..., description="利率类型: FIXED, ARM")
    rate: float = Field(..., description="利率")
    price_15_day: float = Field(..., description="15天锁定价格")
    price_30_day: float = Field(..., description="30天锁定价格")
    price_45_day: float = Field(..., description="45天锁定价格")
    term: str = Field(..., description="贷款期限")
    lender: str = Field(..., description="贷款机构")


class LoanProductFilterRequest(BaseModel):
    """贷款产品筛选请求模型"""
    mortgageType: Optional[str] = Field(None, description="贷款类型: purchase 或 refinance")
    zipCode: Optional[int] = Field(None, description="邮编")
    purchasePrice: Optional[float] = Field(None, description="购买价格")
    downPayment: Optional[float] = Field(None, description="首付金额")
    creditScore: Optional[List[Optional[int]]] = Field(None, description="信用分数范围 [min, max]")
    loanTerm: Optional[int] = Field(None, description="贷款期限(年)")
    armOrFixed: Optional[str] = Field(None, description="贷款类型: fix 或 arm")
    showFhaLoans: Optional[bool] = Field(None, description="是否显示 FHA 贷款")
    showVaLoans: Optional[bool] = Field(None, description="是否显示 VA 贷款")


class GetLoanProductsResponse(BaseModel):
    """获取贷款产品列表响应模型"""
    total: int = Field(..., description="产品总数")
    products: List[LoanProduct] = Field(..., description="贷款产品列表")

