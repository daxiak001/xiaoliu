"""
小柳升级：架构模式识别与推荐系统
解决问题45：识别架构模式并给出最佳建议
"""
import os
import re
from pathlib import Path

class ArchitectureAnalyzer:
    """架构模式分析器"""
    
    ARCHITECTURE_PATTERNS = {
        "MVC": {
            "indicators": ["models/", "views/", "controllers/", "routes/"],
            "keywords": ["Model", "View", "Controller"],
            "suitable_for": "传统Web应用，中小型项目",
            "pros": "结构清晰，易于理解",
            "cons": "Controller容易臃肿"
        },
        "MVVM": {
            "indicators": ["viewmodels/", "databinding", "observable"],
            "keywords": ["ViewModel", "DataBinding"],
            "suitable_for": "前端框架（Vue/React），客户端应用",
            "pros": "双向绑定，UI与业务分离",
            "cons": "学习曲线陡"
        },
        "微服务": {
            "indicators": ["services/", "api-gateway", "docker-compose", "k8s"],
            "keywords": ["ServiceA", "ServiceB", "Gateway", "Discovery"],
            "suitable_for": "大型系统，团队协作",
            "pros": "独立部署，技术栈灵活",
            "cons": "运维复杂，分布式事务难"
        },
        "事件驱动": {
            "indicators": ["events/", "handlers/", "kafka", "rabbitmq"],
            "keywords": ["Event", "Handler", "Publisher", "Subscriber"],
            "suitable_for": "高并发，异步处理",
            "pros": "解耦，高性能",
            "cons": "调试困难，最终一致性"
        },
        "分层架构": {
            "indicators": ["domain/", "application/", "infrastructure/"],
            "keywords": ["Domain", "Application", "Infrastructure"],
            "suitable_for": "DDD，复杂业务逻辑",
            "pros": "业务逻辑清晰，易测试",
            "cons": "层次过多，性能损耗"
        },
        "六边形架构": {
            "indicators": ["ports/", "adapters/", "domain/"],
            "keywords": ["Port", "Adapter", "UseCase"],
            "suitable_for": "高度解耦，可测试性要求高",
            "pros": "依赖倒置，易于替换组件",
            "cons": "概念抽象，上手难"
        }
    }
    
    def analyze_project(self, project_path):
        """分析项目架构"""
        # 1. 扫描目录结构
        dir_structure = self._scan_directories(project_path)
        
        # 2. 识别架构模式
        detected_patterns = self._detect_patterns(dir_structure, project_path)
        
        # 3. 分析业务特点
        business_traits = self._analyze_business(project_path)
        
        # 4. 给出建议
        recommendations = self._recommend_architecture(business_traits, detected_patterns)
        
        return {
            "current_architecture": detected_patterns,
            "business_traits": business_traits,
            "recommendations": recommendations,
            "migration_plan": self._generate_migration_plan(detected_patterns, recommendations)
        }
    
    def _scan_directories(self, project_path):
        """扫描目录结构"""
        dirs = []
        for root, dirnames, filenames in os.walk(project_path):
            for dirname in dirnames:
                dirs.append(dirname.lower())
        return dirs
    
    def _detect_patterns(self, dir_structure, project_path):
        """识别架构模式"""
        scores = {}
        
        for pattern_name, pattern_info in self.ARCHITECTURE_PATTERNS.items():
            score = 0
            evidence = []
            
            # 检查目录指标
            for indicator in pattern_info["indicators"]:
                if any(indicator in d for d in dir_structure):
                    score += 10
                    evidence.append(f"发现目录: {indicator}")
            
            # 检查关键字（扫描文件内容）
            keyword_found = self._search_keywords(project_path, pattern_info["keywords"])
            if keyword_found:
                score += 5
                evidence.extend([f"发现关键字: {kw}" for kw in keyword_found])
            
            if score > 0:
                scores[pattern_name] = {
                    "score": score,
                    "confidence": "高" if score > 15 else "中" if score > 5 else "低",
                    "evidence": evidence,
                    **pattern_info
                }
        
        # 按分数排序
        sorted_patterns = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return sorted_patterns
    
    def _search_keywords(self, project_path, keywords):
        """搜索关键字"""
        found = []
        # 简化版：仅搜索文件名
        for root, dirs, files in os.walk(project_path):
            for file in files:
                for keyword in keywords:
                    if keyword.lower() in file.lower():
                        found.append(keyword)
                        break
        return list(set(found))
    
    def _analyze_business(self, project_path):
        """分析业务特点"""
        traits = {
            "team_size": "未知",
            "complexity": "未知",
            "concurrency": "未知",
            "scalability_need": "未知"
        }
        
        # 简化推断
        file_count = sum(1 for _ in Path(project_path).rglob("*.py"))
        
        if file_count < 50:
            traits["complexity"] = "低（小型项目）"
            traits["team_size"] = "1-3人"
            traits["recommended_architecture"] = "单体架构/MVC"
        elif file_count < 200:
            traits["complexity"] = "中（中型项目）"
            traits["team_size"] = "3-10人"
            traits["recommended_architecture"] = "分层架构/模块化单体"
        else:
            traits["complexity"] = "高（大型项目）"
            traits["team_size"] = "10+人"
            traits["recommended_architecture"] = "微服务/事件驱动"
        
        return traits
    
    def _recommend_architecture(self, business_traits, current_patterns):
        """推荐架构"""
        recommendations = []
        
        complexity = business_traits["complexity"]
        
        # 规则1：小型项目 → 简单架构
        if "小型" in complexity:
            recommendations.append({
                "architecture": "MVC 或 分层架构",
                "reason": "项目规模小，不需要复杂架构",
                "priority": "推荐",
                "migration_cost": "低"
            })
        
        # 规则2：中型项目 → 模块化
        elif "中型" in complexity:
            recommendations.append({
                "architecture": "模块化单体 + 分层架构",
                "reason": "兼顾简单性和可扩展性",
                "priority": "推荐",
                "migration_cost": "中"
            })
        
        # 规则3：大型项目 → 微服务
        else:
            recommendations.append({
                "architecture": "微服务架构",
                "reason": "支持团队独立开发，灵活扩展",
                "priority": "推荐",
                "migration_cost": "高"
            })
            
            recommendations.append({
                "architecture": "事件驱动架构",
                "reason": "高并发场景，异步解耦",
                "priority": "可选",
                "migration_cost": "高"
            })
        
        return recommendations
    
    def _generate_migration_plan(self, current, recommended):
        """生成迁移计划"""
        if not current or not recommended:
            return None
        
        current_arch = current[0][0] if current else "未知"
        target_arch = recommended[0]["architecture"] if recommended else "未知"
        
        plan = {
            "from": current_arch,
            "to": target_arch,
            "phases": [
                {
                    "phase": 1,
                    "name": "评估与准备",
                    "duration": "2周",
                    "tasks": [
                        "全面代码审查",
                        "识别核心模块",
                        "建立测试覆盖",
                        "团队培训"
                    ]
                },
                {
                    "phase": 2,
                    "name": "边界划分",
                    "duration": "4周",
                    "tasks": [
                        "识别业务边界",
                        "定义服务接口",
                        "设计数据迁移方案",
                        "建立API Gateway"
                    ]
                },
                {
                    "phase": 3,
                    "name": "逐步迁移",
                    "duration": "8-12周",
                    "tasks": [
                        "剥离非核心服务",
                        "双写验证数据一致性",
                        "灰度切流量",
                        "监控与优化"
                    ]
                },
                {
                    "phase": 4,
                    "name": "清理与优化",
                    "duration": "2周",
                    "tasks": [
                        "移除旧代码",
                        "性能优化",
                        "文档更新",
                        "团队复盘"
                    ]
                }
            ],
            "total_duration": "16-20周",
            "risks": [
                "数据一致性问题",
                "服务间依赖复杂",
                "性能下降",
                "团队学习曲线"
            ]
        }
        
        return plan

# 使用示例
if __name__ == "__main__":
    analyzer = ArchitectureAnalyzer()
    
    result = analyzer.analyze_project("/path/to/project")
    
    print("🏗️ 当前架构:")
    for pattern_name, pattern_info in result["current_architecture"][:3]:
        print(f"  {pattern_name}: 置信度{pattern_info['confidence']} (分数: {pattern_info['score']})")
        print(f"    证据: {', '.join(pattern_info['evidence'][:3])}")
    
    print("\n💼 业务特点:")
    for key, value in result["business_traits"].items():
        print(f"  {key}: {value}")
    
    print("\n💡 架构建议:")
    for rec in result["recommendations"]:
        print(f"  {rec['architecture']} ({rec['priority']})")
        print(f"    原因: {rec['reason']}")
        print(f"    迁移成本: {rec['migration_cost']}")
    
    if result["migration_plan"]:
        print(f"\n📋 迁移计划: {result['migration_plan']['total_duration']}")
        for phase in result["migration_plan"]["phases"]:
            print(f"  阶段{phase['phase']}: {phase['name']} ({phase['duration']})")

