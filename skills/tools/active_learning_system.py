"""
小柳技能升级：主动学习系统
解决产品经理问题3：快速学习新技术
"""

class ActiveLearningSystem:
    """主动学习系统 - 快速掌握新技术"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.learning_patterns = []
        self.best_practices = {}
    
    def learn_new_technology(self, tech_name, resources=None):
        """
        学习新技术的完整流程
        1. 获取官方文档
        2. 分析核心概念
        3. 实践示例
        4. 总结最佳实践
        5. 举一反三
        """
        learning_plan = {
            "technology": tech_name,
            "phases": []
        }
        
        # Phase 1: 快速概览
        overview = self._quick_overview(tech_name)
        learning_plan["phases"].append({
            "phase": "Overview",
            "content": overview,
            "duration": "30分钟"
        })
        
        # Phase 2: 核心概念
        core_concepts = self._extract_core_concepts(tech_name)
        learning_plan["phases"].append({
            "phase": "Core Concepts",
            "concepts": core_concepts,
            "duration": "2小时"
        })
        
        # Phase 3: 实践
        practice_examples = self._create_practice_examples(tech_name)
        learning_plan["phases"].append({
            "phase": "Practice",
            "examples": practice_examples,
            "duration": "4小时"
        })
        
        # Phase 4: 总结最佳实践
        best_practices = self._summarize_best_practices(tech_name)
        self.best_practices[tech_name] = best_practices
        learning_plan["phases"].append({
            "phase": "Best Practices",
            "practices": best_practices,
            "duration": "1小时"
        })
        
        # Phase 5: 举一反三
        related_techs = self._find_analogies(tech_name)
        learning_plan["phases"].append({
            "phase": "Analogies",
            "related": related_techs,
            "duration": "1小时"
        })
        
        # 保存到知识库
        self.knowledge_base[tech_name] = learning_plan
        
        return learning_plan
    
    def _quick_overview(self, tech_name):
        """快速概览 - 3W1H"""
        return {
            "what": f"{tech_name}是什么",
            "why": f"为什么使用{tech_name}",
            "when": f"什么时候用{tech_name}",
            "how": f"如何使用{tech_name}"
        }
    
    def _extract_core_concepts(self, tech_name):
        """提取核心概念"""
        # 根据技术类型提取不同的核心概念
        concept_templates = {
            "programming_language": [
                "语法特性",
                "类型系统",
                "内存管理",
                "并发模型",
                "标准库"
            ],
            "framework": [
                "架构模式",
                "核心API",
                "生命周期",
                "插件系统",
                "最佳实践"
            ],
            "database": [
                "数据模型",
                "查询语言",
                "事务处理",
                "索引优化",
                "扩展性"
            ]
        }
        
        tech_type = self._identify_tech_type(tech_name)
        return concept_templates.get(tech_type, [])
    
    def _create_practice_examples(self, tech_name):
        """创建实践示例"""
        return [
            {
                "name": "Hello World",
                "complexity": "Beginner",
                "code": "# 基础示例"
            },
            {
                "name": "CRUD操作",
                "complexity": "Intermediate",
                "code": "# 实际应用"
            },
            {
                "name": "完整项目",
                "complexity": "Advanced",
                "code": "# 综合应用"
            }
        ]
    
    def _summarize_best_practices(self, tech_name):
        """总结最佳实践"""
        return {
            "dos": [
                "使用官方推荐的项目结构",
                "遵循命名约定",
                "编写测试",
                "使用版本控制"
            ],
            "donts": [
                "不要过度优化",
                "不要忽略错误处理",
                "不要硬编码配置"
            ],
            "patterns": [
                "常用设计模式",
                "推荐工具链",
                "性能优化技巧"
            ]
        }
    
    def _find_analogies(self, tech_name):
        """找相似技术，举一反三"""
        analogies_map = {
            "Rust": ["C++", "Go"],
            "Go": ["Rust", "C"],
            "React": ["Vue", "Angular"],
            "PostgreSQL": ["MySQL", "MongoDB"]
        }
        
        similar = analogies_map.get(tech_name, [])
        
        return {
            "similar_technologies": similar,
            "transferable_concepts": [
                "从已知技术迁移的概念",
                "可复用的经验"
            ],
            "differences": [
                "关键差异点",
                "需要特别注意的地方"
            ]
        }
    
    def _identify_tech_type(self, tech_name):
        """识别技术类型"""
        type_keywords = {
            "programming_language": ["Rust", "Go", "Python", "Java"],
            "framework": ["React", "Vue", "Django", "Spring"],
            "database": ["PostgreSQL", "MongoDB", "Redis"]
        }
        
        for tech_type, keywords in type_keywords.items():
            if tech_name in keywords:
                return tech_type
        
        return "unknown"
    
    def apply_knowledge(self, tech_name, problem):
        """应用学到的知识解决问题"""
        if tech_name not in self.knowledge_base:
            return {"error": f"还没学习{tech_name}"}
        
        knowledge = self.knowledge_base[tech_name]
        best_practices = self.best_practices.get(tech_name, {})
        
        solution = {
            "problem": problem,
            "approach": "基于最佳实践",
            "references": knowledge["phases"],
            "best_practices_applied": best_practices["dos"]
        }
        
        return solution


class WebLearner:
    """从网络学习新知识"""
    
    def search_and_learn(self, topic):
        """搜索并学习主题"""
        sources = {
            "official_docs": f"https://docs.{topic}.org",
            "tutorials": f"搜索{topic}教程",
            "stackoverflow": f"搜索{topic}常见问题",
            "github": f"搜索{topic}示例项目",
            "blog_posts": f"搜索{topic}最佳实践"
        }
        
        learning_materials = []
        
        for source_type, source_url in sources.items():
            material = {
                "type": source_type,
                "url": source_url,
                "priority": self._get_priority(source_type)
            }
            learning_materials.append(material)
        
        # 按优先级排序
        learning_materials.sort(key=lambda x: x["priority"], reverse=True)
        
        return learning_materials
    
    def _get_priority(self, source_type):
        """获取学习资源优先级"""
        priorities = {
            "official_docs": 10,
            "tutorials": 8,
            "github": 7,
            "stackoverflow": 6,
            "blog_posts": 5
        }
        return priorities.get(source_type, 1)


# 使用示例
if __name__ == "__main__":
    als = ActiveLearningSystem()
    
    # 学习新技术
    plan = als.learn_new_technology("Rust")
    print("学习计划:", plan)
    
    # 应用知识
    solution = als.apply_knowledge("Rust", "构建高性能Web服务")
    print("解决方案:", solution)
    
    # 网络学习
    web_learner = WebLearner()
    materials = web_learner.search_and_learn("WebAssembly")
    print("学习资源:", materials)

