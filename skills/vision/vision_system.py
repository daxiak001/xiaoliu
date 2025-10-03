# -*- coding: utf-8 -*-
"""
视觉感知系统 (VisionSystem)
整合屏幕捕获、OCR识别、元素检测的完整视觉系统

核心功能:
- 统一的视觉接口
- 智能元素定位
- 多策略融合识别
- 视觉缓存优化

版本: v2.0.0
"""

import time
from typing import List, Dict, Optional, Tuple, Any
import numpy as np

try:
    from .screen_capture import ScreenCapture
    from .ocr_engine import OCREngine
    from .element_detector import ElementDetector
    from .multi_ocr_manager import MultiOCRManager
    VISION_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 视觉模块导入失败: {e}")
    VISION_MODULES_AVAILABLE = False


class VisionSystem:
    """
    视觉感知系统
    
    功能：整合所有视觉功能，提供统一的视觉接口
    简单说明：就像AI的"眼睛"，能看到、理解、定位屏幕上的一切
    """
    
    def __init__(self, cache_enabled: bool = True):
        """
        初始化视觉系统
        
        参数:
            cache_enabled: 是否启用视觉缓存
        """
        self.cache_enabled = cache_enabled
        self.vision_cache = {}  # 视觉缓存
        self.last_screenshot = None
        self.last_screenshot_time = 0
        
        if not VISION_MODULES_AVAILABLE:
            print("[ERROR] 视觉模块不可用")
            return
        
        # 初始化各个视觉组件
        try:
            self.screen_capture = ScreenCapture()
            self.ocr_engine = OCREngine()
            self.element_detector = ElementDetector()
            
            # 新增：多OCR引擎管理器
            self.multi_ocr = MultiOCRManager()
            
            print("[INFO] 视觉感知系统初始化完成")
            
        except Exception as e:
            print(f"[ERROR] 视觉系统初始化失败: {str(e)}")
    
    def perceive_screen(self, force_refresh: bool = False):
        """
        感知当前屏幕（兼容接口）
        
        参数:
            force_refresh: 是否强制刷新缓存
            
        返回:
            PIL Image对象或None
        """
        return self.see_screen(force_refresh)
    
    def see_screen(self, force_refresh: bool = False) -> Optional[np.ndarray]:
        """
        看屏幕 - 获取当前屏幕截图
        
        功能说明：就像AI睁开眼睛看屏幕
        
        参数:
            force_refresh: 是否强制刷新 (不使用缓存)
            
        返回:
            numpy.ndarray: 屏幕图像，失败返回None
        """
        if not VISION_MODULES_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return None
        
        try:
            current_time = time.time()
            
            # 检查是否需要使用缓存
            if (not force_refresh and 
                self.cache_enabled and 
                self.last_screenshot is not None and 
                current_time - self.last_screenshot_time < 1.0):  # 1秒内使用缓存
                
                print("[INFO] 使用缓存的屏幕截图")
                return self.last_screenshot
            
            # 获取新的屏幕截图
            screenshot = self.screen_capture.capture_full_screen()
            
            if screenshot is not None:
                self.last_screenshot = screenshot
                self.last_screenshot_time = current_time
                print("[SUCCESS] 屏幕截图获取成功")
            
            return screenshot
            
        except Exception as e:
            print(f"[ERROR] 屏幕截图失败: {str(e)}")
            return None
    
    def read_text_on_screen(self, image):
        """
        读取屏幕文字（兼容接口）
        
        参数:
            image: 屏幕截图
            
        返回:
            str: 屏幕上的文字内容
        """
        text_list = self.read_screen_text(image)
        if text_list:
            return " ".join([item.get('text', '') for item in text_list])
        return ""
    
    def read_screen_text(self, image: Optional[np.ndarray] = None) -> List[Dict]:
        """
        读屏幕文字 - 识别屏幕上的所有文字
        
        功能说明：就像AI能读出屏幕上写的所有内容
        
        参数:
            image: 指定图像，如果为None则使用当前屏幕截图
            
        返回:
            List[Dict]: 识别到的文字列表
        """
        if not VISION_MODULES_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return []
        
        try:
            # 获取图像
            if image is None:
                image = self.see_screen()
                if image is None:
                    return []
            
            # 检查缓存
            cache_key = f"text_{hash(image.tobytes())}"
            if self.cache_enabled and cache_key in self.vision_cache:
                print("[INFO] 使用缓存的文字识别结果")
                return self.vision_cache[cache_key]
            
            # 进行增强OCR识别
            print("[INFO] 使用增强多OCR引擎进行文字识别...")
            
            # 优先使用多OCR引擎管理器
            if hasattr(self, 'multi_ocr') and self.multi_ocr:
                # 将numpy数组转换为PIL Image
                from PIL import Image
                image_pil = Image.fromarray(image)
                
                ocr_result = self.multi_ocr.extract_text(image_pil)
                if ocr_result['success']:
                    # 转换为兼容格式
                    text_results = [{
                        'text': ocr_result['text'],
                        'left': 0, 'top': 0,
                        'width': image_pil.width, 'height': image_pil.height,
                        'conf': int(ocr_result['confidence'] * 100),
                        'engine': ocr_result['engine_used'],
                        'execution_time': ocr_result['execution_time']
                    }]
                    print(f"[SUCCESS] 多OCR引擎识别成功，使用引擎: {ocr_result['engine_used']}")
                else:
                    print("[WARNING] 多OCR引擎失败，降级到传统OCR")
                    text_results = self.ocr_engine.read_screen_text(image)
            else:
                # 降级到原有OCR引擎
                print("[INFO] 使用传统OCR引擎")
                text_results = self.ocr_engine.read_screen_text(image)
            
            # 缓存结果
            if self.cache_enabled:
                self.vision_cache[cache_key] = text_results
            
            return text_results
            
        except Exception as e:
            print(f"[ERROR] 屏幕文字识别失败: {str(e)}")
            return []
    
    def identify_elements(self, image, element_type: str = "all", query: str = None, template = None) -> List[Dict]:
        """
        识别屏幕元素（兼容接口）
        
        参数:
            image: 屏幕截图
            element_type: 元素类型
            query: 查询文本
            template: 模板图像
            
        返回:
            List[Dict]: 找到的元素列表
        """
        if query:
            return self.find_element(query, image)
        else:
            return self.find_element("所有元素", image)
    
    def find_element(self, element_description: str, image: Optional[np.ndarray] = None) -> List[Dict]:
        """
        找元素 - 根据描述查找屏幕元素
        
        功能说明：就像告诉AI"帮我找登录按钮"，AI就能找到
        
        参数:
            element_description: 元素描述 (如"登录按钮", "用户名输入框")
            image: 指定图像，如果为None则使用当前屏幕截图
            
        返回:
            List[Dict]: 找到的元素列表
        """
        if not VISION_MODULES_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return []
        
        try:
            # 获取图像
            if image is None:
                image = self.see_screen()
                if image is None:
                    return []
            
            # 解析元素描述
            element_type, element_text = self._parse_element_description(element_description)
            
            print(f"[INFO] 查找元素: {element_description} (类型: {element_type}, 文字: {element_text})")
            
            # 根据元素类型选择查找策略
            elements = []
            
            if element_type == 'button':
                elements = self.element_detector.find_button(image, element_text)
            elif element_type == 'input':
                elements = self.element_detector.find_input_field(image, element_text)
            elif element_type == 'text':
                # 直接查找文字
                text_matches = self.ocr_engine.find_text_location(image, element_text)
                elements = [self._convert_text_to_element(match) for match in text_matches]
            else:
                # 通用查找：先找文字，再找可点击元素
                text_matches = self.ocr_engine.find_text_location(image, element_text)
                if text_matches:
                    elements = [self._convert_text_to_element(match) for match in text_matches]
                else:
                    # 查找所有可点击元素，然后筛选
                    clickable_elements = self.element_detector.find_clickable_elements(image)
                    elements = self._filter_elements_by_text(clickable_elements, element_text, image)
            
            print(f"[SUCCESS] 找到 {len(elements)} 个匹配元素")
            return elements
            
        except Exception as e:
            print(f"[ERROR] 元素查找失败: {str(e)}")
            return []
    
    def locate_element_precisely(self, element_description: str, 
                               image: Optional[np.ndarray] = None) -> Optional[Tuple[int, int]]:
        """
        精确定位元素 - 返回最佳点击位置
        
        功能说明：找到元素的最佳点击位置
        
        参数:
            element_description: 元素描述
            image: 指定图像
            
        返回:
            Tuple[int, int]: 点击坐标 (x, y)，失败返回None
        """
        try:
            elements = self.find_element(element_description, image)
            
            if not elements:
                print(f"[WARNING] 未找到元素: {element_description}")
                return None
            
            # 选择置信度最高的元素
            best_element = max(elements, key=lambda x: x['confidence'])
            
            # 返回元素中心点
            pos = best_element['position']
            click_x = pos['center_x']
            click_y = pos['center_y']
            
            print(f"[SUCCESS] 元素定位成功: ({click_x}, {click_y}), 置信度: {best_element['confidence']:.2f}")
            return (click_x, click_y)
            
        except Exception as e:
            print(f"[ERROR] 元素定位失败: {str(e)}")
            return None
    
    def analyze_screen_layout(self, image: Optional[np.ndarray] = None) -> Dict:
        """
        分析屏幕布局 - 获取屏幕整体布局信息
        
        功能说明：就像AI能理解整个屏幕的布局结构
        
        参数:
            image: 指定图像
            
        返回:
            Dict: 布局分析结果
        """
        if not VISION_MODULES_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return {}
        
        try:
            # 获取图像
            if image is None:
                image = self.see_screen()
                if image is None:
                    return {}
            
            # 获取所有文字
            all_texts = self.read_screen_text(image)
            
            # 获取所有可点击元素
            clickable_elements = self.element_detector.find_clickable_elements(image)
            
            # 分析布局
            layout_info = {
                'screen_size': {
                    'width': image.shape[1],
                    'height': image.shape[0]
                },
                'text_elements': len(all_texts),
                'clickable_elements': len(clickable_elements),
                'element_distribution': self._analyze_element_distribution(clickable_elements, image.shape),
                'text_regions': self._analyze_text_regions(all_texts),
                'ui_complexity': self._calculate_ui_complexity(all_texts, clickable_elements)
            }
            
            print(f"[SUCCESS] 屏幕布局分析完成")
            print(f"  - 文字元素: {layout_info['text_elements']} 个")
            print(f"  - 可点击元素: {layout_info['clickable_elements']} 个")
            print(f"  - UI复杂度: {layout_info['ui_complexity']:.2f}")
            
            return layout_info
            
        except Exception as e:
            print(f"[ERROR] 屏幕布局分析失败: {str(e)}")
            return {}
    
    def wait_for_element(self, element_description: str, timeout: int = 10, 
                        check_interval: float = 0.5) -> Optional[Tuple[int, int]]:
        """
        等待元素出现 - 等待指定元素在屏幕上出现
        
        功能说明：就像AI耐心等待某个按钮或窗口出现
        
        参数:
            element_description: 元素描述
            timeout: 超时时间 (秒)
            check_interval: 检查间隔 (秒)
            
        返回:
            Tuple[int, int]: 元素位置，超时返回None
        """
        try:
            start_time = time.time()
            
            print(f"[INFO] 等待元素出现: {element_description} (超时: {timeout}秒)")
            
            while time.time() - start_time < timeout:
                # 强制刷新屏幕截图
                position = self.locate_element_precisely(element_description)
                
                if position:
                    elapsed = time.time() - start_time
                    print(f"[SUCCESS] 元素出现，等待时间: {elapsed:.1f}秒")
                    return position
                
                # 等待一段时间后再检查
                time.sleep(check_interval)
            
            print(f"[TIMEOUT] 元素等待超时: {element_description}")
            return None
            
        except Exception as e:
            print(f"[ERROR] 元素等待失败: {str(e)}")
            return None
    
    def _parse_element_description(self, description: str) -> Tuple[str, str]:
        """
        解析元素描述
        
        参数:
            description: 元素描述
            
        返回:
            Tuple[str, str]: (元素类型, 元素文字)
        """
        description_lower = description.lower()
        
        # 识别元素类型
        if '按钮' in description or 'button' in description_lower:
            element_type = 'button'
            # 提取按钮文字
            element_text = description.replace('按钮', '').replace('button', '').strip()
        elif '输入框' in description or '输入' in description or 'input' in description_lower:
            element_type = 'input'
            element_text = description.replace('输入框', '').replace('输入', '').replace('input', '').strip()
        elif '文字' in description or '文本' in description or 'text' in description_lower:
            element_type = 'text'
            element_text = description.replace('文字', '').replace('文本', '').replace('text', '').strip()
        else:
            element_type = 'unknown'
            element_text = description
        
        return element_type, element_text
    
    def _convert_text_to_element(self, text_match: Dict) -> Dict:
        """
        将文字匹配结果转换为元素格式
        """
        return {
            'position': text_match['position'],
            'confidence': text_match['match_score'],
            'detection_method': 'text_recognition',
            'text': text_match['text'],
            'element_type': 'text'
        }
    
    def _filter_elements_by_text(self, elements: List[Dict], target_text: str, 
                                image: np.ndarray) -> List[Dict]:
        """
        根据文字筛选元素
        """
        filtered_elements = []
        
        for element in elements:
            pos = element['position']
            # 提取元素区域的文字
            region_text = self.ocr_engine.extract_text_by_region(
                image, pos['x'], pos['y'], pos['width'], pos['height']
            )
            
            # 检查是否包含目标文字
            if target_text.lower() in region_text.lower():
                element['text'] = region_text
                element['text_match_score'] = len(target_text) / len(region_text) if region_text else 0
                filtered_elements.append(element)
        
        return filtered_elements
    
    def _analyze_element_distribution(self, elements: List[Dict], image_shape: Tuple) -> Dict:
        """
        分析元素分布
        """
        if not elements:
            return {'top': 0, 'middle': 0, 'bottom': 0, 'left': 0, 'center': 0, 'right': 0}
        
        height = image_shape[0]
        width = image_shape[1]
        
        # 垂直分布
        top_count = sum(1 for e in elements if e['position']['center_y'] < height / 3)
        middle_count = sum(1 for e in elements if height / 3 <= e['position']['center_y'] < 2 * height / 3)
        bottom_count = sum(1 for e in elements if e['position']['center_y'] >= 2 * height / 3)
        
        # 水平分布
        left_count = sum(1 for e in elements if e['position']['center_x'] < width / 3)
        center_count = sum(1 for e in elements if width / 3 <= e['position']['center_x'] < 2 * width / 3)
        right_count = sum(1 for e in elements if e['position']['center_x'] >= 2 * width / 3)
        
        return {
            'top': top_count,
            'middle': middle_count,
            'bottom': bottom_count,
            'left': left_count,
            'center': center_count,
            'right': right_count
        }
    
    def _analyze_text_regions(self, texts: List[Dict]) -> Dict:
        """
        分析文字区域
        """
        if not texts:
            return {'total_area': 0, 'average_size': 0, 'density': 0}
        
        total_area = sum(t['position']['width'] * t['position']['height'] for t in texts)
        average_size = total_area / len(texts)
        
        return {
            'total_area': total_area,
            'average_size': average_size,
            'text_count': len(texts),
            'density': len(texts) / (total_area + 1)  # 避免除零
        }
    
    def _calculate_ui_complexity(self, texts: List[Dict], elements: List[Dict]) -> float:
        """
        计算UI复杂度
        """
        # 简单的复杂度计算：基于元素数量和分布
        total_elements = len(texts) + len(elements)
        
        if total_elements == 0:
            return 0.0
        
        # 基础复杂度
        base_complexity = min(total_elements / 50.0, 1.0)  # 50个元素为满复杂度
        
        # 考虑元素类型多样性
        element_types = set()
        for element in elements:
            element_types.add(element.get('element_type', 'unknown'))
        
        type_diversity = len(element_types) / 10.0  # 10种类型为满多样性
        
        # 综合复杂度
        complexity = (base_complexity * 0.7 + type_diversity * 0.3)
        
        return min(complexity, 1.0)
    
    def clear_cache(self):
        """
        清理视觉缓存
        """
        self.vision_cache.clear()
        self.last_screenshot = None
        self.last_screenshot_time = 0
        print("[INFO] 视觉缓存已清理")
    
    def get_system_status(self) -> Dict:
        """
        获取视觉系统状态
        """
        return {
            'modules_available': VISION_MODULES_AVAILABLE,
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self.vision_cache),
            'last_screenshot_time': self.last_screenshot_time,
            'components': {
                'screen_capture': hasattr(self, 'screen_capture'),
                'ocr_engine': hasattr(self, 'ocr_engine'),
                'element_detector': hasattr(self, 'element_detector')
            }
        }


# 使用示例
if __name__ == "__main__":
    # 创建视觉系统实例
    vision = VisionSystem()
    
    print("=== 视觉感知系统测试 ===")
    
    # 获取系统状态
    status = vision.get_system_status()
    print(f"系统状态: {status}")
    
    if VISION_MODULES_AVAILABLE:
        print("\n=== 功能测试 ===")
        
        # 测试屏幕截图
        print("1. 测试屏幕截图...")
        screenshot = vision.see_screen()
        if screenshot is not None:
            print(f"   截图成功，尺寸: {screenshot.shape}")
        
        # 测试文字识别
        print("2. 测试文字识别...")
        texts = vision.read_screen_text()
        print(f"   识别到 {len(texts)} 个文字区域")
        
        # 测试布局分析
        print("3. 测试布局分析...")
        layout = vision.analyze_screen_layout()
        if layout:
            print(f"   布局分析完成，UI复杂度: {layout.get('ui_complexity', 0):.2f}")
        
        print("\n=== 测试完成 ===")
    else:
        print("请安装视觉依赖库后重试")
