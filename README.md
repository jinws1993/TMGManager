# 天马G游戏ROM管理工具

Windows 桌面应用程序，用于管理模拟器游戏 ROM，自动刮削游戏封面、截图和视频，生成天马G/Pegasus Frontend 兼容的 metadata.pegasus.txt 文件。

## 功能

- 📁 扫描ROM目录（支持17种格式）
- 🔍 RAWG API 自动刮削游戏信息
- 🖼️ 下载封面、截图、预告片
- 📝 生成 metadata.pegasus.txt
- 📋 导出到SD卡
- 🌙 深色主题界面

## 运行方式

### Python 环境
```bash
pip install PyQt5 requests beautifulsoup4 lxml
python main.py
```

### 打包的 EXE
直接运行 `dist/PegasusROMManager.exe`

## 使用步骤

1. 获取 RAWG API Key：https://rawg.io/apidocs
2. 添加ROM目录
3. 扫描游戏
4. 设置API Key并刮削
5. 导出到SD卡

## 支持的ROM格式

nes, smc, sfc, gb, gbc, gba, nds, 3ds, cia, iso, bin, chd, pce, psp, zip, 7z, rar