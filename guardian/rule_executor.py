#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端规则执行引擎 v1.0
创建时间: 2025-10-03
部署位置: /home/ubuntu/xiaoliu/guardian/rule_executor.py

功能: 整合边界检测和场景路由，提供统一API
"""

import sys
import os

# 添加guardian目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from role_boundary_detector import RoleBoundaryDetector
from complex_scenario_router import ComplexScenarioRouter
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudRuleExecutor:
    """云端规则执行引擎"""
    
    def __init__(self):
        self.boundary_detector = RoleBoundaryDetector()
        self.scenario_router = ComplexScenarioRouter()
        self.context = {
            "received_prd": False,
            "xiaohu_tested": False,
            "xiaoguan_reviewed": False,
            "current_stage": "requirements",
            "current_scenario": "normal"
        }
        logger.info("✅ 云端规则执行引擎已初始化")
    
    def validate_response(self, role: str, response: str) -> Dict:
        """
        验证角色回复是否符合规则
        
        Args:
            role: 角色名称（xiaohu/xiaoping/xiaoliu/xiaoguan）
            response: 角色的回复内容
            
        Returns:
            验证结果和纠正建议
        """
        logger.info(f"正在验证角色回复: {role}")
        
        if role == "xiaohu":
            result = self.boundary_detector.check_xiaohu(response)
        elif role == "xiaoping":
            result = self.boundary_detector.check_xiaoping(response)
            if result["valid"]:
                self.context["received_prd"] = True
                logger.info("✅ 小平已输出PRD")
        elif role == "xiaoliu":
            result = self.boundary_detector.check_xiaoliu_team_mode(response, self.context)
        elif role == "xiaoguan":
            result = self.boundary_detector.check_xiaoguan(response)
            if result["valid"]:
                self.context["xiaoguan_reviewed"] = True
                logger.info("✅ 小观已完成审查")
        else:
            logger.error(f"未知角色: {role}")
            return {"valid": False, "error": f"Unknown role: {role}"}
        
        if not result["valid"]:
            logger.warning(f"⚠️ 角色越界检测: {role} - {result.get('violations')}")
        
        return result
    
    def process_user_query(self, user_query: str) -> Dict:
        """
        处理用户查询，返回场景和增强规则
        
        Args:
            user_query: 用户输入
            
        Returns:
            场景信息和增强提示词
        """
        logger.info(f"处理用户查询: {user_query[:50]}...")
        
        scenario_result = self.scenario_router.detect_scenario(user_query, self.context)
        
        if scenario_result["detected"]:
            enhanced_prompt = self.scenario_router.get_enhanced_prompt(scenario_result["scenario"])
            self.context["current_scenario"] = scenario_result["scenario"]
            
            logger.info(f"🚨 检测到复杂场景: {scenario_result['name']}")
            
            return {
                "complex_scenario": True,
                "scenario": scenario_result["scenario"],
                "scenario_name": scenario_result["name"],
                "priority": scenario_result["priority"],
                "workflow": scenario_result["workflow"],
                "role_adjustments": scenario_result["adjustments"],
                "enhanced_prompt": enhanced_prompt
            }
        
        logger.info("普通场景，使用标准工作流")
        return {"complex_scenario": False, "scenario": "normal"}
    
    def auto_correct(self, role: str, invalid_response: str, validation_result: Dict) -> str:
        """
        自动纠正违规回复
        
        Args:
            role: 角色名称
            invalid_response: 违规回复
            validation_result: 验证结果
            
        Returns:
            纠正后的回复
        """
        role_names = {
            "xiaohu": "小户（用户代表）",
            "xiaoping": "小平（产品经理）",
            "xiaoliu": "小柳（开发工程师）",
            "xiaoguan": "小观（质量教练）"
        }
        
        role_display = role_names.get(role, role)
        
        if "correction" in validation_result:
            corrected_response = f"""
