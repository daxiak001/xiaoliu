#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色边界检测器 v1.0
创建时间: 2025-10-03
部署位置: /home/ubuntu/xiaoliu/guardian/role_boundary_detector.py

功能: 实时检测每个角色的回复是否越界
"""

import re
from typing import Dict, List

class RoleBoundaryDetector:
    """角色边界实时检测"""
    
    def __init__(self):
        # 小户（用户代表）禁用词汇
        self.xiaohu_forbidden = [
            # 技术术语
            'API', 'api', 'database', 'code', 'function', 'class', 'variable',
            'algorithm', 'framework', 'library', 'import', 'debug', 'deploy',
            '数据库', '代码', '函数', '算法', '接口', '架构', '部署',
            
            # 实现细节
            'implement', 'develop', 'refactor', 'optimize', 'query',
            '实现', '开发', '重构', '优化', '查询',
            
            # 技术建议
            'should use', 'recommend using', 'better to use',
            '应该用', '建议用', '最好用', '可以用'
        ]
        
        # 小平（产品经理）禁用词汇
        self.xiaoping_forbidden = [
            # 代码相关
            'write code', 'code like this', 'function should', 'class design',
            '写代码', '代码应该', '这样写', '函数设计',
            
            # 技术指导
            'technical implementation', 'use this method', 'algorithm should',
            '技术实现', '用这个方法', '算法应该'
        ]
        
        # 小观（质量教练）禁止行为模式
        self.xiaoguan_forbidden_patterns = [
            r'def\s+\w+\s*\(',  # Python函数定义
            r'function\s+\w+\s*\(',  # JavaScript函数
            r'class\s+\w+\s*[:{]',  # 类定义
            r'```python\s+def',  # Python代码块
            r'```javascript\s+function',  # JS代码块
            r'我来帮你写',
            r'I will write',
            r'让我重写',
            r'Let me rewrite'
        ]
    
    def check_xiaohu(self, response: str) -> Dict:
        """
        检查小户是否越界
        
        Args:
            response: 小户的回复内容
            
        Returns:
            验证结果
        """
        violations = []
        
        for word in self.xiaohu_forbidden:
            if word.lower() in response.lower():
                violations.append(f"使用技术术语: '{word}'")
        
        if violations:
            return {
                "valid": False,
                "role": "xiaohu",
                "violations": violations,
                "correction": self._correct_xiaohu_response(response),
                "warning": "小户（用户代表）应该保持纯用户视角，不涉及技术细节"
            }
        
        return {"valid": True, "role": "xiaohu"}
    
    def check_xiaoping(self, response: str) -> Dict:
        """
        检查小平是否越界
        
        Args:
            response: 小平的回复内容
            
        Returns:
            验证结果
        """
        violations = []
        
        for word in self.xiaoping_forbidden:
            if word.lower() in response.lower():
                violations.append(f"涉及代码指导: '{word}'")
        
        # 检查是否包含代码块
        if '```' in response:
            code_langs = ['python', 'javascript', 'java', 'cpp', 'c++', 'go', 'rust']
            if any(f'```{lang}' in response.lower() for lang in code_langs):
                violations.append("产品经理不应该写代码，应该输出PRD文档")
        
        if violations:
            return {
                "valid": False,
                "role": "xiaoping",
                "violations": violations,
                "correction": self._correct_xiaoping_response(response),
                "warning": "小平（产品经理）应该专注于产品设计和PRD，不涉及代码实现"
            }
        
        return {"valid": True, "role": "xiaoping"}
    
    def check_xiaoguan(self, response: str) -> Dict:
        """
        检查小观是否越界
        
        Args:
            response: 小观的回复内容
            
        Returns:
            验证结果
        """
        violations = []
        
        # 检查是否写代码
        for pattern in self.xiaoguan_forbidden_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                violations.append(f"质量教练不应该写代码: 发现 '{matches[0]}'")
        
        if violations:
            return {
                "valid": False,
                "role": "xiaoguan",
                "violations": violations,
                "correction": "小观作为质量教练，应该只审查代码质量并提供改进建议，而不是替小柳写代码。请重新以审查者和导师身份回复。",
                "warning": "小观（质量教练）应该审查和指导，不应该参与实际开发"
            }
        
        return {"valid": True, "role": "xiaoguan"}
    
    def check_xiaoliu_team_mode(self, response: str, context: Dict) -> Dict:
        """
        检查团队模式下小柳是否越界
        
        Args:
            response: 小柳的回复内容
            context: 当前上下文
            
        Returns:
            验证结果
        """
        violations = []
        
        # 检查是否直接交付给用户（应该交给小户）
        if any(word in response.lower() for word in ['交付给用户', 'deliver to user', '给您使用', 'for you to use']):
            if not context.get('xiaohu_tested'):
                violations.append("团队模式下应该先交付给小户测试，不能直接交付用户")
        
        # 检查是否自己做需求分析（应该接收小平的PRD）
        if not context.get('received_prd'):
            if any(word in response.lower() for word in ['我分析了需求', 'I analyzed the requirements', '根据用户需求']):
                violations.append("团队模式下应该接收小平的PRD，不应该自己直接分析用户需求")
        
        # 检查是否自己设计产品方案
        if not context.get('received_prd'):
            if any(word in response.lower() for word in ['我设计了界面', 'I designed the UI', '用户体验设计']):
                violations.append("团队模式下产品设计由小平负责，小柳应专注技术实现")
        
        if violations:
            return {
                "valid": False,
                "role": "xiaoliu",
                "violations": violations,
                "correction": "小柳在团队模式下职责已调整：接收PRD → 技术方案 → 开发代码 → 单元测试 → 交付小户",
                "warning": "请遵守团队模式下的职责分工"
            }
        
        return {"valid": True, "role": "xiaoliu"}
    
    def _correct_xiaohu_response(self, response: str) -> str:
        """
        自动纠正小户的回复
        
        Args:
            response: 原始回复
            
        Returns:
            纠正后的回复
        """
        corrections = {
            'API': '功能接口',
            'api': '功能',
            'database': '数据存储',
            'code': '程序',
            'function': '功能',
            'algorithm': '处理方式',
            '数据库': '数据',
            '代码': '功能',
            '算法': '处理方式',
            '接口': '功能',
            '函数': '功能'
        }
        
        corrected = response
        for tech, user in corrections.items():
            corrected = re.sub(r'\b' + re.escape(tech) + r'\b', user, corrected, flags=re.IGNORECASE)
        
        prefix = "⚠️ [自动纠正] 小户应使用用户语言，已自动转换技术术语：\n\n"
        return prefix + corrected
    
    def _correct_xiaoping_response(self, response: str) -> str:
        """
        自动纠正小平的回复
        
        Args:
            response: 原始回复
            
        Returns:
            纠正后的回复
        """
        # 移除代码块
        corrected = re.sub(r'```[\s\S]*?```', '[技术实现细节由小柳负责，此处仅说明产品需求]', response)
        
        prefix = "⚠️ [自动纠正] 小平应输出PRD文档，不应包含代码实现：\n\n"
        return prefix + corrected

if __name__ == "__main__":
    # 测试代码
    detector = RoleBoundaryDetector()
    
    print("=" * 60)
    print("测试1: 小户越界检测")
    print("=" * 60)
    xiaohu_response = "这个功能很好，但是API设计有问题，建议用RESTful架构"
    result = detector.check_xiaohu(xiaohu_response)
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("测试2: 小平越界检测")
    print("=" * 60)
    xiaoping_response = """
根据需求，我设计了：
```python
def register(email, password):
    return True
```
    """
    result = detector.check_xiaoping(xiaoping_response)
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("测试3: 小观越界检测")
    print("=" * 60)
    xiaoguan_response = "代码质量不好，我来帮你重写：\ndef better_code():\n    pass"
    result = detector.check_xiaoguan(xiaoguan_response)
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("测试4: 团队模式下小柳越界检测")
    print("=" * 60)
    xiaoliu_response = "根据用户需求，我分析了以后直接交付给用户"
    context = {"received_prd": False, "xiaohu_tested": False}
    result = detector.check_xiaoliu_team_mode(xiaoliu_response, context)
    print(f"结果: {result}")

