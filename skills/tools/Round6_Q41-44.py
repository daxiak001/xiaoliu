"""
小柳升级：第6轮问题41-44快速实现
并发/内存泄漏/安全漏洞/可测试性
"""
import ast
import re

# Q41: 并发问题检测
class ConcurrencyDetector:
    """检测竞态条件、死锁、资源竞争"""
    
    def detect_race_condition(self, code):
        """检测竞态条件"""
        issues = []
        
        # 模式1：无锁的共享状态修改
        if "global " in code and "=" in code:
            if "Lock" not in code and "threading" not in code:
                issues.append({
                    "type": "race_condition",
                    "problem": "全局变量修改缺少锁保护",
                    "location": "全局变量赋值",
                    "suggestion": "使用threading.Lock()保护",
                    "example": """
# ❌ 错误
global counter
counter += 1

# ✅ 正确
with lock:
    global counter
    counter += 1
"""
                })
        
        # 模式2：Check-Then-Act模式
        if re.search(r'if.*exists.*:\s*.*create', code, re.DOTALL):
            issues.append({
                "type": "race_condition",
                "problem": "Check-Then-Act模式存在竞态",
                "suggestion": "使用原子操作",
                "example": """
# ❌ 错误
if not file.exists():
    file.create()  # 可能已被其他线程创建

# ✅ 正确
try:
    file.create(exclusive=True)  # 原子操作
except FileExistsError:
    pass
"""
            })
        
        return issues
    
    def detect_deadlock(self, code):
        """检测死锁风险"""
        issues = []
        
        # 检测：多个锁的获取顺序不一致
        lock_acquires = re.findall(r'(\w+)\.acquire\(\)', code)
        if len(set(lock_acquires)) > 1:
            issues.append({
                "type": "deadlock",
                "problem": "多个锁可能导致死锁",
                "suggestion": "始终以相同顺序获取锁",
                "example": """
# ❌ 错误
# 线程1: lock_a.acquire(); lock_b.acquire()
# 线程2: lock_b.acquire(); lock_a.acquire()  # 死锁！

# ✅ 正确
# 所有线程都按 a→b 顺序获取
"""
            })
        
        return issues

# Q42: 内存泄漏检测
class MemoryLeakDetector:
    """检测Python/JS内存泄漏"""
    
    def detect_python_leaks(self, code):
        """Python内存泄漏"""
        issues = []
        
        # 模式1：循环引用
        if "self." in code and "lambda" in code:
            issues.append({
                "type": "circular_reference",
                "problem": "lambda捕获self可能导致循环引用",
                "suggestion": "使用弱引用",
                "example": """
# ❌ 错误
self.callback = lambda: self.method()  # 循环引用

# ✅ 正确
import weakref
weak_self = weakref.ref(self)
self.callback = lambda: weak_self().method()
"""
            })
        
        # 模式2：全局缓存无限增长
        if "cache = {}" in code and "cache[" in code:
            if "del cache" not in code and "cache.clear" not in code:
                issues.append({
                    "type": "unbounded_cache",
                    "problem": "全局缓存无限增长",
                    "suggestion": "使用LRU缓存",
                    "example": """
# ❌ 错误
cache = {}
cache[key] = value  # 永不清理

# ✅ 正确
from functools import lru_cache
@lru_cache(maxsize=128)
def get_data(key): ...
"""
                })
        
        return issues
    
    def detect_js_leaks(self, code):
        """JavaScript内存泄漏"""
        issues = []
        
        # 模式：事件监听未解绑
        if "addEventListener" in code:
            if "removeEventListener" not in code:
                issues.append({
                    "type": "event_listener_leak",
                    "problem": "事件监听器未移除",
                    "suggestion": "组件销毁时移除监听",
                    "example": """
// ❌ 错误
element.addEventListener('click', handler);

// ✅ 正确
componentWillUnmount() {
    element.removeEventListener('click', handler);
}
"""
                })
        
        return issues

