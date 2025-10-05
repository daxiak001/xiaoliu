# -*- coding: utf-8 -*-
"""
小柳核心系统 v5.1
自动导入所有核心模块
"""

# 自动经验记录器 (v1.0新增)
from .auto_experience_recorder import (
    AutoExperienceRecorder,
    get_recorder,
    auto_record
)

__all__ = [
    'AutoExperienceRecorder',
    'get_recorder',
    'auto_record',
]

__version__ = '5.1.0'

