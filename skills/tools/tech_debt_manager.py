"""
小柳升级：技术债务管理系统
解决问题38：识别、量化、优先级排序技术债务
"""
import ast
import json
from datetime import datetime, timedelta

class TechDebtManager:
    """技术债务管理器"""
    
    DEBT_TYPES = {
        "code_smell": {"weight": 0.3, "interest_rate": 0.05},      # 代码坏味道
        "outdated_dependency": {"weight": 0.4, "interest_rate": 0.1},  # 过时依赖
        "missing_test": {"weight": 0.2, "interest_rate": 0.08},    # 缺少测试
        "hard_coded": {"weight": 0.3, "interest_rate": 0.06},      # 硬编码
        "duplicate_code": {"weight": 0.25, "interest_rate": 0.07}, # 重复代码
        "poor_naming": {"weight": 0.15, "interest_rate": 0.04},    # 命名不佳
        "no_documentation": {"weight": 0.2, "interest_rate": 0.05} # 缺少文档
    }
    
    def __init__(self):
        self.debt_inventory = []
    
    def scan_project(self, project_path):
        """扫描项目，识别技术债务"""
        debts = []
        
        # 扫描代码文件
        debts.extend(self._scan_code_smells(project_path))
        debts.extend(self._scan_dependencies(project_path))
        debts.extend(self._scan_test_coverage(project_path))
        
        self.debt_inventory = debts
        return debts
    
    def _scan_code_smells(self, path):
        """扫描代码坏味道"""
        debts = []
        # 示例：长函数
        debts.append({
            "type": "code_smell",
            "subtype": "long_function",
            "location": "user_service.py:create_user()",
            "severity": "medium",
            "description": "函数过长（120行），难以维护",
            "principal": 8,  # 修复成本（人时）
            "discovered_date": datetime.now().isoformat(),
            "impact_areas": ["可维护性", "可读性"]
        })
        return debts
    
    def _scan_dependencies(self, path):
        """扫描过时依赖"""
        debts = []
        debts.append({
            "type": "outdated_dependency",
            "subtype": "security_risk",
            "location": "requirements.txt:django==3.1.0",
            "severity": "high",
            "description": "Django版本过旧，存在安全漏洞",
            "principal": 4,  # 升级成本
            "discovered_date": datetime.now().isoformat(),
            "impact_areas": ["安全性", "性能"]
        })
        return debts
    
    def _scan_test_coverage(self, path):
        """扫描测试覆盖率"""
        debts = []
        debts.append({
            "type": "missing_test",
            "subtype": "no_unit_test",
            "location": "payment_service.py",
            "severity": "high",
            "description": "支付模块缺少单元测试（覆盖率0%）",
            "principal": 12,  # 补充测试成本
            "discovered_date": datetime.now().isoformat(),
            "impact_areas": ["可靠性", "可维护性"]
        })
        return debts
    
    def quantify_debt(self, debt):
        """量化技术债务"""
        # 债务本金（修复成本）
        principal = debt["principal"]
        
        # 利息率（拖延成本）
        interest_rate = self.DEBT_TYPES[debt["type"]]["interest_rate"]
        
        # 债务年龄（天）
        discovered = datetime.fromisoformat(debt["discovered_date"])
        age_days = (datetime.now() - discovered).days
        
        # 累积利息 = 本金 × 利息率 × (年龄/30)
        accumulated_interest = principal * interest_rate * (age_days / 30)
        
        # 总债务 = 本金 + 累积利息
        total_debt = principal + accumulated_interest
        
        return {
            "principal": principal,
            "interest_rate": interest_rate,
            "age_days": age_days,
            "accumulated_interest": round(accumulated_interest, 2),
            "total_debt": round(total_debt, 2),
            "monthly_interest": round(principal * interest_rate, 2)
        }
    
    def prioritize_debts(self):
        """优先级排序"""
        prioritized = []
        
        for debt in self.debt_inventory:
            metrics = self.quantify_debt(debt)
            
            # 计算优先级分数
            priority_score = self._calculate_priority_score(debt, metrics)
            
            prioritized.append({
                **debt,
                "metrics": metrics,
                "priority_score": priority_score
            })
        
        # 按优先级降序排序
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return prioritized
    
    def _calculate_priority_score(self, debt, metrics):
        """计算优先级分数 (0-100)"""
        # 因素1：严重程度 (0-40分)
        severity_scores = {"low": 10, "medium": 25, "high": 40}
        severity_score = severity_scores[debt["severity"]]
        
        # 因素2：累积利息比例 (0-30分)
        interest_ratio = metrics["accumulated_interest"] / metrics["principal"]
        interest_score = min(30, interest_ratio * 100)
        
        # 因素3：影响范围 (0-30分)
        impact_score = len(debt["impact_areas"]) * 10
        
        total = severity_score + interest_score + impact_score
        return min(100, round(total, 1))
    
    def should_payoff_now(self, debt):
        """决策：是否现在偿还"""
        metrics = self.quantify_debt(debt)
        
        # 规则1：月利息超过2人时 → 立即偿还
        if metrics["monthly_interest"] > 2:
            return {
                "decision": "立即偿还",
                "reason": f"月利息{metrics['monthly_interest']}人时过高"
            }
        
        # 规则2：高严重度 + 债务超过本金2倍 → 立即偿还
        if debt["severity"] == "high" and metrics["total_debt"] > metrics["principal"] * 2:
            return {
                "decision": "立即偿还",
                "reason": "高严重度且债务翻倍"
            }
        
        # 规则3：影响安全性 → 立即偿还
        if "安全性" in debt["impact_areas"]:
            return {
                "decision": "立即偿还",
                "reason": "影响安全性"
            }
        
        # 规则4：总债务 < 5人时 → 可延后
        if metrics["total_debt"] < 5:
            return {
                "decision": "可延后",
                "reason": f"总债务{metrics['total_debt']}人时较低"
            }
        
        return {
            "decision": "计划偿还",
            "reason": "纳入下个迭代"
        }
    
    def generate_payoff_plan(self):
        """生成偿还计划"""
        prioritized = self.prioritize_debts()
        
        plan = {
            "immediate": [],  # 立即偿还
            "this_sprint": [],  # 本迭代
            "next_sprint": [],  # 下迭代
            "backlog": []  # 积压
        }
        
        for debt in prioritized:
            decision = self.should_payoff_now(debt)
            
            if decision["decision"] == "立即偿还":
                plan["immediate"].append(debt)
            elif debt["priority_score"] > 70:
                plan["this_sprint"].append(debt)
            elif debt["priority_score"] > 40:
                plan["next_sprint"].append(debt)
            else:
                plan["backlog"].append(debt)
        
        return plan
    
    def generate_report(self):
        """生成技术债务报告"""
        prioritized = self.prioritize_debts()
        plan = self.generate_payoff_plan()
        
        # 总债务
        total_principal = sum(d["metrics"]["principal"] for d in prioritized)
        total_interest = sum(d["metrics"]["accumulated_interest"] for d in prioritized)
        total_debt = sum(d["metrics"]["total_debt"] for d in prioritized)
        
        return {
            "summary": {
                "total_items": len(prioritized),
                "total_principal": round(total_principal, 2),
                "total_interest": round(total_interest, 2),
                "total_debt": round(total_debt, 2),
                "debt_ratio": round(total_interest / total_principal * 100, 1) if total_principal > 0 else 0
            },
            "by_severity": {
                "high": len([d for d in prioritized if d["severity"] == "high"]),
                "medium": len([d for d in prioritized if d["severity"] == "medium"]),
                "low": len([d for d in prioritized if d["severity"] == "low"])
            },
            "payoff_plan": plan,
            "top_5_debts": prioritized[:5]
        }

# 使用示例
if __name__ == "__main__":
    manager = TechDebtManager()
    
    # 扫描项目
    debts = manager.scan_project("/path/to/project")
    
    # 生成报告
    report = manager.generate_report()
    
    print("📊 技术债务报告")
    print(f"  债务总数: {report['summary']['total_items']}")
    print(f"  本金: {report['summary']['total_principal']} 人时")
    print(f"  利息: {report['summary']['total_interest']} 人时")
    print(f"  总债务: {report['summary']['total_debt']} 人时")
    print(f"  债务率: {report['summary']['debt_ratio']}%")
    
    print("\n🔥 偿还计划:")
    print(f"  立即偿还: {len(report['payoff_plan']['immediate'])} 项")
    print(f"  本迭代: {len(report['payoff_plan']['this_sprint'])} 项")

