# -*- coding: utf-8 -*-
"""游戏详情面板组件"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QTextEdit, QLineEdit, QGroupBox, QGridLayout, QSizePolicy,
    QPushButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QImage, QPainter, QIcon


class DetailPanel(QWidget):
    """游戏详情面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_game = None
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setMinimumSize(280, 350)
        self.cover_label.setMaximumSize(280, 350)
        self.cover_label.setStyleSheet("border: 1px solid #3c3c3c; background-color: #1e1e1e;")
        self.cover_label.setText("\n\n\n\n\n未选择游戏\n\n请从左侧列表选择游戏")
        self.cover_label.setFont(QFont("Microsoft YaHei UI", 10))
        scroll_layout.addWidget(self.cover_label, 0, Qt.AlignHCenter)
        
        info_group = QGroupBox("游戏信息")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("名称:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("游戏名称")
        self.name_edit.textChanged.connect(self._on_name_changed)
        info_layout.addWidget(self.name_edit, 0, 1)
        
        info_layout.addWidget(QLabel("平台:"), 1, 0)
        self.platform_label = QLabel("-")
        info_layout.addWidget(self.platform_label, 1, 1)
        
        info_layout.addWidget(QLabel("类型:"), 2, 0)
        self.genre_label = QLabel("-")
        info_layout.addWidget(self.genre_label, 2, 1)
        
        info_layout.addWidget(QLabel("玩家数:"), 3, 0)
        self.players_label = QLabel("-")
        info_layout.addWidget(self.players_label, 3, 1)
        
        info_layout.addWidget(QLabel("文件:"), 4, 0)
        self.file_label = QLabel("-")
        self.file_label.setWordWrap(True)
        info_layout.addWidget(self.file_label, 4, 1)
        
        scroll_layout.addWidget(info_group)
        
        desc_group = QGroupBox("游戏简介")
        desc_layout = QVBoxLayout(desc_group)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("游戏简介...")
        self.desc_edit.textChanged.connect(self._on_description_changed)
        self.desc_edit.setMaximumHeight(150)
        desc_layout.addWidget(self.desc_edit)
        
        scroll_layout.addWidget(desc_group)
        
        screenshot_group = QGroupBox("截图预览")
        screenshot_layout = QVBoxLayout(screenshot_group)
        
        self.screenshot_list = QListWidget()
        self.screenshot_list.setViewMode(QListWidget.IconMode)
        self.screenshot_list.setIconSize(QSize(150, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setMaximumHeight(130)
        screenshot_layout.addWidget(self.screenshot_list)
        
        scroll_layout.addWidget(screenshot_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QGroupBox {
                font-family: "Microsoft YaHei UI";
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #cccccc;
            }
            QLabel {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
            }
            QLineEdit, QTextEdit {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #007acc;
            }
        """)
    
    def set_game(self, game):
        """设置显示的游戏"""
        self.current_game = game
        
        if game is None:
            self._clear_display()
            return
        
        self.name_edit.setText(game.display_name)
        self.platform_label.setText(f"{game.platform} ({game.platform_display})")
        self.genre_label.setText(game.genre or "-")
        self.players_label.setText(str(game.players) if game.players else "-")
        self.file_label.setText(os.path.basename(game.file_path))
        self.desc_edit.setText(game.description or "")
        
        # 加载封面 - 优先使用 boxart，其次使用第一张截图
        cover_loaded = False
        if game.boxart_path and os.path.exists(game.boxart_path):
            cover_loaded = self._load_cover_image(game.boxart_path)
        
        if not cover_loaded and game.screenshot_paths:
            # 使用第一张截图作为封面
            for screenshot in game.screenshot_paths:
                if screenshot and os.path.exists(screenshot):
                    cover_loaded = self._load_cover_image(screenshot)
                    if cover_loaded:
                        break
        
        if not cover_loaded:
            self.cover_label.setText("\n\n\n\n\n封面未刮削")
        
        # 更新截图预览列表
        self._update_screenshot_list(game)
    
    def _update_screenshot_list(self, game):
        """更新截图预览列表"""
        self.screenshot_list.clear()
        
        if not game.screenshot_paths:
            return
        
        for screenshot_path in game.screenshot_paths:
            if screenshot_path and os.path.exists(screenshot_path):
                pixmap = QPixmap(screenshot_path)
                if not pixmap.isNull():
                    icon = pixmap.scaled(
                        150, 100,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                    item = QListWidgetItem()
                    item.setIcon(QIcon(icon))
                    item.setToolTip(screenshot_path)
                    self.screenshot_list.addItem(item)
    
    def _load_cover_image(self, path):
        """加载封面图片"""
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                260, 340,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled)
            return True
        else:
            self.cover_label.setText("\n\n\n\n\n封面加载失败")
            return False
    
    def _clear_display(self):
        """清空显示"""
        self.cover_label.clear()
        self.cover_label.setText("\n\n\n\n\n未选择游戏\n\n请从左侧列表选择游戏")
        self.name_edit.clear()
        self.platform_label.setText("-")
        self.genre_label.setText("-")
        self.players_label.setText("-")
        self.file_label.setText("-")
        self.desc_edit.clear()
        self.screenshot_list.clear()
    
    def _on_name_changed(self, text):
        """名称改变事件"""
        if self.current_game:
            self.current_game.editable_name = text
    
    def _on_description_changed(self):
        """简介改变事件"""
        if self.current_game:
            self.current_game.description = self.desc_edit.toPlainText()
