"""
小柳升级：执行计划器
解决问题7：执行效率问题
"""

class ExecutionPlanner:
    """执行计划器 - 先计划再执行，避免无用功"""
    
    def __init__(self):
        self.execution_templates = {}
        self.load_templates()
    
    def plan_before_execute(self, task_description):
        """
        执行前制定计划
        1. 理解任务
        2. 分解步骤
        3. 验证方向
        4. 检查资源
        5. 预估时间
        """
        plan = {
            "task": task_description,
            "steps": [],
            "validation_points": [],
            "required_resources": [],
            "estimated_time": 0,
            "risks": []
        }
        
        # 1. 分解任务
        steps = self._decompose_task(task_description)
        plan["steps"] = steps
        
        # 2. 添加验证点
        for i, step in enumerate(steps):
            if self._needs_validation(step):
                plan["validation_points"].append({
                    "after_step": i,
                    "validate": f"检查{step}是否正确"
                })
        
        # 3. 检查资源
        plan["required_resources"] = self._check_resources(task_description)
        
        # 4. 识别风险
        plan["risks"] = self._identify_risks(task_description)
        
        # 5. 预估时间
        plan["estimated_time"] = sum(step.get("time", 5) for step in steps)
        
        return plan
    
    def _decompose_task(self, task):
        """分解任务为具体步骤"""
        # 匹配任务类型
        if "添加" in task or "创建" in task:
            return self._get_template("create_feature")
        elif "修复" in task or "bug" in task:
            return self._get_template("fix_bug")
        elif "重构" in task:
            return self._get_template("refactor")
        elif "优化" in task:
            return self._get_template("optimize")
        else:
            return self._get_template("generic")
    
    def _get_template(self, template_name):
        """获取执行模板"""
        return self.execution_templates.get(template_name, [])
    
    def _needs_validation(self, step):
        """判断步骤是否需要验证"""
        validation_keywords = ["搜索", "检查", "分析", "设计"]
        return any(kw in step for kw in validation_keywords)
    
    def _check_resources(self, task):
        """检查所需资源"""
        resources = []
        
        if "数据库" in task:
            resources.append("数据库访问权限")
        if "API" in task:
            resources.append("API文档")
        if "测试" in task:
            resources.append("测试环境")
        
        return resources
    
    def _identify_risks(self, task):
        """识别风险"""
        risks = []
        
        if "重构" in task:
            risks.append({
                "risk": "可能破坏现有功能",
                "mitigation": "先写完整测试"
            })
        
        if "数据库" in task:
            risks.append({
                "risk": "可能影响生产数据",
                "mitigation": "先在测试环境验证"
            })
        
        return risks
    
    def load_templates(self):
        """加载执行模板"""
        self.execution_templates = {
            "create_feature": [
                {"step": "1. 搜索是否已有类似功能", "time": 10},
                {"step": "2. 如果有，分析复用可能性", "time": 15},
                {"step": "3. 设计方案", "time": 20},
                {"step": "4. 编写代码", "time": 60},
                {"step": "5. 编写测试", "time": 30},
                {"step": "6. 更新文档", "time": 15},
                {"step": "7. 验证功能", "time": 10}
            ],
            "fix_bug": [
                {"step": "1. 复现问题", "time": 15},
                {"step": "2. 定位根因", "time": 20},
                {"step": "3. 设计修复方案", "time": 10},
                {"step": "4. 实施修复", "time": 30},
                {"step": "5. 添加回归测试", "time": 20},
                {"step": "6. 验证修复", "time": 10}
            ],
            "refactor": [
                {"step": "1. 写完整测试（确保不破坏功能）", "time": 40},
                {"step": "2. 分析代码结构", "time": 20},
                {"step": "3. 设计新结构", "time": 30},
                {"step": "4. 逐步重构", "time": 60},
                {"step": "5. 运行测试验证", "time": 15},
                {"step": "6. 更新文档", "time": 15}
            ],
            "optimize": [
                {"step": "1. 性能基准测试（记录当前性能）", "time": 20},
                {"step": "2. 性能分析（找瓶颈）", "time": 30},
                {"step": "3. 设计优化方案", "time": 20},
                {"step": "4. 实施优化", "time": 40},
                {"step": "5. 基准测试对比", "time": 20},
                {"step": "6. 验证功能无破坏", "time": 15}
            ],
            "generic": [
                {"step": "1. 理解需求", "time": 10},
                {"step": "2. 搜索现有方案", "time": 10},
                {"step": "3. 设计方案", "time": 15},
                {"step": "4. 执行", "time": 40},
                {"step": "5. 验证", "time": 10},
                {"step": "6. 文档", "time": 10}
            ]
        }


class ExecutionChecklist:
    """执行检查清单 - 确保不遗漏"""
    
    CHECKLISTS = {
        "before_coding": [
            "☐ 是否搜索了现有代码？",
            "☐ 是否理解了需求？",
            "☐ 是否设计了方案？",
            "☐ 是否考虑了边界情况？"
        ],
        "after_coding": [
            "☐ 代码是否有测试？",
            "☐ 文档是否已更新？",
            "☐ 是否处理了异常？",
            "☐ 是否有代码注释？",
            "☐ 是否符合编码规范？"
        ],
        "before_commit": [
            "☐ 测试是否全部通过？",
            "☐ Lint检查是否通过？",
            "☐ 是否有无关文件？",
            "☐ Commit message是否清晰？"
        ]
    }
    
    @classmethod
    def get_checklist(cls, phase):
        """获取检查清单"""
        return cls.CHECKLISTS.get(phase, [])
    
    @classmethod
    def verify_completion(cls, phase, checked_items):
        """验证是否全部完成"""
        checklist = cls.get_checklist(phase)
        total = len(checklist)
        checked = len(checked_items)
        
        return {
            "complete": checked == total,
            "progress": f"{checked}/{total}",
            "missing": [
                item for item in checklist 
                if item not in checked_items
            ]
        }


# 使用示例
if __name__ == "__main__":
    planner = ExecutionPlanner()
    
    # 任务：添加用户注册功能
    plan = planner.plan_before_execute("添加用户注册功能")
    
    print("执行计划:")
    print(f"步骤数: {len(plan['steps'])}")
    print(f"预估时间: {plan['estimated_time']}分钟")
    print(f"验证点: {len(plan['validation_points'])}个")
    print(f"风险: {len(plan['risks'])}个")
    
    print("\n详细步骤:")
    for step in plan['steps']:
        print(f"  - {step['step']} ({step['time']}分钟)")
    
    # 执行前检查清单
    print("\n执行前检查清单:")
    checklist = ExecutionChecklist.get_checklist("before_coding")
    for item in checklist:
        print(f"  {item}")

