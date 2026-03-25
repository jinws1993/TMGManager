# -*- coding: utf-8 -*-
"""数据模型 - Game类定义"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional, List


# 平台映射
PLATFORM_MAP = {
    'nes': 'NES',
    'smc': 'SNES',
    'sfc': 'SNES',
    'gb': 'Game Boy',
    'gbc': 'Game Boy Color',
    'gba': 'Game Boy Advance',
    'nds': 'Nintendo DS',
    '3ds': 'Nintendo 3DS',
    'cia': 'Nintendo 3DS',
    'iso': 'Universal',
    'bin': 'Universal',
    'chd': 'Universal',
    'pce': 'TurboGrafx-16',
    'psp': 'PlayStation Portable',
    'zip': 'Universal',
    '7z': 'Universal',
    'rar': 'Universal',
}

# 平台显示名称
PLATFORM_DISPLAY = {
    'NES': 'Nintendo Entertainment System',
    'SNES': 'Super Nintendo',
    'Game Boy': 'Game Boy',
    'Game Boy Color': 'Game Boy Color',
    'Game Boy Advance': 'Game Boy Advance',
    'Nintendo DS': 'Nintendo DS',
    'Nintendo 3DS': 'Nintendo 3DS',
    'Universal': 'Universal',
    'TurboGrafx-16': 'TurboGrafx-16',
    'PlayStation Portable': 'PlayStation Portable',
}


def get_platform_from_extension(ext: str) -> str:
    """从文件扩展名获取平台名称"""
    ext = ext.lower().lstrip('.')
    return PLATFORM_MAP.get(ext, 'Universal')


def sanitize_filename(name: str) -> str:
    """将游戏名转换为安全的文件名格式"""
    name = name.strip()
    name = re.sub(r'[^\w\s\-\(\)\[\]]', '', name)
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.lower()


def clean_game_name(filename: str) -> str:
    """从ROM文件名中提取干净的游戏名称"""
    name = os.path.splitext(filename)[0]
    name = re.sub(r'[\[\(].*?[\]\)]', '', name)
    name = re.sub(r'\(USA\)|\(Europe\)|\(Japan\)|\(World\)|\(China\)|\(Asia\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(Rev \d+\)|\(V\d+\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'#\d+', '', name)
    name = re.sub(r'[\-_]+', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    return name


@dataclass
class Game:
    """游戏数据类"""
    id: str
    name: str
    file_path: str
    platform: str
    extension: str
    
    # RAWG刮削信息
    rawg_id: Optional[int] = None
    description: str = ""
    genre: str = ""
    players: int = 1
    released: str = ""
    rating: float = 0.0
    
    # 媒体文件路径
    boxart_path: str = ""
    background_path: str = ""
    screenshot_paths: List[str] = field(default_factory=list)
    video_path: str = ""
    
    # 状态
    is_scraped: bool = False
    scrape_error: str = ""
    
    # 可编辑字段
    editable_name: str = ""
    
    def __post_init__(self):
        if not self.editable_name:
            self.editable_name = self.name
    
    @property
    def safe_name(self) -> str:
        """返回安全的文件名格式"""
        return sanitize_filename(self.name)
    
    @property
    def display_name(self) -> str:
        """返回显示名称（优先使用可编辑名称）"""
        return self.editable_name or self.name
    
    @property
    def platform_display(self) -> str:
        """返回平台显示名称"""
        return PLATFORM_DISPLAY.get(self.platform, self.platform)
    
    @property
    def extension_lower(self) -> str:
        """返回小写扩展名"""
        return self.extension.lower().lstrip('.')


@dataclass
class ScrapeResult:
    """刮削结果"""
    success: bool
    game: Optional[Game] = None
    error_message: str = ""
    alternatives: List[dict] = field(default_factory=list)
