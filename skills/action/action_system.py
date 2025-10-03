# -*- coding: utf-8 -*-
"""
操作执行系统 (ActionSystem)
功能：整合鼠标、键盘、窗口管理，执行具体的操作指令

核心功能:
- 执行点击操作
- 执行输入操作
- 执行窗口操作
- 操作序列执行

版本: v2.0.0
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .mouse_controller import MouseController
from .keyboard_controller import KeyboardController
from .window_manager import WindowManager
from .intelligent_retry_manager import IntelligentRetryManager, RetryContext, OperationResult, FailureType


class ActionType(Enum):
    """操作类型枚举"""
    CLICK = "click"
    TYPE = "type"
    KEY_PRESS = "key_press"
    HOTKEY = "hotkey"
    DRAG = "drag"
    SCROLL = "scroll"
    WINDOW_OPEN = "window_open"
    WINDOW_CLOSE = "window_close"
    WINDOW_SWITCH = "window_switch"
    WINDOW_RESIZE = "window_resize"
    WAIT = "wait"


class ActionResult:
    """操作结果"""
    def __init__(self, success: bool, message: str = "", data: Any = None):
        self.success = success
        self.message = message
        self.data = data
        self.timestamp = time.time()
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{status}] {self.message}"


class ActionSystem:
    """
    操作执行系统
    
    功能：整合鼠标、键盘、窗口管理，执行具体的操作指令
    简单说明：就像AI的"手"，能执行各种操作
    """
    
    def __init__(self):
        """初始化操作系统"""
        
        # 初始化各个控制器
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.window = WindowManager()
        
        # 新增：智能重试管理器
        self.retry_manager = IntelligentRetryManager()
        
        # 操作配置
        self.config = {
            'default_delay': 0.5,       # 默认操作延迟
            'retry_count': 3,           # 重试次数
            'timeout': 30,              # 操作超时时间
            'safety_check': True,       # 安全检查
            'enable_intelligent_retry': True,  # 启用智能重试
        }
        
        # 操作历史
        self.action_history = []
        
        print("[INFO] 操作执行系统初始化完成")
    
    def execute_action(self, action_type: str, **kwargs) -> ActionResult:
        """
        执行单个操作
        
        参数:
            action_type: 操作类型
            **kwargs: 操作参数
            
        返回:
            ActionResult: 操作结果
        """
        try:
            print(f"[INFO] 执行操作: {action_type}")
            
            # 记录操作开始
            start_time = time.time()
            
            # 根据操作类型执行相应操作
            if action_type == ActionType.CLICK.value:
                result = self._execute_click(**kwargs)
            elif action_type == ActionType.TYPE.value:
                result = self._execute_type(**kwargs)
            elif action_type == ActionType.KEY_PRESS.value:
                result = self._execute_key_press(**kwargs)
            elif action_type == ActionType.HOTKEY.value:
                result = self._execute_hotkey(**kwargs)
            elif action_type == ActionType.DRAG.value:
                result = self._execute_drag(**kwargs)
            elif action_type == ActionType.SCROLL.value:
                result = self._execute_scroll(**kwargs)
            elif action_type == ActionType.WINDOW_OPEN.value:
                result = self._execute_window_open(**kwargs)
            elif action_type == ActionType.WINDOW_CLOSE.value:
                result = self._execute_window_close(**kwargs)
            elif action_type == ActionType.WINDOW_SWITCH.value:
                result = self._execute_window_switch(**kwargs)
            elif action_type == ActionType.WINDOW_RESIZE.value:
                result = self._execute_window_resize(**kwargs)
            elif action_type == ActionType.WAIT.value:
                result = self._execute_wait(**kwargs)
            else:
                result = ActionResult(False, f"未知操作类型: {action_type}")
            
            # 记录操作历史
            execution_time = time.time() - start_time
            self._record_action(action_type, kwargs, result, execution_time)
            
            return result
            
        except Exception as e:
            error_msg = f"操作执行异常: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return ActionResult(False, error_msg)
    
    def execute_sequence(self, actions: List[Dict[str, Any]]) -> List[ActionResult]:
        """
        执行操作序列
        
        参数:
            actions: 操作列表，每个操作包含 'type' 和其他参数
            
        返回:
            List[ActionResult]: 操作结果列表
        """
        print(f"[INFO] 执行操作序列，共 {len(actions)} 个操作")
        
        results = []
        
        for i, action in enumerate(actions):
            print(f"[INFO] 执行第 {i+1}/{len(actions)} 个操作")
            
            action_type = action.get('type')
            if not action_type:
                result = ActionResult(False, f"操作 {i+1} 缺少类型参数")
                results.append(result)
                continue
            
            # 提取操作参数
            params = {k: v for k, v in action.items() if k != 'type'}
            
            # 执行操作
            result = self.execute_action(action_type, **params)
            results.append(result)
            
            # 如果操作失败且配置了停止策略，则停止执行
            if not result.success and self.config.get('stop_on_failure', False):
                print(f"[WARNING] 操作失败，停止序列执行")
                break
            
            # 操作间延迟
            if i < len(actions) - 1:  # 不是最后一个操作
                delay = action.get('delay', self.config['default_delay'])
                if delay > 0:
                    time.sleep(delay)
        
        success_count = sum(1 for r in results if r.success)
        print(f"[INFO] 操作序列执行完成，成功: {success_count}/{len(results)}")
        
        return results
    
    def _execute_click(self, x: int, y: int, button: str = 'left', **kwargs) -> ActionResult:
        """执行点击操作"""
        try:
            self.mouse.click(x, y, button=button, **kwargs)
            return ActionResult(True, f"点击成功: ({x}, {y})")
        except Exception as e:
            return ActionResult(False, f"点击失败: {str(e)}")
    
    def _execute_type(self, text: str, **kwargs) -> ActionResult:
        """执行输入操作"""
        try:
            self.keyboard.type_text(text, **kwargs)
            return ActionResult(True, f"输入成功: {text[:50]}...")
        except Exception as e:
            return ActionResult(False, f"输入失败: {str(e)}")
    
    def _execute_key_press(self, key: str, **kwargs) -> ActionResult:
        """执行按键操作"""
        try:
            self.keyboard.press_key(key, **kwargs)
            return ActionResult(True, f"按键成功: {key}")
        except Exception as e:
            return ActionResult(False, f"按键失败: {str(e)}")
    
    def _execute_hotkey(self, keys: List[str], **kwargs) -> ActionResult:
        """执行快捷键操作"""
        try:
            self.keyboard.press_hotkey(keys, **kwargs)
            return ActionResult(True, f"快捷键成功: {'+'.join(keys)}")
        except Exception as e:
            return ActionResult(False, f"快捷键失败: {str(e)}")
    
    def _execute_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, **kwargs) -> ActionResult:
        """执行拖拽操作"""
        try:
            self.mouse.drag_and_drop(start_x, start_y, end_x, end_y, **kwargs)
            return ActionResult(True, f"拖拽成功: ({start_x},{start_y}) -> ({end_x},{end_y})")
        except Exception as e:
            return ActionResult(False, f"拖拽失败: {str(e)}")
    
    def _execute_scroll(self, clicks: int, x: int = None, y: int = None, **kwargs) -> ActionResult:
        """执行滚动操作"""
        try:
            self.mouse.scroll(clicks, x, y)
            return ActionResult(True, f"滚动成功: {clicks} 次")
        except Exception as e:
            return ActionResult(False, f"滚动失败: {str(e)}")
    
    def _execute_window_open(self, app_name: str, **kwargs) -> ActionResult:
        """执行打开窗口操作"""
        try:
            success = self.window.open_application(app_name, **kwargs)
            if success:
                return ActionResult(True, f"打开应用成功: {app_name}")
            else:
                return ActionResult(False, f"打开应用失败: {app_name}")
        except Exception as e:
            return ActionResult(False, f"打开应用异常: {str(e)}")
    
    def _execute_window_close(self, app_name: str, **kwargs) -> ActionResult:
        """执行关闭窗口操作"""
        try:
            success = self.window.close_application(app_name, **kwargs)
            if success:
                return ActionResult(True, f"关闭应用成功: {app_name}")
            else:
                return ActionResult(False, f"关闭应用失败: {app_name}")
        except Exception as e:
            return ActionResult(False, f"关闭应用异常: {str(e)}")
    
    def _execute_window_switch(self, window_title: str, **kwargs) -> ActionResult:
        """执行切换窗口操作"""
        try:
            success = self.window.switch_window(window_title, **kwargs)
            if success:
                return ActionResult(True, f"切换窗口成功: {window_title}")
            else:
                return ActionResult(False, f"切换窗口失败: {window_title}")
        except Exception as e:
            return ActionResult(False, f"切换窗口异常: {str(e)}")
    
    def _execute_window_resize(self, window_title: str, width: int, height: int, **kwargs) -> ActionResult:
        """执行调整窗口大小操作"""
        try:
            success = self.window.resize_window(window_title, width, height, **kwargs)
            if success:
                return ActionResult(True, f"调整窗口成功: {window_title} -> {width}x{height}")
            else:
                return ActionResult(False, f"调整窗口失败: {window_title}")
        except Exception as e:
            return ActionResult(False, f"调整窗口异常: {str(e)}")
    
    def _execute_wait(self, duration: float, **kwargs) -> ActionResult:
        """执行等待操作"""
        try:
            print(f"[INFO] 等待 {duration} 秒...")
            time.sleep(duration)
            return ActionResult(True, f"等待完成: {duration} 秒")
        except Exception as e:
            return ActionResult(False, f"等待异常: {str(e)}")
    
    def _record_action(self, action_type: str, params: Dict[str, Any], 
                      result: ActionResult, execution_time: float):
        """记录操作历史"""
        record = {
            'action_type': action_type,
            'params': params,
            'success': result.success,
            'message': result.message,
            'execution_time': execution_time,
            'timestamp': time.time()
        }
        
        self.action_history.append(record)
        
        # 限制历史记录数量
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-500:]
    
    def get_action_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取操作历史"""
        if limit:
            return self.action_history[-limit:]
        return self.action_history.copy()
    
    def clear_action_history(self):
        """清空操作历史"""
        self.action_history.clear()
        print("[INFO] 操作历史已清空")
    
    def get_current_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        try:
            return self.mouse.get_current_position()
        except Exception as e:
            print(f"[ERROR] 获取鼠标位置失败: {str(e)}")
            return (0, 0)
    
    def get_controller_status(self) -> Dict[str, Any]:
        """获取控制器状态"""
        return {
            'initialized': True,
            'mouse_available': self.mouse is not None,
            'keyboard_available': self.keyboard is not None,
            'window_manager_available': self.window is not None,
            'retry_manager_available': hasattr(self, 'retry_manager') and self.retry_manager is not None,
            'config': self.config,
            'action_types': [at.value for at in ActionType]
        }
    
    def execute_with_intelligent_retry(self, action_type: str, **kwargs) -> OperationResult:
        """
        使用智能重试执行操作
        
        参数:
            action_type: 操作类型
            **kwargs: 操作参数
            
        返回:
            OperationResult: 执行结果
        """
        if not self.config.get('enable_intelligent_retry', False):
            # 如果未启用智能重试，使用传统方法
            result = self.execute_action(action_type, **kwargs)
            return OperationResult(result.success if hasattr(result, 'success') else bool(result), 
                                 str(result) if hasattr(result, '__str__') else "操作完成")
        
        # 创建重试上下文
        context = RetryContext(
            operation_type=action_type,
            target=kwargs.get('target', 'unknown'),
            parameters=kwargs
        )
        
        # 定义操作函数
        def operation_func(ctx: RetryContext) -> OperationResult:
            try:
                # 执行实际操作
                result = self.execute_action(ctx.operation_type, **ctx.parameters)
                
                # 转换为OperationResult
                if hasattr(result, 'success'):
                    return result
                elif result:
                    return OperationResult(True, "操作成功", result)
                else:
                    return OperationResult(False, "操作失败", None, failure_type=FailureType.UNKNOWN)
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                # 根据错误信息推断失败类型
                if "not found" in error_msg or "element" in error_msg:
                    failure_type = FailureType.ELEMENT_NOT_FOUND
                elif "click" in error_msg or "mouse" in error_msg:
                    failure_type = FailureType.CLICK_FAILED
                elif "timeout" in error_msg:
                    failure_type = FailureType.TIMEOUT
                else:
                    failure_type = FailureType.UNKNOWN
                
                return OperationResult(False, str(e), None, failure_type=failure_type)
        
        # 使用智能重试执行
        return self.retry_manager.execute_with_retry(operation_func, context)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'mouse_available': hasattr(self.mouse, 'get_current_position'),
            'keyboard_available': hasattr(self.keyboard, 'type_text'),
            'window_available': hasattr(self.window, 'get_all_windows'),
            'action_count': len(self.action_history),
            'config': self.config,
            'last_action': self.action_history[-1] if self.action_history else None
        }


# 使用示例
if __name__ == "__main__":
    # 创建操作系统实例
    action_system = ActionSystem()
    
    print("=== 操作执行系统测试 ===")
    
    # 获取系统状态
    status = action_system.get_system_status()
    print(f"系统状态: {status}")
    
    print("\n=== 单个操作测试 ===")
    
    # 测试等待操作
    result = action_system.execute_action('wait', duration=1)
    print(f"等待操作结果: {result}")
    
    print("\n=== 操作序列测试 ===")
    
    # 测试操作序列
    test_sequence = [
        {'type': 'wait', 'duration': 0.5},
        {'type': 'wait', 'duration': 0.5},
    ]
    
    results = action_system.execute_sequence(test_sequence)
    for i, result in enumerate(results):
        print(f"操作 {i+1} 结果: {result}")
    
    print("\n=== 测试完成 ===")
