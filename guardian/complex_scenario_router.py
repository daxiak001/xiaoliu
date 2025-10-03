#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂场景智能路由器 v1.0
创建时间: 2025-10-03
部署位置: /home/ubuntu/xiaoliu/guardian/complex_scenario_router.py

功能: 自动识别复杂场景，动态加载详细规则
"""

from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplexScenarioRouter:
    """复杂场景智能处理"""
    
    def __init__(self):
        self.scenario_rules = {
            # 场景1: 需求变更（开发中途）
            "requirement_change": {
                "name": "需求变更",
                "triggers": ["需求变更", "改需求", "change requirement", "修改需求", "需求调整"],
                "priority": "high",
                "workflow": [
                    "1. 中断处理器启动，暂停当前开发（小柳）",
                    "2. 小户重新确认新需求，明确新旧需求差异",
                    "3. 小平更新PRD，输出变更影响分析",
                    "4. 小柳评估技术影响和工作量",
                    "5. 继续开发或重新开发"
                ],
                "role_adjustments": {
                    "xiaohu": "必须明确说明：1) 原需求是什么 2) 新需求是什么 3) 为什么要改",
                    "xiaoping": "必须输出变更影响分析：1) 哪些设计需要调整 2) 影响范围多大",
                    "xiaoliu": "必须评估：1) 已完成代码能否复用 2) 新增工作量 3) 技术风险",
                    "xiaoguan": "延后介入，等新功能完成后再审查"
                }
            },
            
            # 场景2: 严重BUG（紧急修复）
            "critical_bug": {
                "name": "紧急BUG修复",
                "triggers": ["严重bug", "生产环境", "critical", "urgent", "紧急", "线上故障"],
                "priority": "critical",
                "workflow": [
                    "1. 小户详细描述问题现象（何时、何地、什么操作、什么表现）",
                    "2. 小柳立即定位问题根源",
                    "3. 小柳快速修复并说明修复方案",
                    "4. 小户立即验证修复效果",
                    "5. 小观事后审查（不阻塞紧急修复）"
                ],
                "role_adjustments": {
                    "xiaohu": "只描述问题现象，不猜测原因。必须说清：1) 做了什么 2) 期望结果 3) 实际结果",
                    "xiaoliu": "优先修复问题，单元测试可以后补",
                    "xiaoping": "暂时不介入，等修复完成后评估是否需要调整产品",
                    "xiaoguan": "事后介入进行复盘，不阻塞紧急修复流程"
                }
            },
            
            # 场景3: 多功能开发（并行任务）
            "parallel_features": {
                "name": "并行功能开发",
                "triggers": ["同时开发", "并行", "多个功能", "parallel", "一起做"],
                "priority": "medium",
                "workflow": [
                    "1. 小平拆分多个PRD文档，每个功能独立成文",
                    "2. 小平标注优先级（P0/P1/P2）",
                    "3. 小柳按优先级顺序逐个实现",
                    "4. 小户可以并行测试已完成功能",
                    "5. 小观在所有功能完成后整体审查"
                ],
                "role_adjustments": {
                    "xiaoping": "必须拆分PRD，每个功能独立文档。必须标注优先级和依赖关系",
                    "xiaoliu": "严格按优先级顺序开发，不要同时开多个功能。完成一个再做下一个",
                    "xiaohu": "可以并行测试多个功能，但每个功能独立报告",
                    "xiaoguan": "等所有功能完成后，进行整体架构审查"
                }
            },
            
            # 场景4: 技术难题（需要深度思考）
            "technical_challenge": {
                "name": "技术难题处理",
                "triggers": ["技术难点", "不知道怎么", "复杂算法", "technical challenge", "实现困难"],
                "priority": "high",
                "workflow": [
                    "1. 小柳明确说明技术难点在哪里",
                    "2. 小柳提出2-3个可能的技术方案",
                    "3. 小平从产品角度评估各方案（用户体验、性能、成本）",
                    "4. 小柳选择最优方案并说明理由",
                    "5. 小柳实现方案",
                    "6. 小观重点审查技术风险和可维护性"
                ],
                "role_adjustments": {
                    "xiaoliu": "可以主动讨论技术方案，提出多个选项让团队评估",
                    "xiaoping": "从产品角度评估（用户体验、性能、成本），不涉及技术实现细节",
                    "xiaohu": "从用户角度说明更关心哪方面（速度、稳定性、界面等）",
                    "xiaoguan": "重点审查：1) 技术风险 2) 可维护性 3) 是否过度设计"
                }
            },
            
            # 场景5: 质量争议（小观拒绝）
            "quality_dispute": {
                "name": "质量审查不通过",
                "triggers": ["质量不通过", "小观拒绝", "代码问题", "quality issue", "审查失败"],
                "priority": "high",
                "workflow": [
                    "1. 小观详细列出所有质量问题（分类：严重/一般/建议）",
                    "2. 小柳逐条回应：接受/拒绝/讨论",
                    "3. 对于有争议的点，双方说明理由",
                    "4. 小柳完成修改",
                    "5. 小观重新审查",
                    "6. 循环2-5直到通过",
                    "7. 小户最终验收"
                ],
                "role_adjustments": {
                    "xiaoguan": "必须给出具体改进建议，不能只说'不好'。问题分级：严重（必须改）、一般（建议改）、建议（可选）",
                    "xiaoliu": "必须逐条响应小观的意见。可以讨论，但严重问题必须改",
                    "xiaoping": "不介入技术质量争议，除非影响产品体验",
                    "xiaohu": "等质量审查通过后再进行验收测试"
                }
            },
            
            # 场景6: 跨模块依赖
            "cross_module_dependency": {
                "name": "跨模块依赖处理",
                "triggers": ["依赖", "依赖其他模块", "需要先完成", "dependency", "前置条件"],
                "priority": "medium",
                "workflow": [
                    "1. 小柳识别依赖关系，列出所有前置模块",
                    "2. 小平调整开发顺序或拆分任务",
                    "3. 小柳按依赖顺序开发",
                    "4. 小户分阶段测试"
                ],
                "role_adjustments": {
                    "xiaoliu": "必须明确说明：1) 依赖哪些模块 2) 为什么依赖 3) 能否解耦",
                    "xiaoping": "重新规划开发顺序，确保依赖模块先完成",
                    "xiaohu": "理解依赖关系，分阶段验收",
                    "xiaoguan": "审查依赖设计是否合理，是否存在循环依赖"
                }
            }
        }
    
    def detect_scenario(self, user_query: str, context: Dict = None) -> Dict:
        """
        检测当前场景
        
        Args:
            user_query: 用户查询
            context: 上下文信息
            
        Returns:
            场景识别结果
        """
        query_lower = user_query.lower()
        context = context or {}
        
        detected_scenarios = []
        
        for scenario_name, scenario_config in self.scenario_rules.items():
            for trigger in scenario_config["triggers"]:
                if trigger.lower() in query_lower:
                    detected_scenarios.append({
                        "scenario": scenario_name,
                        "name": scenario_config["name"],
                        "priority": scenario_config["priority"],
                        "config": scenario_config
                    })
                    break
        
        if not detected_scenarios:
            return {"detected": False, "scenario": "normal"}
        
        # 如果检测到多个场景，返回优先级最高的
        if len(detected_scenarios) > 1:
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            detected_scenarios.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        selected = detected_scenarios[0]
        
        logger.info(f"检测到复杂场景: {selected['name']} (优先级: {selected['priority']})")
        
        return {
            "detected": True,
            "scenario": selected["scenario"],
            "name": selected["name"],
            "priority": selected["priority"],
            "workflow": selected["config"]["workflow"],
            "adjustments": selected["config"]["role_adjustments"]
        }
    
    def get_enhanced_prompt(self, scenario: str) -> str:
        """
        获取场景增强提示词
        
        Args:
            scenario: 场景名称
            
        Returns:
            增强提示词
        """
        if scenario not in self.scenario_rules:
            return ""
        
        config = self.scenario_rules[scenario]
        
        prompt = f"""
