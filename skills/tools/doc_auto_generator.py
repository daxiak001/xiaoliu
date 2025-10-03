"""
小柳升级：文档自动生成器
解决问题16：文档自动化
"""
import ast

class DocAutoGenerator:
    def generate_api_doc(self, code_file):
        """从代码自动生成API文档"""
        tree = ast.parse(open(code_file).read())
        docs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docs.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "args": [arg.arg for arg in node.args.args]
                })
        
        return docs
    
    def generate_changelog(self, commits):
        """自动生成CHANGELOG"""
        changelog = ["# Changelog\n"]
        for commit in commits:
            changelog.append(f"- {commit['message']}")
        return "\n".join(changelog)

