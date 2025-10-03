# -*- coding: utf-8 -*-
"""
窗口管理器 (WindowManager)
功能：管理应用程序窗口，就像AI能帮你管理电脑上的各种程序窗口

核心功能:
- 打开应用程序 ("帮我打开记事本")
- 关闭应用程序 ("帮我关闭浏览器")
- 切换窗口 ("切换到QQ窗口")
- 调整窗口大小 ("把窗口调整到800x600")

版本: v2.0.0
"""

import time
import subprocess
import os
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

try:
    import psutil
    import win32gui
    import win32con
    import win32process
    import win32api
    WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 窗口管理依赖库未安装: {e}")
    print("[INFO] 请安装: pip install psutil pywin32")
    WINDOW_AVAILABLE = False


class WindowState(Enum):
    """窗口状态枚举"""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    HIDDEN = "hidden"


class WindowManager:
    """
    窗口管理器
    
    功能：管理应用程序窗口
    简单说明：就像AI能帮你管理电脑上的各种程序窗口
    """
    
    def __init__(self):
        """初始化窗口管理器"""
        
        # 窗口管理配置
        self.config = {
            'search_timeout': 10,       # 搜索超时时间
            'operation_delay': 0.5,     # 操作延迟
            'retry_count': 3,           # 重试次数
            'window_detection_interval': 0.1,  # 窗口检测间隔
        }
        
        if not WINDOW_AVAILABLE:
            print("[ERROR] 窗口管理功能不可用，请安装必要的依赖库")
            return
        
        # 常用应用程序路径
        self.common_apps = {
            'notepad': 'notepad.exe',
            '记事本': 'notepad.exe',
            'calculator': 'calc.exe',
            '计算器': 'calc.exe',
            'paint': 'mspaint.exe',
            '画图': 'mspaint.exe',
            'cmd': 'cmd.exe',
            '命令提示符': 'cmd.exe',
            'explorer': 'explorer.exe',
            '资源管理器': 'explorer.exe',
        }
        
        # 操作历史记录
        self.operation_history = []
        
        print("[INFO] 窗口管理器初始化完成")
    
    def open_application(self, app_name: str, args: str = "", wait_for_window: bool = True) -> bool:
        """
        打开应用程序
        
        功能说明："帮我打开记事本"
        
        参数:
            app_name: 应用程序名称或路径
            args: 启动参数
            wait_for_window: 是否等待窗口出现
            
        返回:
            bool: 操作是否成功
        """
        if not WINDOW_AVAILABLE:
            print("[ERROR] 窗口管理功能不可用")
            return False
        
        try:
            print(f"[INFO] 打开应用程序: {app_name}")
            
            # 获取应用程序路径
            app_path = self._resolve_app_path(app_name)
            if not app_path:
                print(f"[ERROR] 无法找到应用程序: {app_name}")
                return False
            
            # 启动应用程序
            command = f'"{app_path}" {args}'.strip()
            process = subprocess.Popen(command, shell=True)
            
            # 等待窗口出现
            if wait_for_window:
                window_found = self._wait_for_window_by_process(process.pid)
                if not window_found:
                    print(f"[WARNING] 应用程序启动但未检测到窗口")
            
            # 记录操作
            self._record_operation('open_application', {
                'app_name': app_name,
                'app_path': app_path,
                'process_id': process.pid,
                'timestamp': time.time()
            })
            
            print(f"[SUCCESS] 应用程序打开成功: {app_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 打开应用程序失败: {str(e)}")
            return False
    
    def close_application(self, app_name: str, force: bool = False) -> bool:
        """
        关闭应用程序
        
        功能说明："帮我关闭浏览器"
        
        参数:
            app_name: 应用程序名称
            force: 是否强制关闭
            
        返回:
            bool: 操作是否成功
        """
        if not WINDOW_AVAILABLE:
            print("[ERROR] 窗口管理功能不可用")
            return False
        
        try:
            print(f"[INFO] 关闭应用程序: {app_name}")
            
            # 查找应用程序窗口
            windows = self.find_windows_by_title(app_name)
            if not windows:
                print(f"[WARNING] 未找到应用程序窗口: {app_name}")
                return False
            
            success_count = 0
            for window_info in windows:
                hwnd = window_info['hwnd']
                
                if force:
                    # 强制关闭
                    success = self._force_close_window(hwnd)
                else:
                    # 正常关闭
                    success = self._close_window_gracefully(hwnd)
                
                if success:
                    success_count += 1
            
            # 记录操作
            self._record_operation('close_application', {
                'app_name': app_name,
                'windows_closed': success_count,
                'force': force,
                'timestamp': time.time()
            })
            
            if success_count > 0:
                print(f"[SUCCESS] 成功关闭 {success_count} 个窗口")
                return True
            else:
                print(f"[ERROR] 未能关闭任何窗口")
                return False
                
        except Exception as e:
            print(f"[ERROR] 关闭应用程序失败: {str(e)}")
            return False
    
    def switch_window(self, window_title: str) -> bool:
        """
        切换窗口
        
        功能说明："切换到QQ窗口"
        
        参数:
            window_title: 窗口标题
            
        返回:
            bool: 操作是否成功
        """
        if not WINDOW_AVAILABLE:
            print("[ERROR] 窗口管理功能不可用")
            return False
        
        try:
            print(f"[INFO] 切换到窗口: {window_title}")
            
            # 查找窗口
            windows = self.find_windows_by_title(window_title)
            if not windows:
                print(f"[ERROR] 未找到窗口: {window_title}")
                return False
            
            # 选择第一个匹配的窗口
            target_window = windows[0]
            hwnd = target_window['hwnd']
            
            # 激活窗口
            success = self._activate_window(hwnd)
            
            if success:
                # 记录操作
                self._record_operation('switch_window', {
                    'window_title': window_title,
                    'hwnd': hwnd,
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 窗口切换成功: {target_window['title']}")
            else:
                print(f"[ERROR] 窗口切换失败")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 窗口切换异常: {str(e)}")
            return False
    
    def resize_window(self, window_title: str, width: int, height: int, x: int = None, y: int = None) -> bool:
        """
        调整窗口大小
        
        功能说明："把窗口调整到800x600"
        
        参数:
            window_title: 窗口标题
            width: 窗口宽度
            height: 窗口高度
            x: 窗口X位置 (可选)
            y: 窗口Y位置 (可选)
            
        返回:
            bool: 操作是否成功
        """
        if not WINDOW_AVAILABLE:
            print("[ERROR] 窗口管理功能不可用")
            return False
        
        try:
            print(f"[INFO] 调整窗口大小: {window_title} -> {width}x{height}")
            
            # 查找窗口
            windows = self.find_windows_by_title(window_title)
            if not windows:
                print(f"[ERROR] 未找到窗口: {window_title}")
                return False
            
            # 选择第一个匹配的窗口
            target_window = windows[0]
            hwnd = target_window['hwnd']
            
            # 获取当前窗口位置
            if x is None or y is None:
                rect = win32gui.GetWindowRect(hwnd)
                if x is None:
                    x = rect[0]
                if y is None:
                    y = rect[1]
            
            # 调整窗口大小和位置
            success = win32gui.SetWindowPos(
                hwnd, 0, x, y, width, height,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
            
            if success:
                # 记录操作
                self._record_operation('resize_window', {
                    'window_title': window_title,
                    'hwnd': hwnd,
                    'size': (width, height),
                    'position': (x, y),
                    'timestamp': time.time()
                })
                
                print(f"[SUCCESS] 窗口大小调整成功")
            else:
                print(f"[ERROR] 窗口大小调整失败")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 窗口大小调整异常: {str(e)}")
            return False
    
    def find_windows_by_title(self, title_pattern: str) -> List[Dict[str, Any]]:
        """
        根据标题查找窗口
        
        参数:
            title_pattern: 标题模式 (支持部分匹配)
            
        返回:
            List[Dict]: 匹配的窗口列表
        """
        if not WINDOW_AVAILABLE:
            return []
        
        try:
            windows = []
            
            def enum_windows_callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title and title_pattern.lower() in window_title.lower():
                        # 获取窗口信息
                        rect = win32gui.GetWindowRect(hwnd)
                        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                        
                        window_info = {
                            'hwnd': hwnd,
                            'title': window_title,
                            'rect': rect,
                            'process_id': process_id,
                            'visible': win32gui.IsWindowVisible(hwnd),
                            'enabled': win32gui.IsWindowEnabled(hwnd)
                        }
                        windows_list.append(window_info)
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            print(f"[INFO] 找到 {len(windows)} 个匹配窗口: {title_pattern}")
            return windows
            
        except Exception as e:
            print(f"[ERROR] 查找窗口失败: {str(e)}")
            return []
    
    def get_all_windows(self) -> List[Dict[str, Any]]:
        """
        获取所有可见窗口
        
        返回:
            List[Dict]: 所有窗口列表
        """
        return self.find_windows_by_title("")  # 空字符串匹配所有窗口
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """
        获取当前活动窗口
        
        返回:
            Dict: 活动窗口信息，如果没有返回None
        """
        if not WINDOW_AVAILABLE:
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                
                return {
                    'hwnd': hwnd,
                    'title': window_title,
                    'rect': rect,
                    'process_id': process_id,
                    'visible': win32gui.IsWindowVisible(hwnd),
                    'enabled': win32gui.IsWindowEnabled(hwnd)
                }
            
        except Exception as e:
            print(f"[ERROR] 获取活动窗口失败: {str(e)}")
        
        return None
    
    def _resolve_app_path(self, app_name: str) -> Optional[str]:
        """解析应用程序路径"""
        # 检查是否是完整路径
        if os.path.exists(app_name):
            return app_name
        
        # 检查常用应用程序
        if app_name.lower() in self.common_apps:
            return self.common_apps[app_name.lower()]
        
        # 检查是否在系统PATH中
        try:
            result = subprocess.run(['where', app_name], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def _wait_for_window_by_process(self, process_id: int, timeout: int = None) -> bool:
        """等待进程的窗口出现"""
        if timeout is None:
            timeout = self.config['search_timeout']
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 查找该进程的窗口
                def enum_windows_callback(hwnd, _):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == process_id and win32gui.IsWindowVisible(hwnd):
                        return False  # 找到窗口，停止枚举
                    return True
                
                try:
                    win32gui.EnumWindows(enum_windows_callback, None)
                except:
                    # 如果枚举被中断，说明找到了窗口
                    return True
                
                time.sleep(self.config['window_detection_interval'])
                
            except Exception:
                pass
        
        return False
    
    def _activate_window(self, hwnd: int) -> bool:
        """激活窗口"""
        try:
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(self.config['operation_delay'])
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 激活窗口失败: {str(e)}")
            return False
    
    def _close_window_gracefully(self, hwnd: int) -> bool:
        """正常关闭窗口"""
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.config['operation_delay'])
            return True
        except Exception as e:
            print(f"[ERROR] 正常关闭窗口失败: {str(e)}")
            return False
    
    def _force_close_window(self, hwnd: int) -> bool:
        """强制关闭窗口"""
        try:
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(process_id)
            process.terminate()
            time.sleep(self.config['operation_delay'])
            return True
        except Exception as e:
            print(f"[ERROR] 强制关闭窗口失败: {str(e)}")
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
        print("[INFO] 窗口管理操作历史已清空")
    
    def get_manager_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        return {
            'available': WINDOW_AVAILABLE,
            'config': self.config,
            'operation_count': len(self.operation_history),
            'common_apps_count': len(self.common_apps),
            'last_operation': self.operation_history[-1] if self.operation_history else None
        }


# 使用示例
if __name__ == "__main__":
    # 创建窗口管理器实例
    window_mgr = WindowManager()
    
    print("=== 窗口管理器测试 ===")
    
    # 获取管理器状态
    status = window_mgr.get_manager_status()
    print(f"窗口管理可用性: {status['available']}")
    
    if WINDOW_AVAILABLE:
        print("\n=== 功能测试 ===")
        
        # 获取当前活动窗口
        active_window = window_mgr.get_active_window()
        if active_window:
            print(f"当前活动窗口: {active_window['title']}")
        
        # 获取所有窗口
        all_windows = window_mgr.get_all_windows()
        print(f"可见窗口数量: {len(all_windows)}")
        
        # 显示前5个窗口
        for i, window in enumerate(all_windows[:5]):
            print(f"  {i+1}. {window['title']}")
        
        print("\n=== 测试完成 ===")
    else:
        print("请安装窗口管理依赖库后重试")
