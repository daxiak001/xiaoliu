"""
小柳升级：跨项目知识库
解决问题19：经验跨项目复用
"""

class CrossProjectKnowledge:
    def __init__(self):
        self.solution_templates = {}
        self.best_practices = {}
    
    def save_solution(self, problem, solution, project):
        """保存解决方案为模板"""
        template = {
            "problem": problem,
            "solution": solution,
            "source_project": project,
            "reusable": True
        }
        self.solution_templates[problem] = template
    
    def find_solution(self, problem):
        """查找可复用的解决方案"""
        if problem in self.solution_templates:
            return self.solution_templates[problem]
        return None

