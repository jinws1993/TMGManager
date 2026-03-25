# -*- coding: utf-8 -*-
"""游戏列表组件"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont


class GameListItemDelegate(QStyledItemDelegate):
    """游戏列表项委托"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_bg = QColor('#2d2d2d')
        self.light_bg = QColor('#252526')
        self.selected_bg = QColor('#094771')
        self.text_color = QColor('#cccccc')
        self.scraped_color = QColor('#4ec9b0')
        self.unscraped_color = QColor('#808080')
        self.platform_color = QColor('#569cd6')
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.save()
        
        # 获取游戏数据 - 通过 QListWidget 而不是 model
        try:
            row = index.row()
            # 通过父组件获取 item
            list_widget = self.parent()
            if list_widget and hasattr(list_widget, 'list_widget'):
                item = list_widget.list_widget.item(row)
            else:
                item = None
            
            if item is None:
                painter.restore()
                return
            
            game_data = item.data(Qt.UserRole)
        except Exception as e:
            painter.restore()
            return
        
        if game_data is None:
            painter.restore()
            return
        
        if option.state & QStyle.State_Selected:
            bg_color = self.selected_bg
        elif option.state & QStyle.State_MouseOver:
            bg_color = self.dark_bg
        else:
            bg_color = self.light_bg if index.row() % 2 == 0 else self.dark_bg
        
        painter.fillRect(option.rect, bg_color)
        
        rect = option.rect
        padding = 10
        left = rect.left() + padding
        top = rect.top() + 8
        
        painter.setPen(self.text_color)
        font = QFont("Microsoft YaHei UI")
        
        name_font = QFont(font)
        name_font.setPointSize(10)
        name_font.setBold(True)
        painter.setFont(name_font)
        
        display_name = game_data.get('display_name', 'Unknown')
        platform = game_data.get('platform', '')
        is_scraped = game_data.get('is_scraped', False)
        
        painter.drawText(left, top, display_name)
        
        status_text = "✓" if is_scraped else "○"
        status_color = self.scraped_color if is_scraped else self.unscraped_color
        painter.setPen(status_color)
        painter.drawText(rect.right() - padding - 15, top, status_text)
        
        painter.setPen(self.platform_color)
        platform_font = QFont(font)
        platform_font.setPointSize(8)
        painter.setFont(platform_font)
        painter.drawText(left, top + 18, platform)
        
        painter.restore()
    
    def sizeHint(self, option: QStyleOptionViewItem, index):
        return QSize(option.rect.width(), 50)


class GameListWidget(QWidget):
    """游戏列表组件"""
    
    game_selected = pyqtSignal(object)
    games_selection_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.list_widget.setItemDelegate(GameListItemDelegate(self))
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.list_widget)
    
    def add_game(self, game):
        """添加游戏到列表"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, {
            'game': game,
            'display_name': game.display_name,
            'platform': game.platform,
            'is_scraped': game.is_scraped,
            'file_path': game.file_path,
        })
        item.setSizeHint(QSize(200, 50))
        self.list_widget.addItem(item)
    
    def update_game(self, game):
        """更新游戏信息"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if data['game'].id == game.id:
                item.setData(Qt.UserRole, {
                    'game': game,
                    'display_name': game.display_name,
                    'platform': game.platform,
                    'is_scraped': game.is_scraped,
                    'file_path': game.file_path,
                })
                break
    
    def clear_games(self):
        """清空游戏列表"""
        self.list_widget.clear()
    
    def get_selected_games(self):
        """获取选中的游戏列表"""
        games = []
        for item in self.list_widget.selectedItems():
            data = item.data(Qt.UserRole)
            if data:
                games.append(data['game'])
        return games
    
    def select_all(self):
        """全选"""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(True)
    
    def deselect_all(self):
        """取消全选"""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(False)
    
    def get_all_games(self):
        """获取所有游戏"""
        games = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if data:
                games.append(data['game'])
        return games
    
    def _on_item_clicked(self, item):
        """项点击事件"""
        data = item.data(Qt.UserRole)
        if data:
            self.game_selected.emit(data['game'])
    
    def _on_selection_changed(self):
        """选择改变事件"""
        games = self.get_selected_games()
        self.games_selection_changed.emit(games)
