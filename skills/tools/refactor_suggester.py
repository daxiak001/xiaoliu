"""
小柳升级：智能重构助手
解决问题20：主动建议重构
"""
import ast

class RefactorSuggester:
    def analyze_code(self, code_file):
        """分析代码，提供重构建议"""
        suggestions = []
        tree = ast.parse(open(code_file).read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数长度
                lines = node.end_lineno - node.lineno
                if lines > 50:
                    suggestions.append({
                        "type": "long_function",
                        "location": node.name,
                        "suggestion": "建议拆分为多个小函数"
                    })
        
        return suggestions
    
    def generate_refactor_plan(self, suggestions):
        """生成重构计划"""
        plan = []
        for sug in suggestions:
            plan.append({
                "step": f"重构 {sug['location']}",
                "action": sug['suggestion'],
                "risk": "LOW"
            })
        return plan

