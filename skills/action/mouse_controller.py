# -*- coding: utf-8 -*-
"""
鼠标控制器 (MouseController)
功能：控制鼠标操作，就像AI有了一只手，能进行各种鼠标操作

核心功能:
- 点击操作 (就像用手指点击屏幕上的某个位置)
- 拖拽操作 (就像用手指按住某个东西，然后拖到另一个地方)
- 滚动操作 (就像用手指滑动屏幕，向上或向下滚动)
- 精确定位和智能重试 (准确点击目标位置，失败时自动重试)

版本: v2.0.0
"""

import time
from typing import Tuple, Optional, List, Dict, Any
from enum import Enum
import random

try:
    import pyautogui
    import win32api
    import win32con
    import win32gui
    MOUSE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 鼠标控制依赖库未安装: {e}")
    print("[INFO] 请安装: pip install pyautogui pywin32")
    MOUSE_AVAILABLE = False


class MouseButton(Enum):
    """鼠标按钮枚举"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ClickType(Enum):
    """点击类型枚举"""
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"


class MouseController:
    """
    鼠标控制器
    
    功能：控制鼠标操作
    简单说明：就像AI有了一只手，能进行各种鼠标操作
    """
    
    def __init__(self):
        """初始化鼠标控制器"""
        
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用，请安装必要的依赖库")
            return
        
        # 配置pyautogui
        pyautogui.FAILSAFE = True  # 启用安全模式，鼠标移到左上角停止
        pyautogui.PAUSE = 0.1      # 操作间隔
        
        # 鼠标控制配置
        self.config = {
            'click_delay': 0.1,        # 点击延迟
            'move_duration': 0.3,      # 移动持续时间
            'drag_duration': 0.5,      # 拖拽持续时间
            'scroll_delay': 0.1,       # 滚动延迟
            'retry_count': 3,          # 重试次数
            'retry_delay': 0.5,        # 重试延迟
            'position_tolerance': 5,   # 位置容差(像素)
            'human_like_movement': True, # 启用人性化移动
            'safety_margin': 10        # 安全边距(像素)
        }
        
        # 操作历史记录
        self.operation_history = []
        
        # 当前鼠标位置
        self.current_position = self._get_mouse_position()
        
        print("[INFO] 鼠标控制器初始化完成")
    
    def click(self, x: int, y: int, button: MouseButton = MouseButton.LEFT, 
             click_type: ClickType = ClickType.SINGLE, 
             duration: float = None) -> bool:
        """
        点击操作
        
        功能说明：就像用手指点击屏幕上的某个位置
        
        参数:
            x: X坐标
            y: Y坐标
            button: 鼠标按钮类型
            click_type: 点击类型
            duration: 移动持续时间
            
        返回:
            bool: 操作是否成功
        """
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用")
            return False
        
        try:
            print(f"[INFO] 执行{click_type.value}点击: ({x}, {y}), 按钮: {button.value}")
            
            # 验证坐标有效性
            if not self._validate_coordinates(x, y):
                print(f"[ERROR] 坐标无效: ({x}, {y})")
                return False
            
            # 移动到目标位置
            if not self._move_to_position(x, y, duration):
                print("[ERROR] 移动到目标位置失败")
                return False
            
            # 执行点击
            success = self._perform_click(button, click_type)
            
            if success:
                # 记录操作
                self._record_operation('click', {
                    'position': (x, y),
                    'button': button.value,
                    'click_type': click_type.value,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 点击操作完成: ({x}, {y})")
            else:
                print(f"[ERROR] 点击操作失败: ({x}, {y})")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 点击操作异常: {str(e)}")
            return False
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int,
                     duration: float = None, button: MouseButton = MouseButton.LEFT) -> bool:
        """
        拖拽操作
        
        功能说明：就像用手指按住某个东西，然后拖到另一个地方
        
        参数:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖拽持续时间
            button: 鼠标按钮
            
        返回:
            bool: 操作是否成功
        """
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用")
            return False
        
        try:
            print(f"[INFO] 执行拖拽操作: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            
            # 验证坐标
            if not (self._validate_coordinates(start_x, start_y) and 
                   self._validate_coordinates(end_x, end_y)):
                print("[ERROR] 拖拽坐标无效")
                return False
            
            # 使用指定的持续时间或默认值
            if duration is None:
                duration = self.config['drag_duration']
            
            # 执行拖拽
            if self.config['human_like_movement']:
                success = self._human_like_drag(start_x, start_y, end_x, end_y, duration, button)
            else:
                success = self._direct_drag(start_x, start_y, end_x, end_y, duration, button)
            
            if success:
                # 记录操作
                self._record_operation('drag_and_drop', {
                    'start_position': (start_x, start_y),
                    'end_position': (end_x, end_y),
                    'duration': duration,
                    'button': button.value,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 拖拽操作完成")
            else:
                print(f"[ERROR] 拖拽操作失败")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 拖拽操作异常: {str(e)}")
            return False
    
    def get_current_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        
        返回:
            Tuple[int, int]: 当前鼠标的 (x, y) 坐标
        """
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用")
            return 0, 0
        
        try:
            x, y = pyautogui.position()
            return x, y
        except Exception as e:
            print(f"[ERROR] 获取鼠标位置失败: {str(e)}")
            return 0, 0

    def scroll(self, x: int, y: int, direction: str, amount: int = 3) -> bool:
        """
        滚动操作
        
        功能说明：就像用手指滑动屏幕，向上或向下滚动
        
        参数:
            x: 滚动位置X坐标
            y: 滚动位置Y坐标
            direction: 滚动方向 ('up', 'down', 'left', 'right')
            amount: 滚动量
            
        返回:
            bool: 操作是否成功
        """
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用")
            return False
        
        try:
            print(f"[INFO] 执行滚动操作: ({x}, {y}), 方向: {direction}, 量: {amount}")
            
            # 验证坐标
            if not self._validate_coordinates(x, y):
                print(f"[ERROR] 滚动坐标无效: ({x}, {y})")
                return False
            
            # 移动到滚动位置
            if not self._move_to_position(x, y):
                return False
            
            # 执行滚动
            success = self._perform_scroll(direction, amount)
            
            if success:
                # 记录操作
                self._record_operation('scroll', {
                    'position': (x, y),
                    'direction': direction,
                    'amount': amount,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 滚动操作完成")
            else:
                print(f"[ERROR] 滚动操作失败")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 滚动操作异常: {str(e)}")
            return False
    
    def move_to(self, x: int, y: int, duration: float = None) -> bool:
        """
        移动鼠标到指定位置
        
        参数:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间
            
        返回:
            bool: 操作是否成功
        """
        if not MOUSE_AVAILABLE:
            print("[ERROR] 鼠标控制功能不可用")
            return False
        
        try:
            print(f"[INFO] 移动鼠标到: ({x}, {y})")
            
            # 验证坐标
            if not self._validate_coordinates(x, y):
                return False
            
            # 执行移动
            success = self._move_to_position(x, y, duration)
            
            if success:
                self.current_position = (x, y)
                print(f"[SUCCESS] 鼠标移动完成: ({x}, {y})")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 鼠标移动异常: {str(e)}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        
        返回:
            Tuple[int, int]: 鼠标坐标 (x, y)
        """
        try:
            if MOUSE_AVAILABLE:
                position = self._get_mouse_position()
                self.current_position = position
                return position
            else:
                return (0, 0)
        except Exception as e:
            print(f"[ERROR] 获取鼠标位置失败: {str(e)}")
            return (0, 0)
    
    def click_with_retry(self, x: int, y: int, button: MouseButton = MouseButton.LEFT,
                        max_retries: int = None) -> bool:
        """
        带重试的点击操作
        
        参数:
            x: X坐标
            y: Y坐标
            button: 鼠标按钮
            max_retries: 最大重试次数
            
        返回:
            bool: 操作是否成功
        """
        if max_retries is None:
            max_retries = self.config['retry_count']
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"[INFO] 点击重试 {attempt}/{max_retries}")
                time.sleep(self.config['retry_delay'])
            
            if self.click(x, y, button):
                return True
        
        print(f"[ERROR] 点击操作重试{max_retries}次后仍然失败")
        return False
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """验证坐标有效性"""
        try:
            screen_width, screen_height = pyautogui.size()
            
            # 检查坐标是否在屏幕范围内
            if x < 0 or y < 0 or x >= screen_width or y >= screen_height:
                print(f"[ERROR] 坐标超出屏幕范围: ({x}, {y}), 屏幕尺寸: {screen_width}x{screen_height}")
                return False
            
            # 检查安全边距
            margin = self.config['safety_margin']
            if (x < margin or y < margin or 
                x >= screen_width - margin or y >= screen_height - margin):
                print(f"[WARNING] 坐标接近屏幕边缘: ({x}, {y})")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 坐标验证失败: {str(e)}")
            return False
    
    def _move_to_position(self, x: int, y: int, duration: float = None) -> bool:
        """移动到指定位置"""
        try:
            if duration is None:
                duration = self.config['move_duration']
            
            # 人性化移动
            if self.config['human_like_movement']:
                return self._human_like_move(x, y, duration)
            else:
                return self._direct_move(x, y, duration)
                
        except Exception as e:
            print(f"[ERROR] 鼠标移动失败: {str(e)}")
            return False
    
    def _human_like_move(self, x: int, y: int, duration: float) -> bool:
        """人性化鼠标移动"""
        try:
            current_x, current_y = self._get_mouse_position()
            
            # 计算移动距离
            distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
            
            # 如果距离很短，直接移动
            if distance < 10:
                pyautogui.moveTo(x, y, duration=duration)
                return True
            
            # 生成中间路径点
            steps = max(3, int(distance / 50))  # 每50像素一个步骤
            
            for i in range(1, steps + 1):
                # 计算中间点
                progress = i / steps
                intermediate_x = current_x + (x - current_x) * progress
                intermediate_y = current_y + (y - current_y) * progress
                
                # 添加轻微的随机偏移，模拟人手移动
                if i < steps:  # 最后一步不添加偏移
                    offset_x = random.uniform(-2, 2)
                    offset_y = random.uniform(-2, 2)
                    intermediate_x += offset_x
                    intermediate_y += offset_y
                
                # 移动到中间点
                step_duration = duration / steps
                pyautogui.moveTo(int(intermediate_x), int(intermediate_y), duration=step_duration)
                
                # 短暂停顿
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 人性化移动失败: {str(e)}")
            return False
    
    def _direct_move(self, x: int, y: int, duration: float) -> bool:
        """直接移动"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"[ERROR] 直接移动失败: {str(e)}")
            return False
    
    def _perform_click(self, button: MouseButton, click_type: ClickType) -> bool:
        """执行点击"""
        try:
            button_str = button.value
            
            if click_type == ClickType.SINGLE:
                pyautogui.click(button=button_str)
            elif click_type == ClickType.DOUBLE:
                pyautogui.doubleClick(button=button_str)
            elif click_type == ClickType.TRIPLE:
                pyautogui.tripleClick(button=button_str)
            
            # 点击后短暂延迟
            time.sleep(self.config['click_delay'])
            return True
            
        except Exception as e:
            print(f"[ERROR] 执行点击失败: {str(e)}")
            return False
    
    def _human_like_drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
                        duration: float, button: MouseButton) -> bool:
        """人性化拖拽"""
        try:
            # 移动到起始位置
            if not self._move_to_position(start_x, start_y):
                return False
            
            # 按下鼠标
            pyautogui.mouseDown(button=button.value)
            time.sleep(0.1)
            
            # 人性化移动到结束位置
            success = self._human_like_move(end_x, end_y, duration)
            
            # 释放鼠标
            time.sleep(0.1)
            pyautogui.mouseUp(button=button.value)
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 人性化拖拽失败: {str(e)}")
            return False
    
    def _direct_drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
                    duration: float, button: MouseButton) -> bool:
        """直接拖拽"""
        try:
            pyautogui.drag(end_x - start_x, end_y - start_y, 
                          duration=duration, button=button.value)
            return True
        except Exception as e:
            print(f"[ERROR] 直接拖拽失败: {str(e)}")
            return False
    
    def _perform_scroll(self, direction: str, amount: int) -> bool:
        """执行滚动"""
        try:
            if direction.lower() == 'up':
                pyautogui.scroll(amount)
            elif direction.lower() == 'down':
                pyautogui.scroll(-amount)
            elif direction.lower() == 'left':
                pyautogui.hscroll(-amount)
            elif direction.lower() == 'right':
                pyautogui.hscroll(amount)
            else:
                print(f"[ERROR] 不支持的滚动方向: {direction}")
                return False
            
            time.sleep(self.config['scroll_delay'])
            return True
            
        except Exception as e:
            print(f"[ERROR] 执行滚动失败: {str(e)}")
            return False
    
    def _get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"[ERROR] 获取鼠标位置失败: {str(e)}")
            return (0, 0)
    
    def _record_operation(self, operation_type: str, details: Dict[str, Any]):
        """记录操作历史"""
        record = {
            'type': operation_type,
            'details': details,
            'timestamp': time.time()
        }
        
        self.operation_history.append(record)
        
        # 限制历史记录数量
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-50:]
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """获取操作历史"""
        return self.operation_history.copy()
    
    def clear_operation_history(self):
        """清空操作历史"""
        self.operation_history.clear()
        print("[INFO] 鼠标操作历史已清空")
    
    def get_controller_status(self) -> Dict[str, Any]:
        """获取控制器状态"""
        return {
            'available': MOUSE_AVAILABLE,
            'current_position': self.current_position,
            'config': self.config,
            'operation_count': len(self.operation_history),
            'last_operation': self.operation_history[-1] if self.operation_history else None
        }


# 使用示例
if __name__ == "__main__":
    # 创建鼠标控制器实例
    mouse = MouseController()
    
    print("=== 鼠标控制器测试 ===")
    
    # 获取控制器状态
    status = mouse.get_controller_status()
    print(f"鼠标控制可用性: {status['available']}")
    
    if MOUSE_AVAILABLE:
        print(f"当前鼠标位置: {status['current_position']}")
        
        # 测试基本功能
        print("\n=== 功能测试 ===")
        
        # 获取当前位置
        current_pos = mouse.get_mouse_position()
        print(f"当前位置: {current_pos}")
        
        # 测试移动 (移动到屏幕中央)
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        print(f"测试移动到屏幕中央: ({center_x}, {center_y})")
        if mouse.move_to(center_x, center_y):
            print("移动测试成功")
        
        # 测试点击 (在当前位置点击)
        print("测试点击操作...")
        if mouse.click(center_x, center_y):
            print("点击测试成功")
        
        # 获取操作历史
        history = mouse.get_operation_history()
        print(f"操作历史记录数: {len(history)}")
        
        print("\n=== 测试完成 ===")
    else:
        print("请安装鼠标控制依赖库后重试")
