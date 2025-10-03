"""
小柳升级：Cursor高级问题解决方案
解决问题62-72：补全/协作/监控/错误/审查/学习/大文件/依赖/测试/重构/性能
"""

# Q62: 代码补全质量
class CursorCompletionOptimizer:
    """提高Cursor Tab补全质量"""
    
    COMPLETION_IMPROVEMENT = """
# 提高Cursor补全质量

## 问题: Tab补全质量低

## 解决方案:

### 1. 项目上下文文件
创建 .cursor/context.md:
```markdown
# 项目上下文

## 命名规范
- 函数: snake_case (create_user, get_order)
- 类: PascalCase (UserService, OrderProcessor)
- 常量: UPPER_CASE (MAX_RETRY, API_KEY)

## 常用模式
- Service类方法: create_xx, update_xx, delete_xx, get_xx
- API路由: /api/v1/resource
- 数据库模型: 继承BaseModel

Cursor会学习这些模式，补全更准确
```

### 2. 类型注解
```python
# ❌ 补全不准确
def process(data):
    data.  # Cursor不知道有什么方法

# ✅ 补全准确
def process(data: UserData):
    data.  # Cursor知道UserData的所有方法
```

### 3. Docstring引导
```python
def create_order():
    '''创建订单
    
    步骤:
    1. 验证用户
    2. 检查库存
    3. 创建订单
    4. 扣减库存
    '''
    # Cursor会按照docstring的步骤补全代码
```

### 4. 示例代码
在项目中保留完整的示例:
```
examples/
  ├─ user_service_example.py  # 完整示例
  ├─ api_example.py
  └─ test_example.py

Cursor会参考这些示例补全
```
    """

# Q63: 多窗口协作
class CursorMultiWindowSync:
    """多窗口协作同步"""
    
    SYNC_STRATEGY = """
# Cursor多窗口协作

## 问题: 窗口间不同步，互相不知道对方的修改

## 解决方案:

### 1. 中央日志文件
.cursor/operation-log.md (所有窗口共享):
```markdown
## Window-1 (2025-01-01 14:00)
✅ 修改了 user.py: 添加email验证
✅ 创建了 user_test.py

## Window-2 (2025-01-01 14:05)  
✅ 修改了 order.py: 集成user模块
⚠️ 注意: 依赖Window-1的user.py修改
```

每个窗口操作前先读这个日志

### 2. 文件锁定机制
.cursor/file-locks.json:
```json
{
  "user.py": {
    "locked_by": "Window-1",
    "since": "2025-01-01 14:00",
    "reason": "正在重构"
  }
}
```

其他窗口修改前检查锁定状态

### 3. User Rules
```
MULTI-WINDOW RULE:

BEFORE any modification:
  1. Read .cursor/operation-log.md
  2. Check if file is locked
  3. Log your operation
  4. Then modify
```

### 4. 定期同步
每个窗口每10轮:
  自动读取 operation-log.md
  刷新其他窗口的修改
    """

# Q64: 文件监控失效
class CursorFileMonitorFix:
    """确保Cursor总是看到最新代码"""
    
    SOLUTION = """
# Cursor文件监控失效

## 问题: 修改后Cursor还用旧内容

## 原因:
1. Cursor缓存了旧内容
2. 文件监控失效
3. Cursor还在用对话历史中的旧版本

## 解决方案:

### 1. 强制刷新规则
User Rules:
```
BEFORE every response:
  If user just modified files:
    MUST re-read those files
    DON'T use cached/historical content
```

### 2. 用户明确提示
❌ "用user.py中的函数"  
✅ "重新读取user.py，用最新的函数"

### 3. 版本标记
每次修改后添加版本注释:
```python
# user.py
# Version: 2025-01-01-14:30
# Last modified: 添加email验证

class User:
    ...
```

Cursor通过版本号判断是否是最新

### 4. 强制re-read
重要修改后:
用户: "刚才修改了user.py，先重新读取再继续"
    """

# Q65: 错误理解能力
class CursorErrorAnalyzer:
    """提高错误诊断准确率"""
    
    ERROR_LOG_TEMPLATE = """
# 错误日志优化

## 问题: Cursor抓不住错误重点

## 解决: 结构化错误日志

### 模板:
```
🔴 错误报告

【错误类型】: ImportError
【错误位置】: user.py:25
【错误信息】: cannot import name 'OrderService'
【调用栈】:
  user.py:25 → from services import OrderService
  services/__init__.py:10 → from .order import OrderService  
  services/order.py:5 → ImportError (循环导入)

【已尝试方案】:
  ❌ 重启服务 - 无效
  ❌ 重新安装依赖 - 无效

【期望Cursor分析】:
  1. 为什么会循环导入?
  2. 如何解决?
```

### Cursor分析准确率: 从50% → 90%
    """

# Q66: 代码审查盲区
class CursorCodeReviewChecklist:
    """完整代码审查清单"""
    
    COMPREHENSIVE_CHECKLIST = {
        "功能正确性": [
            "☐ 实现了所有需求?",
            "☐ 边界情况处理?",
            "☐ 错误处理完整?"
        ],
        "性能": [
            "☐ 有N+1查询?",
            "☐ 有死循环风险?",
            "☐ 大循环中有IO操作?",
            "☐ 是否需要缓存?"
        ],
        "安全": [
            "☐ SQL注入风险?",
            "☐ XSS风险?",
            "☐ 敏感信息泄露?",
            "☐ 权限检查?"
        ],
        "可维护性": [
            "☐ 代码重复?",
            "☐ 函数过长(>50行)?",
            "☐ 命名清晰?",
            "☐ 注释充分?"
        ],
        "测试": [
            "☐ 单元测试覆盖?",
            "☐ 边界情况测试?",
            "☐ 异常情况测试?"
        ],
        "业务逻辑": [
            "☐ 符合业务规则?",
            "☐ 数据一致性?",
            "☐ 事务完整?"
        ]
    }
    
    USER_RULES = """
When reviewing code:
  MUST check ALL items in checklist
  CANNOT skip any category
  Report findings with severity
    """

