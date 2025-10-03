# -*- coding: utf-8 -*-
"""
视觉感知模块 (VisionSystem)
让AI能够"看到"屏幕内容，识别界面元素

核心组件:
- ScreenCapture: 屏幕捕获引擎
- ElementDetector: 元素识别引擎  
- OCREngine: OCR文字识别引擎
"""

from .screen_capture import ScreenCapture
from .element_detector import ElementDetector
from .ocr_engine import OCREngine
from .vision_system import VisionSystem

__all__ = [
    'ScreenCapture',
    'ElementDetector', 
    'OCREngine',
    'VisionSystem'
]
