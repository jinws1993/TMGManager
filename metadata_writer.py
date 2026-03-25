# -*- coding: utf-8 -*-
"""metadata.pegasus.txt生成器"""

import os
import shutil
from typing import List, Dict, Tuple
from models import Game


class MetadataWriter:
    """Pegasus Frontend metadata文件生成器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, 'images')
        self.videos_dir = os.path.join(output_dir, 'videos')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保输出目录存在"""
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def generate_metadata(self, games: List[Game], copy_files: bool = True) -> Tuple[str, List[str]]:
        """生成metadata.pegasus.txt文件"""
        lines = []
        failed_files = []
        
        for game in games:
            if not game.is_scraped:
                continue
            
            try:
                self._write_game_entry(lines, game)
                
                if copy_files:
                    self._copy_media_files(game, failed_files)
                    
            except Exception as e:
                failed_files.append(f"{game.name}: {str(e)}")
        
        metadata_path = os.path.join(self.output_dir, 'metadata.pegasus.txt')
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            f.write('\n')
        
        return metadata_path, failed_files
    
    def _write_game_entry(self, lines: List[str], game: Game):
        """写入单个游戏条目"""
        lines.append(f"PLATFORM: {game.platform}")
        lines.append(f"GAME_TITLE: {game.display_name}")
        lines.append(f"FILE: {game.file_path}")
        
        if game.description:
            lines.append(f"description: {game.description}")
        
        if game.players:
            lines.append(f"players: {game.players}")
        
        if game.genre:
            lines.append(f"genre: {game.genre}")
        
        if game.screenshot_paths:
            safe_name = game.safe_name
            lines.append(f"screenshot: images/{safe_name}-screenshot1.jpg")
        
        boxart_path = self._get_local_path(game.boxart_path)
        if boxart_path:
            lines.append(f"marquee: {boxart_path}")
        
        video_path = self._get_local_path(game.video_path)
        if video_path:
            lines.append(f"video: {video_path}")
        
        lines.append("")
    
    def _get_local_path(self, path: str) -> str:
        """获取相对于输出目录的路径"""
        if not path:
            return ''
        
        if path.startswith(self.images_dir):
            return os.path.relpath(path, self.output_dir)
        elif path.startswith(self.videos_dir):
            return os.path.relpath(path, self.output_dir)
        
        return os.path.basename(path)
    
    def _copy_media_files(self, game: Game, failed_files: List[str]):
        """复制媒体文件到输出目录"""
        safe_name = game.safe_name
        
        if game.boxart_path and os.path.exists(game.boxart_path):
            dest_path = os.path.join(self.images_dir, f"{safe_name}-box.jpg")
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(game.boxart_path, dest_path)
                    game.boxart_path = dest_path
                except Exception as e:
                    failed_files.append(f"封面复制失败: {game.name} - {str(e)}")
        
        for i, screenshot_path in enumerate(game.screenshot_paths):
            if screenshot_path and os.path.exists(screenshot_path):
                dest_path = os.path.join(self.images_dir, f"{safe_name}-screenshot{i+1}.jpg")
                if not os.path.exists(dest_path):
                    try:
                        shutil.copy2(screenshot_path, dest_path)
                        game.screenshot_paths[i] = dest_path
                    except Exception as e:
                        failed_files.append(f"截图复制失败: {game.name} - {str(e)}")
        
        if game.video_path and os.path.exists(game.video_path):
            dest_path = os.path.join(self.videos_dir, f"{safe_name}-video.mp4")
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(game.video_path, dest_path)
                    game.video_path = dest_path
                except Exception as e:
                    failed_files.append(f"视频复制失败: {game.name} - {str(e)}")
    
    def write_failed_list(self, failed_games: List[Game]):
        """写入失败列表"""
        if not failed_games:
            return
        
        failed_path = os.path.join(self.output_dir, 'failed.txt')
        
        with open(failed_path, 'w', encoding='utf-8') as f:
            f.write("刮削失败的游戏列表\n")
            f.write("=" * 50 + "\n\n")
            
            for game in failed_games:
                f.write(f"名称: {game.name}\n")
                f.write(f"文件: {game.file_path}\n")
                f.write(f"平台: {game.platform}\n")
                f.write(f"错误: {game.scrape_error}\n")
                f.write("-" * 30 + "\n")
