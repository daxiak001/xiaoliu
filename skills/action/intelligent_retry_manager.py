# -*- coding: utf-8 -*-
"""
智能重试管理器
提供基于失败原因的智能重试策略
"""

import time
import random
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum

class FailureType(Enum):
    """失败类型枚举"""
    ELEMENT_NOT_FOUND = "element_not_found"
    CLICK_FAILED = "click_failed"
    INPUT_FAILED = "input_failed"
    OCR_FAILED = "ocr_failed"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN = "unknown"

@dataclass
class RetryContext:
    """重试上下文"""
    operation_type: str
    target: Any
    parameters: Dict[str, Any]
    attempt_count: int = 0
    last_error: Optional[Exception] = None
    failure_history: List[FailureType] = None
    
    def __post_init__(self):
        if self.failure_history is None:
            self.failure_history = []

@dataclass
class OperationResult:
    """操作结果"""
    success: bool
    message: str = ""
    data: Any = None
    execution_time: float = 0
    failure_type: Optional[FailureType] = None

class IntelligentRetryManager:
    """
    智能重试管理器
    
    功能：根据失败原因智能调整重试策略
    特点：
    - 自适应重试间隔
    - 基于失败类型的策略选择
    - 学习历史失败模式
    - 动态参数调整
    """
    
    def __init__(self):
        self.max_retries = 5
        self.base_wait_time = 1.0  # 基础等待时间（秒）
        self.max_wait_time = 30.0  # 最大等待时间（秒）
        
        # 失败类型统计
        self.failure_stats = {}
        
        # 重试策略映射
        self.retry_strategies = {
            FailureType.ELEMENT_NOT_FOUND: self._retry_element_search,
            FailureType.CLICK_FAILED: self._retry_click_operation,
            FailureType.INPUT_FAILED: self._retry_input_operation,
            FailureType.OCR_FAILED: self._retry_ocr_recognition,
            FailureType.TIMEOUT: self._retry_with_longer_wait,
            FailureType.NETWORK_ERROR: self._retry_network_operation,
            FailureType.PERMISSION_DENIED: self._retry_permission_operation,
            FailureType.UNKNOWN: self._retry_generic
        }
        
        print("[INFO] 智能重试管理器初始化完成")
    
    def execute_with_retry(self, operation: Callable, context: RetryContext) -> OperationResult:
        """
        智能重试执行操作
        
        参数:
            operation: 要执行的操作函数
            context: 重试上下文
            
        返回:
            OperationResult: 执行结果
        """
        print(f"[INFO] 开始智能重试执行: {context.operation_type}")
        
        last_result = None
        
        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                start_time = time.time()
                
                # 执行操作
                result = operation(context)
                execution_time = time.time() - start_time
                
                if isinstance(result, OperationResult):
                    result.execution_time = execution_time
                    if result.success:
                        print(f"[SUCCESS] 操作成功，尝试次数: {attempt + 1}")
                        self._record_success(context, attempt)
                        return result
                    last_result = result
                else:
                    # 兼容性处理：如果返回的不是OperationResult
                    if result:
                        print(f"[SUCCESS] 操作成功，尝试次数: {attempt + 1}")
                        return OperationResult(True, "操作成功", result, execution_time)
                    else:
                        last_result = OperationResult(False, "操作失败", None, execution_time)
                
                # 如果是最后一次尝试，直接返回失败
                if attempt >= self.max_retries:
                    break
                
                # 分析失败原因
                failure_type = self._analyze_failure(last_result, context)
                context.failure_history.append(failure_type)
                
                print(f"[RETRY {attempt + 1}] 失败类型: {failure_type.value}")
                
                # 应用重试策略
                context = self._apply_retry_strategy(context, failure_type, attempt)
                
                # 计算等待时间
                wait_time = self._calculate_wait_time(attempt, failure_type, context)
                
                if wait_time > 0:
                    print(f"[WAIT] 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                
            except Exception as e:
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                print(f"[ERROR] 第 {attempt + 1} 次尝试异常: {str(e)}")
                
                context.last_error = e
                last_result = OperationResult(
                    False, 
                    f"执行异常: {str(e)}", 
                    None, 
                    execution_time,
                    FailureType.UNKNOWN
                )
                
                if attempt >= self.max_retries:
                    break
                
                # 异常情况下的等待
                wait_time = min(self.base_wait_time * (2 ** attempt), self.max_wait_time)
                time.sleep(wait_time)
        
        # 记录最终失败
        self._record_failure(context, self.max_retries + 1)
        
        return last_result or OperationResult(
            False, 
            f"重试 {self.max_retries} 次后仍然失败", 
            None, 
            0, 
            FailureType.UNKNOWN
        )
    
    def _analyze_failure(self, result: OperationResult, context: RetryContext) -> FailureType:
        """分析失败原因"""
        if result.failure_type:
            return result.failure_type
        
        # 基于错误消息分析
        message = result.message.lower()
        
        if "not found" in message or "element" in message:
            return FailureType.ELEMENT_NOT_FOUND
        elif "click" in message or "mouse" in message:
            return FailureType.CLICK_FAILED
        elif "ocr" in message or "text" in message or "recognition" in message:
            return FailureType.OCR_FAILED
        elif "timeout" in message or "time" in message:
            return FailureType.TIMEOUT
        elif "network" in message or "connection" in message:
            return FailureType.NETWORK_ERROR
        elif "permission" in message or "access" in message:
            return FailureType.PERMISSION_DENIED
        else:
            return FailureType.UNKNOWN
    
    def _apply_retry_strategy(self, context: RetryContext, failure_type: FailureType, attempt: int) -> RetryContext:
        """应用重试策略"""
        if failure_type in self.retry_strategies:
            strategy_func = self.retry_strategies[failure_type]
            return strategy_func(context, attempt)
        else:
            return self._retry_generic(context, attempt)
    
    def _retry_element_search(self, context: RetryContext, attempt: int) -> RetryContext:
        """元素查找重试策略"""
        print(f"[STRATEGY] 应用元素查找重试策略 (第{attempt+1}次)")
        
        # 1. 降低匹配精度
        if 'search_tolerance' not in context.parameters:
            context.parameters['search_tolerance'] = 0.8
        else:
            context.parameters['search_tolerance'] = max(0.5, context.parameters['search_tolerance'] - 0.1)
        
        # 2. 尝试不同的检测方法
        detection_methods = ['ocr_text', 'image_match', 'coordinate_estimate', 'fuzzy_match']
        if attempt < len(detection_methods):
            context.parameters['detection_method'] = detection_methods[attempt]
        
        # 3. 扩大搜索区域
        if 'search_area_expansion' not in context.parameters:
            context.parameters['search_area_expansion'] = 1.0
        else:
            context.parameters['search_area_expansion'] += 0.2
        
        # 4. 强制重新截图
        context.parameters['force_new_screenshot'] = True
        
        # 5. 尝试滚动页面
        if attempt >= 2:
            context.parameters['try_scroll'] = True
            context.parameters['scroll_direction'] = 'down' if attempt % 2 == 0 else 'up'
        
        return context
    
    def _retry_click_operation(self, context: RetryContext, attempt: int) -> RetryContext:
        """点击操作重试策略"""
        print(f"[STRATEGY] 应用点击操作重试策略 (第{attempt+1}次)")
        
        # 1. 调整点击位置
        if 'click_offset' not in context.parameters:
            context.parameters['click_offset'] = (0, 0)
        else:
            # 随机偏移，模拟更自然的点击
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            context.parameters['click_offset'] = (offset_x, offset_y)
        
        # 2. 调整点击方式
        click_methods = ['single', 'double', 'right', 'middle']
        if attempt < len(click_methods):
            context.parameters['click_method'] = click_methods[attempt]
        
        # 3. 增加点击前等待时间
        context.parameters['pre_click_wait'] = 0.5 + (attempt * 0.2)
        
        # 4. 尝试不同的点击持续时间
        context.parameters['click_duration'] = 0.1 + (attempt * 0.05)
        
        return context
    
    def _retry_input_operation(self, context: RetryContext, attempt: int) -> RetryContext:
        """输入操作重试策略"""
        print(f"[STRATEGY] 应用输入操作重试策略 (第{attempt+1}次)")
        
        # 1. 清空输入框
        context.parameters['clear_before_input'] = True
        
        # 2. 增加输入延迟
        current_delay = context.parameters.get('input_delay', 0.1)
        context.parameters['input_delay'] = min(current_delay * 1.5, 1.0)
        
        # 3. 尝试重新获取焦点
        context.parameters['refocus'] = True
        
        # 4. 使用不同的输入方法
        input_methods = ['type', 'paste', 'send_keys']
        current_method = context.parameters.get('input_method', 'type')
        try:
            current_index = input_methods.index(current_method)
            next_method = input_methods[(current_index + 1) % len(input_methods)]
            context.parameters['input_method'] = next_method
        except ValueError:
            context.parameters['input_method'] = 'type'
        
        print(f"[STRATEGY] 输入重试策略: 方法={context.parameters['input_method']}, 延迟={context.parameters['input_delay']:.2f}s")
        
        return context
    
    def _retry_ocr_recognition(self, context: RetryContext, attempt: int) -> RetryContext:
        """OCR识别重试策略"""
        print(f"[STRATEGY] 应用OCR识别重试策略 (第{attempt+1}次)")
        
        # 1. 尝试不同的OCR引擎
        ocr_engines = ['paddleocr', 'easyocr', 'tesseract', 'builtin']
        if attempt < len(ocr_engines):
            context.parameters['preferred_ocr_engine'] = ocr_engines[attempt]
        
        # 2. 调整图像预处理
        preprocessing_methods = ['none', 'enhance_contrast', 'denoise', 'sharpen', 'binarize']
        if attempt < len(preprocessing_methods):
            context.parameters['image_preprocessing'] = preprocessing_methods[attempt]
        
        # 3. 调整识别区域
        if 'ocr_region_expansion' not in context.parameters:
            context.parameters['ocr_region_expansion'] = 1.0
        else:
            context.parameters['ocr_region_expansion'] += 0.1
        
        # 4. 降低置信度阈值
        if 'confidence_threshold' not in context.parameters:
            context.parameters['confidence_threshold'] = 0.8
        else:
            context.parameters['confidence_threshold'] = max(0.3, context.parameters['confidence_threshold'] - 0.1)
        
        return context
    
    def _retry_with_longer_wait(self, context: RetryContext, attempt: int) -> RetryContext:
        """超时重试策略"""
        print(f"[STRATEGY] 应用超时重试策略 (第{attempt+1}次)")
        
        # 1. 增加操作超时时间
        if 'operation_timeout' not in context.parameters:
            context.parameters['operation_timeout'] = 30
        else:
            context.parameters['operation_timeout'] += 10
        
        # 2. 增加元素等待时间
        if 'element_wait_time' not in context.parameters:
            context.parameters['element_wait_time'] = 5
        else:
            context.parameters['element_wait_time'] += 3
        
        return context
    
    def _retry_network_operation(self, context: RetryContext, attempt: int) -> RetryContext:
        """网络操作重试策略"""
        print(f"[STRATEGY] 应用网络操作重试策略 (第{attempt+1}次)")
        
        # 1. 增加连接超时时间
        if 'connection_timeout' not in context.parameters:
            context.parameters['connection_timeout'] = 10
        else:
            context.parameters['connection_timeout'] += 5
        
        # 2. 启用重连机制
        context.parameters['enable_reconnect'] = True
        
        return context
    
    def _retry_permission_operation(self, context: RetryContext, attempt: int) -> RetryContext:
        """权限操作重试策略"""
        print(f"[STRATEGY] 应用权限操作重试策略 (第{attempt+1}次)")
        
        # 1. 尝试提升权限
        context.parameters['request_elevated_privileges'] = True
        
        # 2. 尝试替代方法
        context.parameters['use_alternative_method'] = True
        
        return context
    
    def _retry_generic(self, context: RetryContext, attempt: int) -> RetryContext:
        """通用重试策略"""
        print(f"[STRATEGY] 应用通用重试策略 (第{attempt+1}次)")
        
        # 1. 增加通用等待时间
        if 'generic_wait_time' not in context.parameters:
            context.parameters['generic_wait_time'] = 1.0
        else:
            context.parameters['generic_wait_time'] += 0.5
        
        # 2. 启用详细日志
        context.parameters['verbose_logging'] = True
        
        return context
    
    def _calculate_wait_time(self, attempt: int, failure_type: FailureType, context: RetryContext) -> float:
        """计算等待时间"""
        # 基础等待时间（指数退避）
        base_wait = self.base_wait_time * (2 ** attempt)
        
        # 根据失败类型调整
        type_multipliers = {
            FailureType.ELEMENT_NOT_FOUND: 0.5,  # 元素查找失败，快速重试
            FailureType.CLICK_FAILED: 0.3,       # 点击失败，很快重试
            FailureType.OCR_FAILED: 1.0,         # OCR失败，正常等待
            FailureType.TIMEOUT: 2.0,            # 超时，等待更久
            FailureType.NETWORK_ERROR: 3.0,      # 网络错误，等待最久
            FailureType.PERMISSION_DENIED: 1.5,  # 权限错误，适中等待
            FailureType.UNKNOWN: 1.0             # 未知错误，正常等待
        }
        
        multiplier = type_multipliers.get(failure_type, 1.0)
        wait_time = base_wait * multiplier
        
        # 添加随机抖动，避免同时重试
        jitter = random.uniform(0.8, 1.2)
        wait_time *= jitter
        
        # 限制最大等待时间
        return min(wait_time, self.max_wait_time)
    
    def _record_success(self, context: RetryContext, attempts: int):
        """记录成功统计"""
        operation_type = context.operation_type
        if operation_type not in self.failure_stats:
            self.failure_stats[operation_type] = {
                'total_attempts': 0,
                'successful_attempts': 0,
                'avg_retry_count': 0
            }
        
        stats = self.failure_stats[operation_type]
        stats['total_attempts'] += 1
        stats['successful_attempts'] += 1
        
        # 更新平均重试次数
        total_retries = stats.get('total_retries', 0) + attempts
        stats['total_retries'] = total_retries
        stats['avg_retry_count'] = total_retries / stats['successful_attempts']
    
    def _record_failure(self, context: RetryContext, attempts: int):
        """记录失败统计"""
        operation_type = context.operation_type
        if operation_type not in self.failure_stats:
            self.failure_stats[operation_type] = {
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0
            }
        
        stats = self.failure_stats[operation_type]
        stats['total_attempts'] += 1
        stats['failed_attempts'] = stats.get('failed_attempts', 0) + 1
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """获取重试统计信息"""
        return {
            'operation_stats': self.failure_stats,
            'config': {
                'max_retries': self.max_retries,
                'base_wait_time': self.base_wait_time,
                'max_wait_time': self.max_wait_time
            }
        }
    
    def optimize_retry_parameters(self):
        """基于历史数据优化重试参数"""
        print("[INFO] 基于历史数据优化重试参数...")
        
        total_operations = sum(stats.get('total_attempts', 0) for stats in self.failure_stats.values())
        
        if total_operations < 10:
            print("[INFO] 数据量不足，暂不优化")
            return
        
        # 计算整体成功率
        total_success = sum(stats.get('successful_attempts', 0) for stats in self.failure_stats.values())
        success_rate = total_success / total_operations if total_operations > 0 else 0
        
        # 根据成功率调整最大重试次数
        if success_rate < 0.7:
            self.max_retries = min(self.max_retries + 1, 8)
            print(f"[OPTIMIZE] 成功率较低({success_rate:.1%})，增加最大重试次数到 {self.max_retries}")
        elif success_rate > 0.95:
            self.max_retries = max(self.max_retries - 1, 3)
            print(f"[OPTIMIZE] 成功率很高({success_rate:.1%})，减少最大重试次数到 {self.max_retries}")


# 使用示例
if __name__ == "__main__":
    # 创建重试管理器
    retry_manager = IntelligentRetryManager()
    
    # 模拟操作函数
    def mock_operation(context: RetryContext) -> OperationResult:
        """模拟操作"""
        # 模拟随机失败
        import random
        if random.random() < 0.7:  # 70%失败率
            return OperationResult(False, "模拟操作失败", failure_type=FailureType.ELEMENT_NOT_FOUND)
        else:
            return OperationResult(True, "操作成功", {"result": "success"})
    
    # 创建重试上下文
    context = RetryContext(
        operation_type="test_click",
        target="test_button",
        parameters={}
    )
    
    # 执行带重试的操作
    result = retry_manager.execute_with_retry(mock_operation, context)
    
    print(f"\n最终结果: {result}")
    print(f"重试统计: {retry_manager.get_retry_statistics()}")
