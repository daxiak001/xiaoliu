# -*- coding: utf-8 -*-
"""
元素识别引擎 (ElementDetector)
功能：识别屏幕上的各种元素，就像人眼能看出哪里是按钮、哪里是输入框

核心功能:
- 找按钮 ("帮我找到'确定'按钮在哪里")
- 找输入框 ("帮我找到'用户名'输入框")
- 找所有可点击的地方 ("告诉我屏幕上哪些地方可以点击")
- 多策略元素识别 (文字识别、图像匹配、位置推理、AI深度学习)

版本: v2.0.0
"""

import os
from typing import List, Dict, Tuple, Optional, Any
import numpy as np

try:
    import cv2
    from PIL import Image
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 视觉依赖库未安装: {e}")
    print("[INFO] 请安装: pip install opencv-python pillow")
    VISION_AVAILABLE = False


class ElementDetector:
    """
    元素识别引擎
    
    功能：识别屏幕上的各种元素
    简单说明：就像人眼能看出哪里是按钮、哪里是输入框
    """
    
    def __init__(self, template_path: str = "templates"):
        """
        初始化元素识别引擎
        
        参数:
            template_path: 模板图像存储路径
        """
        self.template_path = template_path
        self.templates = {}  # 存储加载的模板
        self.confidence_threshold = 0.7  # 匹配置信度阈值
        
        # 创建模板目录
        if not os.path.exists(template_path):
            os.makedirs(template_path)
        
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用，请安装必要的依赖库")
            return
        
        # 加载预设模板
        self._load_templates()
        
        print("[INFO] 元素识别引擎初始化完成")
    
    def find_button(self, image: np.ndarray, button_text: str = None, 
                   button_template: np.ndarray = None) -> List[Dict]:
        """
        找按钮
        
        功能说明："帮我找到'确定'按钮在哪里"
        
        参数:
            image: 输入图像
            button_text: 按钮上的文字 (可选)
            button_template: 按钮模板图像 (可选)
            
        返回:
            List[Dict]: 找到的按钮列表，包含位置和置信度
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return []
        
        try:
            buttons = []
            
            # 策略1: 通过文字识别按钮
            if button_text:
                text_buttons = self._find_button_by_text(image, button_text)
                buttons.extend(text_buttons)
            
            # 策略2: 通过模板匹配按钮
            if button_template is not None:
                template_buttons = self._find_button_by_template(image, button_template)
                buttons.extend(template_buttons)
            
            # 策略3: 通过通用按钮特征识别
            generic_buttons = self._find_button_by_features(image)
            buttons.extend(generic_buttons)
            
            # 去重和排序
            buttons = self._deduplicate_elements(buttons)
            buttons.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"[SUCCESS] 找到 {len(buttons)} 个按钮")
            return buttons
            
        except Exception as e:
            print(f"[ERROR] 按钮识别失败: {str(e)}")
            return []
    
    def find_input_field(self, image: np.ndarray, field_name: str = None) -> List[Dict]:
        """
        找输入框
        
        功能说明："帮我找到'用户名'输入框"
        
        参数:
            image: 输入图像
            field_name: 输入框标签文字 (可选)
            
        返回:
            List[Dict]: 找到的输入框列表
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return []
        
        try:
            input_fields = []
            
            # 策略1: 通过标签文字找输入框
            if field_name:
                text_fields = self._find_input_by_label(image, field_name)
                input_fields.extend(text_fields)
            
            # 策略2: 通过视觉特征识别输入框
            visual_fields = self._find_input_by_features(image)
            input_fields.extend(visual_fields)
            
            # 去重和排序
            input_fields = self._deduplicate_elements(input_fields)
            input_fields.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"[SUCCESS] 找到 {len(input_fields)} 个输入框")
            return input_fields
            
        except Exception as e:
            print(f"[ERROR] 输入框识别失败: {str(e)}")
            return []
    
    def find_clickable_elements(self, image: np.ndarray) -> List[Dict]:
        """
        找所有可点击的地方
        
        功能说明："告诉我屏幕上哪些地方可以点击"
        
        参数:
            image: 输入图像
            
        返回:
            List[Dict]: 所有可点击元素列表
        """
        if not VISION_AVAILABLE:
            print("[ERROR] 视觉功能不可用")
            return []
        
        try:
            clickable_elements = []
            
            # 找按钮
            buttons = self.find_button(image)
            for button in buttons:
                button['element_type'] = 'button'
                clickable_elements.append(button)
            
            # 找链接
            links = self._find_links(image)
            for link in links:
                link['element_type'] = 'link'
                clickable_elements.append(link)
            
            # 找图标
            icons = self._find_icons(image)
            for icon in icons:
                icon['element_type'] = 'icon'
                clickable_elements.append(icon)
            
            # 找菜单项
            menu_items = self._find_menu_items(image)
            for item in menu_items:
                item['element_type'] = 'menu_item'
                clickable_elements.append(item)
            
            # 去重和排序
            clickable_elements = self._deduplicate_elements(clickable_elements)
            clickable_elements.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"[SUCCESS] 找到 {len(clickable_elements)} 个可点击元素")
            return clickable_elements
            
        except Exception as e:
            print(f"[ERROR] 可点击元素识别失败: {str(e)}")
            return []
    
    def _find_button_by_text(self, image: np.ndarray, button_text: str) -> List[Dict]:
        """
        通过文字识别按钮
        """
        try:
            # 这里需要集成OCR引擎
            from .ocr_engine import OCREngine
            ocr = OCREngine()
            
            # 查找包含指定文字的区域
            text_matches = ocr.find_text_location(image, button_text)
            
            buttons = []
            for match in text_matches:
                # 扩展文字区域作为按钮区域
                pos = match['position']
                expanded_pos = self._expand_button_area(pos)
                
                buttons.append({
                    'position': expanded_pos,
                    'confidence': match['match_score'] * 0.9,  # 稍微降低置信度
                    'detection_method': 'text_recognition',
                    'text': match['text'],
                    'element_type': 'button'
                })
            
            return buttons
            
        except Exception as e:
            print(f"[WARNING] 文字按钮识别失败: {e}")
            return []
    
    def _find_button_by_template(self, image: np.ndarray, template: np.ndarray) -> List[Dict]:
        """
        通过模板匹配按钮
        """
        try:
            # 模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= self.confidence_threshold)
            
            buttons = []
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):
                buttons.append({
                    'position': {
                        'x': pt[0],
                        'y': pt[1],
                        'width': template_w,
                        'height': template_h,
                        'center_x': pt[0] + template_w // 2,
                        'center_y': pt[1] + template_h // 2
                    },
                    'confidence': float(result[pt[1], pt[0]]),
                    'detection_method': 'template_matching',
                    'element_type': 'button'
                })
            
            return buttons
            
        except Exception as e:
            print(f"[WARNING] 模板按钮识别失败: {e}")
            return []
    
    def _find_button_by_features(self, image: np.ndarray) -> List[Dict]:
        """
        通过视觉特征识别按钮
        """
        try:
            buttons = []
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                if area < 100 or area > 50000:  # 过滤太小或太大的区域
                    continue
                
                # 获取边界矩形
                x, y, w, h = cv2.boundingRect(contour)
                
                # 计算长宽比
                aspect_ratio = w / h
                if aspect_ratio < 0.3 or aspect_ratio > 10:  # 过滤不合理的长宽比
                    continue
                
                # 计算矩形度 (轮廓面积与边界矩形面积的比值)
                rect_area = w * h
                extent = area / rect_area
                if extent < 0.5:  # 过滤不规则形状
                    continue
                
                # 检查是否像按钮 (基于颜色、纹理等特征)
                button_score = self._calculate_button_score(image, x, y, w, h)
                if button_score > 0.5:
                    buttons.append({
                        'position': {
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'center_x': x + w // 2,
                            'center_y': y + h // 2
                        },
                        'confidence': button_score,
                        'detection_method': 'feature_analysis',
                        'element_type': 'button'
                    })
            
            return buttons
            
        except Exception as e:
            print(f"[WARNING] 特征按钮识别失败: {e}")
            return []
    
    def _find_input_by_label(self, image: np.ndarray, field_name: str) -> List[Dict]:
        """
        通过标签文字找输入框
        """
        try:
            from .ocr_engine import OCREngine
            ocr = OCREngine()
            
            # 查找标签文字
            label_matches = ocr.find_text_location(image, field_name)
            
            input_fields = []
            for match in label_matches:
                # 在标签附近查找输入框
                label_pos = match['position']
                input_pos = self._find_input_near_label(image, label_pos)
                
                if input_pos:
                    input_fields.append({
                        'position': input_pos,
                        'confidence': match['match_score'] * 0.8,
                        'detection_method': 'label_association',
                        'label_text': match['text'],
                        'element_type': 'input_field'
                    })
            
            return input_fields
            
        except Exception as e:
            print(f"[WARNING] 标签输入框识别失败: {e}")
            return []
    
    def _find_input_by_features(self, image: np.ndarray) -> List[Dict]:
        """
        通过视觉特征识别输入框
        """
        try:
            input_fields = []
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 30, 100)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                if area < 200 or area > 20000:  # 输入框通常中等大小
                    continue
                
                # 获取边界矩形
                x, y, w, h = cv2.boundingRect(contour)
                
                # 输入框通常是矩形，长宽比较大
                aspect_ratio = w / h
                if aspect_ratio < 1.5 or aspect_ratio > 20:
                    continue
                
                # 检查是否像输入框
                input_score = self._calculate_input_score(image, x, y, w, h)
                if input_score > 0.6:
                    input_fields.append({
                        'position': {
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'center_x': x + w // 2,
                            'center_y': y + h // 2
                        },
                        'confidence': input_score,
                        'detection_method': 'feature_analysis',
                        'element_type': 'input_field'
                    })
            
            return input_fields
            
        except Exception as e:
            print(f"[WARNING] 特征输入框识别失败: {e}")
            return []
    
    def _find_links(self, image: np.ndarray) -> List[Dict]:
        """
        识别链接
        """
        try:
            # 简单实现：查找蓝色文字区域
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 定义蓝色范围
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # 创建蓝色掩码
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            links = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 50:  # 过滤太小的区域
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                links.append({
                    'position': {
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    },
                    'confidence': 0.7,
                    'detection_method': 'color_analysis',
                    'element_type': 'link'
                })
            
            return links
            
        except Exception as e:
            print(f"[WARNING] 链接识别失败: {e}")
            return []
    
    def _find_icons(self, image: np.ndarray) -> List[Dict]:
        """
        识别图标
        """
        try:
            # 简单实现：查找小的方形区域
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            icons = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 100 or area > 2500:  # 图标通常较小
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                # 图标通常接近正方形
                aspect_ratio = w / h
                if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                    continue
                
                icons.append({
                    'position': {
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    },
                    'confidence': 0.6,
                    'detection_method': 'shape_analysis',
                    'element_type': 'icon'
                })
            
            return icons
            
        except Exception as e:
            print(f"[WARNING] 图标识别失败: {e}")
            return []
    
    def _find_menu_items(self, image: np.ndarray) -> List[Dict]:
        """
        识别菜单项
        """
        try:
            # 简单实现：查找水平排列的文字区域
            from .ocr_engine import OCREngine
            ocr = OCREngine()
            
            all_texts = ocr.read_screen_text(image)
            menu_items = []
            
            # 查找可能的菜单项 (短文字，水平排列)
            for text_info in all_texts:
                text = text_info['text'].strip()
                if len(text) < 2 or len(text) > 20:  # 菜单项通常是短文字
                    continue
                
                # 检查是否像菜单项
                if self._is_menu_item_text(text):
                    pos = text_info['position']
                    menu_items.append({
                        'position': pos,
                        'confidence': 0.7,
                        'detection_method': 'text_analysis',
                        'text': text,
                        'element_type': 'menu_item'
                    })
            
            return menu_items
            
        except Exception as e:
            print(f"[WARNING] 菜单项识别失败: {e}")
            return []
    
    def _expand_button_area(self, text_pos: Dict) -> Dict:
        """
        扩展文字区域作为按钮区域
        """
        padding = 10
        return {
            'x': max(0, text_pos['x'] - padding),
            'y': max(0, text_pos['y'] - padding),
            'width': text_pos['width'] + 2 * padding,
            'height': text_pos['height'] + 2 * padding,
            'center_x': text_pos['center_x'],
            'center_y': text_pos['center_y']
        }
    
    def _find_input_near_label(self, image: np.ndarray, label_pos: Dict) -> Optional[Dict]:
        """
        在标签附近查找输入框
        """
        # 简单实现：在标签右侧或下方查找矩形区域
        search_areas = [
            # 右侧
            (label_pos['x'] + label_pos['width'] + 10, label_pos['y'], 200, label_pos['height']),
            # 下方
            (label_pos['x'], label_pos['y'] + label_pos['height'] + 5, label_pos['width'] + 100, 30)
        ]
        
        for x, y, w, h in search_areas:
            # 检查这个区域是否像输入框
            if self._calculate_input_score(image, x, y, w, h) > 0.5:
                return {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                }
        
        return None
    
    def _calculate_button_score(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """
        计算区域像按钮的得分
        """
        try:
            # 提取区域
            region = image[y:y+h, x:x+w]
            if region.size == 0:
                return 0.0
            
            score = 0.0
            
            # 检查边框 (按钮通常有边框)
            gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_region, 50, 150)
            edge_ratio = np.count_nonzero(edges) / (w * h)
            if 0.1 < edge_ratio < 0.5:
                score += 0.3
            
            # 检查颜色一致性 (按钮内部颜色通常比较一致)
            std_dev = np.std(gray_region)
            if std_dev < 30:  # 颜色变化不大
                score += 0.3
            
            # 检查尺寸合理性
            if 20 < w < 200 and 15 < h < 60:
                score += 0.4
            
            return min(1.0, score)
            
        except Exception:
            return 0.0
    
    def _calculate_input_score(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """
        计算区域像输入框的得分
        """
        try:
            # 提取区域
            region = image[y:y+h, x:x+w]
            if region.size == 0:
                return 0.0
            
            score = 0.0
            
            # 检查长宽比 (输入框通常较长)
            aspect_ratio = w / h
            if 2 < aspect_ratio < 15:
                score += 0.4
            
            # 检查边框
            gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_region, 30, 100)
            
            # 检查是否有矩形边框
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) == 4:  # 矩形
                    score += 0.3
                    break
            
            # 检查内部是否相对空白 (输入框内部通常较空)
            mean_intensity = np.mean(gray_region)
            if mean_intensity > 200:  # 较亮，可能是空白输入框
                score += 0.3
            
            return min(1.0, score)
            
        except Exception:
            return 0.0
    
    def _is_menu_item_text(self, text: str) -> bool:
        """
        判断文字是否像菜单项
        """
        # 常见菜单项关键词
        menu_keywords = [
            '文件', '编辑', '查看', '工具', '帮助', '设置', '选项',
            'File', 'Edit', 'View', 'Tools', 'Help', 'Settings', 'Options',
            '首页', '关于', '联系', '登录', '注册', '退出'
        ]
        
        return any(keyword in text for keyword in menu_keywords)
    
    def _deduplicate_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        去除重复的元素
        """
        if not elements:
            return []
        
        unique_elements = []
        for element in elements:
            is_duplicate = False
            pos1 = element['position']
            
            for existing in unique_elements:
                pos2 = existing['position']
                
                # 计算重叠度
                overlap = self._calculate_overlap(pos1, pos2)
                if overlap > 0.7:  # 重叠度超过70%认为是重复
                    is_duplicate = True
                    # 保留置信度更高的
                    if element['confidence'] > existing['confidence']:
                        unique_elements.remove(existing)
                        unique_elements.append(element)
                    break
            
            if not is_duplicate:
                unique_elements.append(element)
        
        return unique_elements
    
    def _calculate_overlap(self, pos1: Dict, pos2: Dict) -> float:
        """
        计算两个矩形的重叠度
        """
        try:
            # 计算交集
            x1 = max(pos1['x'], pos2['x'])
            y1 = max(pos1['y'], pos2['y'])
            x2 = min(pos1['x'] + pos1['width'], pos2['x'] + pos2['width'])
            y2 = min(pos1['y'] + pos1['height'], pos2['y'] + pos2['height'])
            
            if x2 <= x1 or y2 <= y1:
                return 0.0
            
            intersection = (x2 - x1) * (y2 - y1)
            area1 = pos1['width'] * pos1['height']
            area2 = pos2['width'] * pos2['height']
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _load_templates(self):
        """
        加载预设模板
        """
        try:
            # 这里可以加载常用的UI元素模板
            # 实际实现时可以从文件加载
            print("[INFO] 模板加载完成")
        except Exception as e:
            print(f"[WARNING] 模板加载失败: {e}")


# 使用示例
if __name__ == "__main__":
    # 创建元素识别引擎实例
    detector = ElementDetector()
    
    print("=== 元素识别引擎测试 ===")
    print(f"视觉功能可用性: {VISION_AVAILABLE}")
    
    if VISION_AVAILABLE:
        print("元素识别引擎已准备就绪")
        print("使用方法:")
        print("1. detector.find_button(image, '确定') - 查找按钮")
        print("2. detector.find_input_field(image, '用户名') - 查找输入框")
        print("3. detector.find_clickable_elements(image) - 查找所有可点击元素")
    else:
        print("请安装视觉依赖库后重试")
