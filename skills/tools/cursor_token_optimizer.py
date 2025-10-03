"""
小柳升级：Cursor Token消耗优化器
解决问题61：避免无谓token消耗，优化对话策略
"""

class CursorTokenOptimizer:
    """Cursor Token消耗优化器"""
    
    TOKEN_WASTE_PATTERNS = {
        "反复读取同一文件": {
            "问题": "对话中多次读取相同文件",
            "浪费": "每次读取消耗大量token",
            "示例": """
# ❌ Token浪费
第5轮: read_file("user.py")  # 1000 tokens
第10轮: read_file("user.py")  # 又1000 tokens (重复!)
第15轮: read_file("user.py")  # 再1000 tokens (重复!)
            """,
            "解决方案": {
                "规则1_对话内缓存": """
User Rules:
If you already read file X in this conversation:
  DON'T read again unless:
    - File was modified
    - User explicitly asks to re-read
    - More than 20 turns have passed
                """,
                "规则2_摘要替代全文": """
# 第1次: 读完整文件
read_file("user.py")  # 1000 tokens

# 第2次: 只读需要的部分
read_file("user.py", offset=100, limit=20)  # 100 tokens

节省: 90% tokens
                """,
                "规则3_记忆关键信息": """
第1次读取后，Cursor自己总结:

📝 user.py 关键信息:
  - User模型: 包含username, email, password
  - 认证方法: authenticate(username, password)
  - 已读取，无需再读

下次直接用这个摘要 (只需50 tokens)
                """
            }
        },
        
        "过长的对话历史": {
            "问题": "对话超过30轮，每次回复都加载全部历史",
            "浪费": "旧对话占用大量token但价值低",
            "触发条件": [
                "对话轮数 > 30",
                "累计token > 100k",
                "开始出现重复内容"
            ],
            "解决方案": {
                "策略1_开新窗口": """
触发条件:
  ✅ 对话超过30轮
  ✅ 切换大功能模块
  ✅ 累计token > 100k

开新窗口前:
  1. 总结当前窗口关键信息 → 保存到文件
  2. 新窗口第一句话: 
     "先读取 session-summary.md 了解上下文"
  3. 继续工作

Token节省: 70-80%
                """,
                "策略2_定期清理": """
每20轮对话:
  Cursor自动总结: 
    "前20轮主要完成: 用户模块、订单模块"
    "关键文件: user.py, order.py"
    "下面继续，之前的细节可忽略"

清理后token: 从50k降到5k
                """
            }
        },
        
        "重复搜索": {
            "问题": "相同问题多次codebase_search",
            "浪费": "每次搜索消耗token+时间",
            "示例": """
# ❌ 重复搜索
第3轮: codebase_search("用户认证逻辑")
第8轮: codebase_search("用户认证逻辑")  # 完全相同!
第12轮: codebase_search("用户认证逻辑")  # 又来!
            """,
            "解决方案": """
User Rules:
SEARCH CACHE RULE:
  If you searched for X in this conversation:
    Result was: Y
    DON'T search again
    Use cached result Y

Cursor自动记录:
  已搜索: "用户认证" → src/auth/login.py
  已搜索: "订单创建" → src/orders/service.py
            """
        },
        
        "不必要的大范围读取": {
            "问题": "一次读取整个大目录",
            "浪费": "大量无关文件消耗token",
            "示例": """
# ❌ Token浪费
grep("def login", path="src/")  # 搜索整个src/
  → 返回50个结果，大部分无关

# ✅ Token节省
先用 codebase_search 定位
  → 找到 src/auth/login.py
再精确搜索:
  grep("def login", path="src/auth/login.py")
  → 只返回1个结果

节省: 95% tokens
            """
        }
    }
    
    def calculate_token_savings(self, optimizations):
        """计算token节省"""
        savings = {
            "避免重复读文件": "60-70%",
            "开新窗口替代长对话": "70-80%",
            "搜索缓存": "80-90%",
            "精确范围读取": "90-95%",
            "总体节省": "平均70%"
        }
        return savings
    
    def when_to_start_new_window(self):
        """何时开新窗口"""
        return {
            "触发条件": {
                "1. 对话轮数": "> 30轮",
                "2. Token消耗": "> 100k tokens",
                "3. 功能切换": "从用户模块切到订单模块",
                "4. 开始重复": "Cursor开始重复搜索/读取",
                "5. 失忆迹象": "Cursor忘记之前说过的话"
            },
            "开新窗口流程": [
                "步骤1: 当前窗口总结关键信息",
                "步骤2: 写入 session-summary-N.md",
                "步骤3: 开新窗口",
                "步骤4: 新窗口第一句: 读取summary了解上下文",
                "步骤5: 继续工作"
            ],
            "summary模板": """
# Session Summary - Window 1

## 完成功能
- ✅ 用户认证模块
- ✅ 订单创建功能

## 关键文件
- src/auth/login.py - JWT认证
- src/orders/service.py - 订单服务

## 技术决策
- 使用PostgreSQL数据库
- 使用Redis缓存
- API遵循RESTful规范

## 下一步
继续开发支付模块
            """
        }
    
    def token_optimization_checklist(self):
        """Token优化检查清单"""
        return {
            "对话开始前": [
                "☐ 是否可以复用之前窗口的结果?",
                "☐ 是否应该先读summary而非重新探索?",
                "☐ 是否明确了需要读取的文件范围?"
            ],
            "对话进行中": [
                "☐ 这个文件是否已经读过?",
                "☐ 这个搜索是否已经做过?",
                "☐ 是否可以用摘要代替全文?",
                "☐ 是否可以精确范围而非全局搜索?"
            ],
            "对话超过20轮": [
                "☐ 是否应该总结并开新窗口?",
                "☐ 是否开始出现重复内容?",
                "☐ Token累计是否已超50k?"
            ]
        }
    
    def user_rules_for_token_saving(self):
        """Token节省User Rules"""
        return """
# Cursor Token优化规则

## Rule 1: 文件读取缓存
If you read file X in this conversation:
  DON'T read again unless modified or explicitly asked
  Use your memory of the file content

## Rule 2: 搜索结果缓存  
If you searched for Y:
  DON'T search again
  Use cached result

## Rule 3: 精确范围
BEFORE reading/searching:
  Use codebase_search to locate first
  Then read/search the specific file/directory
  DON'T read entire src/ if you only need one file

## Rule 4: 摘要优先
For large files (>500 lines):
  First time: Read full file
  Later: Only read needed sections with offset+limit

## Rule 5: 新窗口触发
If conversation > 30 turns:
  Suggest user to start new window
  Summarize current session to file first

## Expected Token Saving: 70%
        """

# 使用示例
if __name__ == "__main__":
    optimizer = CursorTokenOptimizer()
    
    print("💰 Token节省策略:")
    for pattern, details in optimizer.TOKEN_WASTE_PATTERNS.items():
        print(f"\n{pattern}:")
        print(f"  问题: {details['问题']}")
        print(f"  浪费: {details['浪费']}")
    
    print("\n📊 Token节省估算:")
    savings = optimizer.calculate_token_savings({})
    for opt, saving in savings.items():
        print(f"  {opt}: {saving}")
    
    print("\n🚪 何时开新窗口:")
    new_window = optimizer.when_to_start_new_window()
    for condition in new_window["触发条件"].values():
        print(f"  - {condition}")
    
    print("\n📋 Token优化检查清单:")
    checklist = optimizer.token_optimization_checklist()
    for phase, checks in checklist.items():
        print(f"\n{phase}:")
        for check in checks:
            print(f"  {check}")

