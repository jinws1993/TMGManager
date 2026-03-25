# -*- coding: utf-8 -*-
"""配置管理"""

import os
import json
from typing import Optional, List


class Config:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        'rawg_api_key': '',
        'tgdb_api_key': '',
        'download_video': True,
        'screenshot_count': 3,
        'output_directory': '',
        'rom_directories': [],
        'theme': 'dark',
        'language': 'zh_CN',
        'auto_skip_scraped': True,
        'last_export_path': '',
        'proxy_enabled': False,
        'proxy_url': '',
        'auto_translate': True,  # 自动翻译简介为中文
    }
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.expanduser('~'),
                '.pegasus_rom_manager',
                'config.json'
            )
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置项"""
        self.config[key] = value
        self._save_config()
    
    def add_rom_directory(self, directory: str):
        """添加ROM目录"""
        if directory not in self.config['rom_directories']:
            self.config['rom_directories'].append(directory)
            self._save_config()
    
    def remove_rom_directory(self, directory: str):
        """移除ROM目录"""
        if directory in self.config['rom_directories']:
            self.config['rom_directories'].remove(directory)
            self._save_config()
    
    @property
    def rawg_api_key(self) -> str:
        return self.config.get('rawg_api_key', '')
    
    @rawg_api_key.setter
    def rawg_api_key(self, value: str):
        self.config['rawg_api_key'] = value
        self._save_config()
    
    @property
    def download_video(self) -> bool:
        return self.config.get('download_video', True)
    
    @download_video.setter
    def download_video(self, value: bool):
        self.config['download_video'] = value
        self._save_config()
    
    @property
    def screenshot_count(self) -> int:
        return self.config.get('screenshot_count', 3)
    
    @screenshot_count.setter
    def screenshot_count(self, value: int):
        self.config['screenshot_count'] = value
        self._save_config()
    
    @property
    def output_directory(self) -> str:
        return self.config.get('output_directory', '')
    
    @output_directory.setter
    def output_directory(self, value: str):
        self.config['output_directory'] = value
        self._save_config()
    
    @property
    def proxy_enabled(self) -> bool:
        return self.config.get('proxy_enabled', False)
    
    @proxy_enabled.setter
    def proxy_enabled(self, value: bool):
        self.config['proxy_enabled'] = value
        self._save_config()
    
    @property
    def proxy_url(self) -> str:
        return self.config.get('proxy_url', '')
    
    @proxy_url.setter
    def proxy_url(self, value: str):
        self.config['proxy_url'] = value
        self._save_config()
    
    @property
    def tgdb_api_key(self) -> str:
        return self.config.get('tgdb_api_key', '')
    
    @tgdb_api_key.setter
    def tgdb_api_key(self, value: str):
        self.config['tgdb_api_key'] = value
        self._save_config()
    
    @property
    def auto_translate(self) -> bool:
        return self.config.get('auto_translate', True)
    
    @auto_translate.setter
    def auto_translate(self, value: bool):
        self.config['auto_translate'] = value
        self._save_config()
