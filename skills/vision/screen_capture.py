# -*- coding: utf-8 -*-
"""
屏幕捕获引擎 (ScreenCapture)
功能：拍摄屏幕"照片"，就像给AI装了一个摄像头

核心功能:
- 拍摄整个屏幕 (就像拍全景照片)
- 拍摄屏幕某个区域 (就像拍摄特写照片)  
- 拍摄某个窗口 (就像只拍某个应用程序)
- 实时监控屏幕变化

版本: v2.0.0
"""

import time
import os
from typing import Optional, Tuple, List
from datetime import datetime

try:
    import pyautogui
    import cv2
    import numpy as np
    from PIL import Image, ImageGrab
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 视觉依赖库未安装: {e}")
    print("[INFO] 请安装: pip install pyautogui opencv-python pillow")
    VISION_AVAILABLE = False


class ScreenCapture:
    """
    屏幕捕获引擎
    
    功能：拍摄屏幕"照片"
    简单说明：就像用手机拍照一样，AI可以随时拍摄屏幕
    """
    
    def __init__(self, save_path: str = "screenshots"):
        """
        初始化屏幕捕获引擎
        
        参数:
            save_path: 截图保存路径
        """
        self.save_path = save_path
        self.screenshot_count = 0
        self.last_screenshot = None
        self.last_screenshot_time = None
        
        # 创建截图保存目录
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        # 检查依赖库
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用，请安装必要的依赖库")
            return
            
        # 配置pyautogui
        pyautogui.FAILSAFE = True  # 启用安全模式
        pyautogui.PAUSE = 0.1      # 操作间隔
        
        print("[INFO] 屏幕捕获引擎初始化完成")
    
    def capture_full_screen(self, save_file: Optional[str] = None) -> Optional[np.ndarray]:
        """
        拍摄整个屏幕
        
        功能说明：就像拍全景照片，把整个屏幕都拍下来
        
        参数:
            save_file: 保存文件名 (可选)
            
        返回:
            numpy.ndarray: 屏幕图像数组，如果失败返回None
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return None
            
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            print(f"[INFO] 屏幕尺寸: {screen_width}x{screen_height}")
            
            # 捕获整个屏幕
            screenshot = pyautogui.screenshot()
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 保存截图
            if save_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_file = f"fullscreen_{timestamp}_{self.screenshot_count:04d}.png"
            
            save_path = os.path.join(self.save_path, save_file)
            cv2.imwrite(save_path, screenshot_cv)
            
            # 更新状态
            self.screenshot_count += 1
            self.last_screenshot = screenshot_cv
            self.last_screenshot_time = time.time()
            
            print(f"[SUCCESS] 全屏截图已保存: {save_path}")
            return screenshot_cv
            
        except Exception as e:
            print(f"[ERROR] 全屏截图失败: {str(e)}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int, 
                      save_file: Optional[str] = None) -> Optional[np.ndarray]:
        """
        拍摄屏幕某个区域
        
        功能说明：就像拍摄特写照片，只拍屏幕的某个部分
        
        参数:
            x: 区域左上角X坐标
            y: 区域左上角Y坐标  
            width: 区域宽度
            height: 区域高度
            save_file: 保存文件名 (可选)
            
        返回:
            numpy.ndarray: 区域图像数组，如果失败返回None
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return None
            
        try:
            # 验证坐标有效性
            screen_width, screen_height = pyautogui.size()
            if x < 0 or y < 0 or x + width > screen_width or y + height > screen_height:
                print(f"[ERROR] 区域坐标超出屏幕范围: ({x},{y},{width},{height})")
                return None
            
            # 捕获指定区域
            region_screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # 转换为OpenCV格式
            region_cv = cv2.cvtColor(np.array(region_screenshot), cv2.COLOR_RGB2BGR)
            
            # 保存截图
            if save_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_file = f"region_{x}_{y}_{width}x{height}_{timestamp}.png"
            
            save_path = os.path.join(self.save_path, save_file)
            cv2.imwrite(save_path, region_cv)
            
            # 更新状态
            self.screenshot_count += 1
            self.last_screenshot = region_cv
            self.last_screenshot_time = time.time()
            
            print(f"[SUCCESS] 区域截图已保存: {save_path}")
            print(f"[INFO] 区域信息: ({x},{y}) 尺寸: {width}x{height}")
            return region_cv
            
        except Exception as e:
            print(f"[ERROR] 区域截图失败: {str(e)}")
            return None
    
    def capture_window(self, window_title: str, save_file: Optional[str] = None) -> Optional[np.ndarray]:
        """
        拍摄某个窗口
        
        功能说明：就像只拍某个应用程序，专门拍摄指定窗口
        
        参数:
            window_title: 窗口标题 (支持部分匹配)
            save_file: 保存文件名 (可选)
            
        返回:
            numpy.ndarray: 窗口图像数组，如果失败返回None
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return None
            
        try:
            # 查找窗口
            windows = pyautogui.getWindowsWithTitle(window_title)
            if not windows:
                print(f"[ERROR] 未找到窗口: {window_title}")
                return None
            
            # 选择第一个匹配的窗口
            target_window = windows[0]
            print(f"[INFO] 找到窗口: {target_window.title}")
            
            # 激活窗口 (确保窗口在前台)
            try:
                target_window.activate()
                time.sleep(0.2)  # 等待窗口激活
            except Exception as e:
                print(f"[WARNING] 无法激活窗口: {e}")
            
            # 获取窗口位置和大小
            left, top, width, height = target_window.left, target_window.top, target_window.width, target_window.height
            print(f"[INFO] 窗口位置: ({left},{top}) 尺寸: {width}x{height}")
            
            # 捕获窗口区域
            window_screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # 转换为OpenCV格式
            window_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
            
            # 保存截图
            if save_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c for c in window_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                save_file = f"window_{safe_title}_{timestamp}.png"
            
            save_path = os.path.join(self.save_path, save_file)
            cv2.imwrite(save_path, window_cv)
            
            # 更新状态
            self.screenshot_count += 1
            self.last_screenshot = window_cv
            self.last_screenshot_time = time.time()
            
            print(f"[SUCCESS] 窗口截图已保存: {save_path}")
            return window_cv
            
        except Exception as e:
            print(f"[ERROR] 窗口截图失败: {str(e)}")
            return None
    
    def monitor_screen_changes(self, interval: float = 1.0, threshold: float = 0.1) -> bool:
        """
        实时监控屏幕变化
        
        功能说明：像监控摄像头一样，持续观察屏幕是否有变化
        
        参数:
            interval: 监控间隔 (秒)
            threshold: 变化阈值 (0-1之间，越小越敏感)
            
        返回:
            bool: 是否检测到变化
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return False
            
        try:
            # 获取当前屏幕截图
            current_screenshot = self.capture_full_screen()
            if current_screenshot is None:
                return False
            
            # 如果没有上一张截图，保存当前截图作为基准
            if self.last_screenshot is None:
                print("[INFO] 开始监控屏幕变化...")
                return False
            
            # 计算图像差异
            diff = cv2.absdiff(self.last_screenshot, current_screenshot)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # 计算变化百分比
            total_pixels = diff_gray.shape[0] * diff_gray.shape[1]
            changed_pixels = np.count_nonzero(diff_gray > 30)  # 阈值30，可调整
            change_percentage = changed_pixels / total_pixels
            
            # 判断是否有显著变化
            has_change = change_percentage > threshold
            
            if has_change:
                print(f"[DETECTED] 屏幕变化: {change_percentage:.2%}")
                # 保存变化区域
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                diff_path = os.path.join(self.save_path, f"change_diff_{timestamp}.png")
                cv2.imwrite(diff_path, diff)
                print(f"[INFO] 变化图像已保存: {diff_path}")
            
            return has_change
            
        except Exception as e:
            print(f"[ERROR] 屏幕变化监控失败: {str(e)}")
            return False
    
    def get_screen_info(self) -> dict:
        """
        获取屏幕信息
        
        返回:
            dict: 屏幕信息字典
        """
        try:
            if not VISION_AVAILABLE:
                return {"error": "视觉功能不可用"}
            
            screen_width, screen_height = pyautogui.size()
            
            return {
                "screen_size": {
                    "width": screen_width,
                    "height": screen_height
                },
                "screenshot_count": self.screenshot_count,
                "last_screenshot_time": self.last_screenshot_time,
                "save_path": self.save_path,
                "vision_available": VISION_AVAILABLE
            }
            
        except Exception as e:
            return {"error": f"获取屏幕信息失败: {str(e)}"}
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            self.last_screenshot = None
            print("[INFO] 屏幕捕获引擎资源已清理")
        except Exception as e:
            print(f"[ERROR] 资源清理失败: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 创建屏幕捕获实例
    capture = ScreenCapture()
    
    # 测试全屏截图
    print("\n=== 测试全屏截图 ===")
    full_screen = capture.capture_full_screen()
    if full_screen is not None:
        print(f"全屏截图成功，尺寸: {full_screen.shape}")
    
    # 测试区域截图
    print("\n=== 测试区域截图 ===")
    region = capture.capture_region(100, 100, 400, 300)
    if region is not None:
        print(f"区域截图成功，尺寸: {region.shape}")
    
    # 获取屏幕信息
    print("\n=== 屏幕信息 ===")
    screen_info = capture.get_screen_info()
    for key, value in screen_info.items():
        print(f"{key}: {value}")
    
    # 清理资源
    capture.cleanup()
    print("\n=== 测试完成 ===")
