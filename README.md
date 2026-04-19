## 项目介绍
Game Start 是基于 Python Tkinter 制作的个人兴趣软件，功能不完善，仅仅支持自定义添加 Windows 应用程序快捷启动、背景切换、图标自定义等功能，其余功能想到再说。

## 功能特性
1. **游戏自动检测**：默认自动扫描系统注册表，识别已安装的米哈游启动器
2. **自定义程序添加**：支持手动添加任意 `.exe` 程序快捷启动，支持图标自定义
3. **快捷启动**：点击图标一键启动对应程序/游戏
4. **右键菜单**：全局右键菜单支持显示/查找/帮助，实际上有用的只有对游戏图标的右键菜单有用，支持更换图标、删除、恢复默认图标
5. **快捷键支持**：以后有能力再添加功能，实际上只是弹出一个窗口

## 环境要求
- 操作系统：Windows (仅支持Windows，因使用了winreg、ctypes等Windows专属API)
- Python 版本：3.10+
- 依赖库：
- tkinter (Python 内置，一般随 Python 安装)
- pillow (PIL)
- tomli （3.11+及以上默认安装tomllib）
- tomli-w
- 安装方式：在对应的python环境终端中输入 pip install pillow tomli tomli-w

- 目录结构
- game-start/
├── Game_Start_v2.py       # 主程序入口
├── utils.py               # 工具类（配置文件读写、路径处理）
├── config/                # 配置目录
│   └── config.toml        # 项目自带配置文件（无需自动生成）
├── background/            # 背景图片目录（需自行放置图片）
├── win_pic/               # 窗口图片目录（需自行放置图片）
├── pic_cache/             # 图标缓存目录（自动生成）
├── cache/                 # 系统缓存目录（自动生成）
└── start_rail/            # 一些自己游玩的游戏角色信息目录（可更改，程序中通过注释掉    for Character in Message_list: button_list.append(buttons(Win_frame.button_frame, Character))可以关闭对应功能）
    ├── roal_message.txt   # 一些自己游玩的游戏角色信息
    └── url.txt            # 一些自己游玩的游戏角色PV链接

常见问题
启动添加游戏时无权限问题，需要以管理员身份启动编译器（调试时）/以管理员身份启动打包后的程序
图标提取失败：部分 exe 文件无内置图标，程序会自动使用默认图标，可手动更换
游戏检测不到：确保游戏已正常安装（注册表有对应记录），或手动添加启动器路径
配置文件异常：项目自带 config/config.toml，若损坏可从项目仓库重新获取
背景图片不显示：确保图片格式为 jpg/png/gif，且路径无中文 / 特殊字符

开发说明
核心技术：Tkinter（GUI）、PIL（图片处理）、winreg（注册表读取）、ctypes（图标提取）、threading（多线程避免界面卡顿）
打包建议：使用 PyInstaller 打包为目录，需注意资源路径处理（resource_path 函数已适配）

免责声明
本项目仅为个人学习开发使用，请勿用于商业用途
项目中涉及的游戏、角色等版权均归米哈游所有
使用本程序时请遵守相关法律法规及软件使用协议
