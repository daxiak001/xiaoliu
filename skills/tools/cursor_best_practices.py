"""
小柳升级：Cursor最佳实践大全
解决问题55-60：Cursor特定优化
"""

# Q55: 代码理解偏差
ARCHITECTURE_UNDERSTANDING = """
# 帮助Cursor理解整体架构

## 问题: Cursor只见树木不见森林

## 解决方案:

### 1. 架构文档先行
创建 docs/ARCHITECTURE.md:
```
系统采用分层架构:
- API层 (api/) - 处理HTTP请求
- 服务层 (services/) - 业务逻辑
- 数据层 (models/) - 数据模型
- 工具层 (utils/) - 通用工具

依赖规则: API → Services → Models
```

User Rules: 修改代码前必须先读 ARCHITECTURE.md

### 2. 模块地图
创建 MODULE_MAP.md:
```
用户模块 (users/)
  ├─ models/user.py - 用户模型
  ├─ services/auth.py - 认证服务
  └─ api/user_api.py - 用户API

订单模块 (orders/)
  ├─ 依赖: users, products, payments
  └─ ...
```

### 3. codebase_search 先探索
❌ 直接改代码
✅ 先搜索理解: "这个项目如何处理用户认证?"
"""

# Q56: 重复劳动
OPERATION_MEMORY = """
# Cursor操作记忆系统

## 问题: 重复搜索/读取相同内容

## 解决方案:

### User Rules强制记忆:
```
OPERATION MEMORY RULE:

If you already performed these operations in THIS conversation:
  - Searched for X → DON'T search again, use cached result
  - Read file Y → DON'T read again, use cached content
  - Listed directory Z → DON'T list again

Exception: User explicitly asks to re-check
```

### 操作日志自动记录:
每次关键操作后Cursor自动追加到回复末尾:

📝 本轮操作记录:
  ✅ 搜索 "用户认证" → src/auth/
  ✅ 读取 auth/login.py
  ✅ 关键发现: 使用JWT认证

(下次直接引用，不再重复)
"""

# Q57: 并行能力浪费
PARALLEL_OPTIMIZATION = """
# 最大化Cursor并行能力

## 问题: 明明能并行，Cursor却串行

## User Rules强制并行:
```
PARALLEL EXECUTION RULE:

When reading/searching MULTIPLE INDEPENDENT items:
  MUST use parallel tool calls

✅ Good (parallel):
  read_file(user.py) + read_file(order.py) + read_file(product.py)
  All in ONE function_calls block

❌ Bad (sequential):
  read_file(user.py) → wait → read_file(order.py) → wait → ...
```

## 用户提示词优化:
❌ "读user.py，然后读order.py"  (暗示串行)
✅ "同时读取 user.py, order.py, product.py"  (明确并行)
"""

# Q58: User Rules失效
USER_RULES_ENFORCEMENT = """
# 确保User Rules 100%执行

## 问题: 写了规则但Cursor不执行

## 原因分析:
1. 规则太长，Cursor没完全读取
2. 规则表述模糊，Cursor不理解
3. 规则冲突，Cursor选择性执行

## 解决方案:

### 1. 精简规则 (只保留核心)
❌ 1000行规则文档
✅ 50行核心规则 + 外部详细文档引用

### 2. 强制性表述
❌ "建议修改前先读文件"
✅ "MUST read file before ANY modification. No exceptions."

### 3. 分级规则
CRITICAL RULES (绝对不可违反):
  - 修改前必读文件
  - 不得删除用户数据

RECOMMENDED RULES (推荐):
  - 优先用codebase_search
  - 代码添加注释

### 4. 验证机制
每次Cursor回复前自检:
  ☐ 是否读取了文件？
  ☐ 是否搜索了现有代码？
  ☐ 是否更新了文档？

不通过 = 拒绝执行，要求Cursor重新来
"""

# Q59: 文件编辑错误
EDIT_SUCCESS_RATE = """
# 提高search_replace成功率

## 问题: 经常报错 "old_string not found"

## 常见原因:
1. 缩进不匹配 (空格 vs Tab)
2. 多了/少了空格
3. 上下文不足，匹配到多处

## 解决方案:

### 1. 编辑前必读
User Rules:
```
BEFORE any search_replace:
  1. MUST read_file first
  2. Copy EXACT content (including whitespace)
  3. Include 3-5 lines context
```

### 2. 上下文充足
❌ 上下文不足:
old_string = "return True"  # 文件中可能有10处

✅ 上下文充足:
old_string = '''
    if user.is_active:
        login_user(user)
        return True
'''

### 3. 特殊字符处理
Python字符串:
  old_string = "def func():"  ✅
  old_string = 'def func():'  ✅

### 4. 使用replace_all
重命名变量时:
search_replace(
    old_string="old_var",
    new_string="new_var",
    replace_all=True  # 替换所有出现
)

### 5. 失败后的补救
如果search_replace失败:
  1. 重新read_file确认内容
  2. 用grep精确定位
  3. 复制准确的内容
  4. 再次尝试
"""