# Q43: SQL注入/XSS防护
class SecurityVulnerabilityDetector:
    """安全漏洞检测"""
    
    def detect_sql_injection(self, code):
        """SQL注入检测"""
        issues = []
        
        # 模式：字符串拼接SQL
        if re.search(r'(execute|query|sql)\s*\(\s*["\'].*%s.*["\'].*%', code):
            issues.append({
                "type": "sql_injection",
                "severity": "critical",
                "problem": "SQL语句使用字符串拼接",
                "suggestion": "使用参数化查询",
                "example": """
# ❌ 错误 - SQL注入风险
sql = "SELECT * FROM users WHERE name='%s'" % user_input
cursor.execute(sql)

# ✅ 正确 - 参数化查询
sql = "SELECT * FROM users WHERE name=?"
cursor.execute(sql, (user_input,))
"""
            })
        
        return issues
    
    def detect_xss(self, code):
        """XSS检测"""
        issues = []
        
        # 模式：直接插入HTML
        if re.search(r'innerHTML\s*=.*\+', code):
            issues.append({
                "type": "xss",
                "severity": "critical",
                "problem": "未转义的用户输入插入HTML",
                "suggestion": "使用textContent或DOMPurify",
                "example": """
// ❌ 错误 - XSS风险
element.innerHTML = userInput;

// ✅ 正确
element.textContent = userInput;
// 或使用DOMPurify.sanitize(userInput)
"""
            })
        
        return issues

# Q44: 可测试性评估
class TestabilityAnalyzer:
    """代码可测试性分析"""
    
    def analyze(self, code):
        """分析可测试性"""
        score = 100
        issues = []
        
        # 检查1：直接依赖具体类（非接口）
        if "import " in code:
            # 简化检查：是否有依赖注入
            if "__init__" in code and "self." in code:
                if "=" not in code.split("__init__")[1].split(":")[0]:
                    issues.append({
                        "problem": "构造函数缺少依赖注入",
                        "suggestion": "通过构造函数注入依赖",
                        "example": """
# ❌ 难测试
class UserService:
    def __init__(self):
        self.db = Database()  # 硬编码依赖

# ✅ 易测试
class UserService:
    def __init__(self, db):
        self.db = db  # 依赖注入，可Mock
"""
                    })
                    score -= 20
        
        # 检查2：静态方法/全局函数
        if "datetime.now()" in code or "random." in code:
            issues.append({
                "problem": "直接调用datetime.now()难以测试",
                "suggestion": "注入时间provider",
                "example": """
# ❌ 难测试
def process():
    now = datetime.now()  # 无法控制时间

# ✅ 易测试
def process(time_provider=datetime.now):
    now = time_provider()  # 可Mock
"""
            })
            score -= 15
        
        # 检查3：副作用太多
        if "print(" in code or "open(" in code:
            issues.append({
                "problem": "函数有副作用（IO操作）",
                "suggestion": "分离纯函数和副作用",
                "example": """
# ❌ 难测试
def process(data):
    result = calculate(data)
    print(result)  # 副作用
    return result

# ✅ 易测试
def calculate(data):  # 纯函数
    return result
"""
            })
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "testability": "高" if score > 80 else "中" if score > 60 else "低"
        }

# 使用示例
if __name__ == "__main__":
    # 并发检测
    concurrency = ConcurrencyDetector()
    code = """
global counter
counter += 1
"""
    print("🔍 并发问题:", concurrency.detect_race_condition(code))
    
    # 内存泄漏检测
    memory = MemoryLeakDetector()
    print("🔍 内存泄漏:", memory.detect_python_leaks("cache = {}; cache[key] = value"))
    
    # 安全漏洞
    security = SecurityVulnerabilityDetector()
    print("🔍 SQL注入:", security.detect_sql_injection("execute('SELECT * FROM users WHERE id=%s' % user_id)"))
    
    # 可测试性
    testability = TestabilityAnalyzer()
    print("🔍 可测试性:", testability.analyze("def f(): return datetime.now()"))

