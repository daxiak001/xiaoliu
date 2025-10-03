"""
小柳技能升级：任务并行管理器
解决产品经理问题4：同时处理多个任务
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1  # 紧急且重要
    HIGH = 2      # 重要但不紧急
    MEDIUM = 3    # 普通任务
    LOW = 4       # 可延后

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    TESTING = "测试中"
    COMPLETED = "已完成"
    BLOCKED = "被阻塞"

@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    priority: TaskPriority
    estimated_time: int  # 分钟
    dependencies: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0  # 0-100
    subtasks: List[str] = None

class TaskParallelManager:
    """任务并行管理器"""
    
    def __init__(self):
        self.tasks = {}
        self.task_queue = []
        self.active_tasks = []
        self.completed_tasks = []
    
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks[task.id] = task
        self._prioritize_task(task)
    
    def add_multiple_tasks(self, tasks: List[Task]):
        """批量添加任务"""
        for task in tasks:
            self.add_task(task)
        
        # 分析任务依赖关系
        self._analyze_dependencies()
        
        # 生成执行计划
        execution_plan = self._generate_execution_plan()
        
        return execution_plan
    
    def _prioritize_task(self, task: Task):
        """任务优先级排序"""
        # 根据优先级和截止时间排序
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: (t.priority.value, t.estimated_time))
    
    def _analyze_dependencies(self):
        """分析任务依赖"""
        dependency_graph = {}
        
        for task_id, task in self.tasks.items():
            if task.dependencies:
                dependency_graph[task_id] = task.dependencies
        
        # 检测循环依赖
        cycles = self._detect_circular_dependencies(dependency_graph)
        if cycles:
            raise ValueError(f"检测到循环依赖: {cycles}")
        
        return dependency_graph
    
    def _detect_circular_dependencies(self, graph):
        """检测循环依赖"""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def _generate_execution_plan(self):
        """生成执行计划"""
        plan = {
            "phases": [],
            "parallel_tasks": [],
            "sequential_tasks": [],
            "estimated_total_time": 0
        }
        
        # 分组：可并行 vs 必须串行
        can_parallel = []
        must_sequential = []
        
        for task in self.task_queue:
            if not task.dependencies:
                can_parallel.append(task)
            else:
                must_sequential.append(task)
        
        # 第1阶段：并行执行无依赖任务
        if can_parallel:
            plan["phases"].append({
                "phase": 1,
                "type": "parallel",
                "tasks": [t.name for t in can_parallel],
                "estimated_time": max([t.estimated_time for t in can_parallel])
            })
        
        # 后续阶段：按依赖顺序执行
        remaining = must_sequential.copy()
        phase = 2
        
        while remaining:
            ready_tasks = []
            
            for task in remaining:
                deps_completed = all(
                    self.tasks[dep].status == TaskStatus.COMPLETED 
                    for dep in task.dependencies
                )
                if deps_completed:
                    ready_tasks.append(task)
            
            if ready_tasks:
                plan["phases"].append({
                    "phase": phase,
                    "type": "parallel",
                    "tasks": [t.name for t in ready_tasks],
                    "estimated_time": max([t.estimated_time for t in ready_tasks])
                })
                
                for task in ready_tasks:
                    remaining.remove(task)
                
                phase += 1
            else:
                break
        
        # 计算总时间
        plan["estimated_total_time"] = sum(p["estimated_time"] for p in plan["phases"])
        
        return plan
    
    def execute_task(self, task_id: str):
        """执行任务"""
        task = self.tasks[task_id]
        
        # 检查依赖
        if task.dependencies:
            for dep in task.dependencies:
                if self.tasks[dep].status != TaskStatus.COMPLETED:
                    return {
                        "success": False,
                        "reason": f"依赖任务 {dep} 未完成"
                    }
        
        # 分解子任务
        if not task.subtasks:
            task.subtasks = self._decompose_task(task)
        
        # 更新状态
        task.status = TaskStatus.IN_PROGRESS
        self.active_tasks.append(task)
        
        # 执行步骤
        execution_steps = []
        for i, subtask in enumerate(task.subtasks):
            step = {
                "step": i + 1,
                "subtask": subtask,
                "status": "completed",
                "progress": int((i + 1) / len(task.subtasks) * 100)
            }
            execution_steps.append(step)
            task.progress = step["progress"]
        
        # 完成任务
        task.status = TaskStatus.COMPLETED
        self.completed_tasks.append(task)
        self.active_tasks.remove(task)
        
        return {
            "success": True,
            "task": task.name,
            "steps": execution_steps
        }
    
    def _decompose_task(self, task: Task):
        """分解任务为子任务"""
        # 根据任务类型分解
        task_decomposition = {
            "重构模块": [
                "分析现有代码",
                "设计新架构",
                "编写重构代码",
                "运行测试",
                "更新文档"
            ],
            "修复bug": [
                "复现问题",
                "定位原因",
                "编写修复代码",
                "添加测试用例",
                "验证修复"
            ],
            "优化性能": [
                "性能分析",
                "找出瓶颈",
                "实施优化",
                "基准测试",
                "文档更新"
            ],
            "写测试": [
                "分析测试需求",
                "编写测试用例",
                "运行测试",
                "检查覆盖率",
                "完善测试"
            ]
        }
        
        # 匹配任务类型
        for task_type, subtasks in task_decomposition.items():
            if task_type in task.name:
                return subtasks
        
        # 默认分解
        return [
            "理解需求",
            "设计方案",
            "编码实现",
            "测试验证",
            "文档更新"
        ]
    
    def get_status_report(self):
        """获取状态报告"""
        total = len(self.tasks)
        completed = len(self.completed_tasks)
        in_progress = len(self.active_tasks)
        pending = total - completed - in_progress
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "completion_rate": f"{completed/total*100:.1f}%" if total > 0 else "0%",
            "active_tasks": [t.name for t in self.active_tasks],
            "next_tasks": [t.name for t in self.task_queue[:3]]
        }


# 使用示例
if __name__ == "__main__":
    tpm = TaskParallelManager()
    
    # 添加多个任务
    tasks = [
        Task(
            id="task1",
            name="重构用户认证模块",
            description="改进auth模块架构",
            priority=TaskPriority.HIGH,
            estimated_time=180
        ),
        Task(
            id="task2",
            name="修复登录bug",
            description="修复Session过期问题",
            priority=TaskPriority.CRITICAL,
            estimated_time=60,
            dependencies=[]
        ),
        Task(
            id="task3",
            name="优化数据库查询",
            description="解决N+1查询问题",
            priority=TaskPriority.HIGH,
            estimated_time=120
        ),
        Task(
            id="task4",
            name="写单元测试",
            description="为新功能编写测试",
            priority=TaskPriority.MEDIUM,
            estimated_time=90,
            dependencies=["task1"]
        )
    ]
    
    plan = tpm.add_multiple_tasks(tasks)
    print("执行计划:", plan)
    
    # 执行任务
    result = tpm.execute_task("task2")
    print("执行结果:", result)
    
    # 状态报告
    status = tpm.get_status_report()
    print("状态报告:", status)

