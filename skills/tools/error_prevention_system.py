"""
小柳技能升级：错误预防系统
解决产品经理问题2：避免重复犯错
"""

class ErrorPreventionSystem:
    """错误预防系统 - 从错误中学习"""
    
    def __init__(self):
        self.error_database = []
        self.prevention_rules = []
        self.auto_checks = []
    
    def learn_from_error(self, error_info):
        """
        从错误中学习
        记录错误 → 分析原因 → 生成预防规则
        """
        # 记录错误
        error_record = {
            "timestamp": "2025-10-03",
            "error_type": error_info["type"],
            "description": error_info["description"],
            "root_cause": self._analyze_root_cause(error_info),
            "context": error_info.get("context", {}),
            "severity": error_info.get("severity", "Medium")
        }
        
        self.error_database.append(error_record)
        
        # 生成预防规则
        prevention_rule = self._generate_prevention_rule(error_record)
        self.prevention_rules.append(prevention_rule)
        
        # 创建自动检查
        auto_check = self._create_auto_check(error_record)
        self.auto_checks.append(auto_check)
        
        return {
            "learned": True,
            "prevention_rule": prevention_rule,
            "auto_check": auto_check
        }
    
    def check_before_action(self, action_type, context):
        """
        执行动作前的检查
        根据历史错误，检查是否可能重复犯错
        """
        warnings = []
        
        for check in self.auto_checks:
            if check["trigger"] == action_type:
                result = check["check_function"](context)
                if not result["passed"]:
                    warnings.append({
                        "message": result["warning"],
                        "severity": check["severity"],
                        "suggestion": check["suggestion"]
                    })
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }
    
    def _analyze_root_cause(self, error_info):
        """分析错误根本原因"""
        # 常见错误模式匹配
        common_causes = {
            "duplicate_code": "未搜索现有代码",
            "missing_test": "跳过测试步骤",
            "missing_docs": "忘记更新文档",
            "breaking_change": "未检查影响范围",
            "edge_case": "未考虑边界情况"
        }
        
        error_type = error_info["type"]
        return common_causes.get(error_type, "需要深入分析")
    
    def _generate_prevention_rule(self, error_record):
        """根据错误生成预防规则"""
        error_type = error_record["error_type"]
        
        prevention_rules_map = {
            "duplicate_code": {
                "rule": "写代码前必须执行 codebase_search",
                "check": "是否搜索了相似功能",
                "action": "如果找到相似代码，复用并增强"
            },
            "missing_test": {
                "rule": "代码完成后必须写测试",
                "check": "测试覆盖率是否达标",
                "action": "至少编写单元测试和集成测试"
            },
            "missing_docs": {
                "rule": "代码修改必须更新文档",
                "check": "相关文档是否已更新",
                "action": "更新README、API文档、注释"
            },
            "breaking_change": {
                "rule": "修改公共API前必须影响分析",
                "check": "是否分析了调用方",
                "action": "提供兼容层或迁移指南"
            },
            "edge_case": {
                "rule": "实现功能前列出边界情况",
                "check": "是否考虑了null、空数组、极值",
                "action": "为每个边界情况写测试"
            }
        }
        
        return prevention_rules_map.get(error_type, {
            "rule": f"避免{error_type}",
            "check": "通用检查",
            "action": "谨慎处理"
        })
    
    def _create_auto_check(self, error_record):
        """创建自动检查"""
        error_type = error_record["error_type"]
        
        return {
            "name": f"prevent_{error_type}",
            "trigger": self._get_trigger_action(error_type),
            "severity": error_record["severity"],
            "check_function": lambda ctx: self._check_function(error_type, ctx),
            "suggestion": f"参考历史错误 {error_record['timestamp']}"
        }
    
    def _get_trigger_action(self, error_type):
        """获取触发动作"""
        triggers = {
            "duplicate_code": "write_code",
            "missing_test": "complete_feature",
            "missing_docs": "modify_code",
            "breaking_change": "change_api",
            "edge_case": "implement_logic"
        }
        return triggers.get(error_type, "any_action")
    
    def _check_function(self, error_type, context):
        """执行检查"""
        # 这里实现具体检查逻辑
        return {
            "passed": True,
            "warning": ""
        }
    
    def get_prevention_checklist(self, task_type):
        """获取任务类型的预防检查清单"""
        checklist = []
        
        for rule in self.prevention_rules:
            checklist.append({
                "check": rule["check"],
                "action": rule["action"],
                "must_pass": True
            })
        
        return checklist


class CommonMistakePreventer:
    """Claude常见错误预防器"""
    
    COMMON_MISTAKES = {
        "写重复代码": {
            "prevention": "开发前强制执行 codebase_search",
            "check": "搜索关键词，检查是否有相似功能",
            "auto_fix": "如果找到，询问用户是否复用"
        },
        "忘记更新文档": {
            "prevention": "代码变更后自动检查文档",
            "check": "README、API文档是否需要更新",
            "auto_fix": "自动生成文档diff"
        },
        "跳过测试": {
            "prevention": "Feature完成后强制要求测试",
            "check": "是否编写了测试代码",
            "auto_fix": "生成测试模板"
        },
        "不处理边界情况": {
            "prevention": "实现前列出所有边界情况",
            "check": "null、空、极值是否处理",
            "auto_fix": "生成边界测试用例"
        },
        "引入breaking change": {
            "prevention": "修改API前影响分析",
            "check": "是否有调用方会受影响",
            "auto_fix": "提供废弃警告和迁移指南"
        }
    }
    
    @classmethod
    def get_prevention_for(cls, mistake_type):
        """获取特定错误的预防措施"""
        return cls.COMMON_MISTAKES.get(mistake_type, {})
    
    @classmethod
    def all_preventions(cls):
        """获取所有预防措施"""
        return cls.COMMON_MISTAKES


# 使用示例
if __name__ == "__main__":
    eps = ErrorPreventionSystem()
    
    # 记录一个错误
    error = {
        "type": "duplicate_code",
        "description": "创建了重复的登录功能",
        "context": {"module": "auth"},
        "severity": "High"
    }
    
    result = eps.learn_from_error(error)
    print("学习结果:", result)
    
    # 下次写代码前检查
    check_result = eps.check_before_action("write_code", {
        "feature": "user_registration"
    })
    
    if not check_result["safe"]:
        print("⚠️ 警告:", check_result["warnings"])

