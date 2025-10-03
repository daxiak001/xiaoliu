# -*- coding: utf-8 -*-
"""
键盘控制器 (KeyboardController)
功能：控制键盘输入，就像AI会打字，能输入文字和使用快捷键

核心功能:
- 输入文字 (就像在键盘上打字，AI能输入任何文字)
- 按单个按键 (例如：按回车键、ESC键等)
- 按快捷键组合 (例如：Ctrl+C复制、Ctrl+V粘贴等)
- 智能输入和安全控制 (防止误操作，支持输入验证)

版本: v2.0.0
"""

import time
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import re

try:
    import pyautogui
    import keyboard
    import win32api
    import win32con
    KEYBOARD_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 键盘控制依赖库未安装: {e}")
    print("[INFO] 请安装: pip install pyautogui keyboard pywin32")
    KEYBOARD_AVAILABLE = False


class SpecialKey(Enum):
    """特殊按键枚举"""
    ENTER = "enter"
    ESC = "escape"
    TAB = "tab"
    SPACE = "space"
    BACKSPACE = "backspace"
    DELETE = "delete"
    HOME = "home"
    END = "end"
    PAGE_UP = "pageup"
    PAGE_DOWN = "pagedown"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"
    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"
    WIN = "win"


class KeyboardController:
    """
    键盘控制器
    
    功能：控制键盘输入
    简单说明：就像AI会打字，能输入文字和使用快捷键
    """
    
    def __init__(self):
        """初始化键盘控制器"""
        
        # 键盘控制配置
        self.config = {
            'typing_interval': 0.02,    # 打字间隔
            'key_press_duration': 0.1,  # 按键持续时间
            'hotkey_delay': 0.1,        # 快捷键延迟
            'max_input_length': 10000,  # 最大输入长度
            'enable_safety_check': True, # 启用安全检查
            'blocked_keys': ['win+r', 'ctrl+alt+del'], # 禁用的危险按键
            'typing_speed': 'normal'    # 打字速度: slow, normal, fast
        }
        
        if not KEYBOARD_AVAILABLE:
            print("[ERROR] 键盘控制功能不可用，请安装必要的依赖库")
            return
        
        # 配置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05  # 键盘操作间隔更短
        
        # 打字速度配置
        self.typing_speeds = {
            'slow': 0.1,     # 慢速打字
            'normal': 0.02,  # 正常速度
            'fast': 0.005    # 快速打字
        }
        
        # 操作历史记录
        self.operation_history = []
        
        # 常用快捷键映射
        self.common_hotkeys = {
            'copy': 'ctrl+c',
            'paste': 'ctrl+v',
            'cut': 'ctrl+x',
            'undo': 'ctrl+z',
            'redo': 'ctrl+y',
            'select_all': 'ctrl+a',
            'save': 'ctrl+s',
            'open': 'ctrl+o',
            'new': 'ctrl+n',
            'find': 'ctrl+f',
            'replace': 'ctrl+h',
            'close': 'ctrl+w',
            'quit': 'alt+f4',
            'refresh': 'f5',
            'fullscreen': 'f11'
        }
        
        print("[INFO] 键盘控制器初始化完成")
    
    def type_text(self, text: str, interval: float = None, 
                 validate_input: bool = True) -> bool:
        """
        输入文字
        
        功能说明：就像在键盘上打字，AI能输入任何文字
        
        参数:
            text: 要输入的文字
            interval: 打字间隔 (秒)
            validate_input: 是否验证输入
            
        返回:
            bool: 操作是否成功
        """
        if not KEYBOARD_AVAILABLE:
            print("[ERROR] 键盘控制功能不可用")
            return False
        
        try:
            print(f"[INFO] 输入文字: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # 验证输入
            if validate_input and not self._validate_input(text):
                return False
            
            # 使用指定间隔或配置的间隔
            if interval is None:
                speed = self.config['typing_speed']
                interval = self.typing_speeds.get(speed, self.config['typing_interval'])
            
            # 分段输入长文本
            if len(text) > 1000:
                return self._type_long_text(text, interval)
            else:
                return self._type_short_text(text, interval)
                
        except Exception as e:
            print(f"[ERROR] 文字输入异常: {str(e)}")
            return False
    
    def press_key(self, key: Union[str, SpecialKey], duration: float = None) -> bool:
        """
        按单个按键
        
        功能说明：例如：按回车键、ESC键等
        
        参数:
            key: 按键 (字符串或SpecialKey枚举)
            duration: 按键持续时间
            
        返回:
            bool: 操作是否成功
        """
        if not KEYBOARD_AVAILABLE:
            print("[ERROR] 键盘控制功能不可用")
            return False
        
        try:
            # 处理按键名称
            if isinstance(key, SpecialKey):
                key_name = key.value
            else:
                key_name = str(key).lower()
            
            print(f"[INFO] 按键: {key_name}")
            
            # 安全检查
            if self.config['enable_safety_check'] and not self._is_key_safe(key_name):
                print(f"[ERROR] 按键被安全策略阻止: {key_name}")
                return False
            
            # 使用指定持续时间或默认值
            if duration is None:
                duration = self.config['key_press_duration']
            
            # 执行按键
            success = self._perform_key_press(key_name, duration)
            
            if success:
                # 记录操作
                self._record_operation('press_key', {
                    'key': key_name,
                    'duration': duration,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 按键操作完成: {key_name}")
            else:
                print(f"[ERROR] 按键操作失败: {key_name}")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 按键操作异常: {str(e)}")
            return False
    
    def press_hotkey(self, hotkey: Union[str, List[str]], delay: float = None) -> bool:
        """
        按快捷键组合
        
        功能说明：例如：Ctrl+C复制、Ctrl+V粘贴等
        
        参数:
            hotkey: 快捷键组合 (如 'ctrl+c' 或 ['ctrl', 'c'])
            delay: 按键延迟
            
        返回:
            bool: 操作是否成功
        """
        if not KEYBOARD_AVAILABLE:
            print("[ERROR] 键盘控制功能不可用")
            return False
        
        try:
            # 处理快捷键格式
            if isinstance(hotkey, list):
                hotkey_str = '+'.join(hotkey)
            else:
                hotkey_str = str(hotkey).lower()
            
            print(f"[INFO] 快捷键: {hotkey_str}")
            
            # 检查是否是常用快捷键
            if hotkey_str in self.common_hotkeys.values():
                action_name = next(k for k, v in self.common_hotkeys.items() if v == hotkey_str)
                print(f"[INFO] 执行常用操作: {action_name}")
            
            # 安全检查
            if self.config['enable_safety_check'] and not self._is_hotkey_safe(hotkey_str):
                print(f"[ERROR] 快捷键被安全策略阻止: {hotkey_str}")
                return False
            
            # 使用指定延迟或默认值
            if delay is None:
                delay = self.config['hotkey_delay']
            
            # 执行快捷键
            success = self._perform_hotkey(hotkey_str, delay)
            
            if success:
                # 记录操作
                self._record_operation('press_hotkey', {
                    'hotkey': hotkey_str,
                    'delay': delay,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 快捷键操作完成: {hotkey_str}")
            else:
                print(f"[ERROR] 快捷键操作失败: {hotkey_str}")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 快捷键操作异常: {str(e)}")
            return False
    
    def press_common_hotkey(self, action: str) -> bool:
        """
        按常用快捷键
        
        参数:
            action: 操作名称 (如 'copy', 'paste', 'save' 等)
            
        返回:
            bool: 操作是否成功
        """
        if action.lower() in self.common_hotkeys:
            hotkey = self.common_hotkeys[action.lower()]
            print(f"[INFO] 执行常用操作: {action} ({hotkey})")
            return self.press_hotkey(hotkey)
        else:
            print(f"[ERROR] 未知的常用操作: {action}")
            available_actions = ', '.join(self.common_hotkeys.keys())
            print(f"[INFO] 可用操作: {available_actions}")
            return False
    
    def clear_input(self, method: str = 'select_all') -> bool:
        """
        清空当前输入
        
        参数:
            method: 清空方法 ('select_all', 'ctrl_a', 'backspace')
            
        返回:
            bool: 操作是否成功
        """
        try:
            print(f"[INFO] 清空输入，方法: {method}")
            
            if method == 'select_all' or method == 'ctrl_a':
                # 全选然后删除
                if self.press_hotkey('ctrl+a'):
                    time.sleep(0.1)
                    return self.press_key(SpecialKey.DELETE)
            elif method == 'backspace':
                # 连续按退格键 (适用于短文本)
                for _ in range(50):  # 最多删除50个字符
                    if not self.press_key(SpecialKey.BACKSPACE):
                        break
                    time.sleep(0.01)
                return True
            else:
                print(f"[ERROR] 不支持的清空方法: {method}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 清空输入异常: {str(e)}")
            return False
    
    def input_with_clear(self, text: str, clear_first: bool = True) -> bool:
        """
        清空后输入文字
        
        参数:
            text: 要输入的文字
            clear_first: 是否先清空
            
        返回:
            bool: 操作是否成功
        """
        try:
            if clear_first:
                if not self.clear_input():
                    print("[WARNING] 清空输入失败，继续输入")
                time.sleep(0.2)  # 等待清空完成
            
            return self.type_text(text)
            
        except Exception as e:
            print(f"[ERROR] 清空后输入异常: {str(e)}")
            return False
    
    def _validate_input(self, text: str) -> bool:
        """验证输入文字"""
        # 检查长度
        if len(text) > self.config['max_input_length']:
            print(f"[ERROR] 输入文字过长: {len(text)} > {self.config['max_input_length']}")
            return False
        
        # 检查是否包含危险字符或命令
        dangerous_patterns = [
            r'rm\s+-rf',      # Linux删除命令
            r'del\s+/[sf]',   # Windows删除命令
            r'format\s+c:',   # 格式化命令
            r'shutdown',      # 关机命令
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower):
                print(f"[ERROR] 输入包含危险命令模式: {pattern}")
                return False
        
        return True
    
    def _is_key_safe(self, key: str) -> bool:
        """检查单个按键是否安全"""
        # 一般单个按键都是安全的
        dangerous_keys = ['win+r', 'ctrl+alt+del']
        return key not in dangerous_keys
    
    def _is_hotkey_safe(self, hotkey: str) -> bool:
        """检查快捷键是否安全"""
        return hotkey not in self.config['blocked_keys']
    
    def _type_short_text(self, text: str, interval: float) -> bool:
        """输入短文本"""
        try:
            pyautogui.write(text, interval=interval)
            
            # 记录操作
            self._record_operation('type_text', {
                'text_length': len(text),
                'text_preview': text[:100],
                'interval': interval,
                'timestamp': time.time()
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 短文本输入失败: {str(e)}")
            return False
    
    def _type_long_text(self, text: str, interval: float) -> bool:
        """输入长文本 (分段处理)"""
        try:
            chunk_size = 500  # 每次输入500个字符
            total_chunks = (len(text) + chunk_size - 1) // chunk_size
            
            print(f"[INFO] 长文本分段输入: {len(text)}字符, {total_chunks}段")
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                chunk_num = i // chunk_size + 1
                
                print(f"[INFO] 输入第{chunk_num}/{total_chunks}段...")
                
                if not self._type_short_text(chunk, interval):
                    print(f"[ERROR] 第{chunk_num}段输入失败")
                    return False
                
                # 段间短暂停顿
                if i + chunk_size < len(text):
                    time.sleep(0.1)
            
            print("[SUCCESS] 长文本输入完成")
            return True
            
        except Exception as e:
            print(f"[ERROR] 长文本输入失败: {str(e)}")
            return False
    
    def _perform_key_press(self, key: str, duration: float) -> bool:
        """执行按键操作"""
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            return True
        except Exception as e:
            print(f"[ERROR] 按键执行失败: {str(e)}")
            return False
    
    def _perform_hotkey(self, hotkey: str, delay: float) -> bool:
        """执行快捷键操作"""
        try:
            # 解析快捷键
            keys = hotkey.split('+')
            keys = [key.strip() for key in keys]
            
            # 按下所有键
            for key in keys:
                pyautogui.keyDown(key)
                time.sleep(0.01)
            
            # 等待
            time.sleep(delay)
            
            # 释放所有键 (逆序)
            for key in reversed(keys):
                pyautogui.keyUp(key)
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 快捷键执行失败: {str(e)}")
            return False
    
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
        print("[INFO] 键盘操作历史已清空")
    
    def set_typing_speed(self, speed: str):
        """设置打字速度"""
        if speed in self.typing_speeds:
            self.config['typing_speed'] = speed
            print(f"[INFO] 打字速度设置为: {speed}")
        else:
            available_speeds = ', '.join(self.typing_speeds.keys())
            print(f"[ERROR] 无效的打字速度: {speed}, 可用选项: {available_speeds}")
    
    def get_common_hotkeys(self) -> Dict[str, str]:
        """获取常用快捷键列表"""
        return self.common_hotkeys.copy()
    
    def add_custom_hotkey(self, name: str, hotkey: str):
        """添加自定义快捷键"""
        self.common_hotkeys[name.lower()] = hotkey.lower()
        print(f"[INFO] 添加自定义快捷键: {name} = {hotkey}")
    
    def get_controller_status(self) -> Dict[str, Any]:
        """获取控制器状态"""
        return {
            'available': KEYBOARD_AVAILABLE,
            'config': self.config,
            'operation_count': len(self.operation_history),
            'common_hotkeys_count': len(self.common_hotkeys),
            'last_operation': self.operation_history[-1] if self.operation_history else None
        }


# 使用示例
if __name__ == "__main__":
    # 创建键盘控制器实例
    keyboard_ctrl = KeyboardController()
    
    print("=== 键盘控制器测试 ===")
    
    # 获取控制器状态
    status = keyboard_ctrl.get_controller_status()
    print(f"键盘控制可用性: {status['available']}")
    
    if KEYBOARD_AVAILABLE:
        print("\n=== 功能测试 ===")
        
        # 测试文字输入
        print("1. 测试文字输入...")
        test_text = "Hello, World! 你好，世界！"
        if keyboard_ctrl.type_text(test_text):
            print(f"文字输入测试成功: {test_text}")
        
        time.sleep(1)
        
        # 测试按键
        print("2. 测试按键...")
        if keyboard_ctrl.press_key(SpecialKey.ENTER):
            print("回车键测试成功")
        
        time.sleep(1)
        
        # 测试快捷键
        print("3. 测试快捷键...")
        if keyboard_ctrl.press_hotkey('ctrl+a'):
            print("全选快捷键测试成功")
        
        time.sleep(1)
        
        # 测试常用快捷键
        print("4. 测试常用快捷键...")
        if keyboard_ctrl.press_common_hotkey('copy'):
            print("复制操作测试成功")
        
        # 获取操作历史
        history = keyboard_ctrl.get_operation_history()
        print(f"操作历史记录数: {len(history)}")
        
        # 获取常用快捷键
        hotkeys = keyboard_ctrl.get_common_hotkeys()
        print(f"常用快捷键数量: {len(hotkeys)}")
        
        print("\n=== 测试完成 ===")
    else:
        print("请安装键盘控制依赖库后重试")
