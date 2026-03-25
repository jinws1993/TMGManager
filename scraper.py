# -*- coding: utf-8 -*-
"""RAWG API刮削器"""

import time
import requests
from typing import Optional, List, Dict, Any
from models import Game, ScrapeResult


class RAWGSraper:
    """RAWG API刮削器"""
    
    BASE_URL = "https://api.rawg.io/api"
    
    def __init__(self, api_key: str, proxy_url: str = None):
        self.api_key = api_key
        self.proxy_url = proxy_url
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'PegasusROMManager/1.0'
        })
        # 设置代理
        if proxy_url:
            self._session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
    
    def test_proxy_connection(self) -> tuple[bool, str]:
        """测试代理连接"""
        if not self.proxy_url:
            return False, "未设置代理地址"
        
        try:
            # 测试代理是否可用
            test_url = "https://api.rawg.io/api/games"
            params = {'key': self.api_key, 'page_size': 1}
            response = self._session.get(test_url, params=params, timeout=10)
            response.raise_for_status()
            return True, "代理连接成功！"
        except Exception as e:
            return False, f"代理连接失败: {str(e)}"
    
    def search_game(self, game_name: str) -> List[Dict[str, Any]]:
        """搜索游戏"""
        if not self.api_key:
            return []
        
        url = f"{self.BASE_URL}/games"
        params = {
            'key': self.api_key,
            'search': game_name,
            'page_size': 10
        }
        
        try:
            time.sleep(0.5)
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            print(f"搜索失败: {game_name}, 错误: {e}")
            return []
    
    def search_game_with_fallback(self, game_name: str) -> List[Dict[str, Any]]:
        """搜索游戏，带中文备选方案"""
        results = self.search_game(game_name)
        
        if not results and not self._is_likely_chinese(game_name):
            chinese_name = f"{game_name} 游戏"
            results = self.search_game(chinese_name)
        
        return results
    
    def _is_likely_chinese(self, name: str) -> bool:
        """检查是否可能是中文名"""
        return any('\u4e00' <= c <= '\u9fff' for c in name)
    
    def get_game_details(self, rawg_id: int) -> Optional[Dict[str, Any]]:
        """获取游戏详情"""
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/games/{rawg_id}"
        params = {'key': self.api_key}
        
        try:
            time.sleep(0.5)
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取详情失败: {rawg_id}, 错误: {e}")
            return None
    
    def get_screenshots(self, rawg_id: int, count: int = 3) -> List[str]:
        """获取游戏截图URL列表"""
        if not self.api_key:
            return []
        
        url = f"{self.BASE_URL}/games/{rawg_id}/screenshots"
        params = {'key': self.api_key}
        
        try:
            time.sleep(0.5)
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            image_urls = []
            for item in results[:count]:
                image_url = item.get('image', '')
                if image_url:
                    image_urls.append(image_url)
            return image_urls
        except Exception as e:
            print(f"获取截图失败: {rawg_id}, 错误: {e}")
            return []
    
    def get_movie_url(self, rawg_id: int) -> Optional[str]:
        """获取游戏预告片URL"""
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/games/{rawg_id}/movies"
        params = {'key': self.api_key}
        
        try:
            time.sleep(0.5)
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            
            for movie in results:
                if movie.get('data', {}).get('480'):
                    return movie['data']['480']
                elif movie.get('data', {}).get('720'):
                    return movie['data']['720']
                elif movie.get('data', {}).get('1080'):
                    return movie['data']['1080']
                elif movie.get('data', {}).get('max'):
                    return movie['data']['max']
            
            return None
        except Exception as e:
            print(f"获取预告片失败: {rawg_id}, 错误: {e}")
            return None
    
    def scrape_game(self, game: Game, download_video: bool = True, screenshot_count: int = 3, auto_translate: bool = False) -> ScrapeResult:
        """刮削单个游戏"""
        if not self.api_key:
            return ScrapeResult(
                success=False,
                game=game,
                error_message="未设置RAWG API Key"
            )
        
        try:
            search_results = self.search_game_with_fallback(game.name)
            
            if not search_results:
                return ScrapeResult(
                    success=False,
                    game=game,
                    error_message="未找到匹配的游戏"
                )
            
            best_match = search_results[0]
            rawg_id = best_match['id']
            game.rawg_id = rawg_id
            
            details = self.get_game_details(rawg_id)
            if details:
                description = self._clean_description(details.get('description_raw', ''))
                
                # 自动翻译
                if auto_translate and description:
                    from translator import translate_text
                    translated = translate_text(description, self.proxy_url)
                    if translated:
                        game.description = translated
                    else:
                        game.description = description
                else:
                    game.description = description
                
                game.released = details.get('released', '')
                game.rating = details.get('rating', 0.0)
                
                genres = details.get('genres', [])
                if genres:
                    game.genre = genres[0].get('name', '')
                
                metacritic = details.get('metacritic')
                if metacritic:
                    game.players = 1
            
            screenshots = self.get_screenshots(rawg_id, screenshot_count)
            game.screenshot_paths = screenshots
            
            if download_video:
                movie_url = self.get_movie_url(rawg_id)
                if movie_url:
                    game.video_path = movie_url
            
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
    
    def select_alternative(self, game: Game, rawg_id: int, download_video: bool = True, screenshot_count: int = 3) -> ScrapeResult:
        """手动选择游戏后刮削"""
        try:
            game.rawg_id = rawg_id
            
            details = self.get_game_details(rawg_id)
            if details:
                game.description = self._clean_description(details.get('description_raw', ''))
                game.released = details.get('released', '')
                game.rating = details.get('rating', 0.0)
                
                genres = details.get('genres', [])
                if genres:
                    game.genre = genres[0].get('name', '')
            
            screenshots = self.get_screenshots(rawg_id, screenshot_count)
            game.screenshot_paths = screenshots
            
            if download_video:
                movie_url = self.get_movie_url(rawg_id)
                if movie_url:
                    game.video_path = movie_url
            
            game.is_scraped = True
            return ScrapeResult(success=True, game=game)
            
        except Exception as e:
            return ScrapeResult(
                success=False,
                game=game,
                error_message=str(e)
            )
