# -*- coding: utf-8 -*-
"""设置对话框组件"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QCheckBox, QSpinBox, QFormLayout,
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._load_settings()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        api_group = QGroupBox("API 设置")
        api_layout = QFormLayout(api_group)
        
        # RAWG API Key
        rawg_label = QLabel("RAWG API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入您的RAWG API Key")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow(rawg_label, self.api_key_edit)
        
        rawg_help = QLabel("获取RAWG Key: <a href='https://rawg.io/apidocs'>https://rawg.io/apidocs</a>")
        rawg_help.setOpenExternalLinks(True)
        api_layout.addRow("", rawg_help)
        
        # TheGamesDB API Key
        tgdb_label = QLabel("TheGamesDB Key:")
        self.tgdb_key_edit = QLineEdit()
        self.tgdb_key_edit.setPlaceholderText("(可选) 输入TheGamesDB API Key")
        self.tgdb_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow(tgdb_label, self.tgdb_key_edit)
        
        tgdb_help = QLabel("获取TGDB Key: <a href='https://thegamesdb.net/register.php'>https://thegamesdb.net</a>")
        tgdb_help.setOpenExternalLinks(True)
        api_layout.addRow("", tgdb_help)
        
        main_layout.addWidget(api_group)
        
        scrape_group = QGroupBox("刮削选项")
        scrape_layout = QVBoxLayout(scrape_group)
        
        self.download_video_cb = QCheckBox("下载预告片视频")
        scrape_layout.addWidget(self.download_video_cb)
        
        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("截图数量:"))
        self.screenshot_count_spin = QSpinBox()
        self.screenshot_count_spin.setMinimum(1)
        self.screenshot_count_spin.setMaximum(10)
        self.screenshot_count_spin.setValue(3)
        screenshot_layout.addWidget(self.screenshot_count_spin)
        screenshot_layout.addStretch()
        scrape_layout.addLayout(screenshot_layout)
        
        self.skip_scraped_cb = QCheckBox("跳过已刮削的游戏")
        self.skip_scraped_cb.setChecked(True)
        scrape_layout.addWidget(self.skip_scraped_cb)
        
        main_layout.addWidget(scrape_group)
        
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout(output_group)
        
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("选择输出目录...")
        self.output_dir_edit.setReadOnly(True)
        output_dir_layout.addWidget(self.output_dir_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(browse_btn)
        
        output_layout.addRow("输出目录:", output_dir_layout)
        
        main_layout.addWidget(output_group)
        
        # 代理设置组
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QVBoxLayout(proxy_group)
        
        self.proxy_enabled_cb = QCheckBox("启用代理")
        self.proxy_enabled_cb.stateChanged.connect(self._on_proxy_enabled_changed)
        proxy_layout.addWidget(self.proxy_enabled_cb)
        
        proxy_url_layout = QHBoxLayout()
        proxy_url_layout.addWidget(QLabel("代理地址:"))
        self.proxy_url_edit = QLineEdit()
        self.proxy_url_edit.setPlaceholderText("http://192.168.31.143:7890")
        self.proxy_url_edit.setEnabled(False)
        proxy_url_layout.addWidget(self.proxy_url_edit)
        
        self.test_proxy_btn = QPushButton("测试代理")
        self.test_proxy_btn.clicked.connect(self._test_proxy)
        self.test_proxy_btn.setEnabled(False)
        proxy_url_layout.addWidget(self.test_proxy_btn)
        
        proxy_layout.addLayout(proxy_url_layout)
        
        proxy_help = QLabel("格式: http://host:port 或 socks5://host:port")
        proxy_layout.addWidget(proxy_help)
        
        main_layout.addWidget(proxy_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
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
            QLineEdit {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QCheckBox {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
            }
            QSpinBox {
                font-family: "Microsoft YaHei UI";
                font-size: 9pt;
                color: #cccccc;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
        """)
    
    def _load_settings(self):
        """加载设置"""
        self.api_key_edit.setText(self.config.rawg_api_key)
        self.tgdb_key_edit.setText(self.config.tgdb_api_key)
        self.download_video_cb.setChecked(self.config.download_video)
        self.screenshot_count_spin.setValue(self.config.screenshot_count)
        self.skip_scraped_cb.setChecked(self.config.get('auto_skip_scraped', True))
        self.output_dir_edit.setText(self.config.output_directory)
        
        # 加载代理设置
        self.proxy_enabled_cb.setChecked(self.config.proxy_enabled)
        self.proxy_url_edit.setText(self.config.proxy_url)
        self.proxy_url_edit.setEnabled(self.config.proxy_enabled)
        self.test_proxy_btn.setEnabled(self.config.proxy_enabled)
    
    def _save_and_accept(self):
        """保存设置并关闭"""
        if not self.api_key_edit.text() and not self.tgdb_key_edit.text():
            QMessageBox.warning(
                self,
                "警告",
                "请至少输入一个API Key！\n\nRAWG 或 TheGamesDB 至少需要一个才能进行刮削。",
                QMessageBox.Ok
            )
            return
        
        self.config.rawg_api_key = self.api_key_edit.text()
        self.config.tgdb_api_key = self.tgdb_key_edit.text()
        self.config.download_video = self.download_video_cb.isChecked()
        self.config.screenshot_count = self.screenshot_count_spin.value()
        self.config.set('auto_skip_scraped', self.skip_scraped_cb.isChecked())
        
        if self.output_dir_edit.text():
            self.config.output_directory = self.output_dir_edit.text()
        
        # 保存代理设置
        self.config.proxy_enabled = self.proxy_enabled_cb.isChecked()
        self.config.proxy_url = self.proxy_url_edit.text().strip()
        
        self.accept()
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.config.output_directory or ""
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def _on_proxy_enabled_changed(self, state):
        """代理启用状态改变"""
        enabled = (state == Qt.Checked)
        self.proxy_url_edit.setEnabled(enabled)
        self.test_proxy_btn.setEnabled(enabled)
    
    def _test_proxy(self):
        """测试代理连接"""
        proxy_url = self.proxy_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        
        if not proxy_url:
            QMessageBox.warning(self, "警告", "请输入代理地址！", QMessageBox.Ok)
            return
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请先设置RAWG API Key！", QMessageBox.Ok)
            return
        
        # 创建临时scraper测试代理
        from scraper import RAWGSraper
        scraper = RAWGSraper(api_key, proxy_url)
        success, message = scraper.test_proxy_connection()
        
        if success:
            QMessageBox.information(self, "测试结果", message, QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "测试结果", message, QMessageBox.Ok)
