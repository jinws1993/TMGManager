# -*- coding: utf-8 -*-
"""游戏详情面板组件"""

import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QTextEdit, QLineEdit, QGroupBox, QGridLayout, QSizePolicy,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QImage, QPainter, QIcon


class DetailPanel(QWidget):
    """游戏详情面板"""
    
    # 信号：游戏信息更新
    game_updated = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_game = None
        self.output_directory = ""
        self._setup_ui()
        self._apply_styles()
    
    def set_output_directory(self, directory: str):
        """设置输出目录"""
        self.output_directory = directory
    
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
        
        # 封面区域
        cover_layout = QVBoxLayout()
        
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setMinimumSize(280, 350)
        self.cover_label.setMaximumSize(280, 350)
        self.cover_label.setStyleSheet("border: 1px solid #3c3c3c; background-color: #1e1e1e;")
        self.cover_label.setText("\n\n\n\n\n未选择游戏\n\n请从左侧列表选择游戏")
        self.cover_label.setFont(QFont("Microsoft YaHei UI", 10))
        cover_layout.addWidget(self.cover_label, 0, Qt.AlignHCenter)
        
        # 导入封面按钮
        import_cover_btn = QPushButton("导入自定义封面...")
        import_cover_btn.clicked.connect(self._import_cover)
        import_cover_btn.setMaximumWidth(150)
        cover_layout.addWidget(import_cover_btn, 0, Qt.AlignHCenter)
        
        scroll_layout.addLayout(cover_layout)
        
        # 游戏信息
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
        
        # 游戏简介
        desc_group = QGroupBox("游戏简介")
        desc_layout = QVBoxLayout(desc_group)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("游戏简介...")
        self.desc_edit.textChanged.connect(self._on_description_changed)
        self.desc_edit.setMaximumHeight(120)
        desc_layout.addWidget(self.desc_edit)
        
        # 翻译按钮
        translate_btn = QPushButton("翻译为中文")
        translate_btn.clicked.connect(self._translate_description)
        desc_layout.addWidget(translate_btn)
        
        scroll_layout.addWidget(desc_group)
        
        # 截图预览
        screenshot_group = QGroupBox("截图预览")
        screenshot_layout = QVBoxLayout(screenshot_group)
        
        self.screenshot_list = QListWidget()
        self.screenshot_list.setViewMode(QListWidget.IconMode)
        self.screenshot_list.setIconSize(QSize(150, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setMaximumHeight(130)
        screenshot_layout.addWidget(self.screenshot_list)
        
        # 导入截图按钮
        import_screenshot_btn = QPushButton("导入自定义截图...")
        import_screenshot_btn.clicked.connect(self._import_screenshot)
        screenshot_layout.addWidget(import_screenshot_btn)
        
        scroll_layout.addWidget(screenshot_group)
        
        # 视频区域
        video_group = QGroupBox("预告片")
        video_layout = QVBoxLayout(video_group)
        
        self.video_label = QLabel("未设置")
        self.video_label.setWordWrap(True)
        video_layout.addWidget(self.video_label)
        
        import_video_btn = QPushButton("导入自定义视频...")
        import_video_btn.clicked.connect(self._import_video)
        video_layout.addWidget(import_video_btn)
        
        scroll_layout.addWidget(video_group)
        
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
            QPushButton {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """)
    
    def set_game(self, game):
        """设置显示的游戏"""
        self.current_game = game
        
        if game is None:
            self._clear_display()
            return
        
        self.name_edit.blockSignals(True)
        self.name_edit.setText(game.display_name)
        self.name_edit.blockSignals(False)
        
        self.platform_label.setText(f"{game.platform} ({game.platform_display})")
        self.genre_label.setText(game.genre or "-")
        self.players_label.setText(str(game.players) if game.players else "-")
        self.file_label.setText(os.path.basename(game.file_path))
        
        self.desc_edit.blockSignals(True)
        self.desc_edit.setText(game.description or "")
        self.desc_edit.blockSignals(False)
        
        # 更新视频显示
        if game.video_path:
            self.video_label.setText(os.path.basename(game.video_path))
        else:
            self.video_label.setText("未设置")
        
        # 加载封面
        cover_loaded = False
        if game.boxart_path and os.path.exists(game.boxart_path):
            cover_loaded = self._load_cover_image(game.boxart_path)
        
        if not cover_loaded and game.screenshot_paths:
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
        
        if not game or not game.screenshot_paths:
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
        self.video_label.setText("未设置")
    
    def _on_name_changed(self, text):
        """名称改变事件"""
        if self.current_game:
            self.current_game.editable_name = text
    
    def _on_description_changed(self):
        """简介改变事件"""
        if self.current_game:
            self.current_game.description = self.desc_edit.toPlainText()
    
    def _import_cover(self):
        """导入自定义封面"""
        if not self.current_game:
            QMessageBox.warning(self, "提示", "请先选择一个游戏！")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择封面图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp);;所有文件 (*.*)"
        )
        
        if file_path:
            self._copy_media_file(file_path, 'cover')
    
    def _import_screenshot(self):
        """导入自定义截图"""
        if not self.current_game:
            QMessageBox.warning(self, "提示", "请先选择一个游戏！")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择截图",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp);;所有文件 (*.*)"
        )
        
        if file_paths:
            for file_path in file_paths[:5]:  # 最多5张
                self._copy_media_file(file_path, 'screenshot')
    
    def _import_video(self):
        """导入自定义视频"""
        if not self.current_game:
            QMessageBox.warning(self, "提示", "请先选择一个游戏！")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv);;所有文件 (*.*)"
        )
        
        if file_path:
            self._copy_media_file(file_path, 'video')
    
    def _copy_media_file(self, src_path: str, media_type: str):
        """复制媒体文件到输出目录"""
        if not self.output_directory:
            QMessageBox.warning(self, "提示", "请先在设置中配置输出目录！")
            return
        
        safe_name = self.current_game.safe_name
        
        if media_type == 'cover':
            dest_dir = os.path.join(self.output_directory, 'images')
            os.makedirs(dest_dir, exist_ok=True)
            ext = os.path.splitext(src_path)[1]
            dest_path = os.path.join(dest_dir, f"{safe_name}_boxart{ext}")
            self.current_game.boxart_path = dest_path
            
        elif media_type == 'screenshot':
            dest_dir = os.path.join(self.output_directory, 'images')
            os.makedirs(dest_dir, exist_ok=True)
            screenshot_num = len([p for p in self.current_game.screenshot_paths if p]) + 1
            ext = os.path.splitext(src_path)[1]
            dest_path = os.path.join(dest_dir, f"{safe_name}_screenshot{screenshot_num}{ext}")
            self.current_game.screenshot_paths.append(dest_path)
            
        elif media_type == 'video':
            dest_dir = os.path.join(self.output_directory, 'videos')
            os.makedirs(dest_dir, exist_ok=True)
            ext = os.path.splitext(src_path)[1]
            dest_path = os.path.join(dest_dir, f"{safe_name}_video{ext}")
            self.current_game.video_path = dest_path
            self.video_label.setText(os.path.basename(dest_path))
        
        # 复制文件
        try:
            shutil.copy2(src_path, dest_path)
            
            # 刷新显示
            if media_type == 'cover':
                self._load_cover_image(dest_path)
            elif media_type == 'screenshot':
                self._update_screenshot_list(self.current_game)
            
            self.game_updated.emit(self.current_game)
            QMessageBox.information(self, "成功", f"已导入: {os.path.basename(dest_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {e}")
    
    def _translate_description(self):
        """翻译简介为中文"""
        if not self.current_game:
            QMessageBox.warning(self, "提示", "请先选择一个游戏！")
            return
        
        current_text = self.desc_edit.toPlainText()
        if not current_text:
            QMessageBox.warning(self, "提示", "简介为空，无法翻译！")
            return
        
        from translator import translate_text
        
        QMessageBox.information(self, "提示", "正在翻译...")
        
        translated = translate_text(current_text)
        
        if translated:
            self.desc_edit.setText(translated)
            self.current_game.description = translated
            QMessageBox.information(self, "成功", "翻译完成！")
        else:
            QMessageBox.warning(self, "失败", "翻译失败，请检查网络连接。")
