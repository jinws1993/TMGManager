# -*- coding: utf-8 -*-
"""天马G游戏ROM管理工具 - 入口文件"""

import sys
import os
import traceback
import logging
from datetime import datetime

# 设置日志
log_dir = os.path.join(os.path.expanduser('~'), '.pegasus_rom_manager')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'error.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def exception_hook(exc_type, exc_value, exc_tb):
    """全局异常捕获"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.error(f"Uncaught exception:\n{error_msg}")
    print(f"\n=== UNCAUGHT EXCEPTION ===\n{error_msg}", file=sys.stderr)
    
    # 显示错误对话框
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "错误", f"程序发生错误:\n\n{exc_value}\n\n详细信息已保存到:\n{log_file}")
    except:
        pass
    
    sys.exit(1)

sys.excepthook = exception_hook


def main():
    """主函数"""
    try:
        logging.info("Starting application...")
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        app = QApplication(sys.argv)
        app.setApplicationName("天马G游戏ROM管理工具")
        app.setOrganizationName("PegasusROMManager")
        
        app.setStyle('Fusion')
        
        logging.info("Creating main window...")
        from main_window import MainWindow
        
        window = MainWindow()
        window.show()
        # 强制立即刷新显示，避免频闪
        app.processEvents()
        logging.info("Window shown, starting event loop...")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"Error in main: {e}\n{traceback.format_exc()}")
        print(f"\n=== MAIN ERROR ===\n{e}\n{traceback.format_exc()}", file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
