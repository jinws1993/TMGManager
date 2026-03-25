# -*- coding: utf-8 -*-
"""文件下载器"""

import os
import time
import requests
from typing import Optional, List, Tuple
from pathlib import Path


class Downloader:
    """文件下载器"""
    
    def __init__(self, output_dir: str, timeout: int = 30, proxy_url: str = None):
        self.output_dir = output_dir
        self.timeout = timeout
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
    
    def download_image(self, url: str, filepath: str) -> bool:
        """下载图片文件"""
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
        except Exception as e:
            print(f"下载图片失败: {url}, 错误: {e}")
            return False
    
    def download_video(self, url: str, filepath: str, progress_callback=None) -> bool:
        """下载视频文件"""
        try:
            response = self._session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            progress_callback(progress)
            
            return True
        except Exception as e:
            print(f"下载视频失败: {url}, 错误: {e}")
            return False
    
    def download_images_batch(self, images: List[Tuple[str, str]]) -> List[bool]:
        """批量下载图片"""
        results = []
        for url, filepath in images:
            time.sleep(0.1)
            results.append(self.download_image(url, filepath))
        return results
    
    def file_exists(self, filepath: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(filepath)
    
    def get_file_size(self, filepath: str) -> int:
        """获取文件大小（字节）"""
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