## 🚨 复杂场景激活：{config['name']}

### 优先级：{config['priority'].upper()}

### 特殊工作流程
{chr(10).join(config['workflow'])}

### 角色职责调整
"""
        for role, adjustment in config['role_adjustments'].items():
            role_names = {
                "xiaohu": "小户（用户代表）",
                "xiaoping": "小平（产品经理）",
                "xiaoliu": "小柳（开发工程师）",
                "xiaoguan": "小观（质量教练）"
            }
            prompt += f"\n**{role_names.get(role, role)}**:\n{adjustment}\n"
        
        prompt += "\n⚠️ 请严格遵守以上场景特殊规则！\n"
        
        return prompt
    
    def get_all_scenarios(self) -> List[Dict]:
        """获取所有场景列表"""
        return [
            {
                "scenario": name,
                "name": config["name"],
                "priority": config["priority"],
                "triggers": config["triggers"]
            }
            for name, config in self.scenario_rules.items()
        ]

if __name__ == "__main__":
    router = ComplexScenarioRouter()
    
    print("=" * 60)
    print("四角色系统 - 复杂场景路由器测试")
    print("=" * 60)
    
    test_queries = [
        "开发到一半，需求变更了",
        "生产环境出现严重bug，用户无法登录",
        "我想同时开发登录和注册功能",
        "这个算法很复杂，不知道怎么实现",
        "小观说代码质量不通过",
        "这个功能依赖用户管理模块"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"用户查询: {query}")
        print(f"{'='*60}")
        
        result = router.detect_scenario(query, {})
        
        if result['detected']:
            print(f"✅ 检测到场景: {result['name']}")
            print(f"优先级: {result['priority']}")
            print(f"\n增强提示词:")
            print(router.get_enhanced_prompt(result['scenario']))
        else:
            print("普通场景，使用标准工作流")
    
    print(f"\n{'='*60}")
    print("所有支持的场景:")
    print(f"{'='*60}")
    for scenario in router.get_all_scenarios():
        print(f"- {scenario['name']} (优先级: {scenario['priority']})")
        print(f"  触发词: {', '.join(scenario['triggers'][:3])}")

