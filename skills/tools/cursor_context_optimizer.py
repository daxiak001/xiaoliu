"""
小柳升级：Cursor上下文管理优化器
解决问题53：防止Cursor失忆，优化对话策略
"""

class CursorContextOptimizer:
    """Cursor上下文优化器"""
    
    CONTEXT_LIMITS = {
        "Claude Sonnet 4": 200000,  # tokens
        "safe_threshold": 150000,   # 安全阈值
        "warning_threshold": 100000  # 警告阈值
    }
    
    def __init__(self):
        self.critical_info = []  # 关键信息
        self.current_tokens = 0
    
    def optimize_conversation_strategy(self):
        """优化对话策略"""
        return {
            "策略1_关键信息提前": {
                "问题": "Cursor对话太长会忘记前面的内容",
                "解决方案": "每次回复前先读取关键文件",
                "实施": """
# ❌ 错误做法
用户: 修改用户模块
Cursor: 好的 (可能已忘记项目用的是Django)

# ✅ 正确做法
用户: 修改用户模块
Cursor: 
  1. 先读取 快速导航.md (确认技术栈)
  2. 先读取 用户模块相关文件
  3. 再开始修改
                """,
                "User Rules建议": """
BEFORE every response:
1. Read D:/设置/📋 必读要求文档/快速导航.md
2. Read relevant context files
3. Then respond
                """
            },
            
            "策略2_分段对话": {
                "问题": "一个窗口对话太长",
                "解决方案": "重要节点开新窗口，传递关键信息",
                "实施": """
# 对话节点1 (窗口1): 架构设计
  → 完成后总结关键决策到 项目决策.md

# 对话节点2 (窗口2): 功能开发
  → 先读 项目决策.md
  → 再开始开发
                """,
                "触发条件": [
                    "对话超过20轮",
                    "切换大的功能模块",
                    "Cursor开始遗忘"
                ]
            },
            
            "策略3_关键信息固化": {
                "问题": "重要决策在对话中，容易丢失",
                "解决方案": "立即写入文件，不依赖对话记忆",
                "关键信息类型": {
                    "技术栈选择": "写入 tech-stack.md",
                    "架构决策": "写入 architecture.md",
                    "编码规范": "写入 coding-standard.md",
                    "已开发功能": "写入 快速导航.md"
                },
                "User Rules": """
When user makes important decision:
  MUST immediately write to corresponding file
  DON'T rely on conversation memory
                """
            },
            
            "策略4_定期刷新上下文": {
                "问题": "长对话中Cursor渐进式遗忘",
                "解决方案": "每10轮主动重新加载关键信息",
                "实施": """
# 对话第10轮
Cursor自动: 让我先刷新一下关键信息
  → 重新读取 快速导航.md
  → 重新读取 当前功能相关文件
  → 继续对话

# 对话第20轮
Cursor自动: 再次刷新关键信息...
                """,
                "User Rules": """
Every 10 conversation turns:
  Automatically refresh key context
  Re-read navigation and current module files
                """
            },
            
            "策略5_上下文压缩": {
                "问题": "文件太多，上下文爆炸",
                "解决方案": "只读必要部分，用摘要代替全文",
                "技巧": {
                    "大文件": "用offset+limit只读相关函数",
                    "配置文件": "只读摘要，需要时再读详情",
                    "测试文件": "不读，只在写测试时读"
                },
                "示例": """
# ❌ 错误: 一次读10个文件
read_file("user.py")
read_file("order.py")
...  # 上下文爆炸

# ✅ 正确: 先搜索定位，再精准读取
codebase_search("用户认证逻辑在哪")
read_file("user.py", offset=50, limit=30)  # 只读相关部分
                """
            }
        }
    
    def detect_context_overflow_risk(self, conversation_length):
        """检测上下文溢出风险"""
        if conversation_length > 20:
            return {
                "risk": "高",
                "warning": "⚠️ 对话过长，Cursor可能开始遗忘",
                "actions": [
                    "1. 立即保存关键信息到文件",
                    "2. 考虑开新窗口继续",
                    "3. 或要求Cursor重新加载关键上下文"
                ]
            }
        elif conversation_length > 10:
            return {
                "risk": "中",
                "warning": "提示Cursor刷新关键信息",
                "actions": ["要求重新读取快速导航"]
            }
        else:
            return {"risk": "低"}
    
    def generate_context_refresh_prompt(self):
        """生成上下文刷新提示词"""
        return """
🔄 上下文刷新检查点

在继续之前，请先:
1. 重新读取 D:/设置/📋 必读要求文档/快速导航.md
2. 重新读取当前正在开发的模块相关文件
3. 确认你记得:
   - 项目使用的技术栈
   - 当前任务的目标
   - 已完成的功能列表
   
确认完成后，继续我们的对话。
        """
    
    def best_practices_for_long_conversation(self):
        """长对话最佳实践"""
        return {
            "用户侧": {
                "1. 及时总结": "每完成一个功能，要求Cursor更新快速导航",
                "2. 主动刷新": "感觉Cursor遗忘时，要求它重新读取关键文件",
                "3. 开新窗口": "大功能切换时，开新窗口并传递上下文",
                "4. 简化描述": "不要在对话中放大量代码，用文件代替"
            },
            "Cursor侧": {
                "1. 自动保存": "重要信息立即写文件",
                "2. 定期刷新": "每10轮自动重新加载",
                "3. 按需读取": "不要一次读太多文件",
                "4. 关键信息前置": "每次回复前先确认技术栈"
            }
        }

# 使用示例
if __name__ == "__main__":
    optimizer = CursorContextOptimizer()
    
    # 检测风险
    risk = optimizer.detect_context_overflow_risk(conversation_length=15)
    print(f"上下文风险: {risk['risk']}")
    
    # 获取优化策略
    strategies = optimizer.optimize_conversation_strategy()
    print("\n优化策略:")
    for name, strategy in strategies.items():
        print(f"\n{name}:")
        print(f"  问题: {strategy['问题']}")
        print(f"  解决: {strategy['解决方案']}")
    
    # 生成刷新提示
    if risk['risk'] == '高':
        print("\n" + optimizer.generate_context_refresh_prompt())

