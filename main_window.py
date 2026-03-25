# -*- coding: utf-8 -*-
"""主窗口"""

import os
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolBar, QAction, QStatusBar, QLabel, QProgressBar, QPushButton,
    QSplitter, QMessageBox, QFileDialog, QListWidget, QAbstractItemView,
    QGroupBox, QSpinBox, QCheckBox, QFrame, QScrollArea, QProgressDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

from config import Config
from rom_scanner import ROMScanner
from scraper import RAWGSraper
from tgdb_scraper import TheGamesDBScraper
from multi_scraper import MultiSourceScraper
from downloader import Downloader
from metadata_writer import MetadataWriter
from ui.game_list_widget import GameListWidget
from ui.detail_panel import DetailPanel
from ui.settings_dialog import SettingsDialog


class ScrapeWorker(QThread):
    """刮削工作线程"""
    
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, games, config, parent=None):
        super().__init__(parent)
        self.games = games
        self.config = config
        
        # 根据代理设置创建多源刮削器
        proxy_url = config.proxy_url if config.proxy_enabled else None
        self.scraper = MultiSourceScraper(
            config.rawg_api_key, 
            config.tgdb_api_key,
            proxy_url
        )
        self.downloader = Downloader("", proxy_url=proxy_url)
        self._stopped = False
    
    def stop(self):
        self._stopped = True
    
    def run(self):
        results = []
        total = len(self.games)
        
        for i, game in enumerate(self.games):
            if self._stopped:
                break
            
            self.progress.emit(i + 1, total, f"正在刮削: {game.name}")
            
            result = self.scraper.scrape_game(
                game,
                download_video=self.config.download_video,
                screenshot_count=self.config.screenshot_count
            )
            
            if result.success:
                self._download_media(game)
            
            results.append((game, result.success, result.error_message if not result.success else ""))
        
        self.finished.emit(results)
    
    def _download_media(self, game):
        """下载媒体文件"""
        if not game.is_scraped:
            print(f"[DEBUG] Game not scraped: {game.name}")
            return
        
        output_dir = self.config.output_directory
        if not output_dir:
            print(f"[DEBUG] No output directory set")
            return
        
        images_dir = os.path.join(output_dir, 'images')
        videos_dir = os.path.join(output_dir, 'videos')
        
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(videos_dir, exist_ok=True)
        
        safe_name = game.safe_name
        print(f"[DEBUG] Downloading media for: {game.name} (safe_name: {safe_name})")
        print(f"[DEBUG] Screenshots: {game.screenshot_paths}")
        print(f"[DEBUG] Video: {game.video_path}")
        
        # 重新创建downloader以确保使用最新代理设置
        proxy_url = self.config.proxy_url if self.config.proxy_enabled else None
        downloader = Downloader("", proxy_url=proxy_url)
        
        if game.screenshot_paths:
            for i, url in enumerate(game.screenshot_paths[:self.config.screenshot_count]):
                if url:
                    ext = os.path.splitext(url)[1] or '.jpg'
                    filepath = os.path.join(images_dir, f"{safe_name}_screenshot{i+1}{ext}")
                    print(f"[DEBUG] Downloading screenshot: {url[:60]}... -> {filepath}")
                    success = downloader.download_image(url, filepath)
                    print(f"[DEBUG] Screenshot download result: {success}")
                    game.screenshot_paths[i] = filepath
                    time.sleep(0.1)
        
        if self.config.download_video and game.video_path:
            filepath = os.path.join(videos_dir, f"{safe_name}_video.mp4")
            print(f"[DEBUG] Downloading video: {game.video_path[:60]}... -> {filepath}")
            success = downloader.download_video(game.video_path, filepath)
            print(f"[DEBUG] Video download result: {success}")
            game.video_path = filepath
            time.sleep(0.1)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.config = Config()
        self.scanner = ROMScanner()
        self.games = []
        self.scrape_worker = None
        self.is_scraping = False
        
        self._setup_ui()
        self._apply_styles()
        self._create_toolbar()
        self._create_status_bar()
    
    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("天马G游戏ROM管理工具")
        self.setMinimumSize(1200, 750)
        self.resize(1200, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        left_splitter = QSplitter(Qt.Horizontal)
        left_splitter.setMinimumWidth(300)
        left_splitter.setMaximumWidth(450)
        
        self.game_list_widget = GameListWidget()
        self.game_list_widget.game_selected.connect(self._on_game_selected)
        self.game_list_widget.games_selection_changed.connect(self._on_selection_changed)
        left_splitter.addWidget(self.game_list_widget)
        
        self.detail_panel = DetailPanel()
        left_splitter.addWidget(self.detail_panel)
        
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(left_splitter, 3)
        
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_right_panel(self):
        """创建右侧面板"""
        panel = QFrame()
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(320)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 10, 5, 5)
        layout.setSpacing(10)
        
        settings_group = QGroupBox("RAWG设置")
        settings_layout = QVBoxLayout(settings_group)
        
        self.api_key_status = QLabel("API Key: 未设置" if not self.config.rawg_api_key else "API Key: 已设置 ✓")
        settings_layout.addWidget(self.api_key_status)
        
        self.settings_btn = QPushButton("设置...")
        self.settings_btn.clicked.connect(self._show_settings)
        settings_layout.addWidget(self.settings_btn)
        
        layout.addWidget(settings_group)
        
        scrape_options_group = QGroupBox("刮削选项")
        scrape_options_layout = QVBoxLayout(scrape_options_group)
        
        self.download_video_cb = QCheckBox("下载预告片")
        self.download_video_cb.setChecked(self.config.download_video)
        self.download_video_cb.stateChanged.connect(self._on_download_video_changed)
        scrape_options_layout.addWidget(self.download_video_cb)
        
        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("截图数量:"))
        self.screenshot_count_spin = QSpinBox()
        self.screenshot_count_spin.setMinimum(1)
        self.screenshot_count_spin.setMaximum(10)
        self.screenshot_count_spin.setValue(self.config.screenshot_count)
        self.screenshot_count_spin.valueChanged.connect(self._on_screenshot_count_changed)
        screenshot_layout.addWidget(self.screenshot_count_spin)
        screenshot_layout.addStretch()
        scrape_options_layout.addLayout(screenshot_layout)
        
        layout.addWidget(scrape_options_group)
        
        progress_group = QGroupBox("刮削进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.current_game_label = QLabel("")
        self.current_game_label.setWordWrap(True)
        progress_layout.addWidget(self.current_game_label)
        
        layout.addWidget(progress_group)
        
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout(action_group)
        action_layout.setSpacing(8)
        
        self.scrape_selected_btn = QPushButton("刮削选中 (0)")
        self.scrape_selected_btn.clicked.connect(self._scrape_selected)
        self.scrape_selected_btn.setEnabled(False)
        action_layout.addWidget(self.scrape_selected_btn)
        
        self.scrape_all_btn = QPushButton("刮削全部 (0)")
        self.scrape_all_btn.clicked.connect(self._scrape_all)
        self.scrape_all_btn.setEnabled(False)
        action_layout.addWidget(self.scrape_all_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self._stop_scrape)
        self.stop_btn.setEnabled(False)
        action_layout.addWidget(self.stop_btn)
        
        self.export_btn = QPushButton("导出到目录...")
        self.export_btn.clicked.connect(self._export)
        self.export_btn.setEnabled(False)
        action_layout.addWidget(self.export_btn)
        
        layout.addWidget(action_group)
        layout.addStretch()
        
        return panel
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #252526;
                border: none;
                padding: 5px;
                spacing: 10px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                color: #cccccc;
                padding: 8px;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
                border-radius: 3px;
            }
        """)
        
        add_dir_action = QAction("添加ROM目录", self)
        add_dir_action.triggered.connect(self._add_rom_directory)
        toolbar.addAction(add_dir_action)
        
        scan_action = QAction("扫描目录", self)
        scan_action.triggered.connect(self._scan_directories)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        clear_action = QAction("清空列表", self)
        clear_action.triggered.connect(self._clear_games)
        toolbar.addAction(clear_action)
        
        self.addToolBar(toolbar)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #007acc;
                color: white;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label, 1)
        
        self.games_count_label = QLabel("游戏: 0 | 已刮削: 0")
        self.status_bar.addPermanentWidget(self.games_count_label)
    
    def _apply_styles(self):
        """应用全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: "Microsoft YaHei UI";
            }
            QGroupBox {
                font-family: "Microsoft YaHei UI";
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #252526;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #cccccc;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #808080;
            }
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                background-color: #3c3c3c;
                text-align: center;
                color: #cccccc;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
            }
            QLabel {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
            }
            QSpinBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4a4a4a;
                border: none;
            }
            QCheckBox {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
            }
        """)
    
    def _add_rom_directory(self):
        """添加ROM目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择ROM目录",
            ""
        )
        if directory:
            self.config.add_rom_directory(directory)
            self.status_label.setText(f"已添加目录: {directory}")
    
    def _scan_directories(self):
        """扫描ROM目录"""
        directories = self.config.get('rom_directories', [])
        
        if not directories:
            QMessageBox.information(
                self,
                "提示",
                "请先添加ROM目录！\n\n点击工具栏的'添加ROM目录'按钮添加需要扫描的目录。",
                QMessageBox.Ok
            )
            return
        
        # 过滤掉不存在的目录
        valid_directories = [d for d in directories if os.path.isdir(d)]
        invalid_directories = [d for d in directories if not os.path.isdir(d)]
        
        if invalid_directories:
            invalid_list = "\n".join(invalid_directories)
            QMessageBox.warning(
                self,
                "警告",
                f"以下目录不存在或无法访问，已跳过：\n\n{invalid_list}",
                QMessageBox.Ok
            )
        
        if not valid_directories:
            QMessageBox.information(
                self,
                "提示",
                "没有有效的ROM目录可以扫描！\n\n请重新添加有效的目录。",
                QMessageBox.Ok
            )
            return
        
        if not self.config.rawg_api_key:
            result = QMessageBox.warning(
                self,
                "警告",
                "未设置RAWG API Key，将无法进行刮削！\n\n是否继续扫描？",
                QMessageBox.Yes | QMessageBox.No
            )
            if result == QMessageBox.No:
                return
        
        self.status_label.setText("正在扫描ROM文件...")
        self._clear_games()
        
        all_games = []
        for directory in valid_directories:
            try:
                games = self.scanner.scan_directory(directory, recursive=True)
                all_games.extend(games)
            except Exception as e:
                print(f"扫描目录失败 {directory}: {e}")
                import traceback
                traceback.print_exc()
        
        self.games = all_games
        
        for game in self.games:
            self.game_list_widget.add_game(game)
        
        self._update_counts()
        self.status_label.setText(f"扫描完成！共发现 {len(self.games)} 个游戏文件")
        self.scrape_all_btn.setEnabled(len(self.games) > 0)
    
    def _clear_games(self):
        """清空游戏列表"""
        self.games.clear()
        self.scanner.clear()
        self.game_list_widget.clear_games()
        self.detail_panel.set_game(None)
        self._update_counts()
        self.scrape_all_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
    
    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self)
        dialog.exec_()
        
        if self.config.rawg_api_key:
            self.api_key_status.setText("API Key: 已设置 ✓")
        else:
            self.api_key_status.setText("API Key: 未设置")
    
    def _on_download_video_changed(self, state):
        """下载视频选项改变"""
        self.config.download_video = (state == Qt.Checked)
    
    def _on_screenshot_count_changed(self, value):
        """截图数量改变"""
        self.config.screenshot_count = value
    
    def _on_game_selected(self, game):
        """游戏选中"""
        self.detail_panel.set_game(game)
    
    def _on_selection_changed(self, games):
        """选择改变"""
        self.scrape_selected_btn.setText(f"刮削选中 ({len(games)})")
        self.scrape_selected_btn.setEnabled(len(games) > 0 and not self.is_scraping)
    
    def _scrape_selected(self):
        """刮削选中的游戏"""
        games = self.game_list_widget.get_selected_games()
        if not games:
            return
        
        self._start_scrape(games)
    
    def _scrape_all(self):
        """刮削全部游戏"""
        games = self.game_list_widget.get_all_games()
        if not games:
            return
        
        unscraped = [g for g in games if not g.is_scraped] if self.config.get('auto_skip_scraped', True) else games
        
        if not unscraped:
            QMessageBox.information(self, "提示", "所有游戏都已刮削完成！", QMessageBox.Ok)
            return
        
        self._start_scrape(unscraped)
    
    def _start_scrape(self, games):
        """开始刮削"""
        if not self.config.rawg_api_key:
            QMessageBox.warning(
                self,
                "警告",
                "请先设置RAWG API Key！\n\n点击右侧'设置'按钮进行设置。",
                QMessageBox.Ok
            )
            return
        
        self.is_scraping = True
        self._update_scrape_ui(True)
        
        self.scrape_worker = ScrapeWorker(games, self.config, self)
        self.scrape_worker.progress.connect(self._on_scrape_progress)
        self.scrape_worker.finished.connect(self._on_scrape_finished)
        self.scrape_worker.start()
    
    def _stop_scrape(self):
        """停止刮削"""
        if self.scrape_worker and self.is_scraping:
            self.scrape_worker.stop()
            self.is_scraping = False
            self._update_scrape_ui(False)
            self.status_label.setText("刮削已停止")
    
    def _on_scrape_progress(self, current, total, message):
        """刮削进度更新"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"进度: {current}/{total}")
        self.current_game_label.setText(message)
        self.status_label.setText(message)
    
    def _on_scrape_finished(self, results):
        """刮削完成"""
        self.is_scraping = False
        self._update_scrape_ui(False)
        
        success_count = sum(1 for _, success, _ in results if success)
        fail_count = len(results) - success_count
        
        for game, success, error in results:
            if success:
                self.game_list_widget.update_game(game)
            else:
                game.is_scraped = False
                game.scrape_error = error
        
        self._update_counts()
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("完成")
        self.current_game_label.setText("")
        
        self.status_label.setText(f"刮削完成！成功: {success_count}, 失败: {fail_count}")
        
        if fail_count > 0:
            self.export_btn.setEnabled(success_count > 0)
            QMessageBox.information(
                self,
                "刮削完成",
                f"刮削完成！\n\n成功: {success_count}\n失败: {fail_count}\n\n失败的游戏未添加到导出列表。",
                QMessageBox.Ok
            )
        else:
            self.export_btn.setEnabled(success_count > 0)
            QMessageBox.information(
                self,
                "刮削完成",
                f"全部 {success_count} 个游戏刮削成功！",
                QMessageBox.Ok
            )
    
    def _update_scrape_ui(self, scraping):
        """更新刮削相关UI状态"""
        self.scrape_all_btn.setEnabled(not scraping and len(self.games) > 0)
        self.scrape_selected_btn.setEnabled(not scraping)
        self.stop_btn.setEnabled(scraping)
        
        selected_count = len(self.game_list_widget.get_selected_games())
        if not scraping:
            self.scrape_selected_btn.setText(f"刮削选中 ({selected_count})")
    
    def _update_counts(self):
        """更新计数"""
        total = len(self.games)
        scraped = sum(1 for g in self.games if g.is_scraped)
        self.games_count_label.setText(f"游戏: {total} | 已刮削: {scraped}")
    
    def _export(self):
        """导出到目录"""
        scraped_games = [g for g in self.games if g.is_scraped]
        
        if not scraped_games:
            QMessageBox.information(
                self,
                "提示",
                "没有已刮削的游戏可以导出！",
                QMessageBox.Ok
            )
            return
        
        output_dir = self.config.output_directory
        
        if not output_dir or not os.path.isdir(output_dir):
            result = QMessageBox.question(
                self,
                "选择输出目录",
                "未设置输出目录，是否现在选择？",
                QMessageBox.Yes | QMessageBox.No
            )
            if result == QMessageBox.Yes:
                output_dir = QFileDialog.getExistingDirectory(
                    self,
                    "选择输出目录",
                    ""
                )
                if output_dir:
                    self.config.output_directory = output_dir
                else:
                    return
            else:
                return
        
        self.status_label.setText("正在导出...")
        
        writer = MetadataWriter(output_dir)
        metadata_path, failed = writer.generate_metadata(scraped_games, copy_files=True)
        
        if failed:
            writer.write_failed_list([g for g in scraped_games if g.scrape_error])
        
        self.config.set('last_export_path', output_dir)
        
        self.status_label.setText(f"导出完成！")
        
        result_msg = f"导出完成！\n\n输出目录: {output_dir}\n\n生成文件:\n- metadata.pegasus.txt\n- images/ (封面和截图)\n- videos/ (预告片)"
        
        if failed:
            result_msg += f"\n\n警告: {len(failed)} 个文件处理失败"
        
        QMessageBox.information(self, "导出完成", result_msg, QMessageBox.Ok)
