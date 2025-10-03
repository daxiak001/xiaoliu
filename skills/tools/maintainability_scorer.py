"""
小柳升级：代码可维护性评分系统
解决问题37：0-100分量化可维护性
"""
import ast
import re

class MaintainabilityScorer:
    """可维护性评分：0-100分"""
    
    def __init__(self):
        self.weights = {
            "readability": 0.25,      # 可读性 25%
            "complexity": 0.20,       # 复杂度 20%
            "modularity": 0.20,       # 模块化 20%
            "documentation": 0.15,    # 文档 15%
            "testability": 0.10,      # 可测试性 10%
            "consistency": 0.10       # 一致性 10%
        }
    
    def evaluate_file(self, file_path):
        """评估单个文件"""
        code = open(file_path, 'r', encoding='utf-8').read()
        tree = ast.parse(code)
        
        scores = {
            "readability": self._score_readability(code, tree),
            "complexity": self._score_complexity(tree),
            "modularity": self._score_modularity(tree),
            "documentation": self._score_documentation(tree),
            "testability": self._score_testability(tree),
            "consistency": self._score_consistency(code)
        }
        
        # 加权总分
        total_score = sum(
            scores[dim] * self.weights[dim] 
            for dim in scores
        )
        
        return {
            "total_score": round(total_score, 1),
            "grade": self._get_grade(total_score),
            "dimension_scores": scores,
            "recommendations": self._generate_recommendations(scores)
        }
    
    def _score_readability(self, code, tree):
        """可读性评分 (0-100)"""
        score = 100
        
        # 1. 变量命名 (扣分项)
        short_names = re.findall(r'\b[a-z]\b', code)  # 单字母变量
        score -= len(short_names) * 2  # 每个扣2分
        
        # 2. 平均行长度
        lines = code.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines)
        if avg_line_length > 80:
            score -= 10
        
        # 3. 注释比例
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        comment_ratio = comment_lines / len(lines)
        if comment_ratio < 0.1:  # 少于10%
            score -= 15
        
        return max(0, min(100, score))
    
    def _score_complexity(self, tree):
        """复杂度评分 (0-100)"""
        score = 100
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算圈复杂度
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    score -= (complexity - 10) * 5  # 超过10每增1扣5分
        
        return max(0, min(100, score))
    
    def _score_modularity(self, tree):
        """模块化评分 (0-100)"""
        score = 100
        
        # 1. 函数长度
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno
                if func_lines > 50:
                    score -= 10  # 超长函数扣10分
        
        # 2. 类的方法数
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    score -= 15  # 上帝类扣15分
        
        return max(0, min(100, score))
    
    def _score_documentation(self, tree):
        """文档评分 (0-100)"""
        total_functions = 0
        documented_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1
        
        if total_functions == 0:
            return 100
        
        doc_coverage = documented_functions / total_functions
        return round(doc_coverage * 100, 1)
    
    def _score_testability(self, tree):
        """可测试性评分 (0-100)"""
        score = 100
        
        # 检查全局状态依赖
        global_vars = [node for node in ast.walk(tree) 
                      if isinstance(node, ast.Global)]
        score -= len(global_vars) * 10  # 全局变量降低可测试性
        
        return max(0, min(100, score))
    
    def _score_consistency(self, code):
        """一致性评分 (0-100)"""
        score = 100
        lines = code.split('\n')
        
        # 缩进一致性
        indents = [len(line) - len(line.lstrip()) 
                  for line in lines if line.strip()]
        if indents:
            # 检查是否混用tab和空格
            has_tabs = any('\t' in line for line in lines)
            has_spaces = any(line.startswith('    ') for line in lines)
            if has_tabs and has_spaces:
                score -= 20  # 混用tab和空格扣20分
        
        return max(0, min(100, score))
    
    def _calculate_cyclomatic_complexity(self, node):
        """计算圈复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _get_grade(self, score):
        """评级"""
        if score >= 90: return "A - 优秀"
        if score >= 80: return "B - 良好"
        if score >= 70: return "C - 中等"
        if score >= 60: return "D - 及格"
        return "F - 不及格"
    
    def _generate_recommendations(self, scores):
        """生成改进建议"""
        recommendations = []
        
        for dim, score in scores.items():
            if score < 70:
                recommendations.append(self._get_recommendation(dim, score))
        
        return recommendations
    
    def _get_recommendation(self, dimension, score):
        """获取改进建议"""
        suggestions = {
            "readability": "建议：使用有意义的变量名，增加注释，控制行长度",
            "complexity": "建议：拆分复杂函数，降低圈复杂度到10以下",
            "modularity": "建议：拆分长函数和大类，遵循单一职责原则",
            "documentation": "建议：为所有公开函数添加docstring",
            "testability": "建议：减少全局状态，使用依赖注入",
            "consistency": "建议：统一代码风格，使用格式化工具（black/prettier）"
        }
        return {
            "dimension": dimension,
            "score": score,
            "suggestion": suggestions.get(dimension, "需要改进")
        }

# 使用示例
if __name__ == "__main__":
    scorer = MaintainabilityScorer()
    result = scorer.evaluate_file("example.py")
    
    print(f"📊 可维护性评分：{result['total_score']}/100")
    print(f"📈 评级：{result['grade']}")
    print("\n📋 各维度得分：")
    for dim, score in result['dimension_scores'].items():
        print(f"  - {dim}: {score}/100")
    
    if result['recommendations']:
        print("\n💡 改进建议：")
        for rec in result['recommendations']:
            print(f"  - {rec['suggestion']}")

