# -*- coding: utf-8 -*-
"""
OCR文字识别引擎 (OCREngine)
功能：识别屏幕上的文字，就像AI能"读懂"屏幕上的文字

核心功能:
- 读出屏幕上所有文字 (告诉我屏幕上写了什么)
- 找某个文字在哪里 (帮我找'登录'这两个字在屏幕哪个位置)
- 多语言文字识别 (支持中文、英文等)
- 复杂背景文字识别 (能在复杂背景下准确识别文字)

版本: v2.0.0
"""

import re
from typing import List, Dict, Tuple, Optional
import numpy as np

try:
    import cv2
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] OCR依赖库未安装: {e}")
    print("[INFO] 请安装: pip install pytesseract opencv-python pillow")
    print("[INFO] 并下载安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    OCR_AVAILABLE = False


class OCREngine:
    """
    OCR文字识别引擎
    
    功能：识别屏幕上的文字
    简单说明：就像AI能读出屏幕上写的所有文字
    """
    
    def __init__(self, language: str = 'chi_sim+eng'):
        """
        初始化OCR引擎
        
        参数:
            language: 识别语言 ('chi_sim+eng'=中英文, 'eng'=英文, 'chi_sim'=简体中文)
        """
        self.language = language
        self.confidence_threshold = 30  # 置信度阈值
        
        if not OCR_AVAILABLE:
            print("[ERROR] OCR功能不可用，请安装必要的依赖库")
            return
        
        # 测试Tesseract是否可用
        try:
            pytesseract.get_tesseract_version()
            print(f"[INFO] OCR引擎初始化完成，语言: {language}")
        except Exception as e:
            print(f"[ERROR] Tesseract OCR未正确安装: {e}")
            print("[INFO] 请下载安装: https://github.com/tesseract-ocr/tesseract")
    
    def read_screen_text(self, image: np.ndarray, preprocess: bool = True) -> List[Dict]:
        """
        读出屏幕上所有文字
        
        功能说明：告诉我屏幕上写了什么
        
        参数:
            image: 输入图像 (numpy数组)
            preprocess: 是否进行图像预处理
            
        返回:
            List[Dict]: 识别结果列表，每个元素包含文字、位置、置信度
        """
        if not OCR_AVAILABLE:
            print("[ERROR] OCR功能不可用")
            return []
        
        try:
            # 图像预处理
            if preprocess:
                processed_image = self._preprocess_image(image)
            else:
                processed_image = image
            
            # 使用pytesseract进行OCR识别
            # 获取详细信息：文字、位置、置信度
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # 解析OCR结果
            text_results = []
            n_boxes = len(ocr_data['text'])
            
            for i in range(n_boxes):
                # 过滤置信度低的结果
                confidence = int(ocr_data['conf'][i])
                if confidence < self.confidence_threshold:
                    continue
                
                # 过滤空文本
                text = ocr_data['text'][i].strip()
                if not text:
                    continue
                
                # 获取文字位置
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                width = ocr_data['width'][i]
                height = ocr_data['height'][i]
                
                # 添加到结果列表
                text_results.append({
                    'text': text,
                    'position': {
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'center_x': x + width // 2,
                        'center_y': y + height // 2
                    },
                    'confidence': confidence,
                    'level': ocr_data['level'][i]  # 文字层级 (单词/行/段落)
                })
            
            print(f"[SUCCESS] 识别到 {len(text_results)} 个文字区域")
            return text_results
            
        except Exception as e:
            print(f"[ERROR] 文字识别失败: {str(e)}")
            return []
    
    def find_text_location(self, image: np.ndarray, target_text: str, 
                          fuzzy_match: bool = True) -> List[Dict]:
        """
        找某个文字在哪里
        
        功能说明：帮我找'登录'这两个字在屏幕哪个位置
        
        参数:
            image: 输入图像
            target_text: 要查找的文字
            fuzzy_match: 是否启用模糊匹配
            
        返回:
            List[Dict]: 匹配结果列表，包含位置和匹配度
        """
        if not OCR_AVAILABLE:
            print("[ERROR] OCR功能不可用")
            return []
        
        try:
            # 先识别所有文字
            all_texts = self.read_screen_text(image)
            if not all_texts:
                print("[INFO] 未识别到任何文字")
                return []
            
            # 查找匹配的文字
            matches = []
            target_lower = target_text.lower()
            
            for text_info in all_texts:
                text = text_info['text']
                text_lower = text.lower()
                
                # 精确匹配
                if target_text == text:
                    matches.append({
                        **text_info,
                        'match_type': 'exact',
                        'match_score': 1.0
                    })
                # 包含匹配
                elif target_lower in text_lower:
                    match_score = len(target_text) / len(text)
                    matches.append({
                        **text_info,
                        'match_type': 'contains',
                        'match_score': match_score
                    })
                # 模糊匹配
                elif fuzzy_match and self._fuzzy_match(target_text, text):
                    match_score = self._calculate_similarity(target_text, text)
                    if match_score > 0.6:  # 相似度阈值
                        matches.append({
                            **text_info,
                            'match_type': 'fuzzy',
                            'match_score': match_score
                        })
            
            # 按匹配度排序
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            if matches:
                print(f"[SUCCESS] 找到 {len(matches)} 个匹配的文字: '{target_text}'")
                for i, match in enumerate(matches[:3]):  # 只显示前3个结果
                    pos = match['position']
                    print(f"  {i+1}. '{match['text']}' 位置:({pos['center_x']},{pos['center_y']}) "
                          f"匹配度:{match['match_score']:.2f}")
            else:
                print(f"[INFO] 未找到匹配的文字: '{target_text}'")
            
            return matches
            
        except Exception as e:
            print(f"[ERROR] 文字查找失败: {str(e)}")
            return []
    
    def extract_text_by_region(self, image: np.ndarray, x: int, y: int, 
                              width: int, height: int) -> str:
        """
        提取指定区域的文字
        
        参数:
            image: 输入图像
            x, y: 区域左上角坐标
            width, height: 区域宽高
            
        返回:
            str: 识别到的文字
        """
        if not OCR_AVAILABLE:
            print("[ERROR] OCR功能不可用")
            return ""
        
        try:
            # 裁剪指定区域
            region = image[y:y+height, x:x+width]
            
            # 预处理
            processed_region = self._preprocess_image(region)
            
            # OCR识别
            text = pytesseract.image_to_string(
                processed_region, 
                lang=self.language
            ).strip()
            
            print(f"[SUCCESS] 区域文字识别: '{text}'")
            return text
            
        except Exception as e:
            print(f"[ERROR] 区域文字识别失败: {str(e)}")
            return ""
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理，提高OCR识别准确率
        
        参数:
            image: 输入图像
            
        返回:
            numpy.ndarray: 预处理后的图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 高斯模糊去噪
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 自适应阈值二值化
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作，去除噪点
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            print(f"[WARNING] 图像预处理失败: {e}")
            return image
    
    def _fuzzy_match(self, text1: str, text2: str) -> bool:
        """
        模糊匹配判断
        
        参数:
            text1, text2: 要比较的文字
            
        返回:
            bool: 是否模糊匹配
        """
        # 简单的模糊匹配：去除空格和标点符号后比较
        clean1 = re.sub(r'[^\w]', '', text1.lower())
        clean2 = re.sub(r'[^\w]', '', text2.lower())
        
        # 检查是否有公共子串
        if len(clean1) >= 2 and len(clean2) >= 2:
            return clean1 in clean2 or clean2 in clean1
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文字相似度
        
        参数:
            text1, text2: 要比较的文字
            
        返回:
            float: 相似度 (0-1之间)
        """
        try:
            # 简单的相似度计算：基于编辑距离
            len1, len2 = len(text1), len(text2)
            if len1 == 0 or len2 == 0:
                return 0.0
            
            # 动态规划计算编辑距离
            dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
            
            for i in range(len1 + 1):
                dp[i][0] = i
            for j in range(len2 + 1):
                dp[0][j] = j
            
            for i in range(1, len1 + 1):
                for j in range(1, len2 + 1):
                    if text1[i-1] == text2[j-1]:
                        dp[i][j] = dp[i-1][j-1]
                    else:
                        dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
            
            # 计算相似度
            edit_distance = dp[len1][len2]
            max_len = max(len1, len2)
            similarity = 1.0 - (edit_distance / max_len)
            
            return max(0.0, similarity)
            
        except Exception:
            return 0.0
    
    def get_text_statistics(self, image: np.ndarray) -> Dict:
        """
        获取文字统计信息
        
        参数:
            image: 输入图像
            
        返回:
            Dict: 统计信息
        """
        try:
            all_texts = self.read_screen_text(image)
            
            if not all_texts:
                return {"total_texts": 0, "total_characters": 0}
            
            total_characters = sum(len(item['text']) for item in all_texts)
            avg_confidence = sum(item['confidence'] for item in all_texts) / len(all_texts)
            
            # 按置信度分组
            high_confidence = [t for t in all_texts if t['confidence'] >= 80]
            medium_confidence = [t for t in all_texts if 50 <= t['confidence'] < 80]
            low_confidence = [t for t in all_texts if t['confidence'] < 50]
            
            return {
                "total_texts": len(all_texts),
                "total_characters": total_characters,
                "average_confidence": round(avg_confidence, 2),
                "high_confidence_count": len(high_confidence),
                "medium_confidence_count": len(medium_confidence),
                "low_confidence_count": len(low_confidence),
                "language": self.language
            }
            
        except Exception as e:
            return {"error": f"统计信息获取失败: {str(e)}"}


# 使用示例
if __name__ == "__main__":
    # 创建OCR引擎实例
    ocr = OCREngine()
    
    print("=== OCR引擎测试 ===")
    print(f"OCR可用性: {OCR_AVAILABLE}")
    
    if OCR_AVAILABLE:
        # 这里需要一个测试图像
        # 实际使用时，可以从屏幕捕获模块获取图像
        print("OCR引擎已准备就绪")
        print("使用方法:")
        print("1. ocr.read_screen_text(image) - 识别所有文字")
        print("2. ocr.find_text_location(image, '登录') - 查找特定文字")
        print("3. ocr.extract_text_by_region(image, x, y, w, h) - 识别区域文字")
    else:
        print("请安装OCR依赖库后重试")