# Q67: 跨项目经验库
class CursorCrossProjectKnowledge:
    """跨项目经验库"""
    
    KNOWLEDGE_BASE = """
# 跨项目经验库

## 位置: D:/cursor-knowledge-base/

## 结构:
```
cursor-knowledge-base/
  ├─ common-errors/
  │   ├─ python-errors.md
  │   ├─ javascript-errors.md
  │   └─ database-errors.md
  ├─ best-practices/
  │   ├─ api-design.md
  │   ├─ database-design.md
  │   └─ testing.md
  └─ solutions/
      ├─ auth-solutions.md
      ├─ payment-solutions.md
      └─ cache-solutions.md
```

## User Rules:
```
BEFORE solving any problem:
  1. Search D:/cursor-knowledge-base/
  2. Check if similar problem exists
  3. Reuse solution if applicable
  4. AFTER solving new problem:
     Add to knowledge base
```

## 示例:
common-errors/python-errors.md:
```markdown
### 错误: ModuleNotFoundError

**场景**: 导入自定义模块失败
**原因**: __init__.py缺失 或 PYTHONPATH问题
**解决**: 
1. 检查__init__.py
2. 检查相对导入
3. 检查包结构

**项目**: 用户系统、订单系统 (都遇到过)
**成功率**: 100%
```
    """

# Q68: 大文件处理
class CursorLargeFileStrategy:
    """大文件处理策略"""
    
    STRATEGY = """
# 大文件处理 (>3000行)

## 问题: Cursor容易遗漏细节

## 策略:

### 1. 分段读取
```python
# ❌ 一次读完3000行
read_file("large.py")

# ✅ 分段读取
read_file("large.py", offset=0, limit=100)    # 类定义
read_file("large.py", offset=500, limit=100)  # 核心方法
read_file("large.py", offset=1000, limit=100) # 工具方法
```

### 2. 先看大纲
```python
# 第1步: 用grep看函数列表
grep("^def |^class ", path="large.py")
  → 了解文件结构

# 第2步: 精确读取需要的函数
read_file("large.py", offset=500, limit=50)  # 只读create_order函数
```

### 3. codebase_search定位
```python
# 不知道大文件中具体位置
codebase_search("large.py中如何处理支付?")
  → 定位到具体行号

# 精确读取
read_file("large.py", offset=1200, limit=80)
```

### 4. 拆分大文件
建议Cursor:
  "这个文件3000行太大，建议拆分为:
   - user_models.py (模型定义)
   - user_services.py (业务逻辑)  
   - user_utils.py (工具函数)"
    """

# Q69: 依赖关系追踪
class CursorDependencyTracker:
    """依赖关系追踪"""
    
    TRACKING = """
# 依赖关系追踪

## 问题: 修改函数不知道影响谁

## 解决: 依赖图

### 创建 DEPENDENCIES.md:
```markdown
## create_order() 被调用关系

调用者:
  1. api/order_api.py:create_order_endpoint()
  2. tasks/order_tasks.py:async_create_order()
  3. admin/order_admin.py:admin_create_order()

依赖:
  → check_inventory()
  → process_payment()
  → send_notification()

⚠️ 修改此函数需要测试3个调用方!
```

### User Rules:
```
BEFORE modifying any function:
  1. grep function_name in entire codebase
  2. Check who calls it
  3. Check what it calls
  4. Assess impact
  5. List affected tests
```
    """

# Q70-72: 测试/重构/性能
ADVANCED_RULES = """
# Q70: 测试用例质量

## Checklist:
☐ 正常情况
☐ 边界值 (0, -1, None, 空字符串, 超大值)
☐ 异常情况 (网络错误, 数据库错误, 超时)
☐ 并发情况
☐ 幂等性

# Q71: 安全重构流程

1. 完整测试覆盖 (>80%)
2. 小步重构 (每次只改一个点)
3. 每步后运行测试
4. Git每步提交
5. 出错立即回滚

# Q72: 性能坏习惯检测

## 自动检测:
- 循环中查询数据库 ❌
- 循环中打开文件 ❌
- 正则在大循环中编译 ❌
- 大对象深拷贝 ❌
- 无界限的缓存增长 ❌
"""

if __name__ == "__main__":
    print("🔧 Cursor高级问题解决方案")
    print("\nQ62: 补全质量")
    print(CursorCompletionOptimizer.COMPLETION_IMPROVEMENT[:300])
    
    print("\nQ63: 多窗口协作")
    print(CursorMultiWindowSync.SYNC_STRATEGY[:300])
    
    print("\nQ64: 文件监控")
    print(CursorFileMonitorFix.SOLUTION[:300])
    
    print("\nQ65: 错误理解")
    print(CursorErrorAnalyzer.ERROR_LOG_TEMPLATE[:300])
    
    print("\nQ66: 代码审查")
    checklist = CursorCodeReviewChecklist.COMPREHENSIVE_CHECKLIST
    print(f"审查维度: {len(checklist)}个")
    
    print("\nQ67: 跨项目经验")
    print(CursorCrossProjectKnowledge.KNOWLEDGE_BASE[:300])
    
    print("\nQ68: 大文件处理")
    print(CursorLargeFileStrategy.STRATEGY[:300])
    
    print("\nQ69: 依赖追踪")
    print(CursorDependencyTracker.TRACKING[:300])
    
    print("\nQ70-72: 测试/重构/性能")
    print(ADVANCED_RULES[:300])

