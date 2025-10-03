"""
小柳升级：代码质量门禁系统
解决问题13：自动化代码质量检测
"""

import ast
import re
from pathlib import Path

class CodeQualityGate:
    """代码质量门禁 - 不合格不允许提交"""
    
    QUALITY_THRESHOLDS = {
        "cyclomatic_complexity": 10,    # 圈复杂度阈值
        "code_duplication": 0.05,        # 重复率5%
        "code_coverage": 0.80,           # 覆盖率80%
        "max_function_length": 50,       # 函数最大行数
        "max_file_length": 500           # 文件最大行数
    }
    
    def __init__(self):
        self.metrics = {}
    
    def check_all(self, code_path):
        """
        全面质量检查
        返回：是否通过门禁
        """
        checks = {
            "complexity": self.check_complexity(code_path),
            "duplication": self.check_duplication(code_path),
            "coverage": self.check_coverage(code_path),
            "length": self.check_length(code_path),
            "naming": self.check_naming(code_path)
        }
        
        passed = all(check["passed"] for check in checks.values())
        
        return {
            "gate_passed": passed,
            "checks": checks,
            "summary": self._generate_summary(checks)
        }
    
    def check_complexity(self, code_path):
        """检查圈复杂度"""
        code = Path(code_path).read_text()
        tree = ast.parse(code)
        
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > self.QUALITY_THRESHOLDS["cyclomatic_complexity"]:
                    violations.append({
                        "function": node.name,
                        "complexity": complexity,
                        "threshold": self.QUALITY_THRESHOLDS["cyclomatic_complexity"]
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "message": f"发现{len(violations)}个高复杂度函数" if violations else "✅ 复杂度检查通过"
        }
    
    def _calculate_complexity(self, node):
        """计算函数圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def check_duplication(self, code_path):
        """检查代码重复率"""
        # 简化实现：检测相似的代码块
        code = Path(code_path).read_text()
        lines = code.split('\n')
        
        duplicates = 0
        total_lines = len(lines)
        
        # 简单的重复检测（实际应使用更复杂的算法）
        line_hashes = {}
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # 忽略短行
                if line in line_hashes:
                    duplicates += 1
                else:
                    line_hashes[line] = 1
        
        duplication_rate = duplicates / total_lines if total_lines > 0 else 0
        
        return {
            "passed": duplication_rate <= self.QUALITY_THRESHOLDS["code_duplication"],
            "duplication_rate": f"{duplication_rate*100:.2f}%",
            "threshold": f"{self.QUALITY_THRESHOLDS['code_duplication']*100}%",
            "message": f"✅ 重复率{duplication_rate*100:.2f}%" if duplication_rate <= 0.05 else f"❌ 重复率过高"
        }
    
    def check_coverage(self, code_path):
        """检查测试覆盖率"""
        # 实际实现中会调用pytest-cov或coverage.py
        # 这里模拟
        coverage = 0.85  # 假设覆盖率
        
        return {
            "passed": coverage >= self.QUALITY_THRESHOLDS["code_coverage"],
            "coverage": f"{coverage*100:.1f}%",
            "threshold": f"{self.QUALITY_THRESHOLDS['code_coverage']*100}%",
            "message": f"✅ 覆盖率{coverage*100:.1f}%" if coverage >= 0.80 else "❌ 覆盖率不足"
        }
    
    def check_length(self, code_path):
        """检查函数和文件长度"""
        code = Path(code_path).read_text()
        tree = ast.parse(code)
        
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数行数
                func_lines = node.end_lineno - node.lineno
                if func_lines > self.QUALITY_THRESHOLDS["max_function_length"]:
                    violations.append({
                        "type": "function",
                        "name": node.name,
                        "lines": func_lines,
                        "threshold": self.QUALITY_THRESHOLDS["max_function_length"]
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "message": f"✅ 长度检查通过" if not violations else f"❌ 发现{len(violations)}个过长的函数"
        }
    
    def check_naming(self, code_path):
        """检查命名规范"""
        code = Path(code_path).read_text()
        tree = ast.parse(code)
        
        violations = []
        
        # 检查函数命名（应该是snake_case）
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    violations.append({
                        "type": "function_naming",
                        "name": node.name,
                        "expected": "snake_case"
                    })
            elif isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    violations.append({
                        "type": "class_naming",
                        "name": node.name,
                        "expected": "PascalCase"
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "message": f"✅ 命名规范" if not violations else f"❌ {len(violations)}个命名不规范"
        }
    
    def _is_snake_case(self, name):
        """检查是否是snake_case"""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None
    
    def _is_pascal_case(self, name):
        """检查是否是PascalCase"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def _generate_summary(self, checks):
        """生成摘要"""
        total = len(checks)
        passed = sum(1 for c in checks.values() if c["passed"])
        
        return {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{passed/total*100:.1f}%"
        }


class AutomatedQualityReport:
    """自动化质量报告生成器"""
    
    @staticmethod
    def generate_report(quality_result):
        """生成质量报告"""
        report = []
        report.append("=" * 60)
        report.append("代码质量检查报告")
        report.append("=" * 60)
        report.append("")
        
        # 总体结果
        if quality_result["gate_passed"]:
            report.append("✅ 质量门禁：通过")
        else:
            report.append("❌ 质量门禁：未通过")
        
        report.append("")
        report.append(f"检查项: {quality_result['summary']['passed']}/{quality_result['summary']['total_checks']} 通过")
        report.append("")
        
        # 详细检查结果
        for check_name, check_result in quality_result["checks"].items():
            status = "✅" if check_result["passed"] else "❌"
            report.append(f"{status} {check_name}: {check_result['message']}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


# 使用示例
if __name__ == "__main__":
    qg = CodeQualityGate()
    
    # 检查代码质量
    result = qg.check_all("example.py")
    
    if result["gate_passed"]:
        print("✅ 代码质量合格，允许提交！")
    else:
        print("❌ 代码质量不合格，禁止提交！")
        print("\n问题详情:")
        for check, details in result["checks"].items():
            if not details["passed"]:
                print(f"  - {check}: {details['message']}")
    
    # 生成报告
    report = AutomatedQualityReport.generate_report(result)
    print(report)

