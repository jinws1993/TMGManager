# -*- coding: utf-8 -*-
"""多源刮削器 - 同时使用 RAWG 和 TheGamesDB"""

import time
from typing import Optional, List
from models import Game, ScrapeResult
from scraper import RAWGSraper
from tgdb_scraper import TheGamesDBScraper


class MultiSourceScraper:
    """多源刮削器
    
    同时使用多个数据源刮削游戏信息，按优先级合并结果
    """
    
    def __init__(self, rawg_api_key: str = None, tgdb_api_key: str = None, proxy_url: str = None):
        self.rawg_scraper = RAWGSraper(rawg_api_key, proxy_url) if rawg_api_key else None
        self.tgdb_scraper = TheGamesDBScraper(tgdb_api_key, proxy_url)
        self.proxy_url = proxy_url
    
    def scrape_game(self, game: Game, download_video: bool = True, screenshot_count: int = 3) -> ScrapeResult:
        """刮削单个游戏，使用多个数据源"""
        
        # 先尝试 RAWG
        rawg_success = False
        if self.rawg_scraper:
            result = self.rawg_scraper.scrape_game(game, download_video, screenshot_count)
            if result.success:
                rawg_success = True
        
        # 再尝试 TheGamesDB 补充
        tgdb_success = False
        try:
            tgdb_result = self.tgdb_scraper.scrape_game(game, download_video, screenshot_count)
            if tgdb_result.success:
                tgdb_success = True
        except Exception as e:
            print(f"TGDB刮削失败: {e}")
        
        # 判断整体是否成功
        if rawg_success or tgdb_success:
            game.is_scraped = True
            return ScrapeResult(success=True, game=game)
        else:
            return ScrapeResult(
                success=False,
                game=game,
                error_message="所有刮削源均未找到游戏"
            )
    
    def search_game_all_sources(self, game_name: str, platform: str = None) -> dict:
        """在所有源中搜索游戏"""
        results = {
            'rawg': [],
            'tgdb': []
        }
        
        if self.rawg_scraper:
            try:
                results['rawg'] = self.rawg_scraper.search_game(game_name)
            except Exception as e:
                print(f"RAWG搜索失败: {e}")
        
        try:
            results['tgdb'] = self.tgdb_scraper.search_game(game_name, platform)
        except Exception as e:
            print(f"TGDB搜索失败: {e}")
        
        return results
    
    def test_all_sources(self) -> dict:
        """测试所有数据源连接"""
        results = {}
        
        if self.rawg_scraper:
            try:
                success, msg = self.rawg_scraper.test_proxy_connection()
                results['rawg'] = {'success': success, 'message': msg}
            except Exception as e:
                results['rawg'] = {'success': False, 'message': str(e)}
        else:
            results['rawg'] = {'success': False, 'message': '未配置RAWG API Key'}
        
        try:
            success, msg = self.tgdb_scraper.test_connection()
            results['tgdb'] = {'success': success, 'message': msg}
        except Exception as e:
            results['tgdb'] = {'success': False, 'message': str(e)}
        
        return results
