"""
小柳升级：逻辑一致性引擎
解决问题6：逻辑推理的一致性
"""

from datetime import datetime

class LogicConsistencyEngine:
    """逻辑一致性引擎 - 确保决策前后一致"""
    
    def __init__(self):
        self.belief_system = {}      # 核心信念
        self.decision_history = []   # 决策历史
        self.principles = []         # 不可变原则
    
    def establish_principle(self, principle_name, rule):
        """
        建立核心原则（不可更改）
        """
        principle = {
            "name": principle_name,
            "rule": rule,
            "established_at": datetime.now().isoformat(),
            "immutable": True
        }
        
        self.principles.append(principle)
        
        return {
            "established": True,
            "principle": principle_name,
            "status": "IMMUTABLE"
        }
    
    def make_decision(self, question, answer, reasoning):
        """
        做决策前检查是否与历史矛盾
        """
        # 检查是否有历史决策
        conflict = self._check_conflict(question, answer)
        
        if conflict:
            return {
                "allowed": False,
                "conflict": conflict,
                "suggestion": "请review之前的决策"
            }
        
        # 记录决策
        decision = {
            "question": question,
            "answer": answer,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        self.decision_history.append(decision)
        
        return {
            "allowed": True,
            "decision_id": len(self.decision_history)
        }
    
    def _check_conflict(self, question, new_answer):
        """检查是否与历史决策冲突"""
        for past_decision in self.decision_history:
            if self._is_same_question(question, past_decision["question"]):
                if past_decision["answer"] != new_answer:
                    return {
                        "conflicting_decision": past_decision,
                        "reason": "答案不一致"
                    }
        
        return None
    
    def _is_same_question(self, q1, q2):
        """判断是否是同一个问题"""
        # 简化版：关键词匹配
        q1_keywords = set(q1.lower().split())
        q2_keywords = set(q2.lower().split())
        
        overlap = len(q1_keywords & q2_keywords)
        return overlap > len(q1_keywords) * 0.7
    
    def review_decision(self, decision_id):
        """回顾某个决策"""
        if decision_id <= len(self.decision_history):
            return self.decision_history[decision_id - 1]
        return None
    
    def get_stance_on(self, topic):
        """
        我对某个topic的立场是什么？
        确保立场一致
        """
        related_decisions = [
            d for d in self.decision_history
            if topic.lower() in d["question"].lower()
        ]
        
        if related_decisions:
            return {
                "topic": topic,
                "stance": related_decisions[-1]["answer"],
                "based_on": related_decisions[-1]["reasoning"],
                "consistent_since": related_decisions[0]["timestamp"]
            }
        
        return None


class BeliefSystem:
    """信念系统 - 核心原则不可违背"""
    
    CORE_BELIEFS = {
        "code_quality": {
            "belief": "代码质量优先于速度",
            "rules": [
                "测试覆盖率必须>80%",
                "代码必须有文档",
                "不允许重复代码"
            ],
            "never_compromise": True
        },
        "user_data": {
            "belief": "用户数据安全至上",
            "rules": [
                "敏感数据必须加密",
                "必须有备份",
                "不能明文存储密码"
            ],
            "never_compromise": True
        },
        "backward_compatibility": {
            "belief": "向后兼容很重要",
            "rules": [
                "不能随意破坏API",
                "变更要有迁移指南",
                "保持语义化版本"
            ],
            "never_compromise": False  # 可以在重大版本中妥协
        }
    }
    
    @classmethod
    def check_against_beliefs(cls, action):
        """检查行动是否违背信念"""
        violations = []
        
        for belief_name, belief_data in cls.CORE_BELIEFS.items():
            if cls._violates_belief(action, belief_data):
                violations.append({
                    "belief": belief_name,
                    "violated_rule": "...",
                    "severity": "CRITICAL" if belief_data["never_compromise"] else "HIGH"
                })
        
        return violations
    
    @classmethod
    def _violates_belief(cls, action, belief_data):
        """检查是否违背某个信念"""
        # 实际实现中会更复杂
        return False


# 使用示例
if __name__ == "__main__":
    lce = LogicConsistencyEngine()
    
    # 建立核心原则
    lce.establish_principle(
        "database_choice",
        "项目使用PostgreSQL作为主数据库"
    )
    
    # 第1次决策
    result1 = lce.make_decision(
        question="用户表需要email字段吗？",
        answer="是，必须有",
        reasoning="用于用户登录和通知"
    )
    print("第1次决策:", result1)
    
    # 第2次相同问题
    result2 = lce.make_decision(
        question="用户表应该有email字段吗？",
        answer="不一定需要",
        reasoning="可以用手机号登录"
    )
    
    if not result2["allowed"]:
        print("⚠️ 检测到矛盾!")
        print("冲突:", result2["conflict"])
    
    # 检查立场
    stance = lce.get_stance_on("email字段")
    print("我的立场:", stance)

