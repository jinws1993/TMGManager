# -*- coding: utf-8 -*-
"""ROM文件扫描器"""

import os
import hashlib
from typing import List, Set
from models import Game, get_platform_from_extension, clean_game_name


class ROMScanner:
    """ROM文件扫描器"""
    
    SUPPORTED_EXTENSIONS = {
        'nes', 'smc', 'sfc', 'gb', 'gbc', 'gba', 'nds', '3ds',
        'cia', 'iso', 'bin', 'chd', 'pce', 'psp', 'zip', '7z', 'rar'
    }
    
    def __init__(self):
        self.scanned_games: List[Game] = []
        self._scanned_hashes: Set[str] = set()
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[Game]:
        """扫描目录中的ROM文件"""
        games = []
        
        if not os.path.isdir(directory):
            return games
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower().lstrip('.')
                if ext not in self.SUPPORTED_EXTENSIONS:
                    continue
                
                file_path = os.path.join(root, filename)
                game = self._create_game_from_file(file_path, filename)
                
                if game and game.id not in self._scanned_hashes:
                    games.append(game)
                    self._scanned_hashes.add(game.id)
            
            if not recursive:
                break
        
        self.scanned_games.extend(games)
        return games
    
    def _create_game_from_file(self, file_path: str, filename: str) -> Game:
        """从文件创建Game对象"""
        ext = os.path.splitext(filename)[1]
        name = clean_game_name(filename)
        
        if not name:
            return None
        
        game_id = self._generate_game_id(file_path)
        platform = get_platform_from_extension(ext)
        
        return Game(
            id=game_id,
            name=name,
            file_path=file_path,
            platform=platform,
            extension=ext
        )
    
    def _generate_game_id(self, file_path: str) -> str:
        """生成游戏的唯一ID"""
        path_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()[:12]
        return path_hash
    
    def get_games_by_platform(self, platform: str) -> List[Game]:
        """按平台筛选游戏"""
        return [g for g in self.scanned_games if g.platform == platform]
    
    def get_unscraped_games(self) -> List[Game]:
        """获取未刮削的游戏"""
        return [g for g in self.scanned_games if not g.is_scraped]
    
    def get_scraped_games(self) -> List[Game]:
        """获取已刮削的游戏"""
        return [g for g in self.scanned_games if g.is_scraped]
    
    def clear(self):
        """清空扫描结果"""
        self.scanned_games.clear()
        self._scanned_hashes.clear()
