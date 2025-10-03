"""
小柳升级：错误学习系统
解决问题8：从错误中学习，避免重复犯错
"""

import json
from datetime import datetime
from pathlib import Path

class ErrorLearningSystem:
    """错误学习系统 - 记住每一个错误，永不重犯"""
    
    def __init__(self):
        self.error_database_path = Path("D:/xiaoliu_skills/error_database.json")
        self.error_database = self.load_error_database()
        self.prevention_rules = []
    
    def record_error(self, error_info):
        """
        记录错误
        包括：错误类型、原因、解决方案、预防措施
        """
        error_record = {
            "id": len(self.error_database) + 1,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_info["type"],
            "description": error_info["description"],
            "root_cause": error_info.get("root_cause", ""),
            "solution": error_info.get("solution", ""),
            "prevention": self._generate_prevention(error_info),
            "context": error_info.get("context", {}),
            "severity": error_info.get("severity", "Medium"),
            "learned": True
        }
        
        # 添加到数据库
        self.error_database.append(error_record)
        
        # 生成预防规则
        prevention_rule = self._create_prevention_rule(error_record)
        self.prevention_rules.append(prevention_rule)
        
        # 保存
        self.save_error_database()
        
        return {
            "recorded": True,
            "error_id": error_record["id"],
            "prevention_rule": prevention_rule
        }
    
    def check_before_action(self, action_type, context):
        """
        执行动作前检查是否可能重复历史错误
        """
        warnings = []
        
        # 查找相关错误
        related_errors = [
            err for err in self.error_database
            if self._is_related(err, action_type, context)
        ]
        
        for error in related_errors:
            warnings.append({
                "warning": f"警告：之前犯过类似错误 (#{error['id']})",
                "error_description": error["description"],
                "prevention": error["prevention"],
                "severity": error["severity"]
            })
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": [err["prevention"] for err in related_errors]
        }
    
    def _generate_prevention(self, error_info):
        """根据错误生成预防措施"""
        prevention_map = {
            "file_not_found": "执行前检查文件是否存在",
            "duplicate_code": "写代码前先搜索codebase",
            "missing_import": "修改代码后检查import语句",
            "path_error": "使用Path对象而不是字符串拼接",
            "regex_error": "正则表达式特殊字符记得转义",
            "null_reference": "访问对象前检查是否为null/None",
            "index_out_of_range": "访问数组前检查长度",
            "unclosed_resource": "使用with语句自动关闭资源"
        }
        
        error_type = error_info["type"]
        return prevention_map.get(error_type, "具体分析错误原因并预防")
    
    def _create_prevention_rule(self, error_record):
        """创建预防规则"""
        return {
            "rule_id": f"prevent_{error_record['id']}",
            "trigger": error_record["error_type"],
            "check": error_record["prevention"],
            "auto_remind": True
        }
    
    def _is_related(self, error, action_type, context):
        """判断错误是否与当前动作相关"""
        # 简化版：关键词匹配
        action_keywords = action_type.lower().split()
        error_keywords = error["error_type"].lower().split()
        
        overlap = len(set(action_keywords) & set(error_keywords))
        return overlap > 0
    
    def get_error_statistics(self):
        """获取错误统计"""
        total = len(self.error_database)
        
        by_type = {}
        for error in self.error_database:
            error_type = error["error_type"]
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            "total_errors": total,
            "by_type": by_type,
            "most_common": max(by_type.items(), key=lambda x: x[1]) if by_type else None,
            "prevention_rules": len(self.prevention_rules)
        }
    
    def load_error_database(self):
        """加载错误数据库"""
        if self.error_database_path.exists():
            return json.loads(self.error_database_path.read_text())
        return []
    
    def save_error_database(self):
        """保存错误数据库"""
        self.error_database_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_database_path.write_text(
            json.dumps(self.error_database, indent=2, ensure_ascii=False)
        )


class CommonErrorsPrevention:
    """Claude-4常见错误预防"""
    
    COMMON_ERRORS = {
        "1": {
            "error": "忘记检查文件是否存在就读取",
            "example": "open('file.txt') without checking",
            "prevention": "使用 if Path('file.txt').exists() 先检查",
            "code_template": """
from pathlib import Path

file_path = Path('file.txt')
if not file_path.exists():
    print(f"文件不存在: {file_path}")
    return

content = file_path.read_text()
            """
        },
        "2": {
            "error": "写了重复代码",
            "example": "创建了已存在的登录功能",
            "prevention": "开发前强制执行 codebase_search",
            "code_template": """
# 步骤1: 先搜索
search_results = codebase_search("登录功能")

# 步骤2: 如果找到，复用
if search_results:
    print("发现现有代码，复用...")
else:
    print("没有找到，开始开发...")
            """
        },
        "3": {
            "error": "修改代码后忘记更新import",
            "example": "移动了函数位置但import还是旧的",
            "prevention": "修改后运行linter检查",
            "code_template": """
# 修改代码后自动检查
run_linter()  # 会检测未使用的import和缺失的import
            """
        },
        "4": {
            "error": "路径拼接错误",
            "example": "'path/' + 'file.txt' 在Windows上失败",
            "prevention": "使用 Path 对象",
            "code_template": """
from pathlib import Path

# ❌ 错误
path = 'folder/' + 'file.txt'

# ✅ 正确
path = Path('folder') / 'file.txt'
            """
        },
        "5": {
            "error": "正则表达式没转义特殊字符",
            "example": "re.search('.', text) 匹配任意字符而不是点号",
            "prevention": "特殊字符使用 re.escape() 或手动转义",
            "code_template": """
import re

# ❌ 错误
pattern = '.'  # 匹配任意字符

# ✅ 正确
pattern = r'\\.'  # 匹配点号
# 或
pattern = re.escape('.')
            """
        }
    }
    
    @classmethod
    def get_prevention(cls, error_id):
        """获取特定错误的预防措施"""
        return cls.COMMON_ERRORS.get(error_id, {})
    
    @classmethod
    def all_preventions(cls):
        """获取所有预防措施"""
        return cls.COMMON_ERRORS


# 使用示例
if __name__ == "__main__":
    els = ErrorLearningSystem()
    
    # 记录一个错误
    els.record_error({
        "type": "file_not_found",
        "description": "尝试读取不存在的config.json",
        "root_cause": "没有检查文件是否存在",
        "solution": "添加了exists()检查",
        "context": {"file": "config.json"},
        "severity": "Medium"
    })
    
    # 下次执行前检查
    check = els.check_before_action("read_file", {"file": "data.json"})
    
    if not check["safe"]:
        print("⚠️ 警告：")
        for warning in check["warnings"]:
            print(f"  - {warning['warning']}")
            print(f"    预防: {warning['prevention']}")
    
    # 统计
    stats = els.get_error_statistics()
    print(f"\n错误统计: {stats}")

