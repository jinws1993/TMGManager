# -*- coding: utf-8 -*-
"""TheGamesDB API刮削器"""

import time
import requests
from typing import Optional, List, Dict, Any
from models import Game, ScrapeResult


class TheGamesDBScraper:
    """TheGamesDB API刮削器
    
    API文档: https://api.thegamesdb.net/
    需要在 https://thegamesdb.net 注册获取免费 API Key
    """
    
    BASE_URL = "https://api.thegamesdb.net/v1"
    
    # 平台ID映射 (TheGamesDB的平台ID)
    PLATFORM_IDS = {
        'NES': 7,           # Nintendo Entertainment System
        'SNES': 6,          # Super Nintendo Entertainment System
        'N64': 3,           # Nintendo 64
        'GB': 4,            # Game Boy
        'GBC': 41,          # Game Boy Color
        'GBA': 1,           # Game Boy Advance
        'NDS': 8,           # Nintendo DS
        '3DS': 4912,        # Nintendo 3DS
        'PS1': 10,          # Sony PlayStation
        'PS2': 11,          # Sony PlayStation 2
        'PSP': 13,          # Sony PlayStation Portable
        'PSV': 4721,        # Sony PlayStation Vita
        'DC': 8,            # Sega Dreamcast
        'SAT': 21,          # Sega Saturn
        'MD': 36,           # Sega Mega Drive
        'GEN': 20,          # Sega Genesis
        'PCE': 44,          # PC Engine / TurboGrafx-16
        'ARC': 23,          # Arcade
        'PC': 1,            # PC
    }
    
    def __init__(self, api_key: str = None, proxy_url: str = None):
        self.api_key = api_key
        self.proxy_url = proxy_url
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'PegasusROMManager/1.0'
        })
        if api_key:
            self._session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        if proxy_url:
            self._session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
    
    def search_game(self, game_name: str, platform: str = None) -> List[Dict[str, Any]]:
        """搜索游戏"""
        url = f"{self.BASE_URL}/Games/ByGameName"
        params = {
            'name': game_name,
            'fields': 'overview,rating,players,genres,images',
            'include': 'boxart'
        }
        
        # 添加平台过滤
        if platform and platform in self.PLATFORM_IDS:
            params['filter__platform'] = self.PLATFORM_IDS[platform]
        
        try:
            time.sleep(0.5)  # 速率限制
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'Success':
                return data.get('data', {}).get('games', [])
            return []
        except Exception as e:
            print(f"TGDB搜索失败: {game_name}, 错误: {e}")
            return []
    
    def get_game_images(self, game_id: int) -> Dict[str, Any]:
        """获取游戏图片"""
        url = f"{self.BASE_URL}/Games/Images"
        params = {
            'games_id': game_id,
            'fields': 'filename,type,height,width'
        }
        
        try:
            time.sleep(0.5)
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'Success':
                return data.get('data', {})
            return {}
        except Exception as e:
            print(f"TGDB获取图片失败: {game_id}, 错误: {e}")
            return {}
    
    def _get_image_url(self, filename: str, image_type: str = 'boxart') -> str:
        """获取图片URL"""
        base_urls = {
            'boxart': 'https://cdn.thegamesdb.net/images/original/boxart/front/',
            'screenshot': 'https://cdn.thegamesdb.net/images/original/screenshots/',
            'fanart': 'https://cdn.thegamesdb.net/images/original/fanart/',
        }
        return base_urls.get(image_type, base_urls['boxart']) + filename
    
    def scrape_game(self, game: Game, download_video: bool = True, screenshot_count: int = 3) -> ScrapeResult:
        """刮削单个游戏"""
        try:
            # 搜索游戏
            search_results = self.search_game(game.name, game.platform)
            
            if not search_results:
                return ScrapeResult(
                    success=False,
                    game=game,
                    error_message="TheGamesDB未找到匹配的游戏"
                )
            
            # 取第一个结果
            best_match = search_results[0]
            game.tgdb_id = best_match.get('id')
            
            # 设置游戏信息
            if best_match.get('overview'):
                game.description = self._clean_description(best_match['overview'])
            
            if best_match.get('rating'):
                game.rating = float(best_match['rating'])
            
            if best_match.get('players'):
                game.players = best_match['players']
            
            if best_match.get('genres'):
                genres = best_match['genres']
                if isinstance(genres, list) and len(genres) > 0:
                    game.genre = genres[0]
            
            # 获取图片
            images_data = self.get_game_images(game.tgdb_id)
            
            if images_data:
                base_url = "https://cdn.thegamesdb.net/images/original/"
                
                for img in images_data[:screenshot_count + 1]:
                    filename = img.get('filename', '')
                    img_type = img.get('type', '')
                    
                    if not filename:
                        continue
                    
                    url = base_url + filename
                    
                    if img_type == 'boxart' and not game.boxart_path:
                        game.boxart_path = url
                    elif img_type == 'screenshot' and len(game.screenshot_paths) < screenshot_count:
                        game.screenshot_paths.append(url)
                    elif img_type == 'fanart' and not game.background_path:
                        game.background_path = url
            
            game.is_scraped = True
            return ScrapeResult(success=True, game=game)
            
        except Exception as e:
            return ScrapeResult(
                success=False,
                game=game,
                error_message=str(e)
            )
    
    def _clean_description(self, text: str) -> str:
        """清理描述文本"""
        if not text:
            return ''
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.strip()
        if len(text) > 500:
            text = text[:500] + '...'
        return text
    
    def test_connection(self) -> tuple:
        """测试连接"""
        try:
            url = f"{self.BASE_URL}/Platforms"
            params = {'fields': 'name'}
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'Success':
                return True, "TheGamesDB连接成功！"
            return False, f"TheGamesDB返回错误: {data.get('status')}"
        except Exception as e:
            return False, f"TheGamesDB连接失败: {str(e)}"
