# -*- coding: utf-8 -*-
"""
自动经验记录器 v1.0
自动记录所有操作的成功/失败案例

功能：
- 装饰器自动记录
- 成功案例保存
- 失败案例保存
- 智能规则生成

作者：小柳开发团队
版本：v1.0
日期：2025-10-06
"""

import functools
import json
import time
import traceback
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Dict, List

class AutoExperienceRecorder:
    """自动经验记录器"""
    
    def __init__(self):
        """初始化记录器"""
        # 自动检测操作系统
        if os.name == 'nt':  # Windows
            base_path = Path("D:/xiaoliu_data")
        else:  # Linux/Unix
            base_path = Path("/home/ubuntu/xiaoliu/data")
        
        # 数据文件路径
        self.success_db = base_path / "success_cases.json"
        self.failure_db = base_path / "failure_cases.json"
        self.rules_db = base_path / "experience_rules.json"
        
        # 确保目录和文件存在
        self._initialize_databases()
        
        # 统计信息
        self.stats = {
            "total_operations": 0,
            "success_count": 0,
            "failure_count": 0,
            "rules_generated": 0
        }
    
    def _initialize_databases(self):
        """初始化数据库文件"""
        for db in [self.success_db, self.failure_db, self.rules_db]:
            db.parent.mkdir(parents=True, exist_ok=True)
            if not db.exists():
                db.write_text("[]", encoding='utf-8')
    
    def record(self, operation_name: str = None):
        """
        装饰器：自动记录函数执行结果
        
        使用方法：
        @recorder.record("操作名称")
        def some_function():
            pass
        
        参数：
            operation_name: 操作名称（可选，默认使用函数名）
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                start_time = time.time()
                
                # 记录输入
                input_data = {
                    "args": self._safe_str(args),
                    "kwargs": self._safe_str(kwargs)
                }
                
                try:
                    # 执行原函数
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # ✅ 成功！记录成功案例
                    self._record_success(
                        operation=op_name,
                        function=func.__name__,
                        input_data=input_data,
                        result=result,
                        execution_time=execution_time
                    )
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # ❌ 失败！记录失败案例
                    self._record_failure(
                        operation=op_name,
                        function=func.__name__,
                        input_data=input_data,
                        error=e,
                        execution_time=execution_time
                    )
                    
                    # 重新抛出异常（不影响原有流程）
                    raise
            
            return wrapper
        return decorator
    
    def _record_success(self, operation: str, function: str, 
                       input_data: Dict, result: Any, execution_time: float):
        """记录成功案例"""
        case = {
            "id": f"success_{int(time.time() * 1000)}",
            "operation": operation,
            "function": function,
            "input": input_data,
            "output": self._safe_str(result, max_length=500),
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.now().isoformat(),
            "context": self._get_context()
        }
        
        # 保存到数据库
        self._append_to_db(self.success_db, case)
        
        # 更新统计
        self.stats["total_operations"] += 1
        self.stats["success_count"] += 1
        
        # 更新成功模式
        self._update_success_patterns(operation, case)
        
        print(f"✅ 成功案例已记录: {operation} (耗时: {execution_time:.2f}s)")
    
    def _record_failure(self, operation: str, function: str,
                       input_data: Dict, error: Exception, execution_time: float):
        """记录失败案例"""
        case = {
            "id": f"failure_{int(time.time() * 1000)}",
            "operation": operation,
            "function": function,
            "input": input_data,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.now().isoformat(),
            "root_cause": self._analyze_root_cause(error),
            "context": self._get_context()
        }
        
        # 保存到数据库
        self._append_to_db(self.failure_db, case)
        
        # 更新统计
        self.stats["total_operations"] += 1
        self.stats["failure_count"] += 1
        
        # 生成预防规则
        self._generate_prevention_rule(operation, case)
        
        print(f"❌ 失败案例已记录: {operation} - {case['error_type']}")
    
    def _update_success_patterns(self, operation: str, case: Dict):
        """更新成功模式"""
        rules = self._load_rules()
        
        # 查找或创建操作规则
        op_rule = next((r for r in rules if r["operation"] == operation), None)
        
        if op_rule is None:
            op_rule = {
                "operation": operation,
                "success_count": 0,
                "failure_count": 0,
                "best_practices": [],
                "prevention_rules": [],
                "avg_execution_time": 0,
                "last_updated": datetime.now().isoformat()
            }
            rules.append(op_rule)
        
        # 更新成功次数
        op_rule["success_count"] += 1
        
        # 更新平均执行时间
        total_success = op_rule["success_count"]
        old_avg = op_rule["avg_execution_time"]
        new_time = case["execution_time"]
        op_rule["avg_execution_time"] = (old_avg * (total_success - 1) + new_time) / total_success
        
        # 提取最佳实践（快速执行）
        if case["execution_time"] < op_rule["avg_execution_time"] * 0.8:  # 比平均快20%
            best_practice = {
                "description": f"快速执行方式（{case['execution_time']:.2f}s）",
                "input": case["input"],
                "added": datetime.now().isoformat()
            }
            # 避免重复
            if best_practice not in op_rule["best_practices"]:
                op_rule["best_practices"].append(best_practice)
                # 只保留最近5条
                op_rule["best_practices"] = op_rule["best_practices"][-5:]
        
        op_rule["last_updated"] = datetime.now().isoformat()
        
        # 保存规则
        self._save_rules(rules)
    
    def _generate_prevention_rule(self, operation: str, case: Dict):
        """生成预防规则"""
        rules = self._load_rules()
        
        # 查找或创建操作规则
        op_rule = next((r for r in rules if r["operation"] == operation), None)
        
        if op_rule is None:
            op_rule = {
                "operation": operation,
                "success_count": 0,
                "failure_count": 0,
                "best_practices": [],
                "prevention_rules": [],
                "avg_execution_time": 0,
                "last_updated": datetime.now().isoformat()
            }
            rules.append(op_rule)
        
        # 更新失败次数
        op_rule["failure_count"] += 1
        
        # 生成预防规则
        prevention = {
            "rule": f"避免{case['error_type']}: {case['root_cause']}",
            "error_type": case['error_type'],
            "error_message": case['error_message'],
            "frequency": 1,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        # 检查是否已存在相同错误类型的规则
        existing = next(
            (p for p in op_rule["prevention_rules"] 
             if p["error_type"] == case['error_type']),
            None
        )
        
        if existing:
            # 更新频率和最后出现时间
            existing["frequency"] += 1
            existing["last_seen"] = datetime.now().isoformat()
        else:
            # 添加新规则
            op_rule["prevention_rules"].append(prevention)
            self.stats["rules_generated"] += 1
        
        op_rule["last_updated"] = datetime.now().isoformat()
        
        # 保存规则
        self._save_rules(rules)
        
        print(f"📝 已生成预防规则: {prevention['rule']}")
    
    def get_suggestions(self, operation: str) -> Dict:
        """
        获取操作建议
        
        参数：
            operation: 操作名称
            
        返回：
            包含最佳实践和预防规则的字典
        """
        rules = self._load_rules()
        op_rule = next((r for r in rules if r["operation"] == operation), None)
        
        if not op_rule:
            return {
                "operation": operation,
                "has_experience": False,
                "suggestions": [],
                "warnings": []
            }
        
        total = op_rule["success_count"] + op_rule["failure_count"]
        success_rate = op_rule["success_count"] / total if total > 0 else 0
        
        return {
            "operation": operation,
            "has_experience": True,
            "success_rate": round(success_rate, 2),
            "total_operations": total,
            "avg_execution_time": round(op_rule["avg_execution_time"], 2),
            "best_practices": op_rule["best_practices"],
            "warnings": [p["rule"] for p in op_rule["prevention_rules"]],
            "high_risk_errors": [
                p for p in op_rule["prevention_rules"] 
                if p["frequency"] >= 3
            ]
        }
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        rules = self._load_rules()
        
        return {
            **self.stats,
            "total_rules": len(rules),
            "operations_tracked": [r["operation"] for r in rules],
            "most_successful": sorted(
                rules, 
                key=lambda x: x["success_count"], 
                reverse=True
            )[:5],
            "most_problematic": sorted(
                rules,
                key=lambda x: x["failure_count"],
                reverse=True
            )[:5]
        }
    
    def _analyze_root_cause(self, error: Exception) -> str:
        """分析错误根本原因"""
        error_type = type(error).__name__
        
        root_cause_map = {
            "FileNotFoundError": "文件路径不存在，需要检查路径",
            "PermissionError": "权限不足，需要修改文件权限或使用sudo",
            "ConnectionError": "网络连接失败，检查网络或目标服务",
            "TimeoutError": "操作超时，可能需要增加超时时间",
            "KeyError": "字典键不存在，需要先检查键是否存在",
            "IndexError": "索引越界，需要检查数组长度",
            "AttributeError": "对象属性不存在，检查对象类型",
            "ImportError": "模块导入失败，检查依赖是否安装",
            "TypeError": "类型错误，需要类型检查",
            "ValueError": "值错误，需要参数验证",
            "OSError": "操作系统错误，检查系统资源"
        }
        
        return root_cause_map.get(error_type, f"未知错误类型: {error_type}")
    
    def _get_context(self) -> Dict:
        """获取执行上下文"""
        return {
            "os": os.name,
            "cwd": os.getcwd(),
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "timestamp": datetime.now().isoformat()
        }
    
    def _safe_str(self, obj: Any, max_length: int = 200) -> str:
        """安全的字符串转换（避免过长）"""
        try:
            s = str(obj)
            if len(s) > max_length:
                return s[:max_length] + "..."
            return s
        except:
            return "<无法转换为字符串>"
    
    def _append_to_db(self, db_path: Path, data: Dict):
        """追加数据到数据库"""
        try:
            # 读取现有数据
            cases = json.loads(db_path.read_text(encoding='utf-8'))
            
            # 添加新数据
            cases.append(data)
            
            # 只保留最近1000条
            cases = cases[-1000:]
            
            # 保存
            db_path.write_text(
                json.dumps(cases, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"⚠️ 保存数据失败: {e}")
    
    def _load_rules(self) -> List[Dict]:
        """加载规则"""
        try:
            return json.loads(self.rules_db.read_text(encoding='utf-8'))
        except:
            return []
    
    def _save_rules(self, rules: List[Dict]):
        """保存规则"""
        try:
            self.rules_db.write_text(
                json.dumps(rules, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"⚠️ 保存规则失败: {e}")


# 全局实例（单例模式）
_recorder_instance = None

def get_recorder() -> AutoExperienceRecorder:
    """获取全局记录器实例"""
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = AutoExperienceRecorder()
    return _recorder_instance


# 便捷装饰器
def auto_record(operation_name: str = None):
    """
    便捷装饰器：自动记录操作
    
    使用方法：
    @auto_record("SSH连接")
    def ssh_connect():
        pass
    """
    recorder = get_recorder()
    return recorder.record(operation_name)


# 使用示例
if __name__ == "__main__":
    import subprocess
    
    # 测试1: 成功案例
    @auto_record("测试成功操作")
    def test_success():
        """测试成功的操作"""
        return "成功!"
    
    # 测试2: 失败案例
    @auto_record("测试失败操作")
    def test_failure():
        """测试失败的操作"""
        raise FileNotFoundError("测试文件不存在")
    
    print("=" * 60)
    print("🧪 自动经验记录器测试")
    print("=" * 60)
    
    # 执行测试
    print("\n测试1: 成功案例")
    result = test_success()
    print(f"结果: {result}")
    
    print("\n测试2: 失败案例")
    try:
        test_failure()
    except FileNotFoundError:
        print("预期的错误已被捕获")
    
    # 获取建议
    print("\n获取操作建议:")
    recorder = get_recorder()
    suggestions = recorder.get_suggestions("测试失败操作")
    print(json.dumps(suggestions, indent=2, ensure_ascii=False))
    
    # 统计信息
    print("\n统计信息:")
    stats = recorder.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print(f"📁 数据文件位置:")
    print(f"   成功案例: {recorder.success_db}")
    print(f"   失败案例: {recorder.failure_db}")
    print(f"   经验规则: {recorder.rules_db}")
    print("=" * 60)