🚨 云端守护系统 - 角色越界拦截

**角色：** {role_display}
**检测到越界行为：**
{chr(10).join(f"  - {v}" for v in validation_result['violations'])}

**自动纠正：**
{validation_result['correction']}

**提醒：** {validation_result.get('warning', '请遵守角色边界规则')}
"""
            logger.info(f"✅ 已自动纠正 {role} 的越界回复")
            return corrected_response
        
        return invalid_response
    
    def update_context(self, stage: str = None, **kwargs):
        """
        更新上下文状态
        
        Args:
            stage: 工作流阶段
            **kwargs: 其他上下文参数
        """
        if stage:
            self.context["current_stage"] = stage
            logger.info(f"工作流阶段切换: {stage}")
        
        self.context.update(kwargs)
    
    def get_context(self) -> Dict:
        """获取当前上下文"""
        return self.context.copy()
    
    def reset_context(self):
        """重置上下文"""
        self.context = {
            "received_prd": False,
            "xiaohu_tested": False,
            "xiaoguan_reviewed": False,
            "current_stage": "requirements",
            "current_scenario": "normal"
        }
        logger.info("上下文已重置")
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "engine": "CloudRuleExecutor v1.0",
            "status": "active",
            "context": self.context,
            "supported_scenarios": self.scenario_router.get_all_scenarios()
        }

if __name__ == "__main__":
    print("=" * 60)
    print("云端规则执行引擎 - 完整测试")
    print("=" * 60)
    
    executor = CloudRuleExecutor()
    
    # 测试1: 复杂场景识别
    print("\n" + "=" * 60)
    print("测试1: 复杂场景识别")
    print("=" * 60)
    
    user_query = "开发到一半，产品说需求要改"
    scenario = executor.process_user_query(user_query)
    
    if scenario["complex_scenario"]:
        print(f"✅ 检测到复杂场景: {scenario['scenario_name']}")
        print(f"优先级: {scenario['priority']}")
        print(f"\n工作流程:")
        for step in scenario['workflow']:
            print(f"  {step}")
        print(f"\n增强提示词:")
        print(scenario['enhanced_prompt'])
    
    # 测试2: 角色越界检测
    print("\n" + "=" * 60)
    print("测试2: 角色越界检测与自动纠正")
    print("=" * 60)
    
    test_cases = [
        ("xiaohu", "这个功能不错，但API设计有问题，建议用RESTful"),
        ("xiaoping", "根据需求，代码应该这样写：\n```python\ndef test():\n    pass\n```"),
        ("xiaoguan", "代码质量不好，我来帮你重写：\ndef better():\n    return True"),
        ("xiaoliu", "我分析了用户需求后，直接交付给用户了")
    ]
    
    for role, response in test_cases:
        print(f"\n--- 测试角色: {role} ---")
        result = executor.validate_response(role, response)
        
        if result["valid"]:
            print(f"✅ {role} 回复符合规则")
        else:
            print(f"❌ {role} 回复越界")
            corrected = executor.auto_correct(role, response, result)
            print(corrected)
    
    # 测试3: 上下文管理
    print("\n" + "=" * 60)
    print("测试3: 上下文管理")
    print("=" * 60)
    
    print("初始上下文:", executor.get_context())
    
    executor.update_context(stage="development", received_prd=True)
    print("更新后上下文:", executor.get_context())
    
    executor.reset_context()
    print("重置后上下文:", executor.get_context())
    
    # 测试4: 系统状态
    print("\n" + "=" * 60)
    print("测试4: 系统状态")
    print("=" * 60)
    
    status = executor.get_system_status()
    print(f"引擎: {status['engine']}")
    print(f"状态: {status['status']}")
    print(f"支持的场景数: {len(status['supported_scenarios'])}")
    print("支持的场景:")
    for s in status['supported_scenarios']:
        print(f"  - {s['name']} ({s['priority']})")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

