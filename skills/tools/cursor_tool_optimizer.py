"""
小柳升级：Cursor工具调用优化器
解决问题54：提高工具调用成功率
"""

class CursorToolOptimizer:
    """Cursor工具调用优化器"""
    
    COMMON_TOOL_FAILURES = {
        "read_file失败": {
            "现象": "明明应该读文件，Cursor却不读",
            "原因": [
                "路径不确定，Cursor犹豫",
                "文件太大，Cursor害怕",
                "觉得没必要读"
            ],
            "解决方案": {
                "1. 明确路径": """
# ❌ 模糊指令
用户: 看看用户模块

# ✅ 明确指令
用户: 读取 src/models/user.py 文件
                """,
                "2. 分批读取": """
# 文件太大 (>1000行)
先读取 user.py 的 1-100 行（类定义部分）
然后根据需要读取具体函数
                """,
                "3. User Rules强制": """
BEFORE modifying ANY file:
  MUST read the file first
  No exceptions
                """
            }
        },
        
        "grep失败": {
            "现象": "明明有这个函数/变量，grep找不到",
            "原因": [
                "正则表达式错误",
                "搜索路径错误",
                "大小写问题"
            ],
            "解决方案": {
                "1. 转义特殊字符": """
# ❌ 错误: 括号未转义
grep("def create_user()", path="src/")

# ✅ 正确: 转义括号
grep("def create_user\\(", path="src/")
                """,
                "2. 使用-i忽略大小写": """
grep("createuser", i=True)  # 能匹配 CreateUser, createUser
                """,
                "3. 先用codebase_search": """
# 优先用语义搜索
codebase_search("用户创建函数在哪")
# 定位后再用grep精确搜索
grep("def create_user", path="src/services/user.py")
                """
            }
        },
        
        "codebase_search不准": {
            "现象": "搜索结果不相关",
            "原因": [
                "查询词太模糊",
                "查询词太技术化",
                "没有提供上下文"
            ],
            "解决方案": {
                "1. 用完整问题而非关键词": """
# ❌ 关键词搜索
codebase_search("user auth")

# ✅ 完整问题
codebase_search("用户登录时如何验证密码的？")
                """,
                "2. 提供业务上下文": """
# ❌ 技术术语
codebase_search("JWT token")

# ✅ 业务场景
codebase_search("登录成功后如何生成和返回认证令牌？")
                """,
                "3. 分步搜索": """
# 第1步: 找入口
codebase_search("用户注册的入口在哪")

# 第2步: 找具体逻辑
codebase_search("注册时如何验证邮箱格式", target=["src/services/"])
                """
            }
        },
        
        "search_replace失败": {
            "现象": "修改代码时报错: old_string not found",
            "原因": [
                "缩进不匹配 (空格vs Tab)",
                "多了/少了空格",
                "复制粘贴时格式变了"
            ],
            "解决方案": {
                "1. 先read_file看原始格式": """
# 第1步: 读文件看确切内容
read_file("user.py", offset=10, limit=5)

# 第2步: 完全按照原文复制old_string
search_replace(
    file="user.py",
    old_string="    def login(self):",  # 精确4个空格
    new_string="    def login(self, remember=False):"
)
                """,
                "2. 包含足够上下文": """
# ❌ 上下文太少
old_string = "return True"  # 文件中可能有多处

# ✅ 包含上下文（前后3-5行）
old_string = '''
    if user.check_password(password):
        login_user(user)
        return True
'''
                """,
                "3. 用replace_all处理重复": """
# 重命名变量
search_replace(
    file="user.py",
    old_string="old_name",
    new_string="new_name",
    replace_all=True  # 替换所有出现
)
                """
            }
        },
        
        "并行工具调用未使用": {
            "现象": "明明能并行，Cursor却串行执行",
            "原因": [
                "Cursor不确定是否有依赖",
                "User Rules未明确要求并行"
            ],
            "解决方案": {
                "User Rules强制": """
When reading multiple INDEPENDENT files:
  MUST call read_file in PARALLEL (same tool call batch)
  
Example:
  Reading user.py, order.py, product.py (no dependency)
  → Call all 3 read_file in ONE batch
                """,
                "用户提示": """
用户: 同时读取 user.py, order.py, product.py 这三个文件
(加"同时"提示并行)
                """
            }
        }
    }
    
    def generate_tool_call_checklist(self):
        """生成工具调用检查清单"""
        return {
            "read_file": [
                "☐ 路径是否明确？",
                "☐ 文件是否存在？(可先list_dir确认)",
                "☐ 文件是否太大？(>1000行考虑分批)",
                "☐ 是否可以并行读取多个文件？"
            ],
            "grep": [
                "☐ 特殊字符是否转义？(括号、点号)",
                "☐ 是否需要-i忽略大小写？",
                "☐ 搜索路径是否正确？",
                "☐ 是否应该先用codebase_search定位？"
            ],
            "codebase_search": [
                "☐ 是否用完整问题而非关键词？",
                "☐ 是否包含业务上下文？",
                "☐ target_directories是否合理？",
                "☐ 是否需要拆分为多个子查询？"
            ],
            "search_replace": [
                "☐ 是否先read_file确认原始内容？",
                "☐ old_string是否包含足够上下文？",
                "☐ 缩进是否精确匹配？",
                "☐ 是否需要replace_all？"
            ]
        }
    
    def tool_success_rate_improvement_plan(self):
        """工具成功率提升计划"""
        return {
            "阶段1_强制规则": {
                "目标": "从60%提升到80%",
                "措施": [
                    "User Rules: 修改前必须先read_file",
                    "User Rules: grep前必须转义特殊字符",
                    "User Rules: 优先用codebase_search定位"
                ]
            },
            "阶段2_自动检查": {
                "目标": "从80%提升到90%",
                "措施": [
                    "search_replace前自动read_file验证",
                    "grep失败自动retry with -i",
                    "并行调用自动检测"
                ]
            },
            "阶段3_智能优化": {
                "目标": "从90%提升到95%",
                "措施": [
                    "自动学习常见失败模式",
                    "自动选择最佳工具组合",
                    "自动优化查询词"
                ]
            }
        }

# 使用示例
if __name__ == "__main__":
    optimizer = CursorToolOptimizer()
    
    print("🔧 Cursor工具调用常见问题:")
    for problem, details in optimizer.COMMON_TOOL_FAILURES.items():
        print(f"\n{problem}:")
        print(f"  现象: {details['现象']}")
        print(f"  原因: {', '.join(details['原因'])}")
    
    print("\n📋 工具调用检查清单:")
    checklist = optimizer.generate_tool_call_checklist()
    for tool, checks in checklist.items():
        print(f"\n{tool}:")
        for check in checks:
            print(f"  {check}")