# Q60: Cursor优势未充分利用
CURSOR_ADVANTAGES = """
# Cursor的杀手级功能

## 功能1: codebase_search (语义搜索)
优势: 理解意图而非关键词

✅ 最佳实践:
  - 用完整问题: "用户登录后如何生成token?"
  - 而非关键词: "token generate"
  - 提供业务上下文，不用技术黑话

场景:
  - 不知道功能在哪 → codebase_search定位
  - 理解陌生项目 → 连续搜索探索
  - 查找相似代码 → 语义匹配

## 功能2: 多文件并行读取
优势: 一次性加载多个文件

✅ 最佳实践:
  同时读取 user.py, order.py, product.py
  → 3个文件并行读取，节省时间

场景:
  - 理解模块间关系
  - 批量代码审查
  - 跨文件重构

## 功能3: 实时linter
优势: 修改后立即看到错误

✅ 最佳实践:
  User Rules: 
  ```
  After editing ANY file:
    MUST call read_lints on that file
    Fix all errors before proceeding
  ```

场景:
  - 代码格式错误立即修复
  - import错误立即发现
  - 类型错误立即纠正

## 功能4: 增量编辑 (search_replace)
优势: 精准修改，不破坏格式

✅ 最佳实践:
  - 包含充足上下文
  - 只改需要改的部分
  - 保持原有缩进和格式

场景:
  - 大文件局部修改
  - 保持代码风格一致
  - 避免格式混乱

## 功能5: workspace根目录能力
优势: 访问所有项目文件

✅ 最佳实践:
  在项目根目录创建:
    - .cursor/rules.md (项目特定规则)
    - docs/ (架构文档)
    - CONTRIBUTING.md (开发指南)
  
  Cursor自动读取这些文件

## 工作流设计: 充分利用Cursor
1. 需求理解阶段:
   codebase_search → 快速定位相关代码

2. 设计阶段:
   并行读取多个文件 → 理解现有架构

3. 开发阶段:
   read → edit (search_replace) → read_lints → 修复

4. 测试阶段:
   运行测试 → read_lints → 修复错误

5. 文档阶段:
   自动生成/更新文档
"""

# 综合示例
CURSOR_WORKFLOW_EXAMPLE = '''
# Cursor最佳工作流示例

## 场景: 给订单添加优惠券功能

### 阶段1: 探索 (利用codebase_search)
用户: 我想给订单添加优惠券功能

Cursor:
  1. codebase_search("现有优惠券相关功能") → 发现 coupons/
  2. codebase_search("订单创建流程") → 发现 orders/service.py
  3. 并行读取 coupons/models.py, orders/service.py

### 阶段2: 设计
Cursor: 基于现有代码，设计集成方案...
  - 在Order模型添加coupon_id字段
  - 在create_order()中验证优惠券
  - 计算折扣价格

### 阶段3: 开发 (利用search_replace)
Cursor:
  1. read orders/models.py (确认准确内容)
  2. search_replace 添加coupon_id字段
  3. read_lints → 检查错误
  4. read orders/service.py
  5. search_replace 添加优惠券验证逻辑
  6. read_lints → 检查错误

### 阶段4: 测试
Cursor:
  1. 创建测试文件
  2. 运行测试
  3. read_lints → 修复问题

### 阶段5: 文档
Cursor:
  更新 快速导航.md: "订单优惠券功能 ✅"

全程高效，无重复操作！
'''

if __name__ == "__main__":
    print("📚 Cursor最佳实践大全")
    print("\n1. 架构理解:", ARCHITECTURE_UNDERSTANDING[:200])
    print("\n2. 操作记忆:", OPERATION_MEMORY[:200])
    print("\n3. 并行优化:", PARALLEL_OPTIMIZATION[:200])
    print("\n4. 规则执行:", USER_RULES_ENFORCEMENT[:200])
    print("\n5. 编辑成功率:", EDIT_SUCCESS_RATE[:200])
    print("\n6. Cursor优势:", CURSOR_ADVANTAGES[:200])

