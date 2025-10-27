# 贷款产品筛选接口使用说明

## 接口概述

**端点:** `POST /loan-products`

**功能:** 根据用户提供的筛选条件,返回符合条件的贷款产品列表。

**重要:** 所有筛选参数都是可选的,可以传入空对象 `{}` 或不传请求体来获取所有产品。

## 筛选规则说明

### 1. 信用分数筛选 (creditScore)

- **规则:** 当信用分数最低值 >= 700 时,只返回 `tier = "ELITE"` 的产品
- **示例:**
  ```json
  {
    "creditScore": [780, 850]  // 最低分 780 >= 700,筛选 ELITE 产品
  }
  ```

### 2. 贷款期限筛选 (loanTerm)

- **规则:** 匹配产品的 `term` 字段
  - 范围匹配: 如产品 term 为 "21-30",用户输入 30 会匹配
  - 精确匹配: 如产品 term 为 "30",用户输入 30 会匹配
  - ARM 产品: 如产品 term 为 "5/6",用户输入 30 会匹配(ARM 通常是长期贷款)
  
- **示例:**
  ```json
  {
    "loanTerm": 30  // 匹配 term 为 "21-30", "30", "5/6" 等
  }
  ```

### 3. 利率类型筛选 (armOrFixed)

- **规则:** 
  - `"fix"` → 筛选 `arm_or_fixed = "FIXED"` 的产品
  - `"arm"` → 筛选 `arm_or_fixed = "ARM"` 的产品

- **示例:**
  ```json
  {
    "armOrFixed": "fix"  // 只返回固定利率产品
  }
  ```

### 4. VA 贷款筛选 (showVaLoans)

- **规则:**
  - `true`: 包含 `program = "VA"` 的产品
  - `false` 或不传: 不包含 VA 产品
  - 注意: CONV 和 USDA 产品默认总是包含

- **示例:**
  ```json
  {
    "showVaLoans": true  // 返回 CONV + USDA + VA 产品
  }
  ```

### 5. FHA 贷款筛选 (showFhaLoans)

- **规则:**
  - `true`: 包含 `program = "FHA"` 的产品
  - `false` 或不传: 不包含 FHA 产品
  - 注意: CONV 和 USDA 产品默认总是包含

- **示例:**
  ```json
  {
    "showFhaLoans": true  // 返回 CONV + USDA + FHA 产品
  }
  ```

## 组合筛选示例

### 示例 0: 获取所有产品

```json
{}
```

**或者不传请求体**

**结果:** 返回所有 72 个贷款产品

### 示例 1: 高信用分数 + 30年固定利率

```json
{
  "creditScore": [780, 850],
  "loanTerm": 30,
  "armOrFixed": "fix",
  "showFhaLoans": false,
  "showVaLoans": false
}
```

**结果:** 返回 ELITE 等级、30年期、固定利率的 CONV 和 USDA 产品

### 示例 2: 包含所有类型的产品

```json
{
  "creditScore": [650, 700],
  "loanTerm": 30,
  "armOrFixed": "fix",
  "showFhaLoans": true,
  "showVaLoans": true
}
```

**结果:** 返回 STANDARD 等级、30年期、固定利率的所有类型产品(CONV, USDA, FHA, VA)

### 示例 3: ARM 产品

```json
{
  "creditScore": [780, 850],
  "loanTerm": 30,
  "armOrFixed": "arm",
  "showFhaLoans": false,
  "showVaLoans": false
}
```

**结果:** 返回 ELITE 等级、ARM 类型的 CONV 和 USDA 产品

## 响应格式

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

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 |
| `program` | string | 贷款项目类型: CONV, VA, FHA, USDA |
| `tier` | string | 产品等级: ELITE, STANDARD |
| `balance_bucket` | string | 贷款额度分类: STANDARD, HIGH_BALANCE, JUMBO |
| `construction_type` | string | 建筑类型: EXISTING, OTC_ONE_TIME_CLOSE |
| `arm_or_fixed` | string | 利率类型: FIXED, ARM |
| `rate` | float | 利率(%) |
| `price_15_day` | float | 15天锁定价格 |
| `price_30_day` | float | 30天锁定价格 |
| `price_45_day` | float | 45天锁定价格 |
| `term` | string | 贷款期限 |
| `lender` | string | 贷款机构 |

## 测试建议

1. **无筛选条件测试:** 发送空对象 `{}`,验证返回所有产品
2. **单一条件测试:** 每次只传一个筛选条件,验证筛选逻辑
3. **组合条件测试:** 传入多个筛选条件,验证组合筛选逻辑
4. **边界值测试:** 测试信用分数 699 vs 700,验证 ELITE 筛选阈值

## 注意事项

1. 所有筛选条件都是可选的,不传则不应用该筛选
2. 多个筛选条件之间是 **AND** 关系(同时满足)
3. CONV 和 USDA 产品默认总是包含,除非被其他筛选条件排除
4. 信用分数只看最低值(数组第一个元素)来判断是否筛选 ELITE

