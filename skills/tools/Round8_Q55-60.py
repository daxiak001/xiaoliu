"""
小柳升级：第8轮问题55-60
Cursor特定问题优化
"""

# Q55: Cursor的代码理解偏差
class CursorArchitectureUnderstanding:
    """帮助Cursor理解整体架构"""
    
    STRATEGIES = {
        "策略1_架构图先行": """
在让Cursor修改代码前，先给它看架构图:

用户: 开始前，先读取以下文件理解整体架构:
  1. docs/architecture.md (系统架构)
  2. docs/module-map.md (模块关系图)
  3. 快速导航.md (已实现功能)
        """,
        
        "策略2_依赖关系可视化": """
项目根目录创建 DEPENDENCIES.md:

```markdown
# 模块依赖关系

## 核心依赖链
User → Auth → Database
Order → User + Product + Payment
Payment → External API

## 禁止的依赖
❌ Database → User (反向依赖)
❌ Auth → Order (跨层依赖)
```

让Cursor修改前先读这个文件
        """,
        
        "策略3_分层说明": """
创建 LAYERS.md:

```
presentation/  (UI层)
  ↓ 只能调用
application/   (应用层) 
  ↓ 只能调用
domain/        (领域层)
  ↓ 只能调用
infrastructure/ (基础设施层)
```

User Rules: 修改代码前必须确认不违反分层原则
        """,
        
        "策略4_用codebase_search探索": """
# ❌ 错误: 直接改代码
用户: 给订单添加优惠券功能
Cursor: (直接在order.py里加代码，不知道已有coupon模块)

# ✅ 正确: 先探索
用户: 给订单添加优惠券功能
Cursor: 
  1. codebase_search("现有优惠券相关功能在哪")
  2. read相关文件理解设计
  3. 再设计集成方案
        """
    }

# Q56: Cursor的重复劳动
class CursorOperationMemory:
    """Cursor操作记忆系统"""
    
    ANTI_REPETITION_RULES = """
# User Rules: 操作记忆

## 规则1: 搜索结果缓存
If you searched "用户认证逻辑" in this conversation:
  DON'T search again
  Use the previous result

## 规则2: 文件内容记忆
If you already read file X in this conversation:
  DON'T read again unless explicitly asked
  Use the remembered content

## 规则3: 操作日志
After each significant operation, log it:
  "已搜索: 用户认证 → src/auth/login.py"
  "已读取: user.py (包含User类定义)"
  
Next time DON'T repeat the same operation.
    """
    
    IMPLEMENTATION = {
        "方案1_对话内记忆": """
Cursor在每次回复末尾自动总结:

✅ 本轮操作记录:
  - 搜索了"支付流程" → payment/processor.py
  - 读取了 payment/processor.py
  - 创建了 payment/alipay.py

下次用户问支付相关问题，直接用这些信息，不再重复搜索。
        """,
        
        "方案2_操作日志文件": """
项目根目录创建 .cursor/operation-log.md

每次操作后Cursor自动追加:

```markdown
## 2025-01-01 14:30 - 用户认证模块探索
- codebase_search("用户登录") → src/auth/login.py
- read src/auth/login.py → 使用JWT认证
- 关键函数: authenticate_user(), generate_token()

## 2025-01-01 15:00 - 订单模块探索
- codebase_search("订单创建") → src/orders/service.py
...
```

下次直接读这个日志，避免重复探索。
        """
    }

# Q57: Cursor的并行能力浪费
class CursorParallelOptimizer:
    """Cursor并行能力优化"""
    
    USER_RULES_PARALLEL = """
# User Rules: 强制并行

## Rule: Parallel Tool Calls
When you need to:
  - Read multiple INDEPENDENT files
  - Search multiple INDEPENDENT patterns
  - List multiple INDEPENDENT directories

You MUST call tools in PARALLEL (same batch).

## Example ✅:
```python
# 并行读取3个文件
<function_calls>
  <invoke name="read_file"><parameter name="target_file">user.py
