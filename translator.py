# -*- coding: utf-8 -*-
"""翻译工具"""

import requests
from typing import Optional


class Translator:
    """翻译工具类
    
    使用免费翻译API将英文翻译成中文
    """
    
    # MyMemory 免费 API（每日1000词限制）
    TRANSLATE_API = "https://api.mymemory.translated.net/get"
    
    def __init__(self, proxy_url: str = None):
        self.proxy_url = proxy_url
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'PegasusROMManager/1.0'
        })
        if proxy_url:
            self._session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
    
    def translate_to_chinese(self, text: str) -> Optional[str]:
        """将英文翻译成中文
        
        Args:
            text: 英文文本
            
        Returns:
            中文翻译，失败返回None
        """
        if not text:
            return None
        
        # 如果已经是中文，直接返回
        if self._is_chinese(text):
            return text
        
        try:
            params = {
                'q': text[:500],  # MyMemory限制500字符
                'langpair': 'en|zh-CN'
            }
            
            response = self._session.get(
                self.TRANSLATE_API, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('responseStatus') == 200:
                translated = data.get('responseData', {}).get('translatedText')
                if translated:
                    return translated
            
            return None
            
        except Exception as e:
            print(f"翻译失败: {e}")
            return None
    
    def _is_chinese(self, text: str) -> bool:
        """检查文本是否主要是中文"""
        if not text:
            return False
        
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len([c for c in text if c.isalnum()])
        
        return total_chars > 0 and chinese_chars / total_chars > 0.3


# 全局翻译器实例
_translator = None


def get_translator(proxy_url: str = None) -> Translator:
    """获取翻译器实例"""
    global _translator
    if _translator is None:
        _translator = Translator(proxy_url)
    return _translator


def translate_text(text: str, proxy_url: str = None) -> Optional[str]:
    """便捷翻译函数"""
    translator = get_translator(proxy_url)
    return translator.translate_to_chinese(text)
